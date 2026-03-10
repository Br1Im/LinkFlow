# Интеграция СБП для API сервера
import requests
import hashlib
import time
import uuid as uuid_lib

def create_sbp_payment(bot_name, amount, credentials):
    """
    Создать СБП платеж через 1payment.com API
    
    Args:
        bot_name: Название бота
        amount: Сумма платежа
        credentials: Credentials для СБП (partner_id, project_id, secret_key, shop_url)
        
    Returns:
        tuple: (success: bool, data: dict, status_code: int)
    """
    try:
        print(f"[INFO] Creating SBP payment for {bot_name}, amount: {amount}")
        
        # Генерируем уникальный order_id
        order_id = f"api_{bot_name}_{int(time.time())}_{amount}"
        
        # Подготавливаем данные для СБП API
        payment_data = {
            "partner_id": credentials['partner_id'],
            "project_id": credentials['project_id'],
            "amount": int(amount),
            "description": f"Платеж {amount} руб. ({bot_name})",
            "user_id": f"api_user_{int(time.time())}",
            "shop_url": credentials['shop_url'],
            "user_data": order_id,
            "success_url": f"{credentials['shop_url']}/success",
            "failure_url": f"{credentials['shop_url']}/failure"
        }
        
        # Генерируем подпись
        signature = generate_sbp_signature(payment_data, credentials['secret_key'])
        payment_data["sign"] = signature
        
        # Формируем URL с параметрами
        params = "&".join([f"{k}={v}" for k, v in payment_data.items()])
        url = f"https://api.1payment.com/init_form?{params}"
        
        print(f"[INFO] SBP API URL: {url}")
        
        # Отправляем запрос
        response = requests.get(url, timeout=10)
        
        print(f"[INFO] SBP API Response Status: {response.status_code}")
        print(f"[INFO] SBP API Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            
            if "error" in result:
                return False, {
                    'success': False,
                    'error': result.get('error', 'Unknown SBP error'),
                    'bot_name': bot_name
                }, 400
            
            # Успешный ответ - получили payment_url
            payment_url = result.get('url')
            if payment_url:
                print(f"[INFO] Got payment URL: {payment_url}")
                
                # НОВОЕ: Пытаемся получить прямую QR-ссылку (быстро - максимум 6 секунд)
                qr_link = extract_qr_link_from_payment_url(payment_url, timeout=6)
                
                if qr_link:
                    print(f"[INFO] Successfully extracted QR link: {qr_link}")
                    final_qr_link = qr_link
                else:
                    print(f"[WARNING] Could not extract QR link quickly, using payment URL")
                    final_qr_link = payment_url
                
                return True, {
                    'success': True,
                    'payment_url': payment_url,
                    'qr_link': final_qr_link,  # Используем настоящую QR-ссылку
                    'widget_url': payment_url,
                    'payment_id': order_id,
                    'amount': amount,
                    'bot_name': bot_name,
                    'payment_type': 'sbp'
                }, 200
            else:
                return False, {
                    'success': False,
                    'error': 'No payment URL in response',
                    'bot_name': bot_name
                }, 400
        else:
            return False, {
                'success': False,
                'error': f'SBP API error: {response.status_code}',
                'details': response.text,
                'bot_name': bot_name
            }, 400
            
    except requests.RequestException as e:
        print(f"[ERROR] SBP API network error: {e}")
        return False, {
            'success': False,
            'error': 'Network error connecting to SBP API',
            'details': str(e),
            'bot_name': bot_name
        }, 500
        
    except Exception as e:
        print(f"[ERROR] SBP payment creation error: {e}")
        return False, {
            'success': False,
            'error': 'Internal error creating SBP payment',
            'details': str(e),
            'bot_name': bot_name
        }, 500

def extract_qr_link_from_payment_url(payment_url, timeout=6):
    """
    Извлекает прямую QR-ссылку из payment URL используя быструю браузерную автоматизацию
    
    Args:
        payment_url: URL платежа (например, https://gate.minopay.net/abc123)
        timeout: Максимальное время ожидания в секундах (по умолчанию 6)
        
    Returns:
        str: Прямая QR-ссылка qr.nspk.ru или None если не найдена
    """
    import re
    import random
    import json
    
    try:
        print(f"[INFO] Extracting QR link from: {payment_url} (timeout: {timeout}s)")
        
        # Сначала пробуем быстрый подход без браузера (2 секунды)
        qr_link = try_quick_extraction(payment_url)
        if qr_link:
            return qr_link
        
        # Если быстрый подход не сработал, используем браузерную автоматизацию (4 секунды)
        print(f"[INFO] Quick extraction failed, trying browser automation...")
        return try_browser_extraction(payment_url, timeout - 2)
        
    except Exception as e:
        print(f"[ERROR] Error extracting QR link: {e}")
        return None

def try_quick_extraction(payment_url):
    """Быстрая попытка извлечения без браузера"""
    import re
    import random
    import json
    
    try:
        # Загружаем страницу платежа
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ru,en;q=0.9",
        }
        
        response = requests.get(payment_url, headers=headers, timeout=3)
        if response.status_code != 200:
            return None
        
        # Заголовки для AJAX запросов
        ajax_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, */*",
            "Accept-Language": "ru,en;q=0.9",
            "Referer": payment_url,
            "X-Requested-With": "XMLHttpRequest",
        }
        
        payment_id = payment_url.split('/')[-1]
        
        # Пробуем быстрые варианты AJAX запросов
        quick_variants = [
            f"https://gate.minopay.net/pp/{payment_id}/?checkPaymentState=1",
            f"https://gate.minopay.net/pp/spm_{payment_id}/?checkPaymentState=1",
        ]
        
        # Пробуем с коротким ожиданием
        for wait_time in [0.5, 1]:
            if wait_time > 0.5:
                time.sleep(wait_time - 0.5)
            
            for ajax_url in quick_variants:
                try:
                    nc = random.random()
                    ajax_url_with_nc = f"{ajax_url}&nc={nc}"
                    
                    ajax_response = requests.get(ajax_url_with_nc, headers=ajax_headers, timeout=2)
                    
                    if ajax_response.status_code == 200:
                        try:
                            data = ajax_response.json()
                            
                            if isinstance(data, dict) and data.get('action') == 'qrcode' and 'url' in data:
                                qr_url = data['url']
                                if 'qr.nspk.ru' in qr_url:
                                    print(f"[SUCCESS] Quick extraction found QR link: {qr_url}")
                                    return qr_url
                                        
                        except json.JSONDecodeError:
                            pass
                                    
                except Exception:
                    continue
        
        return None
        
    except Exception:
        return None

def try_browser_extraction(payment_url, timeout=4):
    """Извлечение QR-ссылки через быструю браузерную автоматизацию"""
    
    try:
        # Проверяем наличие playwright
        try:
            import asyncio
            from playwright.async_api import async_playwright
        except ImportError:
            print(f"[WARNING] Playwright not available, cannot extract QR link")
            return None
        
        print(f"[INFO] Starting fast browser automation for QR extraction...")
        
        # Запускаем асинхронную функцию
        return asyncio.run(extract_with_playwright(payment_url, timeout))
        
    except Exception as e:
        print(f"[ERROR] Browser extraction failed: {e}")
        return None

async def extract_with_playwright(payment_url, timeout):
    """Быстрое асинхронное извлечение QR-ссылки через Playwright"""
    
    try:
        from playwright.async_api import async_playwright
        import asyncio
        import json
        import re
        
        found_qr_link = None
        
        async with async_playwright() as p:
            # Запускаем браузер в headless режиме с оптимизациями
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu'
                ]
            )
            context = await browser.new_context()
            page = await context.new_page()
            
            # Перехватываем все сетевые запросы
            async def handle_response(response):
                nonlocal found_qr_link
                
                # Если уже нашли QR-ссылку, не обрабатываем дальше
                if found_qr_link:
                    return
                
                url = response.url
                status = response.status
                
                # Проверяем интересные запросы
                if 'checkPaymentState=1' in url and status == 200:
                    try:
                        content_type = response.headers.get('content-type', '')
                        
                        if 'application/json' in content_type:
                            response_text = await response.text()
                            
                            try:
                                json_data = json.loads(response_text)
                                
                                if isinstance(json_data, dict):
                                    if json_data.get('action') == 'qrcode' and 'url' in json_data:
                                        qr_url = json_data['url']
                                        if 'qr.nspk.ru' in qr_url:
                                            print(f"[SUCCESS] Browser found QR link: {qr_url}")
                                            found_qr_link = qr_url
                                            return
                                    
                                    # Проверяем все поля
                                    for key, value in json_data.items():
                                        if isinstance(value, str) and 'qr.nspk.ru' in value:
                                            print(f"[SUCCESS] Browser found QR link in field '{key}': {value}")
                                            found_qr_link = value
                                            return
                                            
                            except json.JSONDecodeError:
                                pass
                                
                    except Exception as e:
                        pass
            
            # Подключаем обработчик ответов
            page.on('response', handle_response)
            
            try:
                # Переходим на страницу платежа
                await page.goto(payment_url, wait_until='domcontentloaded', timeout=timeout*1000//2)
                
                # Ждем загрузки JavaScript и AJAX запросов
                await asyncio.sleep(timeout//2)
                
                # Если QR-ссылка еще не найдена, делаем короткую попытку
                if not found_qr_link:
                    await asyncio.sleep(timeout//4)
                
            except Exception as e:
                print(f"[ERROR] Browser navigation error: {e}")
            
            finally:
                await browser.close()
        
        return found_qr_link
        
    except Exception as e:
        print(f"[ERROR] Playwright extraction error: {e}")
        return None

def generate_sbp_signature(data, secret_key):
    """
    Генерация подписи для СБП API согласно документации 1payment.com
    
    Format: md5("init_form" + concatenated_params_in_alphabetical_order + secret_key)
    """
    # Сортируем параметры по ключу в алфавитном порядке
    sorted_params = sorted(data.items())
    
    # Создаем строку для подписи: init_form + params + secret_key
    sign_string = "init_form"
    
    for key, value in sorted_params:
        if key != "sign":
            sign_string += f"{key}={value}&"
    
    # Убираем последний & и добавляем секретный ключ
    sign_string = sign_string.rstrip("&")
    sign_string += secret_key
    
    # Генерируем MD5 хеш
    signature = hashlib.md5(sign_string.encode('utf-8')).hexdigest()
    
    return signature