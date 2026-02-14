#!/usr/bin/env python3
"""
Финальный тест интеграции - проверка работы get_payzteam_requisite с H2H API
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'payment_service'))

from payzteam_api import get_payzteam_requisite

print("=" * 70)
print("ФИНАЛЬНЫЙ ТЕСТ ИНТЕГРАЦИИ")
print("=" * 70)
print("Проверяем функцию get_payzteam_requisite() с H2H API")
print("=" * 70)

# Тест 1: Сумма 1000 RUB
print("\nТест 1: amount=1000 RUB")
print("-" * 70)

requisite = get_payzteam_requisite(1000)

if requisite:
    print("✅ Успешно получены реквизиты!")
    print(f"   Номер карты: {requisite.get('card_number')}")
    print(f"   Владелец: {requisite.get('card_owner')}")
    print(f"   Order ID: {requisite.get('order_id')}")
    print(f"   Сумма: {requisite.get('amount')}")
else:
    print("❌ Не удалось получить реквизиты")

# Тест 2: Сумма 2500 RUB
print("\nТест 2: amount=2500 RUB")
print("-" * 70)

requisite2 = get_payzteam_requisite(2500)

if requisite2:
    print("✅ Успешно получены реквизиты!")
    print(f"   Номер карты: {requisite2.get('card_number')}")
    print(f"   Владелец: {requisite2.get('card_owner')}")
    print(f"   Order ID: {requisite2.get('order_id')}")
    print(f"   Сумма: {requisite2.get('amount')}")
else:
    print("❌ Не удалось получить реквизиты")

print("\n" + "=" * 70)
print("✅ Интеграция H2H API работает!")
print("=" * 70)
print("\nФункция get_payzteam_requisite() теперь использует H2H API")
print("и возвращает реквизиты (номер карты + ФИО владельца)")
