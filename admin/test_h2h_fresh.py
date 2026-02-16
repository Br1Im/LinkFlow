#!/usr/bin/env python3
"""
Свежий тест H2H API с уникальным external_id
"""
import requests
import json
import time
import random

BASE_URL = "https://api.liberty.top"
ACCESS_TOKEN = "dtpf8uupsbhumevz4pz2jebrqzqmv62o"
MERCHANT_ID = "d5c17c6c-dc40-428a-80e5-2ca01af99f68"

headers = {
    'Accept': 'application/json',
    'Access-Token': ACCESS_TOKEN,
    'Content-Type': 'application/json',
    'X-Max-Wait-Ms': '30000'
}

# Генерируем уникальный external_id
timestamp = int(time.time())
random_part = random.randint(1000, 9999)
external_id = f"FRESH_{timestamp}_{random_part}"

payload = {
    "amount": 2500,
    "currency": "rub",
    "client_id": None,
    "payer_bank": None,
    "external_id": external_id,
    "merchant_id": MERCHANT_ID,
    "callback_url": "",
    "payment_detail_type": "card"
}

print("="*70)
print("СВЕЖИЙ ЗАПРОС К H2H API")
print("="*70)
print(f"URL: {BASE_URL}/api/h2h/order")
print(f"External ID: {external_id}")
print(f"Amount: {payload['amount']}")
print()
print("REQUEST:")
print(json.dumps(payload, indent=2, ensure_ascii=False))
print()
print("="*70)

try:
    response = requests.post(
        f"{BASE_URL}/api/h2h/order",
        json=payload,
        headers=headers,
        timeout=35
    )
    
    print("RESPONSE:")
    print(f"Status Code: {response.status_code}")
    print()
    
    result = response.json()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print()
    print("="*70)
    
    if result.get('success'):
        data = result['data']
        pd = data.get('payment_detail', {})
        print()
        print("✅ УСПЕХ!")
        print(f"Order ID: {data.get('order_id')}")
        print(f"Карта: {pd.get('detail')}")
        print(f"Владелец: {pd.get('initials')}")
        print(f"Банк: {pd.get('bank', 'N/A')}")
        print(f"Gateway: {data.get('payment_gateway_name')} ({data.get('payment_gateway')})")
        print(f"Статус: {data.get('status')}")
        print(f"Истекает: {data.get('expires_at')}")
    else:
        print()
        print("❌ ОШИБКА")
        print(f"Message: {result.get('message', 'N/A')}")
        
except Exception as e:
    print(f"❌ ИСКЛЮЧЕНИЕ: {e}")
