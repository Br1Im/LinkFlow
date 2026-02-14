#!/usr/bin/env python3
"""
Тест эндпоинта с суммой 500 RUB
"""

import requests
import json

url = "http://85.192.56.74/api/create-payment"

payload = {
    "amount": 500,
    "orderId": "TEST-500-001"
}

print(f"Отправка запроса на {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, json=payload, timeout=60)
    print(f"\nStatus: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Ошибка: {e}")
