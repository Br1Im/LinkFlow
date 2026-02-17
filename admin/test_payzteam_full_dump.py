#!/usr/bin/env python3
"""
Полный дамп запроса к PayzTeam API для отправки в поддержку
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'payment_service'))

import json
import time
import requests
import hashlib

MERCHANT_ID = "747"
API_KEY = "f046a50c7e398bc48124437b612ac7ab"
SECRET_KEY = "aa7c2689-98f2-428f-9c03-93e3835c3b1d"
BASE_URL = "https://payzteam.com"

print("=" * 100)
print("ПОЛНЫЙ ДАМП ЗАПРОСА К PAYZTEAM API")
print("=" * 100)

# Тест 1: 500 рублей
print("\n\n" + "=" * 100)
print("ТЕСТ #1: 500 рублей")
print("=" * 100)

uuid1 = f"TEST_{int(time.time())}"
amount1 = "500.00"
client_email = "test@example.com"
fiat_currency = "rub"
payment_method = "abh_c2c"

sign_string1 = f"{client_email}{uuid1}{amount1}{fiat_currency}{payment_method}{SECRET_KEY}"
signature1 = hashlib.sha1(sign_string1.encode('utf-8')).hexdigest()

url = f"{BASE_URL}/exchange/create_deal_v2/{MERCHANT_ID}"

print(f"\n📤 REQUEST:")
print(f"URL: {url}")
print(f"Method: POST")

headers = {
    "Content-Type": "application/json",
    "X-Api-Key": API_KEY
}

print(f"\nHeaders:")
print(json.dumps(headers, indent=2))

payload1 = {
    "client": client_email,
    "amount": amount1,
    "fiat_currency": fiat_currency,
    "uuid": uuid1,
    "language": "ru",
    "payment_method": payment_method,
    "is_intrabank_transfer": False,
    "ip": "127.0.0.1",
    "sign": signature1
}

print(f"\nBody:")
print(json.dumps(payload1, indent=2, ensure_ascii=False))

print(f"\nSign calculation:")
print(f"  String: {sign_string1}")
print(f"  SHA1: {signature1}")

try:
    response1 = requests.post(url, json=payload1, headers=headers, timeout=30)
    
    print(f"\n📥 RESPONSE:")
    print(f"Status: {response1.status_code} {response1.reason}")
    print(f"\nBody:")
    print(json.dumps(response1.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print(f"\n❌ Error: {e}")

time.sleep(2)

# Тест 2: 2500 рублей
print("\n\n" + "=" * 100)
print("ТЕСТ #2: 2500 рублей")
print("=" * 100)

uuid2 = f"TEST_{int(time.time())}"
amount2 = "2500.00"

sign_string2 = f"{client_email}{uuid2}{amount2}{fiat_currency}{payment_method}{SECRET_KEY}"
signature2 = hashlib.sha1(sign_string2.encode('utf-8')).hexdigest()

print(f"\n📤 REQUEST:")
print(f"URL: {url}")
print(f"Method: POST")

print(f"\nHeaders:")
print(json.dumps(headers, indent=2))

payload2 = {
    "client": client_email,
    "amount": amount2,
    "fiat_currency": fiat_currency,
    "uuid": uuid2,
    "language": "ru",
    "payment_method": payment_method,
    "is_intrabank_transfer": False,
    "ip": "127.0.0.1",
    "sign": signature2
}

print(f"\nBody:")
print(json.dumps(payload2, indent=2, ensure_ascii=False))

print(f"\nSign calculation:")
print(f"  String: {sign_string2}")
print(f"  SHA1: {signature2}")

try:
    response2 = requests.post(url, json=payload2, headers=headers, timeout=30)
    
    print(f"\n📥 RESPONSE:")
    print(f"Status: {response2.status_code} {response2.reason}")
    print(f"\nBody:")
    print(json.dumps(response2.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n\n" + "=" * 100)
print("КОНЕЦ ДАМПА")
print("=" * 100)
