#!/usr/bin/env python3
"""
Повторный тест суммы 2501₽ - получим другие реквизиты
"""

import requests
import json

API_URL = "http://85.192.56.74/api/create-payment"

print("Повторный запрос 2501₽...")
print("=" * 60)

response = requests.post(
    API_URL,
    json={"amount": 2501},
    timeout=120
)

result = response.json()
print(json.dumps(result, indent=2, ensure_ascii=False))

if result.get('success'):
    print("\n✅ УСПЕХ!")
    print(f"Карта: {result.get('card_number')}")
    print(f"Владелец: {result.get('card_owner')}")
    print(f"QR: {result.get('qr_link', '')[:80]}...")
else:
    print(f"\n❌ ОШИБКА: {result.get('error')}")
    print(f"Источник реквизитов: {result.get('requisite_source')}")
