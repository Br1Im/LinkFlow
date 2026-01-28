#!/usr/bin/env python3
"""
Тест рабочего кода с хоста
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from multitransfer_payment import MultitransferPayment
from sender_data import SENDER_DATA

def test_payment():
    print("🚀 Тестирую рабочий код с хоста...")
    
    # Создаем экземпляр
    payment = MultitransferPayment(
        sender_data=SENDER_DATA,
        headless=False  # С окном для наблюдения
    )
    
    # Логинимся
    payment.login()
    
    # Создаем платеж
    result = payment.create_payment(
        card_number="9860080323894719",
        owner_name="Nodir Asadullayev",
        amount=100
    )
    
    print("\n" + "="*60)
    print("РЕЗУЛЬТАТ:")
    print("="*60)
    print(f"Success: {result.get('success')}")
    print(f"Time: {result.get('elapsed_time', 0):.1f}s")
    if result.get('payment_link'):
        print(f"Link: {result.get('payment_link')}")
    if result.get('error'):
        print(f"Error: {result.get('error')}")
    print("="*60)
    
    # Закрываем
    payment.close()
    
    return result

if __name__ == "__main__":
    test_payment()
