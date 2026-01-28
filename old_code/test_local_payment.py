#!/usr/bin/env python3
"""
Тест локального запуска создания платежа
"""

import sys
import os

# Данные отправителя
from sender_data import SENDER_DATA
from multitransfer_payment import MultitransferPayment

def test_payment():
    print("🚀 Тест создания платежа локально")
    print("="*70)
    
    # Создаем экземпляр
    payment = MultitransferPayment(
        sender_data=SENDER_DATA,
        headless=False  # Показываем браузер
    )
    
    try:
        # Логинимся (открываем страницу)
        print("1️⃣ Открываю страницу...")
        payment.login()
        
        # Создаем платеж
        print("2️⃣ Создаю платеж...")
        result = payment.create_payment(
            card_number="9860080323894719",
            owner_name="Nodir Asadullayev",
            amount=110
        )
        
        print()
        print("="*70)
        if result.get('success'):
            print("✅ УСПЕХ!")
            print(f"⏱️  Время: {result.get('elapsed_time', 0):.1f}s")
            print(f"🔗 Ссылка: {result.get('payment_link')}")
        else:
            print("❌ ОШИБКА!")
            print(f"Error: {result.get('error')}")
        print("="*70)
        
        return result
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        payment.close()

if __name__ == "__main__":
    test_payment()
