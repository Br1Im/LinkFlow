#!/usr/bin/env python3
"""
Тест API с читаемым выводом
"""

import requests
import json

url = "http://85.192.56.74/api/create-payment"
payload = {"amount": 300}

print("Отправка запроса...")
print(f"URL: {url}")
print(f"Payload: {payload}")
print("=" * 80)

response = requests.post(
    url,
    json=payload,
    headers={"Content-Type": "application/json"},
    timeout=60
)

print(f"\nStatus: {response.status_code}")
print("\nОтвет:")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
