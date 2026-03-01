# Улучшенная версия create_bot_payment с retry-логикой

def create_bot_payment_with_retry(bot_name, amount, credentials):
    """
    Создать платеж с автоматическими повторными попытками
    
    Args:
        bot_name: Название бота
        amount: Сумма платежа
        credentials: Credentials бота (shopId, secret_key, private_key2)
    
    Returns:
        tuple: (success: bool, data: dict, status_code: int)
    """
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
                "items": [
                    {
                        "description": f"Платеж {amount} руб.",
                        "quantity": 1,
                        "price": str(amount),
                        "vat_code": 0,
                        "payment_subject": 1,
                        "payment_mode": 1,
                    }
                ],
                "sign": sign
            }
            
            # Отправляем запрос
            headers = {
                "Authorization": f"Bearer {credentials['private_key2']}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            response = requests.post(
                "https://mulenpay.ru/api/v2/payments",
                json=payload,
                headers=headers,
                timeout=MULENPAY_TIMEOUT
            )
            
            if response.status_code not in [200, 201]:
                raise Exception(f"MulenPay API returned {response.status_code}: {response.text}")
            
            response_data = response.json()
            payment_id = response_data.get('id')
            widget_url = response_data.get('paymentUrl')
            
            if not widget_url:
                raise Exception('Failed to create payment: no widget URL')
            
            print(f"[SUCCESS] Payment created: ID={payment_id}, URL={widget_url}")
            
            # Извлекаем UUID из URL виджета
            uuid_match = re.search(r'/payment/widget/([a-f0-9-]+)', widget_url)
            if not uuid_match:
                raise Exception(f'Invalid widget URL format: {widget_url}')
            
            payment_uuid_from_url = uuid_match.group(1)
            
            # Запрашиваем /sbp endpoint для получения прямой QR-ссылки (с retry)
            qr_link = None
            for sbp_attempt in range(1, 3):
                try:
                    print(f"[INFO] Requesting SBP QR link, attempt {sbp_attempt}/2")
                    time.sleep(0.5)  # Уменьшаем паузу
                    
                    sbp_url = f'https://mulenpay.ru/payment/widget/{payment_uuid_from_url}/sbp'
                    sbp_response = requests.get(sbp_url, timeout=SBP_TIMEOUT)
                    
                    if sbp_response.status_code == 200:
                        sbp_data = sbp_response.json()
                        if sbp_data.get('success') and sbp_data.get('sbp'):
                            qr_payload = sbp_data.get('data', {}).get('qrpayload', '')
                            if qr_payload:
                                qr_link = qr_payload
                                print(f"[SUCCESS] QR link obtained: {qr_link[:50]}...")
                                break
                except Exception as e:
                    print(f"[WARNING] SBP request failed (attempt {sbp_attempt}): {str(e)}")
                    if sbp_attempt < 2:
                        time.sleep(1)  # Уменьшаем паузу перед повтором
            
            # Возвращаем результат
            elapsed_time = time.time() - start_time
            result = {
                'success': True,
                'qr_link': qr_link if qr_link else widget_url,
                'widget_url': widget_url,
                'payment_id': payment_id,
                'amount': amount,
                'bot_name': bot_name,
                'processing_time': round(elapsed_time, 2)
            }
            
            if not qr_link:
                result['warning'] = 'Failed to get direct QR link, returning widget URL'
                print(f"[WARNING] Failed to get QR link, returning widget URL")
            
            print(f"[SUCCESS] Payment completed in {elapsed_time:.2f}s")
            return (True, result, 200)
                
        except requests.exceptions.Timeout as e:
            last_error = e
            elapsed_time = time.time() - start_time
            print(f"[ERROR] Timeout on attempt {attempt}/{MAX_RETRIES} for {bot_name} after {elapsed_time:.2f}s")
            
            # При timeout не ждем долго перед повтором
            if attempt < MAX_RETRIES:
                print(f"[INFO] Retrying immediately...")
                time.sleep(0.5)
            else:
                print(f"[ERROR] All {MAX_RETRIES} attempts failed for {bot_name}")
                
        except Exception as e:
            last_error = e
            error_msg = str(e) if str(e) else 'Unknown error'
            elapsed_time = time.time() - start_time
            print(f"[ERROR] Attempt {attempt}/{MAX_RETRIES} failed for {bot_name} after {elapsed_time:.2f}s: {error_msg}")
            
            # Если это не последняя попытка, ждем перед повтором
            if attempt < MAX_RETRIES:
                wait_time = 1  # Уменьшаем задержку до 1 секунды
                print(f"[INFO] Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                # Последняя попытка не удалась
                print(f"[ERROR] All {MAX_RETRIES} attempts failed for {bot_name}")
    
    # Если все попытки провалились
    import traceback
    total_elapsed_time = time.time() - start_time
    error_details = traceback.format_exc()
    print(f"[ERROR] Final error details after {total_elapsed_time:.2f}s:")
    print(error_details)
    
    return (False, {
        'success': False,
        'error': str(last_error) if str(last_error) else 'Unknown error',
        'error_type': type(last_error).__name__,
        'bot_name': bot_name,
        'processing_time': round(total_elapsed_time, 2)
    }, 500)
