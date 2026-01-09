#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой HTTP webhook сервер БЕЗ Flask - только стандартные библиотеки Python
"""

import json
import uuid
import time
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import logging
import sys
import os

# Добавляем путь к bot модулям
sys.path.append('/home/bot')

try:
    from database import Database
    from webhook_config import API_TOKEN, CARD_NUMBER, CARD_OWNER, SERVER_HOST, SERVER_PORT, SERVER_URL
    from payment_service import create_payment_fast, warmup_for_user, is_browser_ready
    print("✅ Модули бота загружены успешно")
except Exception as e:
    print(f"❌ Ошибка загрузки модулей: {e}")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = Database()

# Глобальная блокировка для синхронизации запросов
request_lock = threading.Lock()
last_request_time = 0

def verify_token(token):
    return token == f"Bearer {API_TOKEN}"

class WebhookHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Обработка CORS preflight запросов"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_POST(self):
        """Обработка POST запросов"""
        global last_request_time
        
        path = urlparse(self.path).path
        
        if path == '/api/payment':
            self.handle_payment()
        elif path.startswith('/api/status/'):
            order_id = path.split('/')[-1]
            self.handle_status(order_id)
        else:
            self.send_error(404, "Not Found")

    def do_GET(self):
        """Обработка GET запросов"""
        path = urlparse(self.path).path
        
        if path == '/api/health':
            self.handle_health()
        elif path.startswith('/api/status/'):
            order_id = path.split('/')[-1]
            self.handle_status(order_id)
        else:
            self.send_error(404, "Not Found")

    def handle_payment(self):
        """Обработка создания платежа"""
        global last_request_time
        
        # СИНХРОНИЗАЦИЯ - обрабатываем запросы по очереди
        with request_lock:
            try:
                # Логируем информацию о запросе
                user_agent = self.headers.get('User-Agent', 'Unknown')
                logger.info(f"📨 Новый запрос: User-Agent={user_agent}")
                
                # Проверка авторизации
                auth_header = self.headers.get('Authorization')
                if not auth_header or not verify_token(auth_header):
                    logger.warning(f"❌ Неавторизованный запрос")
                    self.send_json_response({"success": False, "error": "Unauthorized"}, 401)
                    return
                
                # Проверка Content-Type
                content_type = self.headers.get('Content-Type', '')
                if 'application/json' not in content_type:
                    logger.warning(f"❌ Неверный Content-Type: {content_type}")
                    self.send_json_response({"success": False, "error": "Content-Type must be application/json"}, 400)
                    return
                
                # Получение данных
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length == 0:
                    logger.warning("❌ Пустое тело запроса")
                    self.send_json_response({"success": False, "error": "Empty request body"}, 400)
                    return
                
                post_data = self.rfile.read(content_length)
                try:
                    data = json.loads(post_data.decode('utf-8'))
                except json.JSONDecodeError:
                    logger.warning("❌ Неверный JSON")
                    self.send_json_response({"success": False, "error": "Invalid JSON"}, 400)
                    return
                
                amount = data.get('amount')
                order_id = data.get('orderId')
                
                # Валидация
                if not amount or not order_id:
                    logger.warning(f"❌ Отсутствуют поля: amount={amount}, orderId={order_id}")
                    self.send_json_response({"success": False, "error": "Missing required fields: amount, orderId"}, 400)
                    return
                
                if not isinstance(amount, (int, float)) or amount <= 0:
                    logger.warning(f"❌ Неверная сумма: {amount}")
                    self.send_json_response({"success": False, "error": "Amount must be a positive number"}, 400)
                    return
                
                # Проверка дублирования заказа
                existing_order = db.get_order_by_id(order_id)
                if existing_order:
                    logger.warning(f"❌ Заказ уже существует: {order_id}")
                    self.send_json_response({"success": False, "error": "Order already exists"}, 409)
                    return
                
                logger.info(f"🚀 Создание платежа: orderId={order_id}, amount={amount}")
                
                # Пауза между запросами для стабильности
                current_time = time.time()
                time_since_last = current_time - last_request_time
                if time_since_last < 2.0:  # Минимум 2 секунды между запросами
                    sleep_time = 2.0 - time_since_last
                    logger.info(f"⏳ Пауза {sleep_time:.1f}s для стабильности браузера...")
                    time.sleep(sleep_time)
                
                # Используем ТОЧНО ТАКУЮ ЖЕ логику как в боте
                user_id = 1  # Фиктивный user_id для webhook
                
                # Прогрев браузера (как в боте)
                warmup_result = warmup_for_user(user_id)
                if not warmup_result.get('success'):
                    logger.error(f"Warmup failed: {warmup_result}")
                    self.send_json_response({"success": False, "error": f"Browser warmup failed: {warmup_result.get('error', 'Unknown warmup error')}"}, 500)
                    return
                
                # Создание платежа через payment_service (как в боте)
                result = create_payment_fast(amount, send_callback=None)
                last_request_time = time.time()
                
                if not result or not result.get('payment_link'):
                    error_msg = result.get('error', 'Unknown error') if result else 'No result returned'
                    logger.error(f"❌ Платеж не удался: {error_msg}")
                    self.send_json_response({"success": False, "error": f"Payment creation failed: {error_msg}"}, 500)
                    return
                
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
                    "elapsed_time": result.get('elapsed_time', 0),
                    "user_agent": user_agent
                }
                
                db.save_order(order_data)
                
                logger.info(f"✅ Платеж создан: orderId={order_id}, qrcId={qrc_id}, время={result.get('elapsed_time', 0):.1f}s")
                
                self.send_json_response({
                    "success": True,
                    "orderId": order_id,
                    "qrcId": qrc_id,
                    "qr": result.get('payment_link', ''),
                    "method": "bot_logic",
                    "elapsed_time": result.get('elapsed_time', 0),
                    "curl_fixed": True
                }, 200)
                
            except Exception as e:
                logger.error(f"❌ Неожиданная ошибка: {str(e)}")
                self.send_json_response({"success": False, "error": "Internal server error"}, 500)

    def handle_status(self, order_id):
        """Обработка проверки статуса заказа"""
        try:
            auth_header = self.headers.get('Authorization')
            if not auth_header or not verify_token(auth_header):
                self.send_json_response({"success": False, "error": "Unauthorized"}, 401)
                return
            
            order = db.get_order_by_id(order_id)
            if not order:
                self.send_json_response({"success": False, "error": "Order not found"}, 404)
                return
            
            self.send_json_response({
                "success": True,
                "orderId": order['order_id'],
                "status": order['status'],
                "amount": order['amount'],
                "createdAt": order['created_at'],
                "paymentLink": order.get('payment_link', ''),
                "method": order.get('method', 'unknown')
            }, 200)
            
        except Exception as e:
            logger.error(f"Ошибка получения статуса: {str(e)}")
            self.send_json_response({"success": False, "error": "Internal server error"}, 500)

    def handle_health(self):
        """Обработка health check"""
        browser_status = "ready" if is_browser_ready() else "not_ready"
        
        self.send_json_response({
            "success": True,
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "browser_status": browser_status,
            "mode": "simple_http_synchronized",
            "features": [
                "curl_compatible",
                "fetch_compatible", 
                "synchronized_requests",
                "browser_warmup",
                "real_payments",
                "no_flask_required"
            ]
        }, 200)

    def send_json_response(self, data, status_code=200):
        """Отправка JSON ответа"""
        response = json.dumps(data, ensure_ascii=False, indent=2)
        
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        
        self.wfile.write(response.encode('utf-8'))

    def log_message(self, format, *args):
        """Переопределяем логирование для более красивого вывода"""
        logger.info(f"{self.address_string()} - {format % args}")

def run_server():
    """Запуск HTTP сервера"""
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = HTTPServer(server_address, WebhookHandler)
    
    print("🚀 Запуск ПРОСТОГО HTTP webhook сервера...")
    print(f"📡 API endpoint: {SERVER_URL}/api/payment")
    print(f"🔑 Token: {API_TOKEN}")
    print(f"💳 Card: {CARD_NUMBER}")
    print(f"👤 Owner: {CARD_OWNER}")
    print("✅ CURL СОВМЕСТИМЫЙ - без Flask")
    print("🔄 СИНХРОНИЗАЦИЯ запросов")
    print("⏳ ПАУЗА между запросами для стабильности")
    print("🌐 CORS включен для всех доменов")
    print(f"🚀 Сервер запущен на {SERVER_HOST}:{SERVER_PORT}")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n⏹️ Остановка сервера...")
        httpd.shutdown()

if __name__ == '__main__':
    run_server()