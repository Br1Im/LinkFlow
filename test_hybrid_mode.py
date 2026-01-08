# -*- coding: utf-8 -*-
"""
Тест гибридного режима
"""

import sys
import time

def test_hybrid_mode():
    print("\n" + "="*60)
    print("🧪 ТЕСТ ГИБРИДНОГО РЕЖИМА")
    print("="*60)
    
    # Импорт
    try:
        from hybrid_payment import hybrid_manager
        print("✅ Модуль hybrid_payment импортирован")
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    
    # Данные аккаунта
    account = {
        "phone": "+79880260334",
        "password": "xowxut-wemhej-3zAsno",
        "profile_path": "profile_79880260334"  # Не используется, но нужен для совместимости
    }
    
    # Шаг 1: Авторизация
    print("\n" + "="*60)
    print("1️⃣ АВТОРИЗАЦИЯ И ПОЛУЧЕНИЕ COOKIES")
    print("="*60)
    
    start_time = time.time()
    
    try:
        success = hybrid_manager.authorize_and_get_cookies(account)
        elapsed = time.time() - start_time
        
        if success:
            print(f"\n✅ Авторизация успешна за {elapsed:.1f} сек!")
            print(f"   Статус: {hybrid_manager.is_authorized}")
        else:
            print(f"\n❌ Авторизация не удалась за {elapsed:.1f} сек")
            return False
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n❌ Ошибка авторизации: {e}")
        print(f"   Время: {elapsed:.1f} сек")
        return False
    
    # Шаг 2: Создание платежа
    print("\n" + "="*60)
    print("2️⃣ СОЗДАНИЕ ПЛАТЕЖА")
    print("="*60)
    
    card_number = "9860100125857258"
    owner_name = "IZZET SAMEKEEV"
    amount = 2000
    
    print(f"\n💳 Карта: {card_number}")
    print(f"👤 Владелец: {owner_name}")
    print(f"💰 Сумма: {amount} руб.")
    
    start_time = time.time()
    
    try:
        result = hybrid_manager.create_payment_fast(
            card_number=card_number,
            owner_name=owner_name,
            amount=amount
        )
        
        elapsed = time.time() - start_time
        
        if result.get("success"):
            print(f"\n✅ УСПЕХ за {elapsed:.2f} сек!")
            print(f"\n📊 Результат:")
            print(f"   🔗 Ссылка: {result['payment_link']}")
            print(f"   📷 QR: {result['qr_base64'][:80]}...")
            print(f"   ⏱ Время: {result['elapsed_time']:.2f} сек")
            
            # Сравнение со Selenium
            selenium_time = 15.0
            speedup = selenium_time / elapsed
            print(f"\n🚀 Ускорение:")
            print(f"   Selenium: ~{selenium_time:.0f} сек")
            print(f"   Hybrid: {elapsed:.2f} сек")
            print(f"   Быстрее в {speedup:.1f}x раз!")
            
            return True
        else:
            print(f"\n❌ Ошибка: {result.get('error')}")
            print(f"   Время: {elapsed:.2f} сек")
            return False
            
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n❌ Исключение: {e}")
        print(f"   Время: {elapsed:.2f} сек")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Закрываем ресурсы
        try:
            hybrid_manager.close()
            print("\n🔒 Ресурсы закрыты")
        except:
            pass


if __name__ == "__main__":
    print("\n🚀 Запуск теста гибридного режима...")
    print("⚠️ Убедитесь что Chrome установлен и доступен")
    
    success = test_hybrid_mode()
    
    print("\n" + "="*60)
    if success:
        print("✅ ТЕСТ ПРОЙДЕН УСПЕШНО!")
        print("="*60)
        print("\n💡 Гибридный режим работает!")
        print("   Можно использовать в боте для быстрых платежей")
        sys.exit(0)
    else:
        print("❌ ТЕСТ НЕ ПРОЙДЕН")
        print("="*60)
        print("\n💡 Возможные причины:")
        print("   1. Chrome не установлен или недоступен")
        print("   2. Проблемы с сетью (elecsnet.ru недоступен)")
        print("   3. Неверные данные авторизации")
        print("   4. Проблемы с профилем Chrome")
        print("\n   Бот будет использовать Selenium режим (медленнее, но надежнее)")
        sys.exit(1)
