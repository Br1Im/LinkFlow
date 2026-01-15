#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ОПТИМИЗИРОВАННАЯ админ-панель с параллельной обработкой
ЦЕЛЬ: Поддержка частых запросов (1-3s интервал) и ускорение до 8-12s
"""

from flask import Flask, request, jsonify, render_template_string, render_template
from flask_cors import CORS
import json
import uuid
import time
import os
from datetime import datetime
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
import sys

# Добавляем путь для импорта модулей
sys.path.append('/app/bot')

from payment_service import create_payment_fast as create_payment
from database import db

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], 
     allow_headers=["Content-Type", "Authorization"])

# Middleware для логирования всех запросов
@app.before_request
def log_request():
    """Логирование каждого входящего запроса"""
    logger.info(f"📨 ЗАПРОС: {request.method} {request.path}")
    logger.info(f"   IP: {request.remote_addr}")
    logger.info(f"   Headers: {dict(request.headers)}")
    if request.method in ['POST', 'PUT', 'PATCH']:
        try:
            logger.info(f"   Body: {request.get_json()}")
        except:
            logger.info(f"   Body: {request.get_data()}")

@app.after_request
def log_response(response):
    """Логирование каждого ответа"""
    logger.info(f"📤 ОТВЕТ: {request.method} {request.path} -> {response.status_code}")
    return response

# База данных созданных ссылок
payment_links = {}

# Пул потоков для параллельной обработки
executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix="payment_worker")

# Статистика
stats = {
    'total_requests': 0,
    'successful_requests': 0,
    'failed_requests': 0,
    'concurrent_requests': 0,
    'avg_response_time': 0,
    'start_time': time.time()
}
stats_lock = threading.Lock()

def update_stats(success, response_time):
    """Обновление статистики"""
    with stats_lock:
        stats['total_requests'] += 1
        if success:
            stats['successful_requests'] += 1
        else:
            stats['failed_requests'] += 1
        
        # Обновляем среднее время ответа
        if stats['total_requests'] > 1:
            stats['avg_response_time'] = (
                (stats['avg_response_time'] * (stats['total_requests'] - 1) + response_time) 
                / stats['total_requests']
            )
        else:
            stats['avg_response_time'] = response_time

def process_payment_async(request_id, amount, order_id):
    """Асинхронная обработка платежа"""
    start_time = time.time()
    
    with stats_lock:
        stats['concurrent_requests'] += 1
    
    try:
        logger.info(f"🚀 Начинаю обработку платежа {request_id}: {amount} сум")
        
        # Прямой вызов без очереди для максимальной скорости
        result = create_payment(amount)
        
        elapsed = time.time() - start_time
        
        if result and result.get('success'):
            logger.info(f"✅ Платеж {request_id} успешен за {elapsed:.1f}s")
            
            # Сохраняем результат
            payment_data = {
                'id': request_id,
                'amount': amount,
                'order_id': order_id,
                'payment_link': result.get('payment_link'),
                'qr_base64': result.get('qr_base64'),
                'created_at': datetime.now().isoformat(),
                'processing_time': elapsed,
                'status': 'completed'
            }
            
            payment_links[request_id] = payment_data
            update_stats(True, elapsed)
            
            return {
                'success': True,
                'request_id': request_id,
                'order_id': order_id,
                'payment_link': result.get('payment_link'),
                'qr_base64': result.get('qr_base64'),
                'processing_time': elapsed
            }
        else:
            error = result.get('error', 'Неизвестная ошибка') if result else 'Нет результата'
            logger.error(f"❌ Платеж {request_id} неудачен за {elapsed:.1f}s: {error}")
            
            update_stats(False, elapsed)
            
            return {
                'success': False,
                'request_id': request_id,
                'order_id': order_id,
                'error': error,
                'processing_time': elapsed
            }
            
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"💥 Исключение в платеже {request_id} за {elapsed:.1f}s: {e}")
        
        update_stats(False, elapsed)
        
        return {
            'success': False,
            'request_id': request_id,
            'order_id': order_id,
            'error': str(e),
            'processing_time': elapsed
        }
    finally:
        with stats_lock:
            stats['concurrent_requests'] -= 1

# API TOKEN для авторизации
API_TOKEN = "-3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo"

def verify_token():
    """Проверка Bearer токена"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return False
    
    token = auth_header.split(' ')[1]
    return token == API_TOKEN

@app.route('/api/payment', methods=['POST'])
def create_payment_api_optimized():
    """ОПТИМИЗИРОВАННЫЙ API для создания платежа с параллельной обработкой"""
    
    logger.info("=" * 80)
    logger.info("🔥 НОВЫЙ ЗАПРОС НА СОЗДАНИЕ ПЛАТЕЖА")
    logger.info(f"   Метод: {request.method}")
    logger.info(f"   IP клиента: {request.remote_addr}")
    logger.info(f"   User-Agent: {request.headers.get('User-Agent', 'N/A')}")
    
    # Проверка авторизации
    if not verify_token():
        logger.warning("❌ ОТКЛОНЕН: Неверный токен авторизации")
        return jsonify({
            "success": False,
            "error": "Unauthorized",
            "message": "Invalid or missing Bearer token"
        }), 401
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "Invalid JSON"
            }), 400
        
        # Валидация данных
        amount = data.get('amount')
        order_id = data.get('orderId')
        
        if not amount:
            return jsonify({
                "success": False,
                "error": "Missing required field: amount"
            }), 400
        
        if not isinstance(amount, (int, float)) or amount <= 0:
            return jsonify({
                "success": False,
                "error": "Invalid amount: must be positive number"
            }), 400
        
        if not order_id:
            return jsonify({
                "success": False,
                "error": "Missing required field: orderId"
            }), 400
        
        # Проверка на дублирование orderId
        for existing_payment in payment_links.values():
            if existing_payment.get('order_id') == order_id:
                return jsonify({
                    "success": False,
                    "error": f"Duplicate orderId: {order_id}",
                    "existing_payment": {
                        "request_id": existing_payment['id'],
                        "payment_link": existing_payment.get('payment_link'),
                        "created_at": existing_payment.get('created_at')
                    }
                }), 409
        
        # Генерируем уникальный ID запроса
        request_id = str(uuid.uuid4())
        
        logger.info(f"✅ ВАЛИДАЦИЯ ПРОЙДЕНА")
        logger.info(f"   Request ID: {request_id}")
        logger.info(f"   Amount: {amount} сум")
        logger.info(f"   Order ID: {order_id}")
        logger.info(f"📥 Запуск асинхронной обработки платежа...")
        
        # ПАРАЛЛЕЛЬНАЯ обработка - не ждем результата
        future = executor.submit(process_payment_async, request_id, amount, order_id)
        
        # Ждем результат с таймаутом (для внешних клиентов)
        try:
            result = future.result(timeout=60)  # Увеличен до 60 секунд для стабильной работы
            
            logger.info(f"⏱️  Обработка завершена за {result.get('processing_time', 0):.1f}s")
            
            if result['success']:
                logger.info(f"✅ УСПЕХ: Платеж создан успешно")
                logger.info(f"   Payment Link: {result['payment_link']}")
                logger.info("=" * 80)
                
                # Извлекаем qrcId из payment_link
                payment_link = result['payment_link']
                qrc_id = ""
                if payment_link and "qr.nspk.ru/" in payment_link:
                    # Извлекаем ID между доменом и параметрами
                    parts = payment_link.split("qr.nspk.ru/")
                    if len(parts) > 1:
                        qrc_id = parts[1].split("?")[0]
                
                return jsonify({
                    "success": True,
                    "orderId": result['order_id'],
                    "qrcId": qrc_id,
                    "qr": payment_link
                }), 201
            else:
                logger.error(f"❌ ОШИБКА: {result['error']}")
                logger.info("=" * 80)
                return jsonify({
                    "success": False,
                    "orderId": result['order_id'],
                    "error": result['error']
                }), 500
                
        except TimeoutError:
            # Если превышен таймаут, возвращаем статус "в обработке"
            logger.error(f"⏰ ТАЙМАУТ: Обработка превысила 60 секунд")
            logger.info("=" * 80)
            return jsonify({
                "success": False,
                "orderId": order_id,
                "error": "Processing timeout"
            }), 408
            
    except Exception as e:
        logger.error(f"💥 КРИТИЧЕСКАЯ ОШИБКА API: {e}")
        logger.exception("Полный traceback:")
        logger.info("=" * 80)
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Internal server error"
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Получение статистики системы"""
    if not verify_token():
        return jsonify({"error": "Unauthorized"}), 401
    
    with stats_lock:
        uptime = time.time() - stats['start_time']
        current_stats = stats.copy()
        current_stats['uptime_seconds'] = uptime
        current_stats['uptime_formatted'] = f"{uptime/3600:.1f} hours"
        current_stats['success_rate'] = (
            (current_stats['successful_requests'] / current_stats['total_requests'] * 100)
            if current_stats['total_requests'] > 0 else 0
        )
    
    return jsonify(current_stats)

@app.route('/api/health', methods=['GET'])
def health_check_optimized():
    """Оптимизированная проверка здоровья системы"""
    try:
        # Быстрая проверка компонентов
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "database": "healthy",
                "browser_manager": "healthy",
                "thread_pool": "healthy"
            },
            "stats": {
                "concurrent_requests": stats['concurrent_requests'],
                "total_requests": stats['total_requests'],
                "avg_response_time": f"{stats['avg_response_time']:.1f}s"
            }
        }
        
        # Проверка базы данных
        try:
            accounts = db.get_accounts()
            cards = db.get_requisites()
            if not accounts or not cards:
                health_status["components"]["database"] = "warning"
                health_status["status"] = "degraded"
        except Exception as e:
            health_status["components"]["database"] = "unhealthy"
            health_status["status"] = "unhealthy"
        
        # Проверка пула потоков
        if executor._threads and len(executor._threads) > 0:
            health_status["components"]["thread_pool"] = "healthy"
        else:
            health_status["components"]["thread_pool"] = "warning"
        
        status_code = 200 if health_status["status"] == "healthy" else 503
        return jsonify(health_status), status_code
        
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 503

@app.route('/api/payment/<request_id>', methods=['GET'])
def get_payment_status(request_id):
    """Получение статуса конкретного платежа"""
    if not verify_token():
        return jsonify({"error": "Unauthorized"}), 401
    
    if request_id in payment_links:
        return jsonify(payment_links[request_id])
    else:
        return jsonify({
            "success": False,
            "error": "Payment not found",
            "request_id": request_id
        }), 404

@app.route('/api/cards', methods=['GET', 'POST', 'DELETE'])
def manage_cards():
    """Управление картами"""
    if request.method == 'GET':
        cards = db.get_requisites()
        return jsonify(cards)
    elif request.method == 'POST':
        data = request.json
        card = {
            'card_number': data.get('card_number'),
            'owner_name': data.get('owner_name')
        }
        db.add_requisite(card['card_number'], card['owner_name'])
        return jsonify({'success': True, 'card': card})
    return jsonify({'success': False}), 400

@app.route('/api/cards/<int:index>', methods=['DELETE'])
def delete_card(index):
    """Удаление карты"""
    cards = db.get_requisites()
    if 0 <= index < len(cards):
        db.delete_requisite(index)
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Card not found'}), 404

@app.route('/api/accounts', methods=['GET', 'POST'])
def manage_accounts():
    """Управление аккаунтами"""
    if request.method == 'GET':
        accounts = db.get_accounts()
        return jsonify(accounts)
    elif request.method == 'POST':
        data = request.json
        account = {
            'phone': data.get('phone'),
            'password': data.get('password')
        }
        db.add_account(account['phone'], account['password'])
        return jsonify({'success': True, 'account': account})
    return jsonify({'success': False}), 400

@app.route('/api/accounts/<int:index>', methods=['DELETE'])
def delete_account(index):
    """Удаление аккаунта"""
    accounts = db.get_accounts()
    if 0 <= index < len(accounts):
        db.delete_account(index)
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Account not found'}), 404

@app.route('/api/accounts/<int:index>/check', methods=['POST'])
def check_account(index):
    """Проверка аккаунта"""
    # Заглушка для проверки аккаунта
    return jsonify({'success': True, 'status': 'active'})

@app.route('/api/links', methods=['GET'])
def get_links():
    """Получение всех созданных платежей"""
    links_list = list(payment_links.values())
    # Сортируем по дате создания (новые первые)
    links_list.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return jsonify(links_list)

@app.route('/api/links/<request_id>', methods=['DELETE'])
def delete_link(request_id):
    """Удаление платежа"""
    if request_id in payment_links:
        del payment_links[request_id]
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Payment not found'}), 404

@app.route('/api/create-payment', methods=['POST'])
def create_payment_frontend():
    """Создание платежа из фронтенда"""
    logger.info("=" * 80)
    logger.info("🎨 ЗАПРОС ИЗ ФРОНТЕНДА НА СОЗДАНИЕ ПЛАТЕЖА")
    
    data = request.json
    amount = data.get('amount')
    order_id = data.get('orderId', f'order-{int(time.time())}')
    
    logger.info(f"   Amount: {amount} сум")
    logger.info(f"   Order ID: {order_id}")
    
    if not amount:
        return jsonify({'success': False, 'error': 'Amount is required'}), 400
    
    # Используем существующий оптимизированный эндпоинт
    request_id = str(uuid.uuid4())
    
    logger.info(f"   Request ID: {request_id}")
    logger.info(f"📥 Запуск асинхронной обработки...")
    
    # Запускаем асинхронную обработку
    future = executor.submit(process_payment_async, request_id, amount, order_id)
    
    # Ждем результат (синхронно для фронтенда)
    try:
        result = future.result(timeout=70)  # Ждем до 70 секунд
        
        if request_id in payment_links:
            payment_data = payment_links[request_id]
            
            logger.info(f"✅ УСПЕХ! Платеж создан")
            logger.info(f"   Payment Link: {payment_data.get('payment_link')}")
            logger.info(f"   Processing Time: {payment_data.get('processing_time'):.1f}s")
            logger.info(f"   QR Code: {'Да' if payment_data.get('qr_base64') else 'Нет'}")
            logger.info("=" * 80)
            
            return jsonify({
                'success': True,
                'paymentId': request_id,
                'orderId': order_id,
                'amount': amount,
                'paymentUrl': payment_data.get('payment_link'),
                'qrCode': payment_data.get('qr_base64'),
                'elapsedTime': payment_data.get('processing_time'),
                'createdAt': payment_data.get('created_at')
            })
        else:
            logger.error(f"❌ ОШИБКА: Платеж не найден в payment_links")
            logger.info("=" * 80)
            return jsonify({
                'success': False,
                'error': 'Payment processing failed'
            }), 500
    except TimeoutError:
        logger.error(f"⏰ ТАЙМАУТ: Обработка превысила 70 секунд")
        logger.info("=" * 80)
        return jsonify({
            'success': False,
            'error': 'Payment processing timeout'
        }), 408
    except Exception as e:
        logger.error(f"💥 ИСКЛЮЧЕНИЕ: {e}")
        logger.exception("Полный traceback:")
        logger.info("=" * 80)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/warmup', methods=['POST'])
def warmup_browser():
    """Ручной прогрев браузера"""
    try:
        from payment_service import warmup_for_user
        warmup_result = warmup_for_user(user_id=None)
        return jsonify(warmup_result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/')
def admin_panel():
    """Главная страница админ-панели"""
    return render_template('admin.html')

if __name__ == '__main__':
    logger.info("🚀 Запуск ОПТИМИЗИРОВАННОЙ системы платежей")
    logger.info("⚡ Поддержка параллельной обработки")
    logger.info("🎯 Цель: 8-12 секунд на платеж")
    logger.info("🔥 Поддержка частых запросов (1-3s)")
    
    # Автоматический прогрев браузера при старте
    logger.info("🔥 Запуск автоматического прогрева браузера...")
    try:
        from payment_service import warmup_for_user
        warmup_result = warmup_for_user(user_id=None)
        if warmup_result.get('success'):
            logger.info(f"✅ Браузер прогрет успешно! Режим: {warmup_result.get('mode')}")
        else:
            logger.warning(f"⚠️ Прогрев браузера не удался: {warmup_result.get('error')}")
    except Exception as e:
        logger.error(f"❌ Ошибка прогрева браузера: {e}")
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)