#!/usr/bin/env python3
"""
Тест H2H API с разными параметрами
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
print("ТЕСТ H2H API - РАЗНЫЕ ВАРИАНТЫ")
print("="*60)

# Вариант 1: Минимальный запрос (только обязательные поля)
print("\n1. Минимальный запрос:")
result1 = api.create_order(
    external_id=f"TEST1_{int(time.time())}",
    amount=2500,
    merchant_id=config['merchant_id'],
    currency="rub",
    payment_detail_type="card"
)
print(json.dumps(result1, indent=2, ensure_ascii=False))

# Вариант 2: С client_id
print("\n2. С client_id:")
result2 = api.create_order(
    external_id=f"TEST2_{int(time.time())}",
    amount=2500,
    merchant_id=config['merchant_id'],
    currency="rub",
    payment_detail_type="card",
    client_id="test-client-123"
)
print(json.dumps(result2, indent=2, ensure_ascii=False))

# Вариант 3: С payer_bank
print("\n3. С payer_bank:")
result3 = api.create_order(
    external_id=f"TEST3_{int(time.time())}",
    amount=2500,
    merchant_id=config['merchant_id'],
    currency="rub",
    payment_detail_type="card",
    payer_bank="sberbank"
)
print(json.dumps(result3, indent=2, ensure_ascii=False))

# Вариант 4: Без payment_detail_type
print("\n4. Без payment_detail_type:")
result4 = api.create_order(
    external_id=f"TEST4_{int(time.time())}",
    amount=2500,
    merchant_id=config['merchant_id'],
    currency="rub"
)
print(json.dumps(result4, indent=2, ensure_ascii=False))

print("\n" + "="*60)
