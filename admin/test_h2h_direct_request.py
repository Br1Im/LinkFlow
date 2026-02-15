#!/usr/bin/env python3
"""
Прямой запрос к H2H API с локальной машины
"""

import requests
import json
import time

# Конфигурация H2H API (из requisite_config.py на сервере)
BASE_URL = "https://api.liberty.top"
ACCESS_TOKEN = "dtpf8uupsbhumevz4pz2jebrqzqmv62o"
MERCHANT_ID = "d5c17c6c-dc40-428a-80e5-2ca01af99f68"

# Параметры заказа
external_id = f"TEST_LOCAL_{int(time.time() * 1000)}"
amount = 2500
currency = "rub"
payment_detail_type = "card"

# Формируем запрос
url = f"{BASE_URL}/api/h2h/order"
headers = {
    'Accept': 'application/json',
    'Access-Token': ACCESS_TOKEN,
    'Content-Type': 'application/json'
}

payload = {
    "amount": amount,
    "currency": currency,
    "client_id": None,
    "payer_bank": None,
    "external_id": external_id,
    "merchant_id": MERCHANT_ID,
    "callback_url": "",
    "payment_detail_type": payment_detail_type
}

print("="*60)
print("ОТПРАВКА ЗАПРОСА К H2H API")
print("="*60)
print(f"URL: {url}")
print(f"External ID: {external_id}")
print(f"Amount: {amount}")
print(f"Merchant ID: {MERCHANT_ID[:20]}...")
print()
print("Headers:")
print(json.dumps({k: v[:20] + '...' if k == 'Access-Token' else v for k, v in headers.items()}, indent=2))
print()
print("Payload:")
print(json.dumps(payload, indent=2, ensure_ascii=False))
print()

try:
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    
    print("="*60)
    print("ОТВЕТ ОТ H2H API")
    print("="*60)
    print(f"Status Code: {response.status_code}")
    print()
    
    try:
        data = response.json()
        print("JSON Response:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except:
        print("Raw Response:")
        print(response.text)
    
    print("="*60)
    
except Exception as e:
    print(f"❌ ОШИБКА: {e}")
