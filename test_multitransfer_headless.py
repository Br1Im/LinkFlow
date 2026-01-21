# -*- coding: utf-8 -*-
"""
Тест multitransfer.ru в headless режиме
"""

import sys
sys.path.append('bot')

from multitransfer_service import MultitransferPayment

def test_headless():
    """Тест в headless режиме"""
    
    print("=" * 80)
    print("🧪 ТЕСТ MULTITRANSFER.RU (HEADLESS)")
    print("=" * 80)
    
    # Тестовые данные
    card_number = "9860080323894719"
    owner_name = "Nodir Asadullayev"
    amount = 1000
    
    payment = MultitransferPayment()
    
    try:
        # Инициализация
        print("\n1️⃣ Инициализация...")
        if not payment.login():
            print("❌ Не удалось инициализировать")
            return False
        
        # Создание платежа
        print(f"\n2️⃣ Создание платежа...")
        print(f"   Сумма: {amount}")
        print(f"   Карта: {card_number}")
        print(f"   Владелец: {owner_name}")
        
        result = payment.create_payment(
            card_number=card_number,
            owner_name=owner_name,
            amount=amount
        )
        
        # Результат
        print(f"\n3️⃣ Результат:")
        if result.get('success'):
            print(f"   ✅ Успех!")
            print(f"   Ссылка: {result.get('payment_link')}")
            print(f"   Время: {result.get('elapsed_time'):.1f}s")
            
            # Данные платежа
            if result.get('payment_data'):
                print(f"\n   📊 Данные платежа:")
                for key, value in result['payment_data'].items():
                    print(f"      • {key}: {value}")
        else:
            print(f"   ❌ Ошибка: {result.get('error')}")
            return False
        
        print("\n" + "=" * 80)
        print("✅ ТЕСТ ЗАВЕРШЕН УСПЕШНО")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Закрытие браузера
        print("\n4️⃣ Закрытие браузера...")
        payment.close()


if __name__ == "__main__":
    try:
        success = test_headless()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Тест прерван пользователем")
        sys.exit(1)
