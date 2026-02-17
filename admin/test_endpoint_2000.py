#!/usr/bin/env python3
"""
Тест PayzTeam API на большие суммы
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

amounts = ["2000.00", "2500.00", "3000.00", "5000.00", "10000.00"]

for amount in amounts:
    uuid = f"TEST_{int(time.time())}"
    client_email = "test@example.com"
    fiat_currency = "rub"
    payment_method = "nspk"
    
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
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        result = response.json()
        
        if result.get("success"):
            print(f"✅ {amount} RUB - SUCCESS")
            if "paymentInfo" in result:
                payment_info = result["paymentInfo"]
                print(f"   Payment Link: {payment_info.get('paymentLink', 'N/A')}")
        else:
            print(f"❌ {amount} RUB - {result.get('message', 'ERROR')}")
            
    except Exception as e:
        print(f"❌ {amount} RUB - Exception: {e}")
    
    time.sleep(1)
