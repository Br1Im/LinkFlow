#!/usr/bin/env python3
"""
Тест H2H API с конкретными суммами: 2000, 2100, 2150, 2200, 2350
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

print("="*70)
print("ТЕСТ H2H API - КОНКРЕТНЫЕ СУММЫ")
print("="*70)
print(f"Base URL: {config['base_url']}")
print(f"Merchant ID: {config['merchant_id']}")
print("="*70)

amounts = [2000, 2100, 2150, 2200, 2350]

results = []

for amount in amounts:
    print(f"\n{'='*70}")
    print(f"Сумма: {amount} RUB")
    print(f"{'='*70}")
    
    result = api.create_order(
        external_id=f"TEST_{amount}_{int(time.time())}",
        amount=amount,
        merchant_id=config['merchant_id'],
        currency="rub",
        payment_detail_type="card"
    )
    
    if result.get("success"):
        data = result["data"]
        payment_detail = data.get("payment_detail", {})
        
        print(f"✅ УСПЕХ!")
        print(f"  Order ID: {data.get('order_id')}")
        print(f"  Карта: {payment_detail.get('detail')}")
        print(f"  Владелец: {payment_detail.get('initials')}")
        print(f"  Банк: {payment_detail.get('bank', 'N/A')}")
        print(f"  Gateway: {data.get('payment_gateway_name')} ({data.get('payment_gateway')})")
        print(f"  Истекает: {data.get('expires_at')}")
        
        results.append({
            "amount": amount,
            "success": True,
            "card": payment_detail.get('detail'),
            "owner": payment_detail.get('initials'),
            "order_id": data.get('order_id')
        })
    else:
        error_msg = result.get('details', {}).get('message', result.get('error', 'Unknown error'))
        print(f"❌ ОШИБКА: {error_msg}")
        
        results.append({
            "amount": amount,
            "success": False,
            "error": error_msg
        })
    
    # Небольшая пауза между запросами
    time.sleep(1)

# Итоговая сводка
print(f"\n{'='*70}")
print("ИТОГОВАЯ СВОДКА")
print(f"{'='*70}")

success_count = sum(1 for r in results if r['success'])
fail_count = len(results) - success_count

print(f"\nУспешно: {success_count}/{len(results)}")
print(f"Ошибок: {fail_count}/{len(results)}")

print(f"\nДетали:")
for r in results:
    status = "✅" if r['success'] else "❌"
    if r['success']:
        print(f"  {status} {r['amount']} RUB → {r['owner']} ({r['card']})")
    else:
        print(f"  {status} {r['amount']} RUB → {r['error']}")

print(f"\n{'='*70}")
