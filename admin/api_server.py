#!/usr/bin/env python3
"""
API Server для LinkFlow на порту 5001
Использует Playwright для реальной генерации платежей
"""

from flask import Flask, request, jsonify
from datetime import datetime
import asyncio
import threading
import sys
import os

# Добавляем путь к payment_service
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'payment_service'))

try:
    from payment_service import PaymentService, log
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️ Playwright не установлен. Используется режим прокси.")

app = Flask(__name__)

# Bearer токен для авторизации
API_TOKEN = "-3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo"

# URL админ-панели (для режима прокси)
ADMIN_URL = "http://localhost:5000"

# Глобальный сервис и event loop (для Playwright режима)
payment_service = None
event_loop = None
loop_thread = None


def check_auth():
    """Проверка Bearer токена"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return False
    
    try:
        scheme, token = auth_header.split(' ', 1)
        if scheme.lower() != 'bearer':
            return False
        return token == API_TOKEN
    except:
        return False


def run_event_loop():
    """Запускает event loop в отдельном потоке"""
    global event_loop
    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)
    event_loop.run_forever()


def run_async(coro):
    """Запускает корутину в глобальном event loop"""
    future = asyncio.run_coroutine_threadsafe(coro, event_loop)
    return future.result()


@app.route('/api/payment', methods=['POST'])
def create_payment():
    """API для создания платежа"""
    
    # Проверка авторизации
    if not check_auth():
        return jsonify({
            'success': False,
            'error': 'Unauthorized'
        }), 401
    
    try:
        # Получаем JSON данные
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type must be application/json'
            }), 400
        
        data = request.get_json()
        if data is None:
            return jsonify({
                'success': False,
                'error': 'Invalid JSON'
            }), 400
        
        print(f"📥 Получен запрос: {data}")
        
        # Валидация
        amount = data.get('amount')
        order_id = data.get('orderId')
        
        if not amount or not order_id:
            return jsonify({
                'success': False,
                'error': 'amount and orderId are required'
            }), 400
        
        amount = int(amount)
        
        if amount < 100 or amount > 120000:
            return jsonify({
                'success': False,
                'error': 'Amount must be between 100 and 120000 RUB'
            }), 400
        
        # Получаем данные получателя из запроса или из БД
        card_number = data.get('card_number')
        owner_name = data.get('card_owner')
        custom_sender = data.get('custom_sender')  # dict с кастомными данными отправителя
        
        # Если не указаны в запросе, берем случайный из БД
        if not card_number or not owner_name:
            from admin.database import get_random_beneficiary
            beneficiary = get_random_beneficiary()
            
            if not beneficiary:
                return jsonify({
                    'success': False,
                    'error': 'No active beneficiaries found in database'
                }), 400
            
            card_number = beneficiary['card_number']
            owner_name = beneficiary['card_owner']
            log(f"Используется случайный реквизит: {owner_name} ({card_number})", "INFO")
        
        # Режим работы зависит от наличия Playwright
        if PLAYWRIGHT_AVAILABLE:
            return create_payment_playwright(amount, order_id, card_number, owner_name, custom_sender)
        else:
            return create_payment_proxy(amount, order_id)
        
    except Exception as e:
        print(f"❌ Ошибка API: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def create_payment_playwright(amount, order_id, card_number, owner_name, custom_sender=None):
    """Создание платежа через Playwright"""
    import time
    
    log(f"Создаю платеж через Playwright: amount={amount}, orderId={order_id}", "INFO")
    if custom_sender:
        log(f"Используются кастомные данные отправителя: {custom_sender}", "INFO")
    
    total_start_time = time.time()
    
    global payment_service
    
    # Ждем пока браузер будет готов
    for wait_attempt in range(10):
        if payment_service and payment_service.is_ready:
            break
        if wait_attempt == 0:
            log("Ожидание готовности браузера...", "DEBUG")
        time.sleep(0.5)
    
    if not payment_service or not payment_service.is_ready:
        log("Запускаю браузер...", "INFO")
        payment_service = PaymentService()
        run_async(payment_service.start(headless=True))
    
    # Создаем платеж
    result = run_async(
        payment_service.create_payment_link(
            amount=amount,
            card_number=card_number,
            owner_name=owner_name,
            custom_sender=custom_sender
        )
    )
    
    total_elapsed_time = time.time() - total_start_time
    
    # Перезапускаем браузер для следующего платежа
    try:
        log("Перезапускаю браузер для следующего платежа...", "DEBUG")
        run_async(payment_service.stop())
        time.sleep(0.5)
        run_async(payment_service.start(headless=True))
        log("Браузер перезапущен", "SUCCESS")
    except Exception as e:
        log(f"Ошибка перезапуска браузера: {e}", "ERROR")
    
    # Возвращаем результат
    if result.get('success'):
        return jsonify({
            'success': True,
            'order_id': order_id,
            'amount': amount,
            'status': 'completed',
            'qr_link': result.get('qr_link'),
            'payment_time': result.get('time'),
            'total_time': total_elapsed_time,
            'step1_time': result.get('step1_time'),
            'step2_time': result.get('step2_time'),
            'message': 'Payment created successfully'
        }), 201
    else:
        return jsonify({
            'success': False,
            'order_id': order_id,
            'error': result.get('error', 'Payment creation failed'),
            'payment_time': result.get('time'),
            'total_time': total_elapsed_time
        }), 500


def create_payment_proxy(amount, order_id):
    """Создание платежа через прокси к админ-панели"""
    import requests
    
    print(f"📤 Перенаправляю запрос на админ-панель (Playwright не установлен)")
    
    response = requests.post(
        f'{ADMIN_URL}/api/create-payment',
        json={'amount': amount, 'orderId': order_id},
        timeout=120
    )
    
    if response.status_code == 201:
        result = response.json()
        return jsonify({
            'success': True,
            'payment_id': result.get('order_id'),
            'order_id': order_id,
            'amount': amount,
            'status': 'completed',
            'qr_link': result.get('qr_link'),
            'payment_time': result.get('payment_time'),
            'message': 'Payment created successfully (proxy mode)'
        }), 201
    else:
        error_data = response.json() if response.text else {}
        return jsonify({
            'success': False,
            'error': error_data.get('error', 'Payment creation failed')
        }), response.status_code


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    is_ready = payment_service and payment_service.is_ready if PLAYWRIGHT_AVAILABLE else False
    
    return jsonify({
        'status': 'ok' if (is_ready or not PLAYWRIGHT_AVAILABLE) else 'warming_up',
        'service': 'LinkFlow API',
        'version': '2.0.0',
        'mode': 'playwright' if PLAYWRIGHT_AVAILABLE else 'proxy',
        'browser_ready': is_ready if PLAYWRIGHT_AVAILABLE else None,
        'admin_url': ADMIN_URL if not PLAYWRIGHT_AVAILABLE else None
    })


@app.route('/restart', methods=['POST'])
def restart_service():
    """Перезапуск браузера (только для Playwright режима)"""
    
    if not check_auth():
        return jsonify({
            'success': False,
            'error': 'Unauthorized'
        }), 401
    
    if not PLAYWRIGHT_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Playwright mode not available'
        }), 400
    
    return jsonify({
        'success': True,
        'message': 'Browser restarts automatically for each payment'
    })


@app.route('/api/beneficiaries', methods=['GET'])
def get_beneficiaries():
    """Получить все реквизиты"""
    if not check_auth():
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    try:
        from admin.database import get_all_beneficiaries
        beneficiaries = get_all_beneficiaries()
        return jsonify({'success': True, 'beneficiaries': beneficiaries})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/beneficiaries', methods=['POST'])
def add_beneficiary_endpoint():
    """Добавить новый реквизит с автоматической проверкой"""
    if not check_auth():
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        card_number = data.get('card_number')
        card_owner = data.get('card_owner')
        is_retest = data.get('retest', False)
        existing_id = data.get('beneficiary_id')
        
        if not card_number or not card_owner:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        from admin.database import add_beneficiary, update_beneficiary_verification
        
        # Если это повторная проверка, используем существующий ID
        if is_retest and existing_id:
            beneficiary_id = existing_id
        else:
            # Добавляем новый реквизит
            beneficiary_id = add_beneficiary(card_number, card_owner)
        
        # Создаем тестовый платеж
        if PLAYWRIGHT_AVAILABLE and payment_service:
            test_amount = 110
            test_order_id = f"TEST_{beneficiary_id}_{int(datetime.now().timestamp())}"
            
            try:
                log(f"Запуск тестового платежа для реквизита ID {beneficiary_id}: {card_owner}", "INFO")
                
                # Перезапускаем браузер для чистого состояния
                try:
                    log("Перезапуск браузера для теста...", "DEBUG")
                    run_async(payment_service.stop())
                    import time
                    time.sleep(1)
                    run_async(payment_service.start(headless=True))
                    log("Браузер перезапущен", "SUCCESS")
                except Exception as e:
                    log(f"Ошибка перезапуска браузера: {e}", "WARNING")
                
                # Запускаем тестовый платеж
                result = run_async(payment_service.create_payment_link(
                    amount=test_amount,
                    card_number=card_number,
                    owner_name=card_owner
                ))
                
                log(f"Результат теста: success={result.get('success')}, qr_link={result.get('qr_link')[:50] if result.get('qr_link') else 'None'}", "INFO")
                
                # Обновляем статус верификации
                update_beneficiary_verification(
                    beneficiary_id, 
                    result.get('success', False),
                    test_order_id if result.get('success') else None
                )
                
                return jsonify({
                    'success': True,
                    'beneficiary_id': beneficiary_id,
                    'verified': result.get('success', False),
                    'test_result': result
                })
            except Exception as e:
                # Если тест не прошел
                update_beneficiary_verification(beneficiary_id, False)
                return jsonify({
                    'success': True,
                    'beneficiary_id': beneficiary_id,
                    'verified': False,
                    'error': str(e)
                })
        else:
            # Без проверки (режим прокси)
            return jsonify({
                'success': True,
                'beneficiary_id': beneficiary_id,
                'verified': False,
                'message': 'Verification skipped (Playwright not available)'
            })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/beneficiaries/retest', methods=['POST'])
def retest_beneficiary_endpoint():
    """Повторная проверка существующего реквизита"""
    if not check_auth():
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        beneficiary_id = data.get('beneficiary_id')
        card_number = data.get('card_number')
        card_owner = data.get('card_owner')
        
        if not beneficiary_id or not card_number or not card_owner:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        from admin.database import update_beneficiary_verification
        
        # Создаем тестовый платеж
        if PLAYWRIGHT_AVAILABLE and payment_service:
            test_amount = 110
            test_order_id = f"TEST_{beneficiary_id}_{int(datetime.now().timestamp())}"
            
            try:
                log(f"Повторная проверка реквизита ID {beneficiary_id}: {card_owner}", "INFO")
                
                # Перезапускаем браузер для чистого состояния
                try:
                    log("Перезапуск браузера для теста...", "DEBUG")
                    run_async(payment_service.stop())
                    import time
                    time.sleep(1)
                    run_async(payment_service.start(headless=True))
                    log("Браузер перезапущен", "SUCCESS")
                except Exception as e:
                    log(f"Ошибка перезапуска браузера: {e}", "WARNING")
                
                # Запускаем тестовый платеж
                result = run_async(payment_service.create_payment_link(
                    amount=test_amount,
                    card_number=card_number,
                    owner_name=card_owner
                ))
                
                log(f"Результат повторного теста: success={result.get('success')}", "INFO")
                
                # Обновляем статус верификации
                is_verified = result.get('success', False)
                update_beneficiary_verification(
                    beneficiary_id, 
                    is_verified,
                    test_order_id if is_verified else None
                )
                
                # Если не прошел проверку - отключаем реквизит
                if not is_verified:
                    from admin.database import update_beneficiary_status
                    update_beneficiary_status(beneficiary_id, False)
                    log(f"Реквизит ID {beneficiary_id} отключен (не прошел проверку)", "WARNING")
                
                return jsonify({
                    'success': True,
                    'beneficiary_id': beneficiary_id,
                    'verified': is_verified,
                    'test_result': result
                })
            except Exception as e:
                # Если тест не прошел - отключаем реквизит
                update_beneficiary_verification(beneficiary_id, False)
                from admin.database import update_beneficiary_status
                update_beneficiary_status(beneficiary_id, False)
                log(f"Реквизит ID {beneficiary_id} отключен (ошибка проверки)", "ERROR")
                
                return jsonify({
                    'success': True,
                    'beneficiary_id': beneficiary_id,
                    'verified': False,
                    'error': str(e)
                })
        else:
            return jsonify({
                'success': False,
                'error': 'Playwright not available'
            })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/beneficiaries/<int:beneficiary_id>', methods=['DELETE'])
def delete_beneficiary_endpoint(beneficiary_id):
    """Удалить реквизит"""
    if not check_auth():
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    try:
        from admin.database import delete_beneficiary
        delete_beneficiary(beneficiary_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/beneficiaries/<int:beneficiary_id>/toggle', methods=['POST'])
def toggle_beneficiary_endpoint(beneficiary_id):
    """Включить/выключить реквизит"""
    if not check_auth():
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        is_active = data.get('is_active', True)
        
        from admin.database import update_beneficiary_status
        update_beneficiary_status(beneficiary_id, is_active)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🔌 LinkFlow API Server")
    print("="*60)
    print(f"📍 URL: http://localhost:5001")
    print(f"🔑 Bearer Token: {API_TOKEN}")
    print(f"📊 Endpoints:")
    print(f"   POST   /api/payment")
    print(f"   GET    /health")
    print(f"   POST   /restart")
    
    if PLAYWRIGHT_AVAILABLE:
        print(f"⚡ Mode: Playwright (real browser automation)")
        print("="*60 + "\n")
        
        # Запускаем event loop в отдельном потоке
        print("ℹ️ Запуск event loop...")
        loop_thread = threading.Thread(target=run_event_loop, daemon=True)
        loop_thread.start()
        
        import time
        time.sleep(0.5)
        
        # Прогреваем браузер
        print("ℹ️ Прогрев браузера...")
        payment_service = PaymentService()
        run_async(payment_service.start(headless=True))
        print("✅ Браузер готов к работе!\n")
    else:
        print(f"⚠️ Mode: Proxy (forwarding to {ADMIN_URL})")
        print(f"💡 Установите Playwright для реальной генерации:")
        print(f"   pip install -r requirements_playwright.txt")
        print(f"   playwright install chromium")
        print("="*60 + "\n")
    
    app.run(debug=False, host='0.0.0.0', port=5001, use_reloader=False, threaded=True)
