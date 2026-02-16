#!/usr/bin/env python3
"""
Тест H2H API с пустыми external_id и merchant_id как сказали разработчики KeyGatePay
"""

import requests
import json

BASE_URL = "https://api.liberty.top"
ACCESS_TOKEN = "dtpf8uupsbhumevz4pz2jebrqzqmv62o"

headers = {
    'Accept': 'application/json',
    'Access-Token': ACCESS_TOKEN,
    'Content-Type': 'application/json',
    'X-Max-Wait-Ms': '30000'
}

# Точно как сказали разработчики KeyGatePay
payload = {
    "amount": 2500,
    "currency": "rub",
    "client_id": None,
    "payer_bank": None,
    "external_id": "",
    "merchant_id": "",
    "callback_url": "",
    "payment_detail_type": "card"
}

print("REQUEST:")
print(json.dumps(payload, indent=2, ensure_ascii=False))
print("\n" + "="*70 + "\n")

try:
    response = requests.post(
        f"{BASE_URL}/api/h2h/order",
        json=payload,
        headers=headers,
        timeout=35
    )
    
    print(f"STATUS CODE: {response.status_code}")
    print("\nRESPONSE:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print(f"ERROR: {e}")
