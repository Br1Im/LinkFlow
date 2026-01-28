#!/usr/bin/env python3
"""
Визуальный тест - с открытым браузером
"""

import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from multitransfer_payment import MultitransferPayment
from sender_data import SENDER_DATA

def test_visual():
    print("🚀 ВИЗУАЛЬНЫЙ ТЕСТ - Рабочий код с хоста")
    print("="*70)
    
    start_time = time.time()
    
    # Создаем экземпляр с видимым браузером
    payment = MultitransferPayment(
        sender_data=SENDER_DATA,
        headless=False  # ВИДИМЫЙ БРАУЗЕР
    )
    
    # Логинимся
    payment.login()
    
    # Создаем платеж
    result = payment.create_payment(
        card_number="9860080323894719",
        owner_name="Nodir Asadullayev",
        amount=100
    )
    
    total_time = time.time() - start_time
    
    print("\n" + "="*70)
    print("📊 РЕЗУЛЬТАТ:")
    print("="*70)
    print(f"✅ Success: {result.get('success')}")
    print(f"⏱️  Total Time: {total_time:.1f}s")
    print(f"⏱️  Reported Time: {result.get('elapsed_time', 0):.1f}s")
    if result.get('payment_link'):
        print(f"🔗 Link: {result.get('payment_link')}")
    if result.get('qr_code'):
        print(f"📱 QR: {result.get('qr_code')[:50]}...")
    if result.get('error'):
        print(f"❌ Error: {result.get('error')}")
    print("="*70)
    
    # НЕ закрываем браузер сразу - даем посмотреть
    input("\n👀 Нажми Enter чтобы закрыть браузер...")
    
    # Закрываем
    payment.close()
    
    return result

if __name__ == "__main__":
    test_visual()
