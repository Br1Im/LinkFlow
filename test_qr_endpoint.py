#!/usr/bin/env python3
import requests
import json

url = "http://localhost:5001/api/get-qr-link"
payload = {
    "widget_url": "https://mulenpay.ru/payment/widget/341f0c1b-eab5-4621-87c5-64a1e21d4b63"
}

response = requests.post(url, json=payload)
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
