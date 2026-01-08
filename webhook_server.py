# -*- coding: utf-8 -*-
"""
Webhook сервер для интеграции с платежной системой
Принимает POST запросы и создает QR-коды для оплаты
"""

from flask import Flask, request, jsonify
import json
import uuid
import time
from datetime import datetime
from fast_payment_api import FastPaymentAPI
from database import Database
from webhook_config import API_TOKEN, CARD_NUMBER, CARD_OWNER, SERVER_HOST, SERVER_PORT, SERVER_URL
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# База данных для хранения заказов
db = Database()

def verify_token(token):
    """Проверка Bearer токена"""
    return token == f"Bearer {API_TOKEN}"

@app.route('/api/payment', methods=['POST'])
def create_payment():
    """
    Создание платежа
    
    POST /api/payment
    Headers:
        Authorization: Bearer your-token
        Content-Type: application/json
    
    Body:
        {
            "amount": 100,
            "orderId": "order-id-hash"
        }
    
    Response:
        {
            "success": true,
            "orderId": "order-id-hash",
            "qrcId": "unique-qr-id",
            "qr": "https://qr.nspk.ru/..."
        }
    """
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
        
        logger.info(f"Creating payment: orderId={order_id}, amount={amount}")
        
        # Создание платежа через API
        api = FastPaymentAPI()
        result = api.create_payment(
            card_number=CARD_NUMBER,
            owner_name=CARD_OWNER,
            amount=float(amount)
        )
        
        if not result.get('success'):
            logger.error(f"Payment creation failed: {result.get('error')}")
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
            "payment_link": result['payment_link'],
            "qr_base64": result['qr_base64'],
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "elapsed_time": result.get('elapsed_time', 0)
        }
        
        db.save_order(order_data)
        
        logger.info(f"Payment created successfully: orderId={order_id}, qrcId={qrc_id}")
        
        # Возврат результата
        return jsonify({
            "success": True,
            "orderId": order_id,
            "qrcId": qrc_id,
            "qr": result['payment_link']
        }), 200
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500

@app.route('/api/status/<order_id>', methods=['GET'])
def get_payment_status(order_id):
    """
    Получение статуса платежа
    
    GET /api/status/{orderId}
    Headers:
        Authorization: Bearer your-token
    
    Response:
        {
            "success": true,
            "orderId": "order-id-hash",
            "status": "pending|completed|failed",
            "amount": 100,
            "createdAt": "2024-01-01T12:00:00"
        }
    """
    try:
        # Проверка авторизации
        auth_header = request.headers.get('Authorization')
        if not auth_header or not verify_token(auth_header):
            return jsonify({
                "success": False,
                "error": "Unauthorized"
            }), 401
        
        # Поиск заказа
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
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route('/webhook/nspk', methods=['POST'])
def nspk_callback():
    """
    Callback от НСПК для автоматического закрытия платежей
    
    POST /webhook/nspk
    Body: данные от НСПК о статусе платежа
    """
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

if __name__ == '__main__':
    print("🚀 Запуск webhook сервера...")
    print(f"📡 API endpoint: {SERVER_URL}/api/payment")
    print(f"🔑 Token: {API_TOKEN}")
    print(f"💳 Card: {CARD_NUMBER}")
    print(f"👤 Owner: {CARD_OWNER}")
    
    # Запуск сервера
    app.run(
        host=SERVER_HOST,
        port=SERVER_PORT,
        debug=False      # Продакшн режим
    )