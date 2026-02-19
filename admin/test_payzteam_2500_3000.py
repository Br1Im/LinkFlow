#!/usr/bin/env python3
"""
10 запросов к PayzTeam API от 2500 до 3000 рублей
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

# 10 сумм от 2500 до 3000
amounts = ["2500.00", "2550.00", "2600.00", "2650.00", "2700.00", 
           "2750.00", "2800.00", "2850.00", "2900.00", "3000.00"]

print("=" * 100)
print("10 ЗАПРОСОВ К PAYZTEAM API (2500-3000 RUB)")
print("=" * 100)

for i, amount in enumerate(amounts, 1):вфы
    print(f"\n{'=' * 100}")
    print(f"ЗАПРОС #{i}: {amount} RUB")
    print(f"{'=' * 100}")
    
    uuid = f"TEST_{int(time.time())}"
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
    print(f"Body: {json.dumps(payload, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        result = response.json()
        
        print(f"\n📥 RESPONSE:")
        print(f"Status: {response.status_code}")
        
        if result.get("success"):
            print(f"✅ SUCCESS")
            print(f"   ID: {result.get('id')}")
            print(f"   Status: {result.get('status')}")
            
            if "paymentInfo" in result:
                payment_info = result["paymentInfo"]
                print(f"   Payment Method: {payment_info.get('payment_method')}")
                print(f"   Amount: {payment_info.get('amount')}")
                print(f"   Credentials: {payment_info.get('paymentCredentials')}")
                print(f"   Comment: {payment_info.get('paymentComment')}")
                print(f"   Rate: {payment_info.get('rate')}")
        else:
            print(f"❌ FAILED: {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n❌ Exception: {e}")
    
    if i < len(amounts):
        time.sleep(1)

print(f"\n{'=' * 100}")
print("КОНЕЦ ТЕСТОВ")
print(f"{'=' * 100}")
