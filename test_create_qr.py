#!/usr/bin/env python3
import requests
import json

url = "http://localhost:5001/api/create-qr-payment"
payload = {
    "amount": 3000
}

print("Создаю платеж на 3000 руб...")
response = requests.post(url, json=payload)
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
