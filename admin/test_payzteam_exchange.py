#!/usr/bin/env python3
"""
Тестовый запрос к PayzTeam Exchange API (P2P)
"""

import requests
import hashlib
import json
import time

# Конфигурация
MERCHANT_ID = "747"
API_KEY = "f046a50c7e398bc48124437b612ac7ab"  # API ключ для X-Api-Key
SECRET_KEY = "aa7c2689-98f2-428f-9c03-93e3835c3b1d"  # Секретный ключ для подписи

# Параметры платежа
client_email = "test@test.ru"
amount = "1000.00"
uuid = f"TEST_{int(time.time())}"
fiat_currency = "rub"
payment_method = "abh_c2c"

# Генерация подписи: sha1(client+uuid+amount+fiat_currency+payment_method+SecretKey)
sign_string = f"{client_email}{uuid}{amount}{fiat_currency}{payment_method}{SECRET_KEY}"
signature = hashlib.sha1(sign_string.encode('utf-8')).hexdigest()

# Тело запроса
payload = {
    "client": client_email,
    "amount": amount,
    "fiat_currency": fiat_currency,
    "uuid": uuid,
    "language": "ru",
    "payment_method": payment_method,
    "is_intrabank_transfer": False,
    "ip": "127.0.0.1",
    "sign": signature
}

# Заголовки
headers = {
    "Content-Type": "application/json",
    "X-Api-Key": API_KEY
}

print("=" * 60)
print("ТЕСТОВЫЙ ЗАПРОС К PAYZTEAM EXCHANGE API (P2P)")
print("=" * 60)
print(f"\nMerchant ID: {MERCHANT_ID}")
print(f"UUID: {uuid}")
print(f"Amount: {amount} {fiat_currency}")
print(f"Payment Method: {payment_method}")
print(f"\nURL: https://payzteam.com/exchange/create_deal_v2/{MERCHANT_ID}")
print(f"\nЗаголовки:")
print(json.dumps(headers, indent=2))
print(f"\nТело запроса:")
print(json.dumps(payload, indent=2, ensure_ascii=False))
print(f"\nСтрока для подписи: {sign_string}")
print(f"Подпись (SHA1): {signature}")

print("\n" + "=" * 60)
print("ОТПРАВКА ЗАПРОСА...")
print("=" * 60)

try:
    response = requests.post(
        f"https://payzteam.com/exchange/create_deal_v2/{MERCHANT_ID}",
        json=payload,
        headers=headers,
        timeout=30
    )
    
    print(f"\nСтатус код: {response.status_code}")
    
    print(f"\n" + "=" * 60)
    print("СТРУКТУРА ОТВЕТА:")
    print("=" * 60)
    
    try:
        result = response.json()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Если платеж создан успешно
        if result.get("success"):
            deal_id = result.get("id")
            print(f"\n✅ Платеж создан успешно!")
            print(f"ID платежа: {deal_id}")
            print(f"Статус: {result.get('status')}")
            
            if "paymentInfo" in result:
                print("\n📋 Информация для оплаты:")
                print(json.dumps(result["paymentInfo"], indent=2, ensure_ascii=False))
            
            # Проверяем статус
            print("\n" + "=" * 60)
            print("ПРОВЕРКА СТАТУСА ПЛАТЕЖА")
            print("=" * 60)
            
            status_response = requests.post(
                "https://payzteam.com/exchange/get",
                json={"id": deal_id},
                headers=headers,
                timeout=30
            )
            
            print(f"Статус код: {status_response.status_code}")
            print(json.dumps(status_response.json(), indent=2, ensure_ascii=False))
            
            # Отменяем платеж
            print("\n" + "=" * 60)
            print("ОТМЕНА ПЛАТЕЖА")
            print("=" * 60)
            
            cancel_response = requests.post(
                "https://payzteam.com/exchange/cancel",
                data={"id": str(deal_id)},
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-Api-Key": API_KEY
                },
                timeout=30
            )
            
            print(f"Статус код: {cancel_response.status_code}")
            print(json.dumps(cancel_response.json(), indent=2, ensure_ascii=False))
            
    except Exception as e:
        print(f"Ошибка парсинга JSON: {e}")
        print("Ответ (текст):")
        print(response.text)
    
except requests.exceptions.RequestException as e:
    print(f"\n❌ Ошибка запроса: {e}")

print("\n" + "=" * 60)
print("ЗАВЕРШЕНО")
print("=" * 60)
