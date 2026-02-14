#!/usr/bin/env python3
"""
Тест изменения источника реквизитов
"""

import requests
import json

# Тест 1: Получить текущий источник
print("="*60)
print("Тест 1: Получить текущий источник")
print("="*60)

response = requests.get("http://localhost:5001/api/requisite-source")
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# Тест 2: Изменить источник на 'payzteam'
print("\n" + "="*60)
print("Тест 2: Изменить источник на 'payzteam'")
print("="*60)

response = requests.post(
    "http://localhost:5001/api/requisite-source",
    json={"source": "payzteam"},
    headers={
        "Authorization": "Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo"
    }
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# Тест 3: Проверить что изменилось
print("\n" + "="*60)
print("Тест 3: Проверить что изменилось")
print("="*60)

response = requests.get("http://localhost:5001/api/requisite-source")
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# Тест 4: Вернуть обратно на 'auto'
print("\n" + "="*60)
print("Тест 4: Вернуть обратно на 'auto'")
print("="*60)

response = requests.post(
    "http://localhost:5001/api/requisite-source",
    json={"source": "auto"},
    headers={
        "Authorization": "Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo"
    }
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
