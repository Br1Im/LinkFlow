# -*- coding: utf-8 -*-
"""
Локальный тест для multitransfer.ru
"""

import sys
sys.path.append('bot')

from multitransfer_service import multitransfer_manager

def test_multitransfer():
    """Тест создания платежа через multitransfer.ru"""
    
    print("=" * 80)
    print("🧪 ТЕСТ MULTITRANSFER.RU")
    print("=" * 80)
    
    # Инициализация
    print("\n1️⃣ Инициализация браузера...")
    if not multitransfer_manager.initialize():
        print("❌ Не удалось инициализировать браузер")
        return False
    
    # Тестовые данные
    test_data = {
        "amount": 1000,
        "card_number": "9860080323894719",
        "owner_name": "Nodir Asadullayev"
    }
    
    print(f"\n2️⃣ Создание платежа...")
    print(f"   Сумма: {test_data['amount']}")
    print(f"   Карта: {test_data['card_number']}")
    print(f"   Владелец: {test_data['owner_name']}")
    
    result = multitransfer_manager.create_payment(
        amount=test_data['amount'],
        card_number=test_data['card_number'],
        owner_name=test_data['owner_name']
    )
    
    print(f"\n3️⃣ Результат:")
    if result.get('success'):
        print(f"   ✅ Успех!")
        print(f"   Ссылка: {result.get('payment_link')}")
        print(f"   Время: {result.get('elapsed_time'):.1f}s")
    else:
        print(f"   ❌ Ошибка: {result.get('error')}")
    
    # Пауза перед закрытием - чтобы изучить результат
    print("\n⏸️  Нажмите Enter чтобы закрыть браузер...")
    try:
        input()
    except:
        time.sleep(5)
    
    # Закрытие
    print("\n4️⃣ Закрытие браузера...")
    multitransfer_manager.close()
    
    print("\n" + "=" * 80)
    print("✅ ТЕСТ ЗАВЕРШЕН")
    print("=" * 80)
    
    return result.get('success', False)


if __name__ == "__main__":
    try:
        success = test_multitransfer()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Тест прерван пользователем")
        multitransfer_manager.close()
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Критическая ошибка: {e}")
        multitransfer_manager.close()
        sys.exit(1)
