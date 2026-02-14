#!/usr/bin/env python3
"""
Проверка конфигурации - какой API используется
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'payment_service'))

from requisite_config import get_requisite_service, get_h2h_config

print("=" * 70)
print("ПРОВЕРКА КОНФИГУРАЦИИ")
print("=" * 70)

service = get_requisite_service()
print(f"\nАктивный сервис: {service}")

if service == 'h2h':
    config = get_h2h_config()
    print("\n✅ Используется H2H API")
    print(f"   Base URL: {config['base_url']}")
    print(f"   Merchant ID: {config['merchant_id']}")
    print(f"   Currency: {config['currency']}")
    print(f"   Payment Detail Type: {config['payment_detail_type']}")
    
    # Проверяем правильность URL
    if config['base_url'] == 'https://api.liberty.top':
        print("\n✅ URL правильный!")
    else:
        print(f"\n❌ ОШИБКА: URL должен быть 'https://api.liberty.top'")
        print(f"   Текущий URL: {config['base_url']}")
        
elif service == 'payzteam':
    print("\n❌ ВНИМАНИЕ: Используется старый PayzTeam API!")
    print("   Нужно изменить ACTIVE_REQUISITE_SERVICE на 'h2h'")
    
elif service == 'merchant':
    print("\n⚠️ Используется Merchant API")
    print("   Это тоже работает, но лучше использовать H2H API")

print("\n" + "=" * 70)
