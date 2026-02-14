#!/usr/bin/env python3
"""
Тест суммы 2501₽ через PayzTeam API
"""

import requests
import json

API_URL = "http://85.192.56.74/api/create-payment"

print("Запрос 2501₽ через PayzTeam API...")
print("=" * 60)

response = requests.post(
    API_URL,
    json={
        "amount": 2501,
        "requisite_api": "payzteam"  # Принудительно используем PayzTeam
    },
    timeout=120
)

result = response.json()
print(json.dumps(result, indent=2, ensure_ascii=False))

if result.get('success'):
    print("\n✅ УСПЕХ!")
    print(f"Карта: {result.get('card_number')}")
    print(f"Владелец: {result.get('card_owner')}")
    print(f"Источник: {result.get('requisite_source')}")
    print(f"QR: {result.get('qr_link', '')[:80]}...")
else:
    print(f"\n❌ ОШИБКА: {result.get('error')}")
    print(f"Источник реквизитов: {result.get('requisite_source')}")
