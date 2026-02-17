#!/usr/bin/env python3
"""
Тест PayzTeam API на 2000 рублей с методом abh_c2c
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
print("ЗАПРОС К PAYZTEAM API: 1000 RUB")
print("=" * 100)

uuid = f"TEST_{int(time.time())}"
amount = "1000.00"
client_email = "test@example.com"
fiat_currency = "rub"
payment_method = "abh_c2c"

sign_string = f"{client_email}{uuid}{amount}{fiat_currency}{payment_method}{SECRET_KEY}"
signature = hashlib.sha1(sign_string.encode('utf-8')).hexdigest()

url = f"{BASE_URL}/exchange/create_deal_v2/{MERCHANT_ID}"

headers = {
    "Content-Type": "application/json",
    "X-Api-Key": API_KEY
}

payload = {
    "client": client_email,
    "amount": amount,
    "fiat_currency": fiat_currency,
    "uuid": uuid,
    "language": "ru",
    "payment_method": payment_method,
    "is_intrabank_transfer": False,
    "ip": "127.0.0.1",
    "sign": signature
}

print(f"\n📤 REQUEST:")
print(f"URL: {url}")
print(f"\nHeaders:")
print(json.dumps(headers, indent=2))
print(f"\nBody:")
print(json.dumps(payload, indent=2, ensure_ascii=False))
print(f"\nSign calculation:")
print(f"  String: {sign_string}")
print(f"  SHA1: {signature}")

try:
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    
    print(f"\n📥 RESPONSE:")
    print(f"Status: {response.status_code} {response.reason}")
    
    result = response.json()
    print(f"\nBody:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if result.get("success"):
        print(f"\n✅ SUCCESS")
        print(f"   ID: {result.get('id')}")
        print(f"   Status: {result.get('status')}")
        
        if "paymentInfo" in result:
            payment_info = result["paymentInfo"]
            print(f"\n💳 Payment Info:")
            print(f"   Method: {payment_info.get('payment_method')}")
            print(f"   Amount: {payment_info.get('amount')}")
            print(f"   Credentials: {payment_info.get('paymentCredentials')}")
            print(f"   Comment: {payment_info.get('paymentComment')}")
            print(f"   Rate: {payment_info.get('rate')}")
    else:
        print(f"\n❌ FAILED: {result.get('message', 'Unknown error')}")
        
except Exception as e:
    print(f"\n❌ Exception: {e}")

print(f"\n{'=' * 100}")
