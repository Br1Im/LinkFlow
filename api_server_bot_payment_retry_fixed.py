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
    
    # Используем новый MulenPayClient для MulenPay платежей
    import asyncio
    import sys
    import os
    import uuid as uuid_lib
    import time
    import re

    # Добавляем путь к admin для импорта mulenpay
    sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
    
    from mulenpay import MulenPayClient

    MAX_RETRIES = 2
    last_error = None
    start_time = time.time()

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"[INFO] Bot payment attempt {attempt}/{MAX_RETRIES} for {bot_name}, amount: {amount}")

            # Создаем MulenPay клиент
            client = MulenPayClient(secret_key=credentials['secret_key'])
            
            # Создаем платеж
            payment_uuid = str(uuid_lib.uuid4())
            
            async def create_payment_async():
                try:
                    result = await client.create_payment(
                        private_key2=credentials['private_key2'],
                        currency="rub",
                        amount=str(amount),
                        uuid=payment_uuid,
                        shopId=credentials['shopId'],
                        description=f"Платеж {amount} руб. ({bot_name})",
                        items=[
                            {
                                "description": f"Платеж {amount} руб. ({bot_name})",
                                "quantity": 1,
                                "price": str(amount),
                                "vat_code": 0,
                                "payment_subject": 1,
                                "payment_mode": 1,
                            }
                        ],
                    )
                    return result
                finally:
                    await client.aclose()

            # Запускаем асинхронную функцию
            result = asyncio.run(create_payment_async())
            
            print(f"[INFO] MulenPay response: {result}")

            if result.get('success'):
                # Успешный ответ от MulenPay
                widget_url = result.get('paymentUrl', '')
                payment_id = result.get('id', payment_uuid)
                
                # Пытаемся получить прямую QR-ссылку
                qr_link = widget_url  # По умолчанию используем widget URL
                
                if widget_url:
                    # Извлекаем UUID из URL виджета для получения QR
                    uuid_match = re.search(r'/payment/widget/([a-f0-9-]+)', widget_url)
                    if uuid_match:
                        widget_uuid = uuid_match.group(1)
                        
                        # Пытаемся получить прямую QR-ссылку
                        try:
                            import requests
                            time.sleep(2)  # Ждем подготовки платежа
                            sbp_url = f'https://mulenpay.ru/payment/widget/{widget_uuid}/sbp'
                            sbp_response = requests.get(sbp_url, timeout=5)
                            
                            if sbp_response.status_code == 200:
                                sbp_data = sbp_response.json()
                                if sbp_data.get('success') and sbp_data.get('sbp'):
                                    qr_payload = sbp_data.get('data', {}).get('qrpayload', '')
                                    if qr_payload:
                                        qr_link = qr_payload
                                        print(f"[INFO] Got direct QR link: {qr_link[:50]}...")
                        except Exception as qr_e:
                            print(f"[WARNING] Failed to get direct QR link: {qr_e}")

                return True, {
                    'success': True,
                    'qr_link': qr_link,
                    'widget_url': widget_url,
                    'payment_id': str(payment_id),
                    'amount': amount,
                    'bot_name': bot_name
                }, 200
            else:
                # Ошибка от MulenPay
                error_msg = result.get('error', 'Unknown MulenPay error')
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