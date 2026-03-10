# Улучшенная версия create_bot_payment с retry-логикой

def create_bot_payment_with_retry(bot_name, amount, credentials):
    """
    Создать платеж с автоматическими повторными попытками

    Args:
        bot_name: Название бота
        amount: Сумма платежа
        credentials: Credentials бота (shopId, secret_key, private_key2) или СБП credentials

    Returns:
        tuple: (success: bool, data: dict, status_code: int)
    """
    
    # Проверяем тип платежа - если СБП, используем отдельную функцию
    if credentials.get("type") == "sbp":
        from sbp_api_integration import create_sbp_payment
        return create_sbp_payment(bot_name, amount, credentials)
    
    # Далее идет оригинальная логика для MulenPay
    import re
    import requests
    import time
    import uuid as uuid_lib
    import hashlib
    import json

    MAX_RETRIES = 2  # Уменьшаем количество попыток
    MULENPAY_TIMEOUT = 15  # Timeout для MulenPay API
    SBP_TIMEOUT = 8  # Timeout для SBP запроса
    last_error = None
    start_time = time.time()

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"[INFO] Bot payment attempt {attempt}/{MAX_RETRIES} for {bot_name}, amount: {amount}")

            # Создаем платеж напрямую через requests (синхронно)
            payment_uuid = str(uuid_lib.uuid4())

            # Вычисляем sign
            currency = "rub"
            amount_str = str(amount)
            shop_id = credentials['shopId']
            secret_key = credentials['secret_key']

            raw = f"{currency}{amount_str}{shop_id}{secret_key}"
            sign = hashlib.sha1(raw.encode("utf-8")).hexdigest()

            # Формируем payload
            payload = {
                "currency": currency,
                "amount": int(amount),  # Отправляем как число
                "uuid": payment_uuid,
                "shopId": shop_id,
                "description": f"Платеж {amount} руб. ({bot_name})",
                "sign": sign
            }

            print(f"[INFO] MulenPay payload: {payload}")

            # Отправляем запрос к MulenPay
            response = requests.post(
                "https://mulenpay.ru/api/payment/create",
                json=payload,
                timeout=MULENPAY_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'LinkFlow-API/1.0'
                }
            )

            print(f"[INFO] MulenPay response status: {response.status_code}")
            print(f"[INFO] MulenPay response: {response.text}")

            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    # Успешный ответ от MulenPay
                    widget_url = data.get('widget_url', '')
                    qr_link = data.get('qr_link', '')
                    
                    return True, {
                        'success': True,
                        'qr_link': qr_link,
                        'widget_url': widget_url,
                        'payment_id': payment_uuid,
                        'amount': amount,
                        'bot_name': bot_name
                    }, 200
                else:
                    # Ошибка от MulenPay
                    error_msg = data.get('error', 'Unknown MulenPay error')
                    print(f"[ERROR] MulenPay error: {error_msg}")
                    last_error = error_msg
                    
                    if attempt < MAX_RETRIES:
                        print(f"[INFO] Retrying in 2 seconds...")
                        time.sleep(2)
                        continue
                    else:
                        return False, {
                            'success': False,
                            'error': error_msg,
                            'bot_name': bot_name
                        }, 400
            else:
                # HTTP ошибка
                error_msg = f"HTTP {response.status_code}: {response.text}"
                print(f"[ERROR] MulenPay HTTP error: {error_msg}")
                last_error = error_msg
                
                if attempt < MAX_RETRIES:
                    print(f"[INFO] Retrying in 2 seconds...")
                    time.sleep(2)
                    continue
                else:
                    return False, {
                        'success': False,
                        'error': error_msg,
                        'bot_name': bot_name
                    }, 400

        except requests.Timeout:
            error_msg = f"Timeout after {MULENPAY_TIMEOUT}s"
            print(f"[ERROR] MulenPay timeout: {error_msg}")
            last_error = error_msg
            
            if attempt < MAX_RETRIES:
                print(f"[INFO] Retrying after timeout...")
                time.sleep(1)
                continue
            else:
                return False, {
                    'success': False,
                    'error': error_msg,
                    'bot_name': bot_name
                }, 408

        except requests.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            print(f"[ERROR] MulenPay network error: {error_msg}")
            last_error = error_msg
            
            if attempt < MAX_RETRIES:
                print(f"[INFO] Retrying after network error...")
                time.sleep(2)
                continue
            else:
                return False, {
                    'success': False,
                    'error': error_msg,
                    'bot_name': bot_name
                }, 500

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(f"[ERROR] Unexpected error: {error_msg}")
            last_error = error_msg
            
            if attempt < MAX_RETRIES:
                print(f"[INFO] Retrying after unexpected error...")
                time.sleep(2)
                continue
            else:
                return False, {
                    'success': False,
                    'error': error_msg,
                    'bot_name': bot_name
                }, 500

    # Если дошли сюда, значит все попытки исчерпаны
    total_time = time.time() - start_time
    print(f"[ERROR] All {MAX_RETRIES} attempts failed for {bot_name} in {total_time:.2f}s")
    
    return False, {
        'success': False,
        'error': f'All {MAX_RETRIES} attempts failed. Last error: {last_error}',
        'bot_name': bot_name,
        'attempts': MAX_RETRIES,
        'total_time': round(total_time, 2)
    }, 500