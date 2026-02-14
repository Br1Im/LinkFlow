#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'payment_service'))

from requisite_config import get_requisite_service, get_h2h_config
from h2h_api import get_h2h_requisite
import json

print("="*60)
print("ОТЛАДКА get_payzteam_requisite")
print("="*60)

service = get_requisite_service()
print(f"\nАктивный сервис: {service}")

if service == 'h2h':
    config = get_h2h_config()
    print(f"\nH2H конфигурация:")
    print(f"  base_url: {config['base_url']}")
    print(f"  merchant_id: {config['merchant_id']}")
    
    print(f"\nВызов get_h2h_requisite с amount=2000...")
    result = get_h2h_requisite(
        amount=2000,
        base_url=config['base_url'],
        access_token=config['access_token'],
        merchant_id=config['merchant_id'],
        currency=config.get('currency', 'rub'),
        payment_detail_type=config.get('payment_detail_type', 'card')
    )
    
    print(f"\nРезультат:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
else:
    print(f"Сервис не h2h: {service}")
