#!/usr/bin/env python3
"""
Генерация платежной ссылки через Merchant API
"""

import requests
import json

BASE_URL = "https://liberty.top"  # Для Merchant API используется liberty.top (без api.)
ACCESS_TOKEN = "dtpf8uupsbhumevz4pz2jebrqzqmv62o"
MERCHANT_ID = "d5c17c6c-dc40-428a-80e5-2ca01af99f68"

headers = {
    'Accept': 'application/json',
    'Access-Token': ACCESS_TOKEN,
    'Content-Type': 'application/json',
    'X-Max-Wait-Ms': '30000'
}

payload = {
    "external_id": "PAYMENT_LINK_001",
    "amount": 2500,
    "merchant_id": MERCHANT_ID,
    "currency": "rub",
    "payment_detail_type": "card"
}

print("REQUEST TO MERCHANT API:")
print(json.dumps(payload, indent=2, ensure_ascii=False))
print("\n" + "="*70 + "\n")

response = requests.post(
    f"{BASE_URL}/api/merchant/order",
    json=payload,
    headers=headers,
    timeout=35
)

print("RESPONSE:")
data = response.json()
print(json.dumps(data, indent=2, ensure_ascii=False))

if data.get("success"):
    print("\n" + "="*70)
    print("ПЛАТЕЖНАЯ ССЫЛКА:")
    print(data["data"]["payment_link"])
    print("="*70)
    print("\nРЕКВИЗИТЫ:")
    payment_detail = data["data"].get("payment_detail", {})
    print(f"Номер карты: {payment_detail.get('detail')}")
    print(f"Владелец: {payment_detail.get('initials')}")
