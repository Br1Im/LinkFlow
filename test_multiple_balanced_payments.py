#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест множественных платежей сбалансированного сервера
"""

import requests
import json
import time
import uuid

def test_multiple_balanced_payments():
    """Тест нескольких платежей подряд"""
    
    # Настройки
    base_url = "http://localhost:5000"
    token = "-3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("🚀 Тестирую МНОЖЕСТВЕННЫЕ ПЛАТЕЖИ сбалансированного сервера...")
    print("⚖️ ЦЕЛЬ: стабильность и скорость при нескольких платежах подряд!")
    
    # Создаем несколько платежей
    test_amounts = [6000, 7500, 9000]
    results = []
    
    for i, amount in enumerate(test_amounts, 1):
        print(f"\n{i}️⃣ Создаю платеж #{i} (сумма: {amount})...")
        
        order_id = f"multi_balanced_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        payment_data = {
            "orderId": order_id,
            "amount": amount
        }
        
        print(f"   📋 Order ID: {order_id}")
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{base_url}/api/payment", 
                headers=headers, 
                json=payment_data,
                timeout=30
            )
            
            elapsed = time.time() - start_time
            
            print(f"   ⏱️ Время: {elapsed:.1f} сек")
            print(f"   📡 Статус: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Успех: {data.get('success')}")
                print(f"   🆔 QRC ID: {data.get('qrcId')}")
                
                qr_link = data.get('qr', '')
                if qr_link:
                    print(f"   🔗 Ссылка: {qr_link[:60]}...")
                    
                    # Проверяем достижение цели
                    if elapsed <= 15:
                        print(f"   🎯 ОТЛИЧНО: {elapsed:.1f} сек ✅")
                    elif elapsed <= 20:
                        print(f"   🎯 ХОРОШО: {elapsed:.1f} сек ✅")
                    else:
                        print(f"   🎯 МЕДЛЕННО: {elapsed:.1f} сек ❌")
                
                server_time = data.get('elapsed_time', elapsed)
                results.append({
                    "success": True,
                    "elapsed": elapsed,
                    "server_time": server_time,
                    "amount": amount,
                    "payment_number": i
                })
                    
            else:
                print(f"   ❌ Ошибка: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   📝 Сообщение: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"   📝 Текст ответа: {response.text[:200]}")
                
                results.append({
                    "success": False,
                    "elapsed": elapsed,
                    "amount": amount,
                    "payment_number": i,
                    "error": response.status_code
                })
        
        except requests.exceptions.Timeout:
            elapsed = time.time() - start_time
            print(f"   ⏰ Таймаут после {elapsed:.1f} сек")
            results.append({
                "success": False,
                "elapsed": elapsed,
                "amount": amount,
                "payment_number": i,
                "error": "timeout"
            })
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"   ❌ Ошибка запроса: {e}")
            results.append({
                "success": False,
                "elapsed": elapsed,
                "amount": amount,
                "payment_number": i,
                "error": str(e)
            })
        
        # Проверяем статус браузера после каждого платежа
        try:
            response = requests.get(f"{base_url}/api/health", headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                browser_ready = data.get('browser_ready', False)
                print(f"   🔥 Браузер готов: {browser_ready}")
            else:
                print(f"   ⚠️ Ошибка проверки статуса: {response.status_code}")
        except Exception as e:
            print(f"   ⚠️ Ошибка проверки статуса: {e}")
        
        # Небольшая пауза между платежами
        if i < len(test_amounts):
            print("   ⏳ Пауза 3 сек...")
            time.sleep(3)
    
    # Анализ результатов
    print(f"\n📊 АНАЛИЗ РЕЗУЛЬТАТОВ МНОЖЕСТВЕННЫХ ПЛАТЕЖЕЙ:")
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
        excellent = [r for r in successful if r['elapsed'] <= 15]
        good = [r for r in successful if 15 < r['elapsed'] <= 20]
        slow = [r for r in successful if r['elapsed'] > 20]
        
        print(f"   🏆 Отлично (≤15 сек): {len(excellent)}")
        print(f"   👍 Хорошо (15-20 сек): {len(good)}")
        print(f"   🐌 Медленно (>20 сек): {len(slow)}")
        
        # Проверяем стабильность времени
        if len(times) > 1:
            time_variance = max(times) - min(times)
            print(f"   📊 Разброс времени: {time_variance:.1f} сек")
            if time_variance < 5:
                print(f"   ✅ Стабильность: ОТЛИЧНАЯ (разброс < 5 сек)")
            elif time_variance < 10:
                print(f"   👍 Стабильность: ХОРОШАЯ (разброс < 10 сек)")
            else:
                print(f"   ⚠️ Стабильность: НЕСТАБИЛЬНАЯ (разброс > 10 сек)")
        
        if len(successful) == len(results):
            print(f"   🏆 ИДЕАЛЬНЫЙ РЕЗУЛЬТАТ! Все платежи успешны!")
        elif len(successful) >= len(results) * 0.8:
            print(f"   👍 ХОРОШИЙ РЕЗУЛЬТАТ! {len(successful)}/{len(results)} платежей успешны")
        else:
            print(f"   ⚠️ НЕСТАБИЛЬНЫЙ РЕЗУЛЬТАТ! Только {len(successful)}/{len(results)} платежей успешны")
    
    if failed:
        print(f"   ❌ Ошибки:")
        for r in failed:
            error = r.get('error', 'unknown')
            print(f"      - Платеж #{r['payment_number']} (сумма {r['amount']}): {error} (время: {r['elapsed']:.1f}s)")

if __name__ == "__main__":
    test_multiple_balanced_payments()