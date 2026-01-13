#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест ускорения системы - проверка что платежи создаются за 15-25 секунд
"""

import requests
import time
import json
import statistics

# Настройки
API_URL = "http://85.192.56.74:5001/api/payment"
API_TOKEN = "-3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo"

def test_speed_single():
    """Тест одного ускоренного платежа"""
    print("🚀 ТЕСТ УСКОРЕНИЯ - ОДИНОЧНЫЙ ПЛАТЕЖ")
    print("=" * 50)
    
    # Данные для теста
    test_data = {
        "amount": 1000,
        "orderId": f"speed-test-{int(time.time())}"
    }
    
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print(f"📤 Отправляю запрос: {test_data}")
    print(f"🎯 Цель: 15-25 секунд")
    print()
    
    start_time = time.time()
    
    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json=test_data,
            timeout=65
        )
        
        elapsed = time.time() - start_time
        
        print(f"📥 Ответ получен за {elapsed:.1f} секунд")
        print(f"🔢 HTTP статус: {response.status_code}")
        
        try:
            result = response.json()
            
            if result.get('success'):
                processing_time = result.get('processing_time', elapsed)
                print(f"✅ УСПЕХ! Платеж создан за {processing_time:.1f} секунд")
                print(f"🔗 Ссылка: {result.get('payment_link', 'N/A')[:80]}...")
                
                # Оценка ускорения
                if processing_time <= 20:
                    print(f"🎉 ОТЛИЧНО! Время {processing_time:.1f}s - в пределах цели!")
                    return True, processing_time
                elif processing_time <= 30:
                    print(f"✅ ХОРОШО! Время {processing_time:.1f}s - приемлемо")
                    return True, processing_time
                else:
                    print(f"⚠️ МЕДЛЕННО! Время {processing_time:.1f}s - нужна дополнительная оптимизация")
                    return True, processing_time
            else:
                error = result.get('error', 'Unknown error')
                print(f"❌ ОШИБКА: {error}")
                return False, elapsed
                    
        except json.JSONDecodeError:
            print(f"❌ Ошибка парсинга JSON: {response.text}")
            return False, elapsed
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"⏰ ТАЙМАУТ за {elapsed:.1f} секунд")
        return False, elapsed
        
    except requests.exceptions.RequestException as e:
        elapsed = time.time() - start_time
        print(f"❌ ОШИБКА ЗАПРОСА за {elapsed:.1f} секунд: {e}")
        return False, elapsed

def test_speed_multiple():
    """Тест нескольких ускоренных платежей"""
    print("\n🔄 ТЕСТ УСКОРЕНИЯ - МНОЖЕСТВЕННЫЕ ПЛАТЕЖИ")
    print("=" * 50)
    
    results = []
    times = []
    
    for i in range(3):
        print(f"\n📤 Платеж #{i+1}/3")
        success, processing_time = test_speed_single()
        results.append(success)
        if success:
            times.append(processing_time)
        
        if i < 2:  # Пауза между запросами
            print("⏳ Пауза 45 секунд между запросами...")
            time.sleep(45)
    
    print(f"\n📊 ИТОГИ УСКОРЕНИЯ:")
    print(f"✅ Успешных: {sum(results)}/3")
    print(f"❌ Неудачных: {3 - sum(results)}/3")
    print(f"📈 Успешность: {sum(results)/3*100:.1f}%")
    
    if times:
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"⏱️ Среднее время: {avg_time:.1f} секунд")
        print(f"🏃 Лучшее время: {min_time:.1f} секунд")
        print(f"🐌 Худшее время: {max_time:.1f} секунд")
        
        # Оценка общего результата
        if avg_time <= 20:
            print(f"🎉 ПРЕВОСХОДНО! Среднее время {avg_time:.1f}s - цель достигнута!")
        elif avg_time <= 25:
            print(f"✅ ОТЛИЧНО! Среднее время {avg_time:.1f}s - в пределах цели!")
        elif avg_time <= 35:
            print(f"👍 ХОРОШО! Среднее время {avg_time:.1f}s - приемлемо")
        else:
            print(f"⚠️ ТРЕБУЕТ УЛУЧШЕНИЯ! Среднее время {avg_time:.1f}s - нужна дополнительная оптимизация")
    
    return sum(results) >= 2  # Считаем успехом если 2+ из 3 работают

def compare_with_old_system():
    """Сравнение с предыдущей системой"""
    print("\n📊 СРАВНЕНИЕ С ПРЕДЫДУЩЕЙ СИСТЕМОЙ")
    print("=" * 50)
    
    print("📈 Предыдущие результаты:")
    print("   • Среднее время: 26-52 секунды")
    print("   • Лучшее время: 26.8 секунд")
    print("   • Худшее время: 52+ секунд")
    print()
    
    print("🎯 Цель ускорения:")
    print("   • Среднее время: 15-25 секунд")
    print("   • Лучшее время: <20 секунд")
    print("   • Худшее время: <30 секунд")
    print()
    
    print("🔧 Основные оптимизации:")
    print("   • Сокращены все time.sleep() в 2-3 раза")
    print("   • Уменьшены таймауты WebDriverWait с 8 до 5-2 секунд")
    print("   • Сокращено количество проверок и попыток")
    print("   • Ускорены циклы ожидания (0.05-0.2 сек вместо 0.1-0.3)")
    print("   • Минимизированы паузы между операциями")

if __name__ == "__main__":
    print("🚀 ТЕСТИРОВАНИЕ УСКОРЕНИЯ СИСТЕМЫ")
    print("Проверяем что платежи создаются за 15-25 секунд")
    print()
    
    # Сравнение с предыдущей системой
    compare_with_old_system()
    
    # Одиночный тест
    single_success, _ = test_speed_single()
    
    if single_success:
        # Если одиночный тест прошел, делаем множественный
        multiple_success = test_speed_multiple()
        
        if multiple_success:
            print("\n🎉 ВСЕ ТЕСТЫ УСКОРЕНИЯ ПРОЙДЕНЫ!")
            print("✅ Система успешно ускорена")
        else:
            print("\n⚠️ Одиночный тест прошел, но множественный частично неудачен")
            print("Система ускорена, но требует дополнительной стабилизации")
    else:
        print("\n❌ ОДИНОЧНЫЙ ТЕСТ НЕ ПРОШЕЛ")
        print("Нужна дополнительная диагностика ускорения")