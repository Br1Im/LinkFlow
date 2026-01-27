#!/usr/bin/env python3
"""
Тест полной автоматизации
"""

from fully_automatic_api import FullyAutomaticAPI

def test_single_payment():
    """Тест одного платежа"""
    print("🧪 ТЕСТ: Один автоматический платеж")
    
    auto_api = FullyAutomaticAPI(headless=False)  # С GUI для наблюдения
    
    qr_link = auto_api.create_qr_payment(
        card_number="9860080323894719",
        recipient_name="Nodir Asadullayev",
        amount=110
    )
    
    if qr_link:
        print(f"✅ УСПЕХ: {qr_link}")
        return True
    else:
        print("❌ НЕУДАЧА")
        return False

def test_multiple_payments():
    """Тест нескольких платежей"""
    print("🧪 ТЕСТ: Несколько автоматических платежей")
    
    auto_api = FullyAutomaticAPI(headless=True)
    
    payments = [
        {"card": "9860080323894719", "name": "Test User 1", "amount": 110},
        {"card": "9860080323894719", "name": "Test User 2", "amount": 150}
    ]
    
    results = auto_api.create_multiple_payments(payments)
    
    success_count = sum(1 for r in results if r["success"])
    print(f"✅ Успешно: {success_count}/{len(payments)}")
    
    return success_count > 0

def main():
    """Запуск всех тестов"""
    print("🚀 ЗАПУСК ТЕСТОВ АВТОМАТИЗАЦИИ\n")
    
    tests = [
        ("Один платеж", test_single_payment),
        ("Несколько платежей", test_multiple_payments)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"🧪 {test_name}")
        print('='*50)
        
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Ошибка в тесте: {e}")
            results.append((test_name, False))
    
    # Итоги
    print(f"\n{'='*50}")
    print("📊 ИТОГИ ТЕСТОВ")
    print('='*50)
    
    for test_name, success in results:
        status = "✅ ПРОШЕЛ" if success else "❌ ПРОВАЛЕН"
        print(f"{test_name}: {status}")
    
    success_count = sum(1 for _, success in results if success)
    print(f"\nОбщий результат: {success_count}/{len(results)} тестов прошли")
    
    if success_count == len(results):
        print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ! Автоматизация работает!")
    else:
        print("⚠️ Есть проблемы с автоматизацией")

if __name__ == "__main__":
    main()