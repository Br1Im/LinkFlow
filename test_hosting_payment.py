#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест создания платежа на хостинге
"""

import requests
import json
import time
import uuid

# Настройки
SERVER_URL = "http://85.192.56.74:5000"
API_TOKEN = "-3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo"

def test_payment(amount):
    """Тестирует создание платежа"""
    
    order_id = f"test-{int(time.time())}-{uuid.uuid4().hex[:6]}"
    
    print(f"\n{'='*60}")
    print(f"Тест создания платежа: {amount} руб")
    print(f"Order ID: {order_id}")
    print(f"{'='*60}")
    
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'amount': amount,
        'orderId': order_id
    }
    
    print(f"\n📤 Отправка запроса...")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{SERVER_URL}/api/payment",
            headers=headers,
            json=data,
            timeout=120
        )
        
        elapsed = time.time() - start_time
        
        print(f"\n📥 Ответ получен за {elapsed:.1f}s")
        print(f"Статус: {response.status_code}")
        
        try:
            result = response.json()
            print(f"\n📋 Результат:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if response.status_code == 200 and result.get('success'):
                print(f"\n✅ УСПЕХ!")
                print(f"Ссылка: {result.get('payment_link', 'N/A')[:80]}...")
                return True
            else:
                print(f"\n❌ ОШИБКА: {result.get('error', 'Unknown error')}")
                return False
                
        except:
            print(f"\n❌ Не удалось распарсить JSON")
            print(f"Ответ: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"\n⏱️ ТАЙМАУТ (>120s)")
        return False
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ СОЗДАНИЯ ПЛАТЕЖЕЙ НА ХОСТИНГЕ")
    print("="*60)
    
    tests = [
        ("Минимальная сумма (1000 руб)", 1000, True),
        ("Средняя сумма (5000 руб)", 5000, True),
        ("Большая сумма (50000 руб)", 50000, True),
        ("Слишком маленькая (100 руб)", 100, False),
        ("Слишком большая (150000 руб)", 150000, False),
    ]
    
    results = []
    
    for name, amount, should_succeed in tests:
        print(f"\n\n{'#'*60}")
        print(f"# {name}")
        print(f"{'#'*60}")
        
        success = test_payment(amount)
        
        if should_succeed:
            results.append((name, success, "✅" if success else "❌"))
        else:
            results.append((name, not success, "✅" if not success else "❌"))
        
        time.sleep(2)  # Пауза между тестами
    
    # Итоги
    print(f"\n\n{'='*60}")
    print("ИТОГИ ТЕСТИРОВАНИЯ")
    print(f"{'='*60}")
    
    for name, passed, icon in results:
        print(f"{icon} {name}: {'PASSED' if passed else 'FAILED'}")
    
    total = len(results)
    passed = sum(1 for _, p, _ in results if p)
    
    print(f"\n{'='*60}")
    print(f"Пройдено: {passed}/{total}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
