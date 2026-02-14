#!/usr/bin/env python3
"""
Полный тест: проверка что api_server.py использует H2H API для получения реквизитов
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'payment_service'))

print("=" * 70)
print("ТЕСТ ПОЛНОГО ПРОЦЕССА")
print("=" * 70)

# Шаг 1: Проверяем конфигурацию
print("\n1. Проверка конфигурации:")
print("-" * 70)

from requisite_config import get_requisite_service, get_h2h_config

service = get_requisite_service()
print(f"   Активный сервис: {service}")

if service == 'h2h':
    config = get_h2h_config()
    print(f"   ✅ H2H API активен")
    print(f"   URL: {config['base_url']}")
else:
    print(f"   ❌ ОШИБКА: Активен {service}, а должен быть h2h")
    sys.exit(1)

# Шаг 2: Тестируем функцию get_payzteam_requisite
print("\n2. Тест функции get_payzteam_requisite():")
print("-" * 70)

from payzteam_api import get_payzteam_requisite

requisite = get_payzteam_requisite(1500)

if requisite:
    print(f"   ✅ Реквизиты получены через H2H API")
    print(f"   Номер карты: {requisite.get('card_number')}")
    print(f"   Владелец: {requisite.get('card_owner')}")
    print(f"   Order ID: {requisite.get('order_id')}")
else:
    print(f"   ❌ Не удалось получить реквизиты")
    sys.exit(1)

# Шаг 3: Проверяем что api_server.py импортирует правильную функцию
print("\n3. Проверка api_server.py:")
print("-" * 70)

with open('admin/api_server.py', 'r', encoding='utf-8') as f:
    content = f.read()
    
if 'from payzteam_api import get_payzteam_requisite' in content:
    print("   ✅ api_server.py импортирует get_payzteam_requisite")
else:
    print("   ❌ ОШИБКА: api_server.py не импортирует get_payzteam_requisite")
    sys.exit(1)

if 'payzteam_future = executor.submit(get_payzteam_requisite, amount)' in content:
    print("   ✅ api_server.py вызывает get_payzteam_requisite")
else:
    print("   ❌ ОШИБКА: api_server.py не вызывает get_payzteam_requisite")
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
print("=" * 70)
print("\nВывод:")
print("1. Конфигурация настроена на H2H API")
print("2. Функция get_payzteam_requisite() работает с H2H API")
print("3. api_server.py использует get_payzteam_requisite()")
print("\n➡️ Скрипт на хосте 85.192.56.74 будет брать реквизиты через H2H API")
print("=" * 70)
