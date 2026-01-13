#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест стабильности Chrome Driver
Проверяем действительно ли Chrome крашится или проблема в другом
"""

import requests
import time
import json

def test_payment_stability():
    """Тестируем стабильность создания платежей"""
    
    url = "http://85.192.56.74:5001/api/payment"
    headers = {
        "Authorization": "Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo",
        "Content-Type": "application/json"
    }
    
    results = []
    
    print("🧪 ТЕСТ СТАБИЛЬНОСТИ CHROME DRIVER")
    print("=" * 50)
    
    for i in range(5):
        test_num = i + 1
        amount = 1000 + (i * 100)  # 1000, 1100, 1200, 1300, 1400
        
        print(f"\n🔬 Тест #{test_num}: Платеж на {amount} сум")
        print(f"⏰ Время: {time.strftime('%H:%M:%S')}")
        
        start_time = time.time()
        
        try:
            response = requests.post(
                url, 
                json={"amount": amount, "orderId": f"test_{test_num}_{int(time.time())}"},
                headers=headers,
                timeout=35  # 35 секунд таймаут
            )
            
            elapsed = time.time() - start_time
            
            if response.status_code in [200, 201]:  # 200 OK или 201 Created
                data = response.json()
                if data.get('success'):
                    print(f"✅ УСПЕХ за {elapsed:.1f}s")
                    print(f"   Ссылка: {data.get('payment_link', 'N/A')[:60]}...")
                    results.append({
                        "test": test_num,
                        "success": True,
                        "time": elapsed,
                        "error": None
                    })
                else:
                    error = data.get('error', 'Неизвестная ошибка')
                    print(f"❌ ОШИБКА за {elapsed:.1f}s: {error}")
                    results.append({
                        "test": test_num,
                        "success": False,
                        "time": elapsed,
                        "error": error
                    })
            else:
                print(f"❌ HTTP {response.status_code} за {elapsed:.1f}s")
                results.append({
                    "test": test_num,
                    "success": False,
                    "time": elapsed,
                    "error": f"HTTP {response.status_code}"
                })
                
        except requests.exceptions.Timeout:
            elapsed = time.time() - start_time
            print(f"⏰ ТАЙМАУТ за {elapsed:.1f}s")
            results.append({
                "test": test_num,
                "success": False,
                "time": elapsed,
                "error": "Timeout"
            })
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"💥 ИСКЛЮЧЕНИЕ за {elapsed:.1f}s: {e}")
            results.append({
                "test": test_num,
                "success": False,
                "time": elapsed,
                "error": str(e)
            })
        
        # Интервал между тестами
        if i < 4:  # Не ждем после последнего теста
            print(f"⏳ Пауза 10 секунд...")
            time.sleep(10)
    
    # Анализ результатов
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 50)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"✅ Успешных: {len(successful)}/{len(results)} ({len(successful)/len(results)*100:.0f}%)")
    print(f"❌ Неудачных: {len(failed)}/{len(results)} ({len(failed)/len(results)*100:.0f}%)")
    
    if successful:
        avg_time = sum(r['time'] for r in successful) / len(successful)
        min_time = min(r['time'] for r in successful)
        max_time = max(r['time'] for r in successful)
        print(f"⏱️ Время успешных: {avg_time:.1f}s (мин: {min_time:.1f}s, макс: {max_time:.1f}s)")
    
    if failed:
        print(f"\n❌ Типы ошибок:")
        error_types = {}
        for r in failed:
            error = r['error'] or 'Unknown'
            if 'Chrome Driver' in error:
                error_type = 'Chrome Driver потерян'
            elif 'Timeout' in error or 'timeout' in error.lower():
                error_type = 'Таймаут'
            elif 'Connection' in error:
                error_type = 'Проблемы соединения'
            else:
                error_type = error[:50]
            
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        for error_type, count in error_types.items():
            print(f"   • {error_type}: {count} раз")
    
    # Выводы
    print(f"\n🎯 ВЫВОДЫ:")
    if len(successful) >= 4:
        print("✅ Система работает стабильно")
    elif len(successful) >= 2:
        print("⚠️ Система работает с перебоями")
    else:
        print("❌ Система нестабильна")
    
    # Сохраняем результаты
    with open('chrome_stability_test_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_tests': len(results),
            'successful': len(successful),
            'failed': len(failed),
            'success_rate': len(successful)/len(results)*100,
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"📄 Результаты сохранены в chrome_stability_test_results.json")
    
    return results

if __name__ == "__main__":
    test_payment_stability()