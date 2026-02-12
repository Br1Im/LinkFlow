import requests
import json
import random
import time

API_URL = "http://85.192.56.74/api/payment"
API_TOKEN = "Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo"

for i in range(1, 11):
    amount = random.randint(1000, 5000)
    order_id = f"TEST_{i:02d}"
    
    print(f"\n{'='*60}")
    print(f"Запрос #{i}: {amount} RUB (orderId: {order_id})")
    print('='*60)
    
    payload = {
        "amount": amount,
        "orderId": order_id
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": API_TOKEN
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=120)
        result = response.json()
        
        if result.get("success"):
            print(f"✅ Успех!")
            print(f"   QR: {result.get('qr_link', 'N/A')[:80]}...")
            print(f"   Время: {result.get('payment_time', 0):.2f}s")
            print(f"   Step1: {result.get('step1_time', 0):.2f}s")
            print(f"   Step2: {result.get('step2_time', 0):.2f}s")
        else:
            print(f"❌ Ошибка: {result.get('error', 'Unknown')}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    if i < 10:
        time.sleep(1)

print(f"\n{'='*60}")
print("Все запросы завершены")
print('='*60)
