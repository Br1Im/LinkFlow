#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест одного платежа для проверки оптимизированной системы
"""

import requests
import time
import json

def test_single_payment():
    """Тест одного платежа"""
    
    url = "http://85.192.56.74:5001/api/payment"
    headers = {
        "Authorization": "Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo",
        "Content-Type": "application/json"
    }
    
    amount = 1500
    order_id = f"single_test_{int(time.time())}"
    
    print(f"🧪 Тест одного платежа: {amount} сум")
    print(f"📋 Order ID: {order_id}")
    print(f"⏰ Время начала: {time.strftime('%H:%M:%S')}")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            url, 
            json={"amount": amount, "orderId": order_id},
            headers=headers,
            timeout=20  # 20 секунд таймаут
        )
        
        elapsed = time.time() - start_time
        
        print(f"📊 Ответ получен за {elapsed:.1f}s")
        print(f"📊 HTTP статус: {response.status_code}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"✅ Успех: {data.get('success', False)}")
            
            if data.get('success'):
                print(f"🔗 Ссылка: {data.get('payment_link', 'N/A')[:80]}...")
                print(f"⏱️ Время обработки: {data.get('processing_time', 'N/A')}s")
                return True
            else:
                print(f"❌ Ошибка: {data.get('error', 'Unknown')}")
                return False
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📄 Детали: {error_data}")
            except:
                print(f"📄 Текст ответа: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"⏰ ТАЙМАУТ за {elapsed:.1f}s")
        return False
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"💥 ИСКЛЮЧЕНИЕ за {elapsed:.1f}s: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ТЕСТ ОПТИМИЗИРОВАННОЙ СИСТЕМЫ")
    print("=" * 40)
    
    success = test_single_payment()
    
    print("=" * 40)
    if success:
        print("🎉 ТЕСТ ПРОЙДЕН!")
    else:
        print("❌ ТЕСТ НЕ ПРОЙДЕН!")
        print("💡 Нужно проверить логи сервера")