#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Локальный тест создания платежа
"""

import requests
import json
import time

def test_payment():
    """Тест создания платежа на локальном сервере"""
    
    print("🚀 ТЕСТ ЛОКАЛЬНОЙ СИСТЕМЫ")
    print("=" * 50)
    
    # Данные для запроса
    data = {
        "amount": 1000,
        "orderId": f"test-local-{int(time.time())}"
    }
    
    headers = {
        "Authorization": "Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo",
        "Content-Type": "application/json"
    }
    
    url = "http://localhost:5001/api/payment"
    
    print(f"📡 Отправляю запрос на {url}")
    print(f"📊 Данные: {json.dumps(data, ensure_ascii=False)}")
    print()
    
    start_time = time.time()
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=70)
        elapsed = time.time() - start_time
        
        print(f"⏱️ Время ответа: {elapsed:.1f} секунд")
        print(f"📈 Статус код: {response.status_code}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            print("✅ УСПЕХ!")
            print(f"🔗 Ссылка на оплату: {result.get('payment_link', 'Не найдена')}")
            print(f"⏱️ Время создания: {result.get('elapsed_time', 'Не указано')} сек")
            print(f"🆔 ID запроса: {result.get('request_id', 'Не указан')}")
            
            if result.get('success'):
                print()
                print("🎉 ПЛАТЕЖ СОЗДАН УСПЕШНО!")
                return True
            else:
                print(f"❌ Ошибка: {result.get('error', 'Неизвестная ошибка')}")
                return False
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            print(f"📄 Ответ: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"⏰ ТАЙМАУТ после {elapsed:.1f} секунд")
        return False
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Ошибка после {elapsed:.1f} секунд: {e}")
        return False

if __name__ == "__main__":
    print()
    success = test_payment()
    print()
    print("=" * 50)
    if success:
        print("🎯 РЕЗУЛЬТАТ: СИСТЕМА РАБОТАЕТ!")
    else:
        print("⚠️ РЕЗУЛЬТАТ: ТРЕБУЕТСЯ ПРОВЕРКА")
    print("=" * 50)
