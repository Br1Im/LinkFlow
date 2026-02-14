#!/usr/bin/env python3
"""
Проверка конфигурации на сервере
"""

import sys
import os

# Добавляем путь к payment_service
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'payment_service'))

from requisite_config import get_requisite_service, get_h2h_config

print("="*60)
print("ПРОВЕРКА КОНФИГУРАЦИИ")
print("="*60)

service = get_requisite_service()
print(f"\nАктивный сервис: {service}")

if service == 'h2h':
    config = get_h2h_config()
    print(f"\nH2H конфигурация:")
    print(f"  base_url: {config['base_url']}")
    print(f"  merchant_id: {config['merchant_id']}")
    print(f"  access_token: {config['access_token'][:20]}...")
    print(f"  currency: {config.get('currency', 'rub')}")
    print(f"  payment_detail_type: {config.get('payment_detail_type', 'card')}")
    
    # Тестируем импорт H2H API
    try:
        from h2h_api import get_h2h_requisite
        print(f"\n✅ H2H API импортирован успешно")
        
        # Пробуем получить реквизиты
        print(f"\nТестовый запрос к H2H API...")
        result = get_h2h_requisite(
            amount=300,
            base_url=config['base_url'],
            access_token=config['access_token'],
            merchant_id=config['merchant_id'],
            currency=config.get('currency', 'rub'),
            payment_detail_type=config.get('payment_detail_type', 'card')
        )
        
        if result:
            print(f"✅ Реквизиты получены:")
            print(f"  Карта: {result.get('card_number')}")
            print(f"  Владелец: {result.get('card_owner')}")
            print(f"  Order ID: {result.get('order_id')}")
        else:
            print(f"❌ Реквизиты не получены (result = None)")
            
    except Exception as e:
        print(f"❌ Ошибка импорта H2H API: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*60)
