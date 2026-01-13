#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ЛОКАЛЬНЫЙ ТЕСТ СОЗДАНИЯ ПЛАТЕЖА
Простая версия для тестирования скорости 8-12 секунд
"""

import sys
import os
import time
import json

# Добавляем путь для импорта модулей
sys.path.append('bot')

def test_local_payment():
    """Тестирует создание платежа локально"""
    print("🚀 ЛОКАЛЬНЫЙ ТЕСТ СОЗДАНИЯ ПЛАТЕЖА")
    print("=" * 50)
    
    try:
        # Импортируем модули
        from payment_service_ultra import create_payment_fast
        
        # Тестовые данные
        amount = 1000
        
        print(f"💰 Создаю платеж на {amount} сум...")
        start_time = time.time()
        
        # Создаем платеж
        result = create_payment_fast(amount)
        
        elapsed = time.time() - start_time
        
        print(f"\n⏱️ Время выполнения: {elapsed:.2f} секунд")
        
        if result and result.get('success'):
            print("✅ УСПЕХ!")
            print(f"🔗 Ссылка: {result.get('payment_link', 'N/A')}")
            print(f"📱 QR код: {'Создан' if result.get('qr_base64') else 'Не создан'}")
            
            # Оценка скорости
            if elapsed < 8:
                print(f"🎉 ОТЛИЧНО! {elapsed:.2f}s < 8s")
            elif elapsed < 12:
                print(f"✅ ЦЕЛЬ ДОСТИГНУТА! {elapsed:.2f}s < 12s")
            elif elapsed < 30:
                print(f"⚠️ ПРИЕМЛЕМО. {elapsed:.2f}s < 30s")
            else:
                print(f"❌ МЕДЛЕННО! {elapsed:.2f}s > 30s")
                
        else:
            print("❌ ОШИБКА!")
            error = result.get('error', 'Неизвестная ошибка') if result else 'Нет результата'
            print(f"Ошибка: {error}")
            
        return result
        
    except Exception as e:
        print(f"💥 ИСКЛЮЧЕНИЕ: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_multiple_payments(count=3):
    """Тестирует несколько платежей подряд"""
    print(f"\n🔥 ТЕСТ {count} ПЛАТЕЖЕЙ ПОДРЯД")
    print("=" * 50)
    
    results = []
    
    for i in range(count):
        print(f"\n📊 Платеж {i+1}/{count}")
        result = test_local_payment()
        
        if result:
            results.append({
                'success': result.get('success', False),
                'elapsed': result.get('elapsed_time', 0),
                'error': result.get('error')
            })
        
        if i < count - 1:
            print("⏳ Пауза 3 секунды...")
            time.sleep(3)
    
    # Статистика
    print(f"\n📈 СТАТИСТИКА {count} ПЛАТЕЖЕЙ")
    print("=" * 50)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"✅ Успешных: {len(successful)}/{count}")
    print(f"❌ Ошибок: {len(failed)}/{count}")
    
    if successful:
        times = [r['elapsed'] for r in successful]
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"⏱️ Среднее время: {avg_time:.2f}s")
        print(f"⏱️ Минимальное: {min_time:.2f}s")
        print(f"⏱️ Максимальное: {max_time:.2f}s")
        
        if avg_time < 12:
            print(f"🎯 ЦЕЛЬ ДОСТИГНУТА! {avg_time:.2f}s < 12s")
        else:
            print(f"⚠️ Нужна оптимизация: {avg_time:.2f}s > 12s")
    
    return results

if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════╗
║              ЛОКАЛЬНОЕ ТЕСТИРОВАНИЕ ПЛАТЕЖЕЙ              ║
║                     Цель: 8-12 секунд                     ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Проверяем что мы в правильной директории
    if not os.path.exists('bot'):
        print("❌ Директория 'bot' не найдена!")
        print("💡 Запустите скрипт из корневой директории проекта")
        exit(1)
    
    # Проверяем наличие модулей
    try:
        sys.path.append('bot')
        import payment_service_ultra
        import browser_manager
        import database
        print("✅ Все модули найдены")
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("💡 Убедитесь что все файлы на месте")
        exit(1)
    
    # Запускаем тесты
    print("\n🔍 Тест одного платежа:")
    test_local_payment()
    
    print("\n🔍 Тест нескольких платежей:")
    test_multiple_payments(3)
    
    print("\n✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")