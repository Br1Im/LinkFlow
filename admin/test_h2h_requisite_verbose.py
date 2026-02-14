#!/usr/bin/env python3
import sys
import os
import time
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'payment_service'))

from h2h_api import H2HAPI
from requisite_config import get_h2h_config

config = get_h2h_config()

api = H2HAPI(base_url=config['base_url'], access_token=config['access_token'])

external_id = f"VERBOSE_{int(time.time() * 1000)}"

print("="*60)
print("VERBOSE TEST H2H API")
print("="*60)
print(f"External ID: {external_id}")
print(f"Amount: 2000")
print(f"Merchant ID: {config['merchant_id']}")
print(f"Currency: {config['currency']}")
print(f"Payment Detail Type: {config['payment_detail_type']}")
print("="*60)

result = api.create_order(
    external_id=external_id,
    amount=2000,
    merchant_id=config['merchant_id'],
    currency=config['currency'],
    payment_detail_type=config['payment_detail_type']
)

print(f"\nПолный ответ API:")
print(json.dumps(result, indent=2, ensure_ascii=False))

print(f"\nАнализ:")
print(f"  result.get('success'): {result.get('success')}")
print(f"  'data' in result: {'data' in result}")

if result.get("success") and "data" in result:
    data = result["data"]
    payment_detail = data.get("payment_detail", {})
    print(f"  payment_detail: {json.dumps(payment_detail, indent=4, ensure_ascii=False)}")
    
    if payment_detail:
        print(f"\n✅ Реквизиты найдены:")
        print(f"  Карта: {payment_detail.get('detail', '')}")
        print(f"  Владелец: {payment_detail.get('initials', '')}")
    else:
        print(f"\n❌ payment_detail пустой!")
else:
    print(f"\n❌ Ошибка: success={result.get('success')}, есть data={'data' in result}")
