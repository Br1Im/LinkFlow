#!/usr/bin/env python3
"""
Тест H2H API с разными суммами
"""

import requests
import json
import time

BASE_URL = "https://api.liberty.top"
ACCESS_TOKEN = "dtpf8uupsbhumevz4pz2jebrqzqmv62o"
MERCHANT_ID = "d5c17c6c-dc40-428a-80e5-2ca01af99f68"

headers = {
    'Accept': 'application/json',
    'Access-Token': ACCESS_TOKEN,
    'Content-Type': 'application/json',
    'X-Max-Wait-Ms': '30000'
}

amounts = [1000, 1100, 1500, 2000, 2100, 2500, 3000, 5000]

for amount in amounts:
    payload = {
        "amount": amount,
        "currency": "rub",
        "external_id": f"TEST_{int(time.time())}",
        "merchant_id": MERCHANT_ID,
        "payment_detail_type": "card"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/h2h/order",
            json=payload,
            headers=headers,
            timeout=35
        )
        
        result = response.json()
        
        if result.get("success"):
            print(f"✅ {amount} RUB - SUCCESS")
            if "data" in result and "payment_detail" in result["data"]:
                detail = result["data"]["payment_detail"]
                print(f"   Card: {detail.get('detail')}")
                print(f"   Owner: {detail.get('initials')}")
        else:
            print(f"❌ {amount} RUB - {result.get('message', 'ERROR')}")
            
    except Exception as e:
        print(f"❌ {amount} RUB - Exception: {e}")
    
    time.sleep(1)
