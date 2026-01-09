# -*- coding: utf-8 -*-
"""
Webhook сервер использующий точно такую же логику как Telegram бот
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import uuid
import time
from datetime import datetime
from database import Database
from webhook_config import API_TOKEN, CARD_NUMBER, CARD_OWNER, SERVER_HOST, SERVER_PORT, SERVER_URL
from payment_service import create_payment_fast, warmup_for_user, is_browser_ready
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins="*", methods=["GET", "POST", "OPTIONS"], 
     allow_headers=["Content-Type", "Authorization"])

db = Database()

def verify_token(token):
    return token == f"Bearer {API_TOKEN}"

@app.route('/api/payment', methods=['POST', 'OPTIONS'])
def create_payment():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        # Проверка авторизации
        auth_header = request.headers.get('Authorization')
        if not auth_header or not verify_token(auth_header):
            return jsonify({"success": False, "error": "Unauthorized"}), 401
        
        if request.content_type != 'application/json':
            return jsonify({"success": False, "error": "Content-Type must be application/json"}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Invalid JSON"}), 400
        
        amount = data.get('amount')
        order_id = data.get('orderId')
        
        if not amount or not order_id:
            return jsonify({"success": False, "error": "Missing required fields: amount, orderId"}), 400
        
        if not isinstance(amount, (int, float)) or amount <= 0:
            return jsonify({"success": False, "error": "Amount must be a positive number"}), 400
        
        existing_order = db.get_order_by_id(order_id)
        if existing_order:
            return jsonify({"success": False, "error": "Order already exists"}), 409
        
        logger.info(f"Creating payment via BOT LOGIC: orderId={order_id}, amount={amount}")
        
        # Используем ТОЧНО ТАКУЮ ЖЕ логику как в боте
        user_id = 1  # Фиктивный user_id для webhook
        
        # Прогрев браузера (как в боте)
        warmup_for_user(user_id)
        
        # Создание платежа через payment_service (как в боте)
        result = create_payment_fast(amount, user_id)
        
        if not result.get('success'):
            logger.error(f"Bot logic payment failed: {result.get('error')}")
            return jsonify({"success": False, "error": f"Payment creation failed: {result.get('error')}"}), 500
        
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
            "method": "bot_logic_payment_service",
            "elapsed_time": result.get('elapsed_time', 0)
        }
        
        db.save_order(order_data)
        
        logger.info(f"BOT LOGIC payment created successfully: orderId={order_id}, qrcId={qrc_id}")
        
        return jsonify({
            "success": True,
            "orderId": order_id,
            "qrcId": qrc_id,
            "qr": result.get('payment_link', ''),
            "bot_logic": True
        }), 200
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
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
            "createdAt": order['created_at']
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return jsonify({"success": False, "error": "Internal server error"}), 500

@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health_check():
    if request.method == 'OPTIONS':
        return '', 200
        
    return jsonify({
        "success": True,
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "browser_ready": is_browser_ready()
    }), 200

@app.route('/webhook/nspk', methods=['POST', 'OPTIONS'])
def nspk_callback():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        data = request.get_json()
        logger.info(f"NSPK callback received: {data}")
        return jsonify({"success": True, "message": "Callback processed"}), 200
    except Exception as e:
        logger.error(f"NSPK callback error: {str(e)}")
        return jsonify({"success": False, "error": "Callback processing failed"}), 500

if __name__ == '__main__':
    print("🚀 Запуск webhook сервера (логика Telegram бота)...")
    print(f"📡 API endpoint: {SERVER_URL}/api/payment")
    print(f"🔑 Token: {API_TOKEN}")
    print(f"💳 Card: {CARD_NUMBER}")
    print(f"👤 Owner: {CARD_OWNER}")
    print("🤖 Использует payment_service.py как в Telegram боте")
    print("🌐 CORS включен для всех доменов")
    
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=False)