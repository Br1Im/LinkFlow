#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест ультра-быстрого сервера - цель 15 секунд
"""

import requests
import json
import time
import uuid

def test_ultra_fast_payment():
    """Тест ультра-быстрого создания платежа"""
    
    # Настройки
    base_url = "http://localhost:5000"
    token = "-3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("🚀 Тестирую УЛЬТРА-БЫСТРЫЙ сервер...")
    print("⚡ ЦЕЛЬ: 15 секунд или меньше!")
    
    # Проверяем статус браузера
    print("\n1️⃣ Проверяю статус ультра-быстрого браузера...")
    try:
        response = requests.get(f"{base_url}/api/health", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            browser_ready = data.get('browser_ready', False)
            print(f"   ✅ Статус: {data.get('status')}")
            print(f"   🔥 Браузер готов: {browser_ready}")
            print(f"   🕐 Время: {data.get('timestamp')}")
            print(f"   ⚡ Режим: {data.get('mode')}")
            
            if not browser_ready:
                print("   ⚠️ Браузер не готов, ожидаю...")
                time.sleep(5)
        else:
            print(f"   ❌ Ошибка статуса: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Ошибка подключения: {e}")
        return
    
    # Создаем несколько платежей для тестирования
    test_amounts = [5000, 7500, 10000]
    results = []
    
    for i, amount in enumerate(test_amounts, 1):
        print(f"\n{i}️⃣ Создаю ультра-быстрый платеж #{i}...")
        
        order_id = f"ultra_fast_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
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
                timeout=30  # Уменьшаем таймаут для агрессивного тестирования
            )
            
            elapsed = time.time() - start_time
            
            print(f"\n   📊 Результат платежа #{i}:")
            print(f"   ⏱️ Время: {elapsed:.1f} сек")
            print(f"   📡 Статус: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Успех: {data.get('success')}")
                print(f"   🆔 QRC ID: {data.get('qrcId')}")
                
                qr_link = data.get('qr', '')
                if qr_link:
                    print(f"   🔗 Ссылка: {qr_link[:80]}...")
                    
                    # Проверяем достижение цели
                    if elapsed <= 15:
                        print(f"   🎯 ЦЕЛЬ ДОСТИГНУТА: {elapsed:.1f} сек ✅")
                    else:
                        print(f"   🎯 ЦЕЛЬ НЕ ДОСТИГНУТА: {elapsed:.1f} сек ❌")
                else:
                    print(f"   ❌ Ссылка не получена")
                
                # Проверяем дополнительные поля
                if 'ultra_fast_mode' in data:
                    print(f"   ⚡ Ультра-быстрый режим: {data['ultra_fast_mode']}")
                if 'elapsed_time' in data:
                    print(f"   ⏱️ Время сервера: {data['elapsed_time']:.1f} сек")
                
                results.append({
                    "success": True,
                    "elapsed": elapsed,
                    "server_time": data.get('elapsed_time', elapsed),
                    "amount": amount
                })
                    
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
                            with open(f'error_screenshot_ultra_fast_{i}.png', 'wb') as f:
                                f.write(base64.b64decode(screenshot_base64))
                            print(f"   📸 Скриншот ошибки сохранен: error_screenshot_ultra_fast_{i}.png")
                            
                except:
                    print(f"   📝 Текст ответа: {response.text[:200]}")
                
                results.append({
                    "success": False,
                    "elapsed": elapsed,
                    "amount": amount,
                    "error": response.status_code
                })
        
        except requests.exceptions.Timeout:
            elapsed = time.time() - start_time
            print(f"   ⏰ Таймаут после {elapsed:.1f} сек")
            results.append({
                "success": False,
                "elapsed": elapsed,
                "amount": amount,
                "error": "timeout"
            })
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"   ❌ Ошибка запроса: {e}")
            print(f"   ⏱️ Время до ошибки: {elapsed:.1f} сек")
            results.append({
                "success": False,
                "elapsed": elapsed,
                "amount": amount,
                "error": str(e)
            })
        
        # Небольшая пауза между платежами
        if i < len(test_amounts):
            print("   ⏳ Пауза между платежами...")
            time.sleep(2)
    
    # Проверяем статус после всех платежей
    print(f"\n{len(test_amounts)+1}️⃣ Проверяю статус после всех платежей...")
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
    
    # Анализ результатов
    print(f"\n📊 АНАЛИЗ РЕЗУЛЬТАТОВ:")
    print(f"   📈 Всего тестов: {len(results)}")
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"   ✅ Успешных: {len(successful)}")
    print(f"   ❌ Неудачных: {len(failed)}")
    
    if successful:
        times = [r['elapsed'] for r in successful]
        server_times = [r.get('server_time', r['elapsed']) for r in successful]
        
        print(f"   ⏱️ Среднее время: {sum(times)/len(times):.1f} сек")
        print(f"   ⏱️ Минимальное время: {min(times):.1f} сек")
        print(f"   ⏱️ Максимальное время: {max(times):.1f} сек")
        print(f"   ⏱️ Среднее время сервера: {sum(server_times)/len(server_times):.1f} сек")
        
        # Проверяем достижение цели
        target_achieved = [r for r in successful if r['elapsed'] <= 15]
        print(f"   🎯 Достигли цели (≤15 сек): {len(target_achieved)}/{len(successful)}")
        
        if target_achieved:
            print(f"   🏆 УСПЕХ! Цель достигнута в {len(target_achieved)} из {len(successful)} случаев!")
        else:
            print(f"   ⚠️ Цель не достигнута ни разу. Нужна дополнительная оптимизация.")
    
    if failed:
        print(f"   ❌ Ошибки:")
        for r in failed:
            error = r.get('error', 'unknown')
            print(f"      - Сумма {r['amount']}: {error} (время: {r['elapsed']:.1f}s)")

if __name__ == "__main__":
    test_ultra_fast_payment()