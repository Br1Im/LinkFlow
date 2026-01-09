# -*- coding: utf-8 -*-
"""
Webhook сервер с использованием существующей автоматизации
Использует HybridPaymentManager для автоматического создания платежей
"""

from flask import Flask, request, jsonify
import json
import uuid
import time
from datetime import datetime
from database import Database
from webhook_config import API_TOKEN, CARD_NUMBER, CARD_OWNER, SERVER_HOST, SERVER_PORT, SERVER_URL
from hybrid_payment import HybridPaymentManager
import logging
import threading

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
db = Database()

# Глобальный менеджер платежей
payment_manager = None
manager_lock = threading.Lock()

# Данные аккаунта для авторизации
ACCOUNT_DATA = {
    "phone": "+79880260334",
    "password": "xowxut-wemhej-3zAsno",
    "profile_path": "profile_79880260334"
}

def get_payment_manager():
    """Получение авторизованного менеджера платежей"""
    global payment_manager
    
    with manager_lock:
        if payment_manager is None or not payment_manager.is_authorized:
            logger.info("Создание нового менеджера платежей...")
            
            # Закрываем старый если есть
            if payment_manager:
                try:
                    payment_manager.close()
                except:
                    pass
            
            # Создаем новый
            payment_manager = HybridPaymentManager()
            
            # Авторизуемся
            if not payment_manager.authorize_and_get_cookies(ACCOUNT_DATA):
                logger.error("Ошибка авторизации менеджера платежей")
                payment_manager = None
                return None
            
            logger.info("Менеджер платежей авторизован успешно")
        
        return payment_manager

def verify_token(token):
    """Проверка Bearer токена"""
    return token == f"Bearer {API_TOKEN}"

@app.route('/api/payment', methods=['POST'])
def create_payment():
    """Создание платежа через гибридную автоматизацию"""
    try:
        # Проверка авторизации
        auth_header = request.headers.get('Authorization')
        if not auth_header or not verify_token(auth_header):
            return jsonify({
                "success": False,
                "error": "Unauthorized"
            }), 401
        
        # Проверка Content-Type
        if request.content_type != 'application/json':
            return jsonify({
                "success": False,
                "error": "Content-Type must be application/json"
            }), 400
        
        # Получение данных
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "Invalid JSON"
            }), 400
        
        amount = data.get('amount')
        order_id = data.get('orderId')
        
        # Валидация
        if not amount or not order_id:
            return jsonify({
                "success": False,
                "error": "Missing required fields: amount, orderId"
            }), 400
        
        if not isinstance(amount, (int, float)) or amount <= 0:
            return jsonify({
                "success": False,
                "error": "Amount must be a positive number"
            }), 400
        
        # Проверка дублирования заказа
        existing_order = db.get_order_by_id(order_id)
        if existing_order:
            return jsonify({
                "success": False,
                "error": "Order already exists"
            }), 409
        
        logger.info(f"Creating payment via hybrid automation: orderId={order_id}, amount={amount}")
        
        # Получаем менеджер платежей
        manager = get_payment_manager()
        if not manager:
            return jsonify({
                "success": False,
                "error": "Payment manager not available"
            }), 500
        
        # Создание платежа через гибридную автоматизацию
        result = manager.create_payment_fast(
            card_number=CARD_NUMBER,
            owner_name=CARD_OWNER,
            amount=float(amount)
        )
        
        if not result.get('success'):
            logger.error(f"Hybrid payment failed: {result.get('error')}")
            
            # Пробуем пересоздать менеджер при ошибке
            with manager_lock:
                if payment_manager:
                    try:
                        payment_manager.close()
                    except:
                        pass
                    payment_manager = None
            
            return jsonify({
                "success": False,
                "error": f"Payment creation failed: {result.get('error')}"
            }), 500
        
        # Генерация уникального QRC ID
        qrc_id = f"QR{int(time.time())}{uuid.uuid4().hex[:8].upper()}"
        
        # Сохранение заказа в базу данных
        order_data = {
            "order_id": order_id,
            "qrc_id": qrc_id,
            "amount": amount,
            "payment_link": result.get('payment_link', ''),
            "qr_base64": result.get('qr_base64', ''),
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "method": "hybrid_automation",
            "elapsed_time": result.get('elapsed_time', 0)
        }
        
        db.save_order(order_data)
        
        logger.info(f"Payment created successfully: orderId={order_id}, qrcId={qrc_id}, time={result.get('elapsed_time', 0):.2f}s")
        
        # Возврат результата
        return jsonify({
            "success": True,
            "orderId": order_id,
            "qrcId": qrc_id,
            "qr": result.get('payment_link', '')
        }), 200
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500

@app.route('/api/status/<order_id>', methods=['GET'])
def get_payment_status(order_id):
    """Получение статуса платежа"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not verify_token(auth_header):
            return jsonify({
                "success": False,
                "error": "Unauthorized"
            }), 401
        
        order = db.get_order_by_id(order_id)
        if not order:
            return jsonify({
                "success": False,
                "error": "Order not found"
            }), 404
        
        return jsonify({
            "success": True,
            "orderId": order['order_id'],
            "status": order['status'],
            "amount": order['amount'],
            "createdAt": order['created_at']
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Проверка работоспособности сервера"""
    return jsonify({
        "success": True,
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "payment_manager_status": "authorized" if payment_manager and payment_manager.is_authorized else "not_authorized"
    }), 200

@app.route('/webhook/nspk', methods=['POST'])
def nspk_callback():
    """Callback от НСПК для автоматического закрытия платежей"""
    try:
        data = request.get_json()
        logger.info(f"NSPK callback received: {data}")
        
        # Здесь обработка callback от НСПК
        # Обновление статуса заказа в базе данных
        
        return jsonify({
            "success": True,
            "message": "Callback processed"
        }), 200
        
    except Exception as e:
        logger.error(f"NSPK callback error: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Callback processing failed"
        }), 500

# Graceful shutdown
import atexit

def cleanup():
    """Очистка ресурсов при завершении"""
    global payment_manager
    if payment_manager:
        try:
            payment_manager.close()
        except:
            pass

atexit.register(cleanup)

if __name__ == '__main__':
    print("🚀 Запуск webhook сервера с гибридной автоматизацией...")
    print(f"📡 API endpoint: {SERVER_URL}/api/payment")
    print(f"🔑 Token: {API_TOKEN}")
    print(f"💳 Card: {CARD_NUMBER}")
    print(f"👤 Owner: {CARD_OWNER}")
    print(f"📱 Account: {ACCOUNT_DATA['phone']}")
    print("🤖 Используется HybridPaymentManager для автоматического создания платежей")
    
    app.run(
        host=SERVER_HOST,
        port=SERVER_PORT,
        debug=False
    )