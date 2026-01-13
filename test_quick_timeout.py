#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрый тест нового таймаута 60 секунд
"""

import requests
import time
import json

# Настройки
API_URL = "http://85.192.56.74:5001/api/payment"
API_TOKEN = "-3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo"

def quick_test():
    """Быстрый тест таймаута 60 секунд"""
    print("🧪 БЫСТРЫЙ ТЕСТ ТАЙМАУТА 60 СЕКУНД")
    print("=" * 50)
    
    # Данные для теста
    test_data = {
        "amount": 1000,
        "orderId": f"quick-timeout-test-{int(time.time())}"
    }
    
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print(f"📤 Отправляю запрос: {test_data}")
    print(f"⏰ Ожидаемый таймаут: 60 секунд")
    print()
    
    start_time = time.time()
    
    try:
        # Отправляем запрос с увеличенным таймаутом на клиенте
        response = requests.post(
            API_URL,
            headers=headers,
            json=test_data,
            timeout=65  # Клиентский таймаут больше серверного
        )
        
        elapsed = time.time() - start_time
        
        print(f"📥 Ответ получен за {elapsed:.1f} секунд")
        print(f"🔢 HTTP статус: {response.status_code}")
        
        try:
            result = response.json()
            print(f"📋 Результат:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if result.get('success'):
                print(f"✅ УСПЕХ! Платеж создан за {elapsed:.1f} секунд")
                print(f"🔗 Ссылка: {result.get('payment_link', 'N/A')[:80]}...")
                return True
            else:
                error = result.get('error', 'Unknown error')
                if 'timeout' in error.lower():
                    print(f"⏰ ТАЙМАУТ: {error}")
                    print(f"⚠️ Время выполнения: {elapsed:.1f} секунд")
                    if elapsed >= 59:  # Близко к 60 секундам
                        print("✅ Таймаут работает корректно (60 секунд)")
                        return True
                    else:
                        print("❌ Таймаут сработал слишком рано")
                        return False
                else:
                    print(f"❌ ОШИБКА: {error}")
                    return False
                    
        except json.JSONDecodeError:
            print(f"❌ Ошибка парсинга JSON: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"⏰ КЛИЕНТСКИЙ ТАЙМАУТ за {elapsed:.1f} секунд")
        print("❌ Клиентский таймаут сработал раньше серверного")
        return False
        
    except requests.exceptions.RequestException as e:
        elapsed = time.time() - start_time
        print(f"❌ ОШИБКА ЗАПРОСА за {elapsed:.1f} секунд: {e}")
        return False

if __name__ == "__main__":
    print("🚀 БЫСТРЫЙ ТЕСТ ИСПРАВЛЕНИЯ ТАЙМАУТА")
    print("Проверяем что система работает с таймаутом 60 секунд")
    print()
    
    success = quick_test()
    
    if success:
        print("\n🎉 ТЕСТ ПРОЙДЕН!")
        print("✅ Исправление таймаута работает корректно")
    else:
        print("\n❌ ТЕСТ НЕ ПРОШЕЛ")
        print("Нужна дополнительная диагностика")