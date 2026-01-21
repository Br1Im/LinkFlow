# -*- coding: utf-8 -*-
"""
Тестовый скрипт для multitransfer.ru
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import time
from src.multitransfer_payment import MultitransferPayment


def test_multitransfer():
    """Тест создания платежа через multitransfer.ru"""
    
    print("\n" + "="*80)
    print("🧪 ТЕСТ MULTITRANSFER.RU")
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
            print(f"📷 QR: {result.get('qr_base64', 'N/A')[:50]}...")
            print(f"⏱️  Время: {result.get('elapsed_time'):.1f} сек")
            
            # Сохраняем скриншот успеха
            try:
                payment.driver.save_screenshot("/app/screenshots/success.png")
                print(f"📸 Скриншот сохранен: /app/screenshots/success.png")
            except:
                pass
            
            return True
        else:
            print(f"❌ ОШИБКА: {result.get('error')}")
            print(f"⏱️  Время: {result.get('elapsed_time', 0):.1f} сек")
            
            # Сохраняем скриншот ошибки
            try:
                payment.driver.save_screenshot("/app/screenshots/error.png")
                print(f"📸 Скриншот ошибки: /app/screenshots/error.png")
            except:
                pass
            
            return False
    
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        
        # Сохраняем скриншот критической ошибки
        try:
            if payment.driver:
                payment.driver.save_screenshot("/app/screenshots/critical_error.png")
                print(f"📸 Скриншот: /app/screenshots/critical_error.png")
        except:
            pass
        
        return False
    
    finally:
        # Пауза перед закрытием (для Docker)
        print(f"\n⏸️  Ожидание 5 секунд перед закрытием...")
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
        success = test_multitransfer()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Тест прерван пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Критическая ошибка: {e}")
        sys.exit(1)
