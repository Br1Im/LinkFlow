# -*- coding: utf-8 -*-
"""
ИСПРАВЛЕННЫЙ webhook сервер - обрабатывает curl КАК fetch
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import uuid
import time
from datetime import datetime
import threading
import logging

# Импорты из bot директории
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'bot'))

from database import Database
from webhook_config import API_TOKEN, CARD_NUMBER, CARD_OWNER, SERVER_HOST, SERVER_PORT, SERVER_URL
from payment_service import create_payment_fast, warmup_for_user, is_browser_ready

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins="*", methods=["GET", "POST", "OPTIONS"], 
     allow_headers=["Content-Type", "Authorization"])

db = Database()

# Глобальная блокировка для синхронизации запросов
request_lock = threading.Lock()
last_request_time = 0
browser_warmed_up = False

def verify_token(token):
    return token == f"Bearer {API_TOKEN}"

def ensure_browser_ready():
    """Убеждаемся что браузер готов к работе"""
    global browser_warmed_up
    
    if not browser_warmed_up or not is_browser_ready():
        logger.info("🔥 Прогреваю браузер для работы...")
        
        user_id = 1  # Фиктивный user_id для webhook
        warmup_result = warmup_for_user(user_id)
        
        if warmup_result.get('success'):
            browser_warmed_up = True
            logger.info("✅ Браузер прогрет и готов!")
            return True
        else:
            logger.error(f"❌ Не удалось прогреть браузер: {warmup_result}")
            return False
    
    return True

@app.route('/api/payment', methods=['POST', 'OPTIONS'])
def create_payment():
    global last_request_time
    
    if request.method == 'OPTIONS':
        return '', 200
    
    # СИНХРОНИЗАЦИЯ - обрабатываем запросы по очереди
    with request_lock:
        try:
            current_time = time.time()
            
            # Логируем информацию о запросе
            user_agent = request.headers.get('User-Agent', 'Unknown')
            logger.info(f"📨 Новый запрос: User-Agent={user_agent}")
            
            # Проверка авторизации
            auth_header = request.headers.get('Authorization')
            if not auth_header or not verify_token(auth_header):
                logger.warning(f"❌ Неавторизованный запрос")
                return jsonify({"success": False, "error": "Unauthorized"}), 401
            
            # Проверка Content-Type
            if request.content_type != 'application/json':
                logger.warning(f"❌ Неверный Content-Type: {request.content_type}")
                return jsonify({"success": False, "error": "Content-Type must be application/json"}), 400
            
            # Получение данных
            data = request.get_json()
            if not data:
                logger.warning("❌ Пустой JSON")
                return jsonify({"success": False, "error": "Invalid JSON"}), 400
            
            amount = data.get('amount')
            order_id = data.get('orderId')
            
            # Валидация
            if not amount or not order_id:
                logger.warning(f"❌ Отсутствуют поля: amount={amount}, orderId={order_id}")
                return jsonify({"success": False, "error": "Missing required fields: amount, orderId"}), 400
            
            if not isinstance(amount, (int, float)) or amount <= 0:
                logger.warning(f"❌ Неверная сумма: {amount}")
                return jsonify({"success": False, "error": "Amount must be a positive number"}), 400
            
            # Проверка дублирования заказа
            existing_order = db.get_order_by_id(order_id)
            if existing_order:
                logger.warning(f"❌ Заказ уже существует: {order_id}")
                return jsonify({"success": False, "error": "Order already exists"}), 409
            
            logger.info(f"🚀 Создание платежа: orderId={order_id}, amount={amount}")
            
            # Убеждаемся что браузер готов
            if not ensure_browser_ready():
                return jsonify({"success": False, "error": "Browser warmup failed"}), 500
            
            # Пауза между запросами для стабильности
            time_since_last = current_time - last_request_time
            if time_since_last < 2.0:  # Минимум 2 секунды между запросами
                sleep_time = 2.0 - time_since_last
                logger.info(f"⏳ Пауза {sleep_time:.1f}s для стабильности браузера...")
                time.sleep(sleep_time)
            
            # Создание платежа через payment_service (КАК В БОТЕ)
            logger.info("💳 Создаю платеж через браузер...")
            result = create_payment_fast(amount, send_callback=None)
            
            last_request_time = time.time()
            
            if not result or not result.get('payment_link'):
                error_msg = result.get('error', 'Unknown error') if result else 'No result returned'
                logger.error(f"❌ Платеж не удался: {error_msg}")
                return jsonify({"success": False, "error": f"Payment creation failed: {error_msg}"}), 500
            
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
                "method": result.get('method', 'browser'),
                "elapsed_time": result.get('elapsed_time', 0),
                "user_agent": user_agent
            }
            
            db.save_order(order_data)
            
            logger.info(f"✅ Платеж создан: orderId={order_id}, qrcId={qrc_id}, время={result.get('elapsed_time', 0):.1f}s")
            
            return jsonify({
                "success": True,
                "orderId": order_id,
                "qrcId": qrc_id,
                "qr": result.get('payment_link', ''),
                "method": result.get('method', 'browser'),
                "elapsed_time": result.get('elapsed_time', 0),
                "curl_compatible": True
            }), 200
            
        except Exception as e:
            logger.error(f"❌ Неожиданная ошибка: {str(e)}")
            return jsonify({"success": False, "error": "Internal server error"}), 500

@app.route('/api/status/<order_id>', methods=['GET', 'OPTIONS'])
def get_payment_status(order_id):
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not verify_token(auth_header):
            return jsonify({"success": False, "error": "Unauthorized"}), 401
        
        order = db.get_order_by_id(order_id)
        if not order:
            return jsonify({"success": False, "error": "Order not found"}), 404
        
        return jsonify({
            "success": True,
            "orderId": order['order_id'],
            "status": order['status'],
            "amount": order['amount'],
            "createdAt": order['created_at'],
            "paymentLink": order.get('payment_link', ''),
            "method": order.get('method', 'unknown')
        }), 200
        
    except Exception as e:
        logger.error(f"Ошибка получения статуса: {str(e)}")
        return jsonify({"success": False, "error": "Internal server error"}), 500

@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health_check():
    if request.method == 'OPTIONS':
        return '', 200
        
    browser_status = "ready" if is_browser_ready() else "not_ready"
    
    return jsonify({
        "success": True,
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "browser_status": browser_status,
        "mode": "curl_fixed_synchronized",
        "features": [
            "curl_compatible",
            "fetch_compatible", 
            "synchronized_requests",
            "browser_warmup",
            "real_payments"
        ]
    }), 200

if __name__ == '__main__':
    print("🚀 Запуск ИСПРАВЛЕННОГО webhook сервера...")
    print(f"📡 API endpoint: {SERVER_URL}/api/payment")
    print(f"🔑 Token: {API_TOKEN}")
    print(f"💳 Card: {CARD_NUMBER}")
    print(f"👤 Owner: {CARD_OWNER}")
    print("✅ CURL = FETCH - одинаковая обработка")
    print("🔄 СИНХРОНИЗАЦИЯ запросов")
    print("🔥 АВТОМАТИЧЕСКИЙ прогрев браузера")
    print("⏳ ПАУЗА между запросами для стабильности")
    print("🌐 CORS включен для всех доменов")
    
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=False)