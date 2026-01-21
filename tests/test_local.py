# -*- coding: utf-8 -*-
"""
Локальный тест multitransfer.ru (без Docker)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import time
from src.multitransfer_payment import MultitransferPayment


def test_local():
    """Быстрый локальный тест"""
    
    print("\n" + "="*80)
    print("🧪 ЛОКАЛЬНЫЙ ТЕСТ MULTITRANSFER.RU")
    print("="*80)
    
    # Тестовые данные
    test_data = {
        "card_number": "9860080323894719",
        "owner_name": "Nodir Asadullayev",
        "amount": 1000
    }
    
    print(f"\n📋 Тестовые данные:")
    print(f"   Карта: {test_data['card_number']}")
    print(f"   Владелец: {test_data['owner_name']}")
    print(f"   Сумма: {test_data['amount']} руб.")
    print(f"\n⚠️  ВНИМАНИЕ: Браузер откроется в видимом режиме")
    print(f"   Вы сможете наблюдать за процессом")
    
    input("\nНажмите Enter для начала теста...")
    
    # Создаем экземпляр
    payment = MultitransferPayment()
    
    try:
        # Инициализация
        print(f"\n1️⃣ Инициализация браузера...")
        if not payment.login():
            print("❌ Не удалось инициализировать браузер")
            return False
        
        # Создание платежа
        print(f"\n2️⃣ Создание платежа...")
        result = payment.create_payment(
            card_number=test_data['card_number'],
            owner_name=test_data['owner_name'],
            amount=test_data['amount']
        )
        
        # Результат
        print(f"\n3️⃣ Результат:")
        print("="*80)
        
        if result.get('success'):
            print(f"✅ УСПЕХ!")
            print(f"🔗 Ссылка: {result.get('payment_link')}")
            if result.get('qr_base64'):
                print(f"📷 QR: {result.get('qr_base64')[:50]}...")
            print(f"⏱️  Время: {result.get('elapsed_time'):.1f} сек")
            return True
        else:
            print(f"❌ ОШИБКА: {result.get('error')}")
            print(f"⏱️  Время: {result.get('elapsed_time', 0):.1f} сек")
            return False
    
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Пауза перед закрытием
        print(f"\n⏸️  Нажмите Enter для закрытия браузера...")
        try:
            input()
        except:
            time.sleep(5)
        
        # Закрытие
        print(f"\n4️⃣ Закрытие браузера...")
        payment.close()
        
        print("\n" + "="*80)
        print("✅ ТЕСТ ЗАВЕРШЕН")
        print("="*80)


if __name__ == "__main__":
    import sys
    
    try:
        success = test_local()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Тест прерван пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Критическая ошибка: {e}")
        sys.exit(1)
