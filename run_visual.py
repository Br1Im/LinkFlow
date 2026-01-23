#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Запуск скрипта с визуализацией (без Docker)
"""

import sys
import os

# Добавляем src в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from multitransfer_payment import MultitransferPayment
from config import EXAMPLE_RECIPIENT_DATA

def main():
    print("🚀 Запуск с визуализацией браузера")
    print("=" * 60)
    
    # Создаём экземпляр с headless=False для визуализации
    payment = MultitransferPayment(headless=False)
    
    try:
        # Логин (инициализация)
        print("\n1️⃣ Открываю браузер...")
        payment.login()
        
        input("\n⏸️  Нажми Enter чтобы начать создание платежа...")
        
        # Создание платежа
        print("\n2️⃣ Создаю платёж...")
        result = payment.create_payment(
            card_number=EXAMPLE_RECIPIENT_DATA["card_number"],
            owner_name=EXAMPLE_RECIPIENT_DATA["owner_name"],
            amount=EXAMPLE_RECIPIENT_DATA["amount"]
        )
        
        # Результат
        print("\n" + "=" * 60)
        print("📊 РЕЗУЛЬТАТ:")
        print("=" * 60)
        
        if result.get("success"):
            print("✅ Успех!")
            print(f"🔗 Ссылка: {result.get('payment_link')}")
            print(f"⏱️  Время: {result.get('elapsed_time'):.1f} сек")
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
        input("\n⏸️  Нажми Enter чтобы закрыть браузер...")
        print("\n3️⃣ Закрываю браузер...")
        payment.close()
        print("\n✅ Готово!")

if __name__ == "__main__":
    main()
