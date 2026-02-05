#!/usr/bin/env python3
"""
Тест системы логирования
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'admin', 'payment_service'))

from payment_service import PaymentService, current_payment_logs


async def test_logs():
    """Тестируем что логи собираются"""
    print("🧪 Тест системы логирования\n")
    
    service = PaymentService()
    
    try:
        print("1️⃣ Запускаем браузер...")
        await service.start(headless=True)
        print(f"   ✅ Браузер запущен\n")
        
        print("2️⃣ Создаем тестовый платеж...")
        result = await service.create_payment_link(
            amount=1000,
            card_number="9860080323894719",
            owner_name="Nodir Asadullayev"
        )
        
        print(f"\n3️⃣ Результат:")
        print(f"   Success: {result.get('success')}")
        print(f"   Error: {result.get('error')}")
        print(f"   Time: {result.get('time'):.2f}s")
        
        print(f"\n4️⃣ Логи в результате:")
        logs = result.get('logs', [])
        print(f"   Всего логов: {len(logs)}")
        
        if logs:
            print(f"\n   Первые 10 логов:")
            for i, log in enumerate(logs[:10], 1):
                print(f"   {i}. [{log['level']}] {log['message'][:80]}")
        else:
            print("   ❌ ЛОГИ ПУСТЫЕ!")
        
        print(f"\n5️⃣ Глобальная переменная current_payment_logs:")
        print(f"   Всего логов: {len(current_payment_logs)}")
        
    finally:
        await service.stop()
        print("\n🛑 Браузер закрыт")


if __name__ == '__main__':
    asyncio.run(test_logs())
