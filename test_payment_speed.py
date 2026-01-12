# -*- coding: utf-8 -*-
"""
Тест скорости создания платежей
Сравнение разных методов для достижения 8-12 секунд
"""

import requests
import time
import json

# Настройки
API_URL = "http://127.0.0.1:5001/api/create-payment"
TEST_AMOUNT = 10000  # Тестовая сумма в сумах

def test_payment_creation():
    """Тестирует создание одного платежа и возвращает время"""
    print("\n" + "="*60)
    print(f"🚀 ТЕСТ: Создание платежа на сумму {TEST_AMOUNT} сум")
    print("="*60)
    
    start_time = time.time()
    
    try:
        response = requests.post(
            API_URL,
            json={
                "amount": TEST_AMOUNT,
                "description": f"Тестовый платеж {TEST_AMOUNT} сум"
            },
            timeout=120
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                payment_link = data.get('payment_link', 'N/A')
                server_time = data.get('elapsed_time', 0)
                mode = data.get('mode', 'unknown')
                
                print(f"\n✅ УСПЕХ!")
                print(f"⏱️  Общее время: {elapsed:.2f}s")
                print(f"⏱️  Время сервера: {server_time:.2f}s")
                print(f"🔧 Режим: {mode}")
                print(f"🔗 Ссылка: {payment_link[:60]}...")
                
                # Оценка скорости
                if elapsed < 8:
                    print(f"🎉 ОТЛИЧНО! Время {elapsed:.2f}s < 8s")
                elif elapsed < 12:
                    print(f"✅ ЦЕЛЬ ДОСТИГНУТА! Время {elapsed:.2f}s < 12s")
                elif elapsed < 20:
                    print(f"⚠️  ПРИЕМЛЕМО. Время {elapsed:.2f}s < 20s")
                else:
                    print(f"❌ МЕДЛЕННО! Время {elapsed:.2f}s > 20s")
                
                return {
                    'success': True,
                    'elapsed': elapsed,
                    'server_time': server_time,
                    'mode': mode,
                    'link': payment_link
                }
            else:
                error = data.get('error', 'Unknown error')
                print(f"\n❌ ОШИБКА: {error}")
                print(f"⏱️  Время до ошибки: {elapsed:.2f}s")
                return {
                    'success': False,
                    'elapsed': elapsed,
                    'error': error
                }
        else:
            print(f"\n❌ HTTP ERROR: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return {
                'success': False,
                'elapsed': time.time() - start_time,
                'error': f"HTTP {response.status_code}"
            }
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"\n⏰ TIMEOUT после {elapsed:.2f}s")
        return {
            'success': False,
            'elapsed': elapsed,
            'error': 'Timeout'
        }
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n💥 ИСКЛЮЧЕНИЕ: {e}")
        return {
            'success': False,
            'elapsed': elapsed,
            'error': str(e)
        }

def run_multiple_tests(count=5):
    """Запускает несколько тестов подряд для проверки стабильности"""
    print("\n" + "🔥"*30)
    print(f"ЗАПУСК {count} ТЕСТОВ")
    print("🔥"*30)
    
    results = []
    
    for i in range(count):
        print(f"\n📊 Тест {i+1}/{count}")
        result = test_payment_creation()
        results.append(result)
        
        if i < count - 1:
            print("\n⏳ Пауза 2 секунды перед следующим тестом...")
            time.sleep(2)
    
    # Статистика
    print("\n" + "="*60)
    print("📈 СТАТИСТИКА")
    print("="*60)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"\n✅ Успешных: {len(successful)}/{count}")
    print(f"❌ Ошибок: {len(failed)}/{count}")
    
    if successful:
        times = [r['elapsed'] for r in successful]
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        # Анализ режимов
        modes = [r.get('mode', 'unknown') for r in successful]
        warmed_count = modes.count('warmed')
        cold_count = modes.count('cold')
        
        print(f"\n⏱️  Среднее время: {avg_time:.2f}s")
        print(f"⏱️  Минимальное: {min_time:.2f}s")
        print(f"⏱️  Максимальное: {max_time:.2f}s")
        print(f"🔧 Прогретый браузер: {warmed_count}/{len(successful)}")
        print(f"🔧 Холодный старт: {cold_count}/{len(successful)}")
        
        if avg_time < 8:
            print(f"\n🎉🎉🎉 ПРЕВОСХОДНО! Среднее время {avg_time:.2f}s < 8s")
        elif avg_time < 12:
            print(f"\n🎯 ЦЕЛЬ ДОСТИГНУТА! Среднее время {avg_time:.2f}s < 12s")
        elif avg_time < 20:
            print(f"\n✅ Хорошо! Среднее время {avg_time:.2f}s < 20s")
            print(f"💡 Нужно ещё {avg_time - 12:.2f}s для достижения цели 12s")
        else:
            print(f"\n⚠️  Нужна оптимизация! Среднее время {avg_time:.2f}s")
            print(f"💡 Нужно ускорить на {avg_time - 12:.2f}s")
    
    if failed:
        print(f"\n❌ Ошибки:")
        for i, r in enumerate(failed, 1):
            print(f"  {i}. {r.get('error', 'Unknown')}")
    
    return results

def check_browser_status():
    """Проверяет статус браузера"""
    try:
        response = requests.get("http://127.0.0.1:5001/api/pool/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                pool_info = data.get('pool', {})
                print(f"🔧 Статус браузера: {pool_info}")
                return pool_info
    except:
        pass
    return None

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║         ТЕСТИРОВАНИЕ СКОРОСТИ СОЗДАНИЯ ПЛАТЕЖЕЙ          ║
    ║                    Цель: 8-12 секунд                      ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Проверка доступности API
    print("🔍 Проверка доступности API...")
    try:
        response = requests.get("http://127.0.0.1:5001/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ API доступен")
        else:
            print(f"⚠️  API вернул код {response.status_code}")
    except Exception as e:
        print(f"❌ API недоступен: {e}")
        print("💡 Убедитесь что Docker контейнер запущен: docker-compose up -d")
        exit(1)
    
    # Проверка статуса браузера
    print("\n🔍 Проверка статуса браузера...")
    browser_status = check_browser_status()
    if browser_status:
        if browser_status.get('ready'):
            print("✅ Браузер прогрет и готов к работе")
        else:
            print("⚠️  Браузер не прогрет - будет использован холодный старт")
    
    # Запуск тестов
    results = run_multiple_tests(count=5)  # Финальный тест стабильности
    
    print("\n" + "="*60)
    print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("="*60)
    
    # Рекомендации
    successful = [r for r in results if r['success']]
    if successful:
        avg_time = sum(r['elapsed'] for r in successful) / len(successful)
        
        print("\n💡 РЕКОМЕНДАЦИИ:")
        if avg_time > 12:
            print("   - Убедитесь что браузер прогрет")
            print("   - Проверьте скорость интернета")
            print("   - Рассмотрите использование пула браузеров")
        elif avg_time > 8:
            print("   - Цель достигнута! Можно дополнительно оптимизировать")
        else:
            print("   - Отличная скорость! Система работает оптимально")
    
    print()
