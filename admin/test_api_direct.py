#!/usr/bin/env python3
"""
Тест прямого вызова API на сервере
"""

import requests
import json

url = "http://localhost:5001/api/payment"

payload = {
    "amount": 300,
    "orderId": "TEST-DEBUG-001"
}

headers = {
    "Content-Type": "application/json"
}

print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print(f"Headers: {headers}")
print("\nОтправка запроса...")

try:
    response = requests.post(url, json=payload, headers=headers, timeout=60)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"\nResponse Body:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print(f"\nОшибка: {e}")
