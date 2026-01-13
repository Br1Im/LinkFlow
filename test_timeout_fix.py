#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест исправления таймаута - проверка что система работает с 45 секундами
"""

import requests
import time
import json

# Настройки
API_URL = "http://85.192.56.74:5001/api/payment"
API_TOKEN = "-3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo"

def test_timeout_fix():
    """Тест исправления таймаута"""
    print("🧪 ТЕСТ ИСПРАВЛЕНИЯ ТАЙМАУТА (45 секунд)")
    print("=" * 50)
    
    # Данные для теста
    test_data = {
        "amount": 1000,
        "orderId": f"timeout-fix-test-{int(time.time())}"
    }
    
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print(f"📤 Отправляю запрос: {test_data}")
    print(f"🌐 URL: {API_URL}")
    print(f"⏰ Ожидаемый таймаут: 45 секунд")
    print()
    
    start_time = time.time()
    
    try:
        # Отправляем запрос с увеличенным таймаутом на клиенте
        response = requests.post(
            API_URL,
            headers=headers,
            json=test_data,
            timeout=50  # Клиентский таймаут больше серверного
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
                print(f"🔗 Ссылка: {result.get('payment_link', 'N/A')}")
                return True
            else:
                error = result.get('error', 'Unknown error')
                if 'timeout' in error.lower():
                    print(f"⏰ ТАЙМАУТ: {error}")
                    print(f"⚠️ Время выполнения: {elapsed:.1f} секунд")
                    if elapsed >= 44:  # Близко к 45 секундам
                        print("✅ Таймаут работает корректно (45 секунд)")
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

def test_multiple_requests():
    """Тест нескольких запросов подряд"""
    print("\n🔄 ТЕСТ НЕСКОЛЬКИХ ЗАПРОСОВ")
    print("=" * 50)
    
    results = []
    
    for i in range(3):
        print(f"\n📤 Запрос #{i+1}/3")
        success = test_timeout_fix()
        results.append(success)
        
        if i < 2:  # Пауза между запросами
            print("⏳ Пауза 60 секунд между запросами...")
            time.sleep(60)
    
    print(f"\n📊 ИТОГИ:")
    print(f"✅ Успешных: {sum(results)}/3")
    print(f"❌ Неудачных: {3 - sum(results)}/3")
    print(f"📈 Успешность: {sum(results)/3*100:.1f}%")
    
    return sum(results) >= 2  # Считаем успехом если 2+ из 3 работают

if __name__ == "__main__":
    print("🚀 ТЕСТИРОВАНИЕ ИСПРАВЛЕНИЯ ТАЙМАУТА")
    print("Проверяем что система работает с увеличенным таймаутом 45 секунд")
    print()
    
    # Одиночный тест
    single_success = test_timeout_fix()
    
    if single_success:
        # Если одиночный тест прошел, делаем множественный
        multiple_success = test_multiple_requests()
        
        if multiple_success:
            print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
            print("✅ Исправление таймаута работает корректно")
        else:
            print("\n⚠️ Одиночный тест прошел, но множественный частично неудачен")
    else:
        print("\n❌ ОДИНОЧНЫЙ ТЕСТ НЕ ПРОШЕЛ")
        print("Нужна дополнительная диагностика")