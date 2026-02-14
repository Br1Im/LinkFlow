#!/usr/bin/env python3
"""
Тест создания платежа через PayzTeam
"""

import requests
import json

url = "http://85.192.56.74/api/create-payment"

payload = {
    "amount": 1000,
    "orderId": "TEST-PAYZTEAM-001"
}

print(f"Отправка запроса на {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, json=payload, timeout=120)
    print(f"\nStatus: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Ошибка: {e}")
