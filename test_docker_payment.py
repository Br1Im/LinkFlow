#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест создания платежа через Docker
"""

import sys
import os
sys.path.insert(0, '/app')

from src.multitransfer_payment import MultitransferPayment

print("\n" + "="*60)
print("🐳 DOCKER TEST - Создание платежа")
print("="*60)

payment = MultitransferPayment(headless=True)

try:
    print("\n1️⃣ Инициализация...")
    if payment.login():
        print("✅ Браузер запущен")
        
        print("\n2️⃣ Создание платежа...")
        result = payment.create_payment(
            card_number="9860080323894719",
            owner_name="Nodir Asadullayev",
            amount=500
        )
        
        if result.get("success"):
            print("\n" + "="*60)
            print("✅ ПЛАТЕЖ СОЗДАН УСПЕШНО!")
            print("="*60)
            print(f"🔗 Ссылка: {result['payment_link']}")
            print(f"⏱️  Время: {result['elapsed_time']:.1f} сек")
            
            if result.get('payment_data'):
                print("\n📊 Данные платежа:")
                for key, value in result['payment_data'].items():
                    print(f"   • {key}: {value}")
        else:
            print("\n" + "="*60)
            print("❌ ОШИБКА СОЗДАНИЯ ПЛАТЕЖА")
            print("="*60)
            print(f"Ошибка: {result.get('error')}")
    else:
        print("❌ Не удалось инициализировать браузер")
        
except Exception as e:
    print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    print("\n3️⃣ Закрытие браузера...")
    payment.close()
    print("✅ Готово")
