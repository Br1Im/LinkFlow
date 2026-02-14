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
    
    try:
        # Получаем JSON данные
        print(f"📥 Content-Type: {request.content_type}")
        print(f"📥 Is JSON: {request.is_json}")
        print(f"📥 Raw data: {request.data[:200]}")
        
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': f'Content-Type must be application/json, got: {request.content_type}'
            }), 400
        
        data = request.get_json(force=True)  # force=True to parse even if content-type is wrong
        if data is None:
            return jsonify({
                'success': False,
                'error': 'Invalid JSON'
            }), 400
        
        print(f"📥 Получен запрос: {data}")
        
        # Валидация
        amount = data.get('amount')
        order_id = data.get('orderId')
        
        # Генерируем orderId автоматически, если не передан
        if not order_id:
            from datetime import datetime
            order_id = f"ORDER_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if not amount:
            return jsonify({
                'success': False,
                'error': 'amount is required'
            }), 400
        
        amount = int(amount)
        
        if amount < 100 or amount > 120000:
            return jsonify({
                'success': False,
                'error': 'Amount must be between 100 and 120000 RUB'
            }), 400
        
        # Получаем данные получателя из запроса
        card_number = data.get('card_number')
        owner_name = data.get('card_owner')
        custom_sender = data.get('custom_sender')  # dict с кастомными данными отправителя
        requisite_api = data.get('requisite_api', 'auto')  # auto, h2h, payzteam
        
        # Валидация requisite_api
        if requisite_api not in ['auto', 'h2h', 'payzteam']:
            return jsonify({
                'success': False,
                'error': 'requisite_api must be "auto", "h2h" or "payzteam"'
            }), 400
        
        # Преобразуем card_number в строку если это число
        if card_number is not None:
            card_number = str(card_number)
        
        # НЕ получаем из БД здесь - это будет сделано в create_payment_playwright
        # с возможностью использования PayzTeam API
        
        # Режим работы зависит от наличия Playwright
        if PLAYWRIGHT_AVAILABLE:
            return create_payment_playwright(amount, order_id, card_number, owner_name, custom_sender, requisite_api)
        else:
            # Для прокси режима нужны реквизиты из БД
            if not card_number or not owner_name:
                import database
                beneficiary = database.get_random_beneficiary()
                
                if not beneficiary:
                    return jsonify({
                        'success': False,
                        'error': 'No active beneficiaries found in database'
                    }), 400
                
                card_number = str(beneficiary['card_number'])
                owner_name = beneficiary['card_owner']
                log(f"Используется случайный реквизит: {owner_name} ({card_number})", "INFO")
            
            return create_payment_proxy(amount, order_id)
        
    except Exception as e:
        print(f"❌ Ошибка API: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def create_payment_playwright(amount, order_id, card_number, owner_name, custom_sender=None, requisite_api='auto'):
    """Создание платежа через Playwright
    
    Args:
        requisite_api: 'auto' (H2H -> PayzTeam), 'h2h' (только H2H), 'payzteam' (только PayzTeam)
    """
    import time
    import concurrent.futures
    
    # Импортируем функции получения реквизитов
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'payment_service'))
    from h2h_api import get_h2h_requisite
    from payzteam_api import get_payzteam_requisite
    
    log(f"Создаю платеж через Playwright: amount={amount}, orderId={order_id}, requisite_api={requisite_api}", "INFO")
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
    
    # Запускаем запросы к API параллельно в зависимости от requisite_api
    h2h_future = None
    payzteam_future = None
    requisite_source = "database"  # По умолчанию из БД
    
    # Если реквизиты не указаны явно, получаем от API
    if not card_number or not owner_name:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            if requisite_api == 'auto':
                # Запускаем оба параллельно, но приоритет у H2H
                log("Запускаю параллельные запросы к H2H и PayzTeam API...", "INFO")
                h2h_future = executor.submit(get_h2h_requisite, amount)
                payzteam_future = executor.submit(get_payzteam_requisite, amount)
            elif requisite_api == 'h2h':
                log("Запускаю запрос к H2H API...", "INFO")
                h2h_future = executor.submit(get_h2h_requisite, amount)
            elif requisite_api == 'payzteam':
                log("Запускаю запрос к PayzTeam API...", "INFO")
                payzteam_future = executor.submit(get_payzteam_requisite, amount)
    
    # Создаем платеж (первый этап начнется сразу)
    # Если реквизиты не указаны, передаем None - они будут получены позже
    result = run_async(
        payment_service.create_payment_link(
            amount=amount,
            card_number=card_number,
            owner_name=owner_name,
            custom_sender=custom_sender,
            h2h_future=h2h_future,
            payzteam_future=payzteam_future,
            requisite_api=requisite_api
        )
    )
    
    # Определяем источник реквизитов из результата
    requisite_source = result.get('requisite_source', 'database')
    
    total_elapsed_time = time.time() - total_start_time
    
    # Получаем логи из результата
    logs = result.get('logs', [])
    log(f"📊 Получено логов из payment_service: {len(logs)}", "DEBUG")
    
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
        # Оставляем только важные логи (ошибки и предупреждения)
        important_logs = [l for l in logs if l.get('level') in ['error', 'warning']]
        print(f"📤 Успех. Логов: {len(logs)}, важных: {len(important_logs)}")
        
        return jsonify({
            'success': True,
            'order_id': order_id,
            'amount': amount,
            'status': 'completed',
            'qr_link': result.get('qr_link'),
            'card_number': result.get('card_number'),
            'card_owner': result.get('card_owner'),
            'payment_time': result.get('time'),
            'total_time': total_elapsed_time,
            'step1_time': result.get('step1_time'),
            'step2_time': result.get('step2_time'),
            'requisite_source': requisite_source,
            'message': 'Payment created successfully'
        }), 201
    else:
        # При ошибке возвращаем только последние 5 логов
        error_logs = logs[-5:] if len(logs) > 5 else logs
        print(f"📤 Ошибка. Возвращаю последние {len(error_logs)} логов")
        
        return jsonify({
            'success': False,
            'order_id': order_id,
            'error': result.get('error', 'Payment creation failed'),
            'payment_time': result.get('time'),
            'total_time': total_elapsed_time,
            'requisite_source': requisite_source,
            'logs': error_logs
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


@app.route('/api/get-qr-link', methods=['POST'])
def get_qr_link():
    """Получить прямую QR-ссылку из виджета MulenPay
    
    Request:
        {
            "widget_url": "https://mulenpay.ru/payment/widget/UUID"
        }
    
    Response:
        {
            "success": true,
            "qr_link": "https://qr.nspk.ru/...",
            "widget_url": "https://mulenpay.ru/payment/widget/UUID"
        }
    """
    import re
    import requests
    import time
    
    data = request.get_json()
    widget_url = data.get('widget_url')
    
    if not widget_url:
        return jsonify({
            'success': False,
            'error': 'widget_url is required'
        }), 400
    
    # Извлекаем UUID из URL виджета
    uuid_match = re.search(r'/payment/widget/([a-f0-9-]+)', widget_url)
    if not uuid_match:
        return jsonify({
            'success': False,
            'error': 'Invalid widget URL format'
        }), 400
    
    payment_uuid = uuid_match.group(1)
    
    # Ждём немного, чтобы система подготовила платёж
    time.sleep(2)
    
    # Запрашиваем /sbp endpoint для получения прямой QR-ссылки
    sbp_url = f'https://mulenpay.ru/payment/widget/{payment_uuid}/sbp'
    
    try:
        sbp_response = requests.get(sbp_url, timeout=5)
        if sbp_response.status_code == 200:
            sbp_data = sbp_response.json()
            if sbp_data.get('success') and sbp_data.get('sbp'):
                qr_payload = sbp_data.get('data', {}).get('qrpayload', '')
                if qr_payload:
                    return jsonify({
                        'success': True,
                        'qr_link': qr_payload,
                        'widget_url': widget_url
                    })
        
        return jsonify({
            'success': False,
            'error': 'Failed to get QR link from MulenPay',
            'widget_url': widget_url
        }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'widget_url': widget_url
        }), 500


@app.route('/api/create-qr-payment', methods=['POST'])
def create_qr_payment():
    """Создать платеж через MulenPay и получить прямую QR-ссылку
    
    Request:
        {
            "amount": 3000
        }
    
    Response:
        {
            "success": true,
            "qr_link": "https://qr.nspk.ru/...",
            "widget_url": "https://mulenpay.ru/payment/widget/UUID",
            "payment_id": "123456",
            "amount": 3000
        }
    """
    import re
    import requests
    import time
    import uuid as uuid_lib
    
    # Импортируем MulenPay клиент
    sys.path.insert(0, os.path.dirname(__file__))
    from mulenpay import MulenPayClient
    
    data = request.get_json()
    amount = data.get('amount')
    
    if not amount:
        return jsonify({
            'success': False,
            'error': 'amount is required'
        }), 400
    
    try:
        amount = int(amount)
        if amount < 3000 or amount > 5000:
            return jsonify({
                'success': False,
                'error': 'Amount must be between 3000 and 5000 RUB'
            }), 400
    except ValueError:
        return jsonify({
            'success': False,
            'error': 'Invalid amount format'
        }), 400
    
    # Создаем MulenPay клиент
    secret_key = 'b48d74485fcf7b4a2cade546bdebcaf3692945ffeeb7ff98729a758f6322684c'
    mp_client = MulenPayClient(secret_key=secret_key)
    
    try:
        # Создаем платеж
        response = run_async(mp_client.create_payment(
            private_key2="nVT5DyeFCJGMe04THqN8hE7usCTiiSpuHiOHdWkac9f96f48",
            currency="rub",
            amount=str(amount),
            uuid=str(uuid_lib.uuid4()),
            shopId="280",
            description=f"Платеж {amount} руб.",
            items=[
                {
                    "description": f"Платеж {amount} руб.",
                    "quantity": 1,
                    "price": str(amount),
                    "vat_code": 0,
                    "payment_subject": 1,
                    "payment_mode": 1,
                }
            ],
        ))
        
        payment_id = response.get('id')
        widget_url = response.get('paymentUrl')
        
        if not widget_url:
            return jsonify({
                'success': False,
                'error': 'Failed to create payment'
            }), 500
        
        # Извлекаем UUID из URL виджета
        uuid_match = re.search(r'/payment/widget/([a-f0-9-]+)', widget_url)
        if not uuid_match:
            return jsonify({
                'success': False,
                'error': 'Invalid widget URL format',
                'widget_url': widget_url
            }), 500
        
        payment_uuid = uuid_match.group(1)
        
        # Ждём немного, чтобы система подготовила платёж
        time.sleep(2)
        
        # Запрашиваем /sbp endpoint для получения прямой QR-ссылки
        sbp_url = f'https://mulenpay.ru/payment/widget/{payment_uuid}/sbp'
        
        sbp_response = requests.get(sbp_url, timeout=5)
        if sbp_response.status_code == 200:
            sbp_data = sbp_response.json()
            if sbp_data.get('success') and sbp_data.get('sbp'):
                qr_payload = sbp_data.get('data', {}).get('qrpayload', '')
                if qr_payload:
                    return jsonify({
                        'success': True,
                        'qr_link': qr_payload,
                        'widget_url': widget_url,
                        'payment_id': payment_id,
                        'amount': amount
                    })
        
        # Если не удалось получить QR-ссылку, возвращаем виджет
        return jsonify({
            'success': True,
            'qr_link': widget_url,  # Fallback на виджет
            'widget_url': widget_url,
            'payment_id': payment_id,
            'amount': amount,
            'warning': 'Failed to get direct QR link, returning widget URL'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


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
        import database
        beneficiaries = database.get_all_beneficiaries()
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
        
        import database
        
        # Если это повторная проверка, используем существующий ID
        if is_retest and existing_id:
            beneficiary_id = existing_id
        else:
            # Добавляем новый реквизит
            beneficiary_id = database.add_beneficiary(card_number, card_owner)
        
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
                database.update_beneficiary_verification(
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
                database.update_beneficiary_verification(beneficiary_id, False)
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
        
        import database
        
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
                database.update_beneficiary_verification(
                    beneficiary_id, 
                    is_verified,
                    test_order_id if is_verified else None
                )
                
                # Если не прошел проверку - отключаем реквизит
                if not is_verified:
                    database.update_beneficiary_status(beneficiary_id, False)
                    log(f"Реквизит ID {beneficiary_id} отключен (не прошел проверку)", "WARNING")
                
                return jsonify({
                    'success': True,
                    'beneficiary_id': beneficiary_id,
                    'verified': is_verified,
                    'test_result': result
                })
            except Exception as e:
                # Если тест не прошел - отключаем реквизит
                database.update_beneficiary_verification(beneficiary_id, False)
                database.update_beneficiary_status(beneficiary_id, False)
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
        import database
        database.delete_beneficiary(beneficiary_id)
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
        
        import database
        database.update_beneficiary_status(beneficiary_id, is_active)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/convert-currency', methods=['POST'])
def convert_currency():
    """Конвертация RUB -> UZS через API multitransfer.ru
    
    Request:
        {
            "amount_rub": 5000
        }
    
    Response:
        {
            "success": true,
            "amount_rub": 5000.0,
            "amount_uzs": 758950.0,
            "exchange_rate": 151.79,
            "commission": {...}
        }
    """
    try:
        data = request.get_json()
        amount_rub = data.get('amount_rub')
        
        if not amount_rub:
            return jsonify({
                'success': False,
                'error': 'amount_rub is required'
            }), 400
        
        try:
            amount_rub = float(amount_rub)
            if amount_rub <= 0:
                return jsonify({
                    'success': False,
                    'error': 'amount_rub must be positive'
                }), 400
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid amount_rub format'
            }), 400
        
        # Импортируем конвертер
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'payment_service'))
        from currency_converter import CurrencyConverter
        
        converter = CurrencyConverter()
        result = converter.convert_rub_to_uzs(amount_rub)
        
        if result:
            return jsonify(result), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Currency conversion failed'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/requisite-source', methods=['GET'])
def get_requisite_source():
    """Получить текущий источник реквизитов"""
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'payment_service'))
        from requisite_config import get_requisite_service
        
        service = get_requisite_service()
        
        return jsonify({
            'success': True,
            'source': service
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/requisite-source', methods=['POST'])
def set_requisite_source():
    """Установить источник реквизитов
    
    Request:
        {
            "source": "auto" | "h2h" | "payzteam"
        }
    """
    if not check_auth():
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        source = data.get('source')
        
        if not source:
            return jsonify({
                'success': False,
                'error': 'source is required'
            }), 400
        
        if source not in ['auto', 'h2h', 'payzteam']:
            return jsonify({
                'success': False,
                'error': 'source must be "auto", "h2h" or "payzteam"'
            }), 400
        
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'payment_service'))
        from requisite_config import set_requisite_service
        
        set_requisite_service(source)
        
        return jsonify({
            'success': True,
            'source': source,
            'message': f'Requisite source changed to {source}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


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
