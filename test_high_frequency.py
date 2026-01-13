#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест высокочастотных запросов
Проверяем стабильность при интервале 1-3 секунды между запросами
"""

import requests
import time
import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

def single_payment_test(test_id, amount, delay_before=0):
    """Один тест создания платежа"""
    if delay_before > 0:
        time.sleep(delay_before)
    
    url = "http://85.192.56.74:5001/api/payment"
    headers = {
        "Authorization": "Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo",
        "Content-Type": "application/json"
    }
    
    start_time = time.time()
    
    try:
        response = requests.post(
            url, 
            json={"amount": amount, "orderId": f"freq_test_{test_id}_{int(time.time())}"},
            headers=headers,
            timeout=40  # 40 секунд таймаут для частых запросов
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code in [200, 201]:
            data = response.json()
            success = data.get('success', False)
            error = data.get('error', 'Unknown') if not success else None
            
            return {
                "test_id": test_id,
                "success": success,
                "time": elapsed,
                "error": error,
                "status_code": response.status_code
            }
        else:
            return {
                "test_id": test_id,
                "success": False,
                "time": elapsed,
                "error": f"HTTP {response.status_code}",
                "status_code": response.status_code
            }
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        return {
            "test_id": test_id,
            "success": False,
            "time": elapsed,
            "error": "Timeout",
            "status_code": 0
        }
        
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            "test_id": test_id,
            "success": False,
            "time": elapsed,
            "error": str(e),
            "status_code": 0
        }

def test_sequential_requests():
    """Тест последовательных запросов с коротким интервалом"""
    print("🔥 ТЕСТ ПОСЛЕДОВАТЕЛЬНЫХ ЧАСТЫХ ЗАПРОСОВ")
    print("=" * 60)
    
    results = []
    intervals = [1, 2, 3]  # Интервалы в секундах
    
    for interval in intervals:
        print(f"\n📊 Тестирую интервал {interval} секунд между запросами")
        print("-" * 40)
        
        interval_results = []
        
        for i in range(5):  # 5 запросов для каждого интервала
            test_id = f"{interval}s_{i+1}"
            amount = 1000 + (i * 100)
            
            print(f"🔬 Запрос {i+1}/5 (интервал {interval}s): {amount} сум")
            
            result = single_payment_test(test_id, amount)
            interval_results.append(result)
            
            if result['success']:
                print(f"   ✅ Успех за {result['time']:.1f}s")
            else:
                print(f"   ❌ Ошибка за {result['time']:.1f}s: {result['error']}")
            
            # Ждем интервал (кроме последнего запроса)
            if i < 4:
                time.sleep(interval)
        
        # Анализ результатов для интервала
        successful = [r for r in interval_results if r['success']]
        success_rate = len(successful) / len(interval_results) * 100
        
        print(f"\n📈 Результаты для интервала {interval}s:")
        print(f"   Успешность: {len(successful)}/{len(interval_results)} ({success_rate:.0f}%)")
        
        if successful:
            avg_time = sum(r['time'] for r in successful) / len(successful)
            print(f"   Среднее время: {avg_time:.1f}s")
        
        results.extend(interval_results)
        
        # Пауза между тестами разных интервалов
        if interval < intervals[-1]:
            print(f"⏳ Пауза 15 секунд перед следующим интервалом...")
            time.sleep(15)
    
    return results

def test_concurrent_requests():
    """Тест одновременных запросов"""
    print("\n\n⚡ ТЕСТ ОДНОВРЕМЕННЫХ ЗАПРОСОВ")
    print("=" * 60)
    
    concurrent_counts = [2, 3, 5]  # Количество одновременных запросов
    results = []
    
    for count in concurrent_counts:
        print(f"\n📊 Тестирую {count} одновременных запросов")
        print("-" * 40)
        
        # Подготавливаем задачи
        tasks = []
        for i in range(count):
            test_id = f"concurrent_{count}_{i+1}"
            amount = 1500 + (i * 100)
            tasks.append((test_id, amount))
        
        # Запускаем одновременно
        start_time = time.time()
        concurrent_results = []
        
        with ThreadPoolExecutor(max_workers=count) as executor:
            # Отправляем все запросы одновременно
            future_to_task = {
                executor.submit(single_payment_test, task[0], task[1]): task 
                for task in tasks
            }
            
            # Собираем результаты
            for future in as_completed(future_to_task):
                result = future.result()
                concurrent_results.append(result)
                
                if result['success']:
                    print(f"   ✅ Запрос {result['test_id']}: {result['time']:.1f}s")
                else:
                    print(f"   ❌ Запрос {result['test_id']}: {result['time']:.1f}s - {result['error']}")
        
        total_time = time.time() - start_time
        
        # Анализ результатов
        successful = [r for r in concurrent_results if r['success']]
        success_rate = len(successful) / len(concurrent_results) * 100
        
        print(f"\n📈 Результаты для {count} одновременных запросов:")
        print(f"   Успешность: {len(successful)}/{len(concurrent_results)} ({success_rate:.0f}%)")
        print(f"   Общее время: {total_time:.1f}s")
        
        if successful:
            avg_time = sum(r['time'] for r in successful) / len(successful)
            max_time = max(r['time'] for r in successful)
            min_time = min(r['time'] for r in successful)
            print(f"   Время ответов: {avg_time:.1f}s (мин: {min_time:.1f}s, макс: {max_time:.1f}s)")
        
        results.extend(concurrent_results)
        
        # Пауза между тестами
        if count < concurrent_counts[-1]:
            print(f"⏳ Пауза 20 секунд перед следующим тестом...")
            time.sleep(20)
    
    return results

def analyze_results(sequential_results, concurrent_results):
    """Анализ всех результатов"""
    print("\n\n📊 ОБЩИЙ АНАЛИЗ РЕЗУЛЬТАТОВ")
    print("=" * 60)
    
    all_results = sequential_results + concurrent_results
    successful = [r for r in all_results if r['success']]
    failed = [r for r in all_results if not r['success']]
    
    print(f"📈 Общая статистика:")
    print(f"   Всего тестов: {len(all_results)}")
    print(f"   Успешных: {len(successful)} ({len(successful)/len(all_results)*100:.1f}%)")
    print(f"   Неудачных: {len(failed)} ({len(failed)/len(all_results)*100:.1f}%)")
    
    if successful:
        times = [r['time'] for r in successful]
        print(f"\n⏱️ Время успешных запросов:")
        print(f"   Среднее: {sum(times)/len(times):.1f}s")
        print(f"   Минимум: {min(times):.1f}s")
        print(f"   Максимум: {max(times):.1f}s")
    
    if failed:
        print(f"\n❌ Анализ ошибок:")
        error_types = {}
        for r in failed:
            error = r['error']
            if 'Timeout' in error:
                error_type = 'Таймаут (>40s)'
            elif 'Chrome Driver' in error:
                error_type = 'Chrome Driver потерян'
            elif 'Connection' in error:
                error_type = 'Проблемы соединения'
            elif 'HTTP' in error:
                error_type = f'HTTP ошибка ({error})'
            else:
                error_type = error[:30]
            
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        for error_type, count in error_types.items():
            print(f"   • {error_type}: {count} раз")
    
    # Выводы
    print(f"\n🎯 ВЫВОДЫ:")
    success_rate = len(successful) / len(all_results) * 100
    
    if success_rate >= 90:
        print("✅ Система отлично справляется с частыми запросами")
    elif success_rate >= 70:
        print("⚠️ Система работает с частыми запросами, но есть проблемы")
    elif success_rate >= 50:
        print("❌ Система плохо справляется с частыми запросами")
    else:
        print("💥 Система не готова к частым запросам")
    
    # Рекомендации
    print(f"\n💡 РЕКОМЕНДАЦИИ:")
    if success_rate < 90:
        print("   • Увеличить таймауты")
        print("   • Оптимизировать обработку очереди")
        print("   • Рассмотреть пул браузеров")
    
    if any('Timeout' in r['error'] for r in failed):
        print("   • Много таймаутов - нужно ускорить обработку")
    
    if any('Chrome Driver' in r['error'] for r in failed):
        print("   • Chrome Driver нестабилен при нагрузке")
    
    # Сохраняем результаты
    with open('high_frequency_test_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'sequential_results': sequential_results,
            'concurrent_results': concurrent_results,
            'summary': {
                'total_tests': len(all_results),
                'successful': len(successful),
                'failed': len(failed),
                'success_rate': success_rate
            }
        }, f, ensure_ascii=False, indent=2)
    
    print(f"📄 Результаты сохранены в high_frequency_test_results.json")

def main():
    """Основная функция тестирования"""
    print("🚀 ТЕСТИРОВАНИЕ ВЫСОКОЧАСТОТНЫХ ЗАПРОСОВ")
    print("=" * 60)
    print("Цель: Проверить стабильность при интервалах 1-3 секунды")
    print("Методы: Последовательные и одновременные запросы")
    print("=" * 60)
    
    # Тест последовательных запросов
    sequential_results = test_sequential_requests()
    
    # Пауза между типами тестов
    print(f"\n⏳ Пауза 30 секунд между типами тестов...")
    time.sleep(30)
    
    # Тест одновременных запросов
    concurrent_results = test_concurrent_requests()
    
    # Анализ результатов
    analyze_results(sequential_results, concurrent_results)

if __name__ == "__main__":
    main()