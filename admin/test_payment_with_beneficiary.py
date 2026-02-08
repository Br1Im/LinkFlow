#!/usr/bin/env python3
"""
Тестовый запуск создания платежа с реквизитами из БД
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'payment_service'))

from payment_service import PaymentService
import database

async def test_payment():
    # Получаем случайный реквизит
    beneficiary = database.get_random_beneficiary()
    
    if not beneficiary:
        print("❌ Нет активных реквизитов в БД")
        return
    
    print("=" * 60)
    print("ТЕСТОВЫЙ ПЛАТЕЖ С РЕКВИЗИТАМИ ИЗ БД")
    print("=" * 60)
    print(f"\nРеквизит:")
    print(f"  ID: {beneficiary['id']}")
    print(f"  Владелец: {beneficiary['card_owner']}")
    print(f"  Карта: {beneficiary['card_number']}")
    print(f"\nСумма: 1000 RUB")
    print("\n" + "=" * 60)
    
    # Создаем сервис
    service = PaymentService()
    
    try:
        # Запускаем браузер в headless режиме для production
        await service.start(headless=True, compact_window=False)
        
        # Создаем платеж
        result = await service.create_payment_link(
            amount=1000,
            card_number=beneficiary['card_number'],
            owner_name=beneficiary['card_owner']
        )
        
        print("\n" + "=" * 60)
        print("РЕЗУЛЬТАТ:")
        print("=" * 60)
        print(f"Success: {result['success']}")
        print(f"Time: {result['time']:.2f}s")
        
        if result['success']:
            print(f"QR Link: {result['qr_link'][:100]}..." if result['qr_link'] else "QR Link: None")
        else:
            print(f"Error: {result['error']}")
        
        print("=" * 60)
        
    finally:
        await service.stop()

if __name__ == "__main__":
    asyncio.run(test_payment())
