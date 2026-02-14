#!/usr/bin/env python3
"""
Отладка H2H API
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'payment_service'))

from h2h_api import H2HAPI
from requisite_config import get_h2h_config

config = get_h2h_config()

print("="*60)
print("ТЕСТ H2H API")
print("="*60)
print(f"Base URL: {config['base_url']}")
print(f"Merchant ID: {config['merchant_id']}")
print(f"Access Token: {config['access_token'][:20]}...")
print("="*60)

api = H2HAPI(
    base_url=config['base_url'],
    access_token=config['access_token']
)

# Создаем заказ
import time
external_id = f"DEBUG_{int(time.time())}"

print(f"\nСоздание заказа...")
print(f"External ID: {external_id}")
print(f"Amount: 300")
print(f"Currency: {config['currency']}")
print(f"Payment Detail Type: {config['payment_detail_type']}")

result = api.create_order(
    external_id=external_id,
    amount=300,
    merchant_id=config['merchant_id'],
    currency=config['currency'],
    payment_detail_type=config['payment_detail_type']
)

print(f"\nРезультат:")
print(json.dumps(result, indent=2, ensure_ascii=False))

if result.get("success") and "data" in result:
    data = result["data"]
    payment_detail = data.get("payment_detail", {})
    
    print(f"\nPayment Detail:")
    print(json.dumps(payment_detail, indent=2, ensure_ascii=False))
    
    if payment_detail:
        print(f"\nРеквизиты:")
        print(f"  Карта: {payment_detail.get('detail', '')}")
        print(f"  Владелец: {payment_detail.get('initials', '')}")
    else:
        print(f"\n❌ payment_detail пустой!")
else:
    print(f"\n❌ Ошибка: success={result.get('success')}, data={result.get('data')}")
