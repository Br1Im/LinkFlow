#!/usr/bin/env python3
"""
Простой тест генерации платежа
"""
import asyncio
import sys
from payment_service import PaymentService

async def main():
    print("="*60)
    print("ТЕСТ ГЕНЕРАЦИИ ПЛАТЕЖА")
    print("="*60)
    print()
    
    # Данные
    card_number = '9860606753188378'
    owner_name = 'ASIYA ESEMURATOVA'
    amount = 1000
    
    print(f"Карта: {card_number}")
    print(f"Получатель: {owner_name}")
    print(f"Сумма: {amount} RUB")
    print()
    
    # Создаем сервис
    service = PaymentService()
    
    try:
        # Запускаем браузер (headless=False для визуального режима)
        print("Запуск браузера...")
        await service.start(headless=False)
        print("Браузер запущен!")
        print()
        
        # Создаем платеж
        print("Создание платежа...")
        result = await service.create_payment_link(
            amount=amount,
            card_number=card_number,
            owner_name=owner_name
        )
        
        print()
        print("="*60)
        print("РЕЗУЛЬТАТ")
        print("="*60)
        
        if result.get('success'):
            print(f"✅ Успех!")
            print(f"QR-ссылка: {result.get('qr_link')}")
            print(f"Время: {result.get('time')} сек")
            print(f"  Этап 1: {result.get('step1_time')} сек")
            print(f"  Этап 2: {result.get('step2_time')} сек")
        else:
            print(f"❌ Ошибка: {result.get('error')}")
        
    finally:
        await service.stop()
        print("\nБраузер закрыт")

if __name__ == "__main__":
    asyncio.run(main())
