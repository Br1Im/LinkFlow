#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки генерации платежных ссылок
Использование: python test_payment.py [сумма]
"""

import sys
import time
from payment_automation import create_payment_link
from database import db

def test_payment(amount=5000):
    """Тестирует создание платежа с указанной суммой"""
    
    print(f"\n{'='*60}")
    print(f"🧪 ТЕСТ ГЕНЕРАЦИИ ПЛАТЕЖА")
    print(f"{'='*60}\n")
    
    requisites = db.get_requisites()
    
    if not requisites:
        print("❌ Нет реквизитов в базе!")
        print("Добавьте реквизиты через бота: /admin -> Управление реквизитами")
        return False
    
    requisite = requisites[0]
    
    print(f"📋 Параметры теста:")
    print(f"   Карта: {requisite['card_number']}")
    print(f"   Владелец: {requisite['owner_name']}")
    print(f"   Сумма: {amount} руб.\n")
    
    start_time = time.time()
    
    result = create_payment_link(
        card_number=requisite['card_number'],
        owner_name=requisite['owner_name'],
        amount=amount
    )
    
    elapsed = time.time() - start_time
    
    print(f"\n{'='*60}")
    
    if "error" in result:
        print(f"❌ ТЕСТ ПРОВАЛЕН")
        print(f"{'='*60}")
        print(f"Ошибка: {result['error']}")
        print(f"Время: {elapsed:.1f} сек")
        return False
    else:
        print(f"✅ ТЕСТ УСПЕШЕН")
        print(f"{'='*60}")
        print(f"⏱️  Время генерации: {result['elapsed_time']:.1f} сек")
        print(f"🔗 Ссылка: {result['payment_link']}")
        print(f"📱 Аккаунт: {result['account_used']}")
        print(f"🖼️  QR-код: {result['qr_file']}")
        
        # Удаляем QR-код после теста
        import os
        try:
            os.remove(result['qr_file'])
            print(f"🗑️  QR-код удален")
        except:
            pass
        
        return True

if __name__ == "__main__":
    # Получаем сумму из аргументов командной строки
    amount = 5000
    if len(sys.argv) > 1:
        try:
            amount = float(sys.argv[1])
        except ValueError:
            print(f"❌ Неверная сумма: {sys.argv[1]}")
            print(f"Использование: python test_payment.py [сумма]")
            sys.exit(1)
    
    # Проверяем диапазон
    if amount < 1000 or amount > 100000:
        print(f"❌ Сумма должна быть от 1000 до 100000 руб.")
        sys.exit(1)
    
    # Запускаем тест
    success = test_payment(amount)
    
    sys.exit(0 if success else 1)
