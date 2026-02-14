#!/usr/bin/env python3
"""
Тест разных режимов получения реквизитов
"""

import requests
import json
import time

url = "http://85.192.56.74/api/create-payment"

tests = [
    {
        "name": "Режим AUTO (по умолчанию)",
        "payload": {"amount": 300}
    },
    {
        "name": "Режим AUTO (явно указан)",
        "payload": {"amount": 300, "requisite_api": "auto"}
    },
    {
        "name": "Режим H2H (только H2H API)",
        "payload": {"amount": 300, "requisite_api": "h2h"}
    },
    {
        "name": "Режим PayzTeam (только PayzTeam API)",
        "payload": {"amount": 300, "requisite_api": "payzteam"}
    }
]

for i, test in enumerate(tests):
    print("=" * 80)
    print(f"Тест {i+1}: {test['name']}")
    print("=" * 80)
    print(f"Payload: {test['payload']}")
    
    response = requests.post(
        url,
        json=test['payload'],
        headers={"Content-Type": "application/json"},
        timeout=60
    )
    
    print(f"\nStatus: {response.status_code}")
    print("\nОтвет:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    if i < len(tests) - 1:
        print("\n⏳ Пауза 3 секунды...\n")
        time.sleep(3)

print("\n" + "=" * 80)
print("Тестирование завершено")
print("=" * 80)
