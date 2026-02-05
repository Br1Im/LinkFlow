#!/usr/bin/env python3
"""
Тест платежа с новыми реквизитами IQLAS TLEUOV
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'admin', 'payment_service'))

from payment_service import PaymentService

async def main():
    # Тестируем с рабочими реквизитами
    test_cases = [
        {
            'card': '9860606753188378',
            'owner': 'ASIYA ESEMURATOVA',
            'amount': 110,
            'name': 'ASIYA ESEMURATOVA (проверенный)'
        }
    ]
    
    service = PaymentService()
    
    try:
        print("🚀 Запуск браузера с маленьким окном для мониторинга...")
        await service.start(headless=False, compact_window=True)  # Маленькое окно
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n{'='*60}")
            print(f"ТЕСТ {i}: {test['name']} - {test['card']}")
            print(f"{'='*60}\n")
            
            result = await service.create_payment_link(
                amount=test['amount'],
                card_number=test['card'],
                owner_name=test['owner']
            )
            
            if result['success']:
                print(f"\n✅ УСПЕХ!")
                print(f"QR ссылка: {result['qr_link']}")
                print(f"Время: {result['time']:.2f}s")
                print(f"Этап 1: {result['step1_time']:.2f}s")
                print(f"Этап 2: {result['step2_time']:.2f}s")
            else:
                print(f"\n❌ ОШИБКА: {result['error']}")
                print(f"Время: {result['time']:.2f}s")
            
            # Пауза между тестами
            if i < len(test_cases):
                print("\n⏳ Пауза 5 секунд перед следующим тестом...")
                await asyncio.sleep(5)
        
    finally:
        await service.stop()
        print("\n🛑 Браузер закрыт")

if __name__ == '__main__':
    asyncio.run(main())
