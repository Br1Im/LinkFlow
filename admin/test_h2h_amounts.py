#!/usr/bin/env python3
"""
Тест H2H API с разными суммами
"""

import sys
import os
import json
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'payment_service'))

from h2h_api import H2HAPI
from requisite_config import get_h2h_config

config = get_h2h_config()

api = H2HAPI(
    base_url=config['base_url'],
    access_token=config['access_token']
)

print("="*60)
print("ТЕСТ H2H API - РАЗНЫЕ СУММЫ")
print("="*60)

amounts = [100, 300, 500, 1000, 1500, 2000, 2500, 3000]

for amount in amounts:
    print(f"\nСумма: {amount} RUB")
    result = api.create_order(
        external_id=f"AMOUNT_TEST_{amount}_{int(time.time())}",
        amount=amount,
        merchant_id=config['merchant_id'],
        currency="rub",
        payment_detail_type="card"
    )
    
    if result.get("success"):
        payment_detail = result["data"].get("payment_detail", {})
        print(f"  ✅ Успех! Карта: {payment_detail.get('detail')}, Владелец: {payment_detail.get('initials')}")
    else:
        print(f"  ❌ Ошибка: {result.get('details', {}).get('message', 'Unknown error')}")
    
    time.sleep(0.5)

print("\n" + "="*60)
