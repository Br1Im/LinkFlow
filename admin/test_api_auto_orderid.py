#!/usr/bin/env python3
"""
Тест API с автогенерацией orderId
"""

import requests
import json

url = "http://85.192.56.74/api/payment"

# Тест 1: Только amount
print("=" * 80)
print("Тест 1: Только amount (orderId должен сгенерироваться автоматически)")
print("=" * 80)

payload = {"amount": 300}

response = requests.post(
    url,
    json=payload,
    headers={"Content-Type": "application/json"},
    timeout=60
)

print(f"Status: {response.status_code}")
print(f"Response:")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

print("\n" + "=" * 80)
