#!/usr/bin/env python3
"""
Тест PayzTeam с суммами 2500 и 3000 рублей
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'payment_service'))

import json
import time
import requests
import hashlib

# ============================================
# РЕАЛЬНЫЕ CREDENTIALS
# ============================================
MERCHANT_ID = "747"
API_KEY = "f046a50c7e398bc48124437b612ac7ab"
SECRET_KEY = "aa7c2689-98f2-428f-9c03-93e3835c3b1d"
BASE_URL = "https://payzteam.com"

def test_amount(amount):
    """Тест с указанной суммой"""
    
    uuid = f"TEST_{int(time.time())}"
    client_email = "test@example.com"
    fiat_currency = "rub"
    payment_method = "nspk"
    language = "ru"
    client_ip = "127.0.0.1"
    is_intrabank_transfer = False
    
    # Генерация подписи
    sign_string = f"{client_email}{uuid}{amount}{fiat_currency}{payment_method}{SECRET_KEY}"
    signature = hashlib.sha1(sign_string.encode('utf-8')).hexdigest()
    
    print("=" * 80)
    print(f"🔌 PayzTeam API - Тест с суммой {amount} RUB")
    print("=" * 80)
    
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
        "language": language,
        "payment_method": payment_method,
        "is_intrabank_transfer": is_intrabank_transfer,
        "ip": client_ip,
        "sign": signature
    }
    
    print(f"\n📤 ЗАПРОС:")
    print(f"UUID: {uuid}")
    print(f"Сумма: {amount} RUB")
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"\n📥 ОТВЕТ:")
        print(f"Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if result.get("success"):
                print(f"\n✅ Платеж создан успешно!")
                print(f"   ID: {result.get('id')}")
                print(f"   Status: {result.get('status')}")
                
                if "paymentInfo" in result:
                    print("\n💳 Информация для оплаты:")
                    print(json.dumps(result["paymentInfo"], indent=2, ensure_ascii=False))
                return True
            else:
                print(f"\n❌ Ошибка: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"\n❌ Ошибка: {str(e)}")
        return False

# ============================================
# ОСНОВНОЙ КОД
# ============================================
if __name__ == "__main__":
    amounts = ["2500.00", "3000.00"]
    
    for i, amount in enumerate(amounts):
        test_amount(amount)
        
        if i < len(amounts) - 1:
            print(f"\n⏳ Пауза 2 секунды...\n")
            time.sleep(2)
    
    print("\n" + "=" * 80)
