#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест с правильной суммой (1000 вместо 100)
"""

import requests
import json
import time
import uuid

SERVER_URL = "http://85.192.56.74:5000"
API_TOKEN = "-3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo"

order_id = f"test-1000-{int(time.time())}-{uuid.uuid4().hex[:6]}"
amount = 1000  # Правильная сумма!

headers = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json'
}

data = {
    'amount': amount,
    'orderId': order_id
}

print(f"🧪 ТЕСТ С ПРАВИЛЬНОЙ СУММОЙ: {amount}")
print(f"📋 Order ID: {order_id}")
print()

try:
    print("⏳ Отправка запроса...")
    start_time = time.time()
    
    response = requests.post(
        f"{SERVER_URL}/api/payment",
        headers=headers,
        json=data,
        timeout=60
    )
    
    elapsed = time.time() - start_time
    
    print(f"⏱️ Время ответа: {elapsed:.3f}s")
    print(f"📊 HTTP статус: {response.status_code}")
    print()
    
    if response.status_code == 200:
        result = response.json()
        print("✅ УСПЕХ!")
        print(f"🆔 Order ID: {result.get('orderId')}")
        print(f"🔗 QRC ID: {result.get('qrcId')}")
        
        payment_link = result.get('qr', '')
        if payment_link:
            print(f"💳 Ссылка для оплаты: {payment_link}")
            
            if 'qr.nspk.ru' in payment_link:
                print("✅ Ссылка NSPK валидная!")
            else:
                print("⚠️ Ссылка не NSPK формата")
        else:
            print("❌ Ссылка для оплаты НЕ СОЗДАНА")
            
    else:
        print("❌ ОШИБКА!")
        try:
            error_data = response.json()
            print(f"📄 Ошибка: {error_data.get('error', 'Unknown error')}")
            print(f"📄 Полный ответ:")
            print(json.dumps(error_data, indent=2, ensure_ascii=False))
        except:
            print(f"📄 Ответ: {response.text}")
            
except Exception as e:
    print(f"❌ ОШИБКА: {e}")
