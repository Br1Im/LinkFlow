#!/usr/bin/env python3
"""
Один запрос к H2H API - полное тело ответа.
"""

import requests
import json

BASE_URL = "https://api.liberty.top"
ACCESS_TOKEN = "dtpf8uupsbhumevz4pz2jebrqzqmv62o"
MERCHANT_ID = "d5c17c6c-dc40-428a-80e5-2ca01af99f68"

headers = {
    'Accept': 'application/json',
    'Access-Token': ACCESS_TOKEN,
    'Content-Type': 'application/json',
    'X-Max-Wait-Ms': '30000'
}

payload = {
    "amount": 2500,
    "currency": "rub",
    "client_id": None,
    "payer_bank": None,
    "external_id": "TEST_CUSTOM_006",
    "merchant_id": MERCHANT_ID,
    "callback_url": "",
    "payment_detail_type": "card"
}

print("REQUEST:")
print(json.dumps(payload, indent=2, ensure_ascii=False))
print("\n" + "="*70 + "\n")

response = requests.post(
    f"{BASE_URL}/api/h2h/order",
    json=payload,
    headers=headers,
    timeout=35
)

print("RESPONSE:")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
