#!/usr/bin/env python3
"""
Современная админ-панель для создания платёжных ссылок с SQLite БД
Тёмная тема, крутой дизайн, постоянное хранение данных
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import csv
import io
from datetime import datetime, timedelta
import random
import time
import threading
import requests

# Import database module
import database as db

app = Flask(__name__)

# API конфигурация
API_URL = os.getenv('API_URL', 'http://localhost:5001')
API_TOKEN = os.getenv('API_TOKEN', '-3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo')

# Данные получателя по умолчанию
DEFAULT_CARD = '9860080323894719'
DEFAULT_OWNER = 'Nodir Asadullayev'

# Блокировка для предотвращения одновременной генерации
payment_lock = threading.Lock()
current_generation = {
    'in_progress': False,
    'order_id': None,
    'started_at': None
}

# Хранилище логов для текущего платежа
current_payment_logs = []
payment_logs_lock = threading.Lock()


def init_default_settings():
    """Initialize default settings if not exist"""
    settings = db.get_all_settings()
    
    if not settings:
        default_settings = {
            'api_url': API_URL,
            'api_token': API_TOKEN,
            'max_amount': 120000,
            'min_amount': 100,
            'auto_retry': True,
            'notifications_enabled': True,
            'default_card': DEFAULT_CARD,
            'default_owner': DEFAULT_OWNER
        }
        db.update_settings(default_settings)
        db.add_log('info', 'Настройки по умолчанию инициализированы')


def generate_demo_data():
    """Генерация демо-данных отключена - используем реальные данные"""
    pass  # Демо-данные больше не генерируются


@app.route('/static/<path:filename>')
def static_files(filename):
    """Отдача статических файлов"""
    return send_from_directory('static', filename)


@app.route('/')
def index():
    """Главная страница админки"""
    return render_template('index.html')


def create_mulenpay_payment(amount, order_id):
    """Создание платежа через MulenPay API"""
    import asyncio
    from mulenpay import MulenPayClient
    
    try:
        # Валидация суммы для MulenPay (3000-5000)
        if amount < 3000 or amount > 5000:
            return jsonify({
                'success': False,
                'error': 'Для MulenPay сумма должна быть от 3000 до 5000 RUB'
            }), 400
        
        # Конфигурация MulenPay (из рабочего бота Nutrition)
        private_key2 = 'nVT5DyeFCJGMe04THqN8hE7usCTiiSpuHiOHdWkac9f96f48'
        secret_key = 'b48d74485fcf7b4a2cade546bdebcaf3692945ffeeb7ff98729a758f6322684c'
        shop_id = '280'  # Строка, как в боте
        
        # Создаем клиент
        client = MulenPayClient(secret_key=secret_key)
        
        # Создаем платеж асинхронно
        async def create_async():
            try:
                # Создаём платёж
                result = await client.create_payment(
                    private_key2=private_key2,
                    currency="rub",
                    amount=str(amount),
                    uuid=order_id,
                    shopId=shop_id,
                    description=f"Платеж {order_id}",
                    items=[
                        {
                            "description": f"Платеж {order_id}",
                            "quantity": 1,
                            "price": str(amount),
                            "vat_code": 0,
                            "payment_subject": 1,
                            "payment_mode": 1,
                        }
                    ]
                )
                
                # Получаем payment_id для запроса статуса
                payment_id = result.get('id')
                payment_url = result.get('paymentUrl', '')
                
                # Извлекаем UUID из paymentUrl для запроса /sbp
                import re
                uuid_match = re.search(r'/payment/widget/([a-f0-9-]+)', payment_url)
                if uuid_match:
                    payment_uuid = uuid_match.group(1)
                    
                    # Ждём немного, чтобы система подготовила платёж
                    import asyncio
                    await asyncio.sleep(2)
                    
                    # Запрашиваем /sbp endpoint для получения прямой QR-ссылки
                    sbp_url = f'https://mulenpay.ru/payment/widget/{payment_uuid}/sbp'
                    
                    # Используем синхронный requests для простоты
                    import requests
                    try:
                        sbp_response = requests.get(sbp_url, timeout=5)
                        if sbp_response.status_code == 200:
                            sbp_data = sbp_response.json()
                            if sbp_data.get('success') and sbp_data.get('sbp'):
                                qr_link = sbp_data.get('data', {}).get('qrpayload', '')
                                if qr_link:
                                    result['qr_link'] = qr_link
                                else:
                                    result['qr_link'] = payment_url
                            else:
                                result['qr_link'] = payment_url
                        else:
                            result['qr_link'] = payment_url
                    except Exception:
                        result['qr_link'] = payment_url
                else:
                    result['qr_link'] = payment_url
                
                await client.aclose()
                return result
            except Exception as e:
                await client.aclose()
                raise e
        
        # Запускаем асинхронную функцию
        start_time = time.time()
        result = asyncio.run(create_async())
        generation_time = time.time() - start_time
        
        # Используем QR-ссылку из result (уже извлечена в create_async)
        qr_link = result.get('qr_link', '')
        
        # Генерируем ID платежа
        all_payments = db.get_all_payments()
        payment_id = f'PAY-{len(all_payments) + 1}'
        
        # Сохраняем в БД
        payment_record = {
            'id': payment_id,
            'order_id': order_id,
            'amount': amount,
            'success': True,
            'status': 'completed',
            'qr_link': qr_link,
            'payment_time': round(generation_time, 2),
            'timestamp': datetime.now().isoformat(),
            'payment_system': 'mulenpay'
        }
        
        db.add_payment(payment_record)
        db.add_log('success', f'MulenPay платёж {order_id} создан успешно за {generation_time:.2f}с')
        
        return jsonify({
            'success': True,
            'order_id': order_id,
            'payment_id': payment_id,
            'amount': amount,
            'status': 'completed',
            'qr_link': qr_link,
            'payment_time': round(generation_time, 2),
            'payment_system': 'mulenpay',
            'mulenpay_id': result.get('id'),
            'message': 'Payment created successfully via MulenPay'
        }), 201
        
    except Exception as e:
        db.add_log('error', f'Ошибка MulenPay: {str(e)}')
        return jsonify({
            'success': False,
            'error': f'MulenPay error: {str(e)}'
        }), 500


@app.route('/api/create-payment', methods=['POST'])
def create_payment():
    """Создание платежа через реальный API на порту 5001 или MulenPay"""
    global current_generation
    
    try:
        data = request.get_json()
        
        amount = data.get('amount')
        payment_system = data.get('payment_system', 'multitransfer')  # По умолчанию multitransfer
        # ID заказа генерируется автоматически
        order_id = data.get('orderId') or f'ORD-{int(time.time())}-{random.randint(1000, 9999)}'
        
        # Если выбран MulenPay - используем его
        if payment_system == 'mulenpay':
            return create_mulenpay_payment(amount, order_id)
        
        # Иначе используем multitransfer (текущая логика)
        # Получаем кастомные данные если указаны
        custom_card = data.get('card_number')
        custom_owner = data.get('card_owner')
        custom_sender = data.get('custom_sender')  # dict с данными отправителя
        
        if not amount:
            return jsonify({
                'success': False,
                'error': 'Сумма обязательна'
            }), 400
        
        # Проверка блокировки
        if current_generation['in_progress']:
            elapsed = (datetime.now() - current_generation['started_at']).total_seconds()
            return jsonify({
                'success': False,
                'error': f'Уже генерируется платёж {current_generation["order_id"]}. Попробуйте через {max(0, int(60 - elapsed))} сек.',
                'in_progress': True,
                'current_order': current_generation['order_id'],
                'elapsed_time': round(elapsed, 1)
            }), 409
        
        # Валидация суммы
        try:
            amount = int(amount)
            settings = db.get_all_settings()
            min_amount = settings.get('min_amount', 100)
            max_amount = settings.get('max_amount', 120000)
            
            if amount < min_amount or amount > max_amount:
                return jsonify({
                    'success': False,
                    'error': f'Сумма должна быть от {min_amount} до {max_amount} RUB'
                }), 400
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Неверный формат суммы'
            }), 400
        
        # Устанавливаем блокировку и очищаем логи
        with payment_lock:
            current_generation['in_progress'] = True
            current_generation['order_id'] = order_id
            current_generation['started_at'] = datetime.now()
        
        with payment_logs_lock:
            current_payment_logs.clear()
            current_payment_logs.append({
                'timestamp': datetime.now().isoformat(),
                'level': 'info',
                'message': f'Начало создания платежа {order_id} на сумму {amount}₽'
            })
        
        # Очищаем файл логов
        import os
        logs_file = os.path.join(os.path.dirname(__file__), 'current_payment_logs.json')
        try:
            if os.path.exists(logs_file):
                os.remove(logs_file)
        except:
            pass
        
        try:
            # Засекаем время начала
            start_time = time.time()
            
            # Получаем настройки
            settings = db.get_all_settings()
            
            # НЕ передаем реквизиты - они будут получены от PayzTeam API
            # Только если явно указаны кастомные реквизиты - используем их
            api_url = settings.get('api_url', API_URL)
            api_token = settings.get('api_token', API_TOKEN)
            
            # Отправляем запрос на реальный API (порт 5001)
            import requests
            
            api_payload = {
                'amount': amount,
                'orderId': order_id,
                'requisite_api': data.get('requisite_api', 'auto')  # Передаём источник реквизитов
            }
            
            # Добавляем кастомные реквизиты только если они явно указаны
            if custom_card and custom_owner:
                api_payload['card_number'] = custom_card
                api_payload['card_owner'] = custom_owner
                log_msg = f'Используются кастомные реквизиты: {custom_owner} ({custom_card})'
                db.add_log('info', log_msg)
                with payment_logs_lock:
                    current_payment_logs.append({
                        'timestamp': datetime.now().isoformat(),
                        'level': 'info',
                        'message': log_msg
                    })
            else:
                log_msg = 'Реквизиты будут получены от PayzTeam API'
                db.add_log('info', log_msg)
                with payment_logs_lock:
                    current_payment_logs.append({
                        'timestamp': datetime.now().isoformat(),
                        'level': 'info',
                        'message': log_msg
                    })
            
            # Добавляем кастомные данные отправителя если указаны
            if custom_sender:
                api_payload['custom_sender'] = custom_sender
                log_msg = f'Используются кастомные данные отправителя: {custom_sender.get("last_name")} {custom_sender.get("first_name")}'
                db.add_log('info', log_msg)
                with payment_logs_lock:
                    current_payment_logs.append({
                        'timestamp': datetime.now().isoformat(),
                        'level': 'info',
                        'message': log_msg
                    })
            
            headers = {
                'Authorization': f'Bearer {api_token}',
                'Content-Type': 'application/json'
            }
            
            target_url = f'{api_url}/api/payment'
            log_msg = f'Отправка запроса на {target_url} для заказа {order_id}'
            print(f"🔍 DEBUG: {log_msg}")  # Консольный лог для отладки
            print(f"🔍 DEBUG: Payload: {api_payload}")
            db.add_log('info', log_msg)
            with payment_logs_lock:
                current_payment_logs.append({
                    'timestamp': datetime.now().isoformat(),
                    'level': 'info',
                    'message': log_msg
                })
            
            response = requests.post(
                target_url,
                json=api_payload,
                headers=headers,
                timeout=120  # 2 минуты таймаут
            )
            
            # Вычисляем время генерации
            generation_time = time.time() - start_time
            
            print(f"🔍 DEBUG: Ответ от API - Status: {response.status_code}, Time: {generation_time:.2f}s")
            
            # Генерируем ID платежа
            all_payments = db.get_all_payments()
            payment_id = f'PAY-{len(all_payments) + 1}'
            
            if response.status_code == 201:
                # Успешный ответ от API
                api_data = response.json()
                
                # Получаем логи из ответа API
                api_logs = api_data.get('logs', [])
                print(f"📥 Получено {len(api_logs)} логов от API сервера")  # Отладка
                
                # Добавляем логи в хранилище текущего платежа
                with payment_logs_lock:
                    current_payment_logs.extend(api_logs)
                    print(f"📊 Всего логов в хранилище: {len(current_payment_logs)}")  # Отладка
                
                # Получаем реквизиты: кастомные если были переданы, иначе из ответа API (или N/A)
                card_used = custom_card if custom_card else api_data.get('card_number', 'N/A')
                owner_used = custom_owner if custom_owner else api_data.get('card_owner', 'N/A')
                
                payment_data = {
                    'id': payment_id,
                    'order_id': order_id,
                    'amount': amount,
                    'success': True,
                    'status': 'completed',
                    'qr_link': api_data.get('qr_link'),
                    'payment_time': round(generation_time, 2),
                    'timestamp': datetime.now().isoformat(),
                    'card': card_used,
                    'owner': owner_used
                }
                
                # Сохраняем в БД
                db.add_payment(payment_data)
                log_msg = f'Платёж {order_id} создан успешно: {amount}₽ за {generation_time:.2f}с'
                db.add_log('success', log_msg)
                with payment_logs_lock:
                    current_payment_logs.append({
                        'timestamp': datetime.now().isoformat(),
                        'level': 'success',
                        'message': log_msg
                    })
                
                return jsonify({
                    'success': True,
                    'order_id': order_id,
                    'amount': amount,
                    'status': 'completed',
                    'qr_link': api_data.get('qr_link'),
                    'payment_time': round(generation_time, 2),
                    'generation_time': round(generation_time, 2),
                    'total_time': round(generation_time, 2),
                    'message': 'Payment created successfully'
                }), 201
            else:
                # Ошибка от API
                error_msg = response.json().get('error', 'Unknown error') if response.text else 'API error'
                
                # Получаем логи даже при ошибке
                try:
                    api_logs = response.json().get('logs', [])
                    print(f"📥 Получено {len(api_logs)} логов от API сервера (ошибка)")  # Отладка
                    with payment_logs_lock:
                        current_payment_logs.extend(api_logs)
                        print(f"📊 Всего логов в хранилище: {len(current_payment_logs)}")  # Отладка
                except:
                    pass
                
                # Получаем реквизиты: кастомные если были переданы, иначе N/A
                card_used = custom_card if custom_card else 'N/A'
                owner_used = custom_owner if custom_owner else 'N/A'
                
                payment_data = {
                    'id': payment_id,
                    'order_id': order_id,
                    'amount': amount,
                    'success': False,
                    'status': 'failed',
                    'qr_link': None,
                    'payment_time': round(generation_time, 2),
                    'timestamp': datetime.now().isoformat(),
                    'card': card_used,
                    'owner': owner_used
                }
                
                db.add_payment(payment_data)
                log_msg = f'Платёж {order_id} не удался: {error_msg}'
                db.add_log('error', log_msg)
                with payment_logs_lock:
                    current_payment_logs.append({
                        'timestamp': datetime.now().isoformat(),
                        'level': 'error',
                        'message': log_msg
                    })
                
                return jsonify({
                    'success': False,
                    'order_id': order_id,
                    'error': error_msg,
                    'payment_time': round(generation_time, 2),
                    'generation_time': round(generation_time, 2),
                    'total_time': round(generation_time, 2)
                }), 500
        
        finally:
            # Снимаем блокировку
            with payment_lock:
                current_generation['in_progress'] = False
                current_generation['order_id'] = None
                current_generation['started_at'] = None
        
    except Exception as e:
        # Снимаем блокировку при ошибке
        with payment_lock:
            current_generation['in_progress'] = False
            current_generation['order_id'] = None
            current_generation['started_at'] = None
        
        db.add_log('error', f'Ошибка создания платежа: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Проверка статуса API"""
    return jsonify({
        'status': 'ok',
        'service': 'LinkFlow Admin Panel with Database',
        'version': '3.0.0',
        'database': 'SQLite',
        'browser_ready': True,
        'generation_in_progress': current_generation['in_progress'],
        'current_order': current_generation['order_id'] if current_generation['in_progress'] else None
    })


@app.route('/api/generation-status', methods=['GET'])
def generation_status():
    """Проверка статуса текущей генерации"""
    if current_generation['in_progress']:
        elapsed = (datetime.now() - current_generation['started_at']).total_seconds()
        return jsonify({
            'in_progress': True,
            'order_id': current_generation['order_id'],
            'elapsed_time': round(elapsed, 1),
            'started_at': current_generation['started_at'].isoformat()
        })
    else:
        return jsonify({
            'in_progress': False
        })


@app.route('/api/analytics', methods=['GET'])
def analytics():
    """Получение аналитики"""
    period = request.args.get('period', '30')
    
    try:
        days = int(period)
    except:
        days = 30
    
    now = datetime.now()
    cutoff = now - timedelta(days=days)
    
    # Получаем платежи из БД
    filtered = db.get_payments_by_period(cutoff)
    
    # Группируем по дням
    daily_stats = {}
    for payment in filtered:
        date = datetime.fromisoformat(payment['timestamp']).date().isoformat()
        if date not in daily_stats:
            daily_stats[date] = {'total': 0, 'success': 0, 'failed': 0, 'amount': 0}
        
        daily_stats[date]['total'] += 1
        if payment['success']:
            daily_stats[date]['success'] += 1
            daily_stats[date]['amount'] += payment['amount']
        else:
            daily_stats[date]['failed'] += 1
    
    # Конвертируем в массив для графиков
    chart_data = []
    for date in sorted(daily_stats.keys()):
        stats = daily_stats[date]
        chart_data.append({
            'date': date,
            'total': stats['total'],
            'success': stats['success'],
            'failed': stats['failed'],
            'amount': stats['amount'],
            'success_rate': round((stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0, 1)
        })
    
    return jsonify({
        'success': True,
        'period_days': days,
        'chart_data': chart_data,
        'total_payments': len(filtered),
        'total_success': sum(1 for p in filtered if p['success']),
        'total_failed': sum(1 for p in filtered if not p['success']),
        'total_amount': sum(p['amount'] for p in filtered if p['success']),
        'avg_payment_time': round(sum(p['payment_time'] for p in filtered if p['payment_time']) / len(filtered), 2) if filtered else 0
    })


@app.route('/api/payments', methods=['GET'])
def get_payments():
    """Получение списка платежей с фильтрацией"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    status = request.args.get('status', 'all')
    search = request.args.get('search', '')
    
    result = db.get_payments(status=status, search=search, page=page, per_page=per_page)
    
    return jsonify({
        'success': True,
        **result
    })


@app.route('/api/payments/<payment_id>', methods=['GET'])
def get_payment_detail(payment_id):
    """Получение детальной информации о платеже"""
    payment = db.get_payment_by_id(payment_id)
    
    if not payment:
        return jsonify({'success': False, 'error': 'Платёж не найден'}), 404
    
    return jsonify({
        'success': True,
        'payment': payment
    })


@app.route('/api/export', methods=['GET'])
def export_data():
    """Экспорт данных"""
    format_type = request.args.get('format', 'json')
    status = request.args.get('status', 'all')
    
    # Получаем все платежи
    all_payments = db.get_all_payments()
    
    # Фильтрация
    if status == 'success':
        filtered = [p for p in all_payments if p['success']]
    elif status == 'failed':
        filtered = [p for p in all_payments if not p['success']]
    else:
        filtered = all_payments
    
    if format_type == 'csv':
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=['id', 'order_id', 'amount', 'status', 'timestamp', 'payment_time'])
        writer.writeheader()
        for payment in filtered:
            writer.writerow({
                'id': payment['id'],
                'order_id': payment['order_id'],
                'amount': payment['amount'],
                'status': payment['status'],
                'timestamp': payment['timestamp'],
                'payment_time': payment['payment_time']
            })
        
        return output.getvalue(), 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': f'attachment; filename=payments_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        }
    else:
        return jsonify({
            'success': True,
            'data': filtered,
            'exported_at': datetime.now().isoformat()
        })


@app.route('/api/settings', methods=['GET', 'POST'])
def settings():
    """Управление настройками"""
    if request.method == 'GET':
        settings = db.get_all_settings()
        return jsonify({
            'success': True,
            'settings': settings
        })
    else:
        data = request.get_json()
        db.update_settings(data)
        db.add_log('settings', f'Настройки обновлены: {", ".join(data.keys())}')
        
        return jsonify({
            'success': True,
            'settings': db.get_all_settings()
        })


@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Получение логов системы"""
    limit = int(request.args.get('limit', 50))
    logs = db.get_logs(limit=limit)
    
    return jsonify({
        'success': True,
        'logs': logs
    })


@app.route('/api/payment-logs/current', methods=['GET'])
def get_current_payment_logs():
    """Получение логов текущего создаваемого платежа из файла"""
    import json
    import os
    
    logs_file = os.path.join(os.path.dirname(__file__), 'current_payment_logs.json')
    
    try:
        if os.path.exists(logs_file):
            with open(logs_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        else:
            logs = []
    except:
        logs = []
    
    # Также добавляем логи из памяти
    with payment_logs_lock:
        memory_logs = current_payment_logs.copy()
    
    # Объединяем логи из файла и памяти
    all_logs = logs + memory_logs
    
    return jsonify({
        'success': True,
        'logs': all_logs,
        'in_progress': current_generation['in_progress'],
        'order_id': current_generation['order_id']
    })


@app.route('/api/payment-logs/add', methods=['POST'])
def add_payment_log():
    """Добавление лога от API сервера в текущий платеж"""
    try:
        data = request.get_json()
        print(f"📥 Получен лог: {data.get('level')} - {data.get('message')}")  # Отладка
        with payment_logs_lock:
            current_payment_logs.append(data)
        return jsonify({'success': True})
    except Exception as e:
        print(f"❌ Ошибка добавления лога: {e}")
        return jsonify({'success': False}), 500


@app.route('/api/stats/summary', methods=['GET'])
def stats_summary():
    """Сводная статистика"""
    stats = db.get_stats_summary()
    
    return jsonify({
        'success': True,
        **stats
    })


@app.route('/api/beneficiaries', methods=['GET'])
def get_beneficiaries():
    """Получение всех реквизитов"""
    beneficiaries = db.get_all_beneficiaries()
    return jsonify({
        'success': True,
        'beneficiaries': beneficiaries
    })


@app.route('/api/beneficiaries', methods=['POST'])
def add_beneficiary():
    """Добавление нового реквизита с проверкой"""
    data = request.get_json()
    card_number = data.get('card_number')
    card_owner = data.get('card_owner')
    
    if not card_number or not card_owner:
        return jsonify({
            'success': False,
            'error': 'Необходимо указать номер карты и владельца'
        }), 400
    
    # Отправляем запрос на API сервер для создания и проверки
    try:
        response = requests.post(
            f'{API_URL}/api/beneficiaries',
            json={'card_number': card_number, 'card_owner': card_owner},
            headers={'Authorization': f'Bearer {API_TOKEN}'},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            db.add_log('success' if result.get('verified') else 'warning', 
                      f"Реквизит добавлен: {card_owner} - {'✓ Проверен' if result.get('verified') else '✗ Не прошел проверку'}")
            return jsonify(result)
        else:
            return jsonify(response.json()), response.status_code
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/beneficiaries/<int:beneficiary_id>', methods=['DELETE'])
def delete_beneficiary(beneficiary_id):
    """Удаление реквизита"""
    try:
        db.delete_beneficiary(beneficiary_id)
        db.add_log('info', f"Реквизит удален: ID {beneficiary_id}")
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/beneficiaries/<int:beneficiary_id>/toggle', methods=['POST'])
def toggle_beneficiary(beneficiary_id):
    """Включение/выключение реквизита"""
    data = request.get_json()
    is_active = data.get('is_active', True)
    
    try:
        db.update_beneficiary_status(beneficiary_id, is_active)
        db.add_log('info', f"Реквизит {'активирован' if is_active else 'деактивирован'}: ID {beneficiary_id}")
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/beneficiaries/retest', methods=['POST'])
def retest_beneficiary():
    """Повторная проверка реквизита"""
    data = request.get_json()
    beneficiary_id = data.get('beneficiary_id')
    card_number = data.get('card_number')
    card_owner = data.get('card_owner')
    
    if not beneficiary_id or not card_number or not card_owner:
        return jsonify({
            'success': False,
            'error': 'Необходимо указать все параметры'
        }), 400
    
    # Отправляем запрос на API сервер для проверки
    try:
        response = requests.post(
            f'{API_URL}/api/beneficiaries/retest',
            json={
                'beneficiary_id': beneficiary_id,
                'card_number': card_number,
                'card_owner': card_owner
            },
            headers={'Authorization': f'Bearer {API_TOKEN}'},
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            db.add_log('success' if result.get('verified') else 'warning', 
                      f"Повторная проверка реквизита ID {beneficiary_id}: {'✓ Успешно' if result.get('verified') else '✗ Не прошел'}")
            return jsonify(result)
        else:
            return jsonify(response.json()), response.status_code
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎨 LinkFlow Admin Panel with Database")
    print("="*60)
    print(f"📍 URL: http://localhost:5000")
    print(f"💾 Database: SQLite (linkflow.db)")
    print("="*60 + "\n")
    
    # Создаём папки
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Инициализируем БД
    print("🔧 Инициализация базы данных...")
    db.init_database()
    
    # Инициализируем настройки
    init_default_settings()
    
    # Демо-данные больше не генерируются
    # generate_demo_data()
    
    db.add_log('info', 'Сервер запущен')
    
    print("\n✅ Сервер готов к работе!")
    print("💡 Демо-данные отключены - используйте реальные платежи")
    print("🔒 Защита от одновременной генерации активна\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
