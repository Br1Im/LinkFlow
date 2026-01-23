#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый запуск скрипта
"""

import sys
import os

# Добавляем src в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from multitransfer_payment import MultitransferPayment
from config import EXAMPLE_RECIPIENT_DATA

def main():
    print("🚀 Тестовый запуск LinkFlow")
    print("=" * 50)
    
    # Создаём экземпляр (headless=False чтобы видеть браузер)
    payment = MultitransferPayment(headless=False)
    
    try:
        # Логин (инициализация)
        print("\n1️⃣ Инициализация...")
        payment.login()
        
        # Создание платежа
        print("\n2️⃣ Создание платежа...")
        result = payment.create_payment(
            card_number=EXAMPLE_RECIPIENT_DATA["card_number"],
            owner_name=EXAMPLE_RECIPIENT_DATA["owner_name"],
            amount=EXAMPLE_RECIPIENT_DATA["amount"]
        )
        
        # Результат
        print("\n" + "=" * 50)
        print("📊 РЕЗУЛЬТАТ:")
        print("=" * 50)
        
        if result.get("success"):
            print("✅ Успех!")
            print(f"🔗 Ссылка: {result.get('payment_link')}")
            print(f"⏱️  Время: {result.get('elapsed_time'):.1f} сек")
            
            if result.get("payment_data"):
                print("\n📋 Данные платежа:")
                for key, value in result["payment_data"].items():
                    print(f"   • {key}: {value}")
        else:
            print("❌ Ошибка!")
            print(f"   {result.get('error')}")
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Прервано пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n3️⃣ Закрытие браузера...")
        payment.close()
        print("\n✅ Готово!")

if __name__ == "__main__":
    main()
