#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест исправленного быстрого сервера
"""

import requests
import json
import time
import uuid

def test_fast_payment():
    """Тест быстрого создания платежа"""
    
    # Настройки
    base_url = "http://localhost:5000"
    token = "-3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("🚀 Тестирую исправленный быстрый сервер...")
    
    # Проверяем статус браузера
    print("\n1️⃣ Проверяю статус браузера...")
    try:
        response = requests.get(f"{base_url}/api/health", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            browser_ready = data.get('browser_ready', False)
            print(f"   ✅ Статус: {data.get('status')}")
            print(f"   🔥 Браузер готов: {browser_ready}")
            print(f"   🕐 Время: {data.get('timestamp')}")
            
            if not browser_ready:
                print("   ⚠️ Браузер не готов, ожидаю...")
                time.sleep(5)
        else:
            print(f"   ❌ Ошибка статуса: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Ошибка подключения: {e}")
        return
    
    # Создаем платеж
    print("\n2️⃣ Создаю быстрый платеж...")
    
    order_id = f"test_fast_{int(time.time())}_{uuid.uuid4().hex[:8]}"
    amount = 7500
    
    payment_data = {
        "orderId": order_id,
        "amount": amount
    }
    
    print(f"   📋 Order ID: {order_id}")
    print(f"   💰 Amount: {amount}")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{base_url}/api/payment", 
            headers=headers, 
            json=payment_data,
            timeout=60  # Увеличиваем таймаут
        )
        
        elapsed = time.time() - start_time
        
        print(f"\n📊 Результат:")
        print(f"   ⏱️ Время: {elapsed:.1f} сек")
        print(f"   📡 Статус: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Успех: {data.get('success')}")
            print(f"   🆔 QRC ID: {data.get('qrcId')}")
            
            qr_link = data.get('qr', '')
            if qr_link:
                print(f"   🔗 Ссылка: {qr_link[:80]}...")
                print(f"   🎯 ЦЕЛЬ ДОСТИГНУТА: {elapsed:.1f} сек {'✅' if elapsed <= 15 else '❌'}")
            else:
                print(f"   ❌ Ссылка не получена")
            
            # Проверяем дополнительные поля
            if 'fast_warmed_mode' in data:
                print(f"   🔥 Быстрый режим: {data['fast_warmed_mode']}")
            if 'elapsed_time' in data:
                print(f"   ⏱️ Время сервера: {data['elapsed_time']:.1f} сек")
                
        else:
            print(f"   ❌ Ошибка: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   📝 Сообщение: {error_data.get('error', 'Unknown error')}")
                
                # Если есть скриншот, сохраняем его
                if 'screenshot' in error_data:
                    screenshot_data = error_data['screenshot']
                    if screenshot_data.startswith('data:image/png;base64,'):
                        import base64
                        screenshot_base64 = screenshot_data.split(',')[1]
                        with open('error_screenshot_fast.png', 'wb') as f:
                            f.write(base64.b64decode(screenshot_base64))
                        print(f"   📸 Скриншот ошибки сохранен: error_screenshot_fast.png")
                        
            except:
                print(f"   📝 Текст ответа: {response.text[:200]}")
    
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"   ⏰ Таймаут после {elapsed:.1f} сек")
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"   ❌ Ошибка запроса: {e}")
        print(f"   ⏱️ Время до ошибки: {elapsed:.1f} сек")
    
    # Проверяем статус после платежа
    print("\n3️⃣ Проверяю статус после платежа...")
    try:
        response = requests.get(f"{base_url}/api/health", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            browser_ready = data.get('browser_ready', False)
            print(f"   🔥 Браузер готов: {browser_ready}")
        else:
            print(f"   ❌ Ошибка статуса: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

if __name__ == "__main__":
    test_fast_payment()