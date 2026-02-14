#!/usr/bin/env python3
"""
Тест различных вариантов запросов к H2H API
"""

import requests
import time

BASE_URL = "https://liberty.top"
ACCESS_TOKEN = "dtpf8uupsbhumevz4pz2jebrqzqmv62o"
MERCHANT_ID = "d5c17c6c-dc40-428a-80e5-2ca01af99f68"

print("=" * 70)
print("🔍 Тест различных вариантов H2H API запросов")
print("=" * 70)

# Вариант 1: Минимальный запрос (только обязательные поля)
print("\n📦 Вариант 1: Минимальный запрос")
print("-" * 70)

payload1 = {
    "external_id": f"TEST_{int(time.time() * 1000)}_1",
    "amount": 1000,
    "merchant_id": MERCHANT_ID
}

headers = {
    'Accept': 'application/json',
    'Access-Token': ACCESS_TOKEN,
    'Content-Type': 'application/json'
}

try:
    response = requests.post(
        f"{BASE_URL}/api/h2h/order",
        json=payload1,
        headers=headers,
        timeout=35
    )
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.text[:500]}")
except Exception as e:
    print(f"Ошибка: {e}")

# Вариант 2: С currency
print("\n📦 Вариант 2: С currency")
print("-" * 70)

payload2 = {
    "external_id": f"TEST_{int(time.time() * 1000)}_2",
    "amount": 1000,
    "merchant_id": MERCHANT_ID,
    "currency": "rub"
}

try:
    response = requests.post(
        f"{BASE_URL}/api/h2h/order",
        json=payload2,
        headers=headers,
        timeout=35
    )
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.text[:500]}")
except Exception as e:
    print(f"Ошибка: {e}")

# Вариант 3: С payment_gateway
print("\n📦 Вариант 3: С payment_gateway")
print("-" * 70)

payload3 = {
    "external_id": f"TEST_{int(time.time() * 1000)}_3",
    "amount": 1000,
    "merchant_id": MERCHANT_ID,
    "payment_gateway": "sberbank"
}

try:
    response = requests.post(
        f"{BASE_URL}/api/h2h/order",
        json=payload3,
        headers=headers,
        timeout=35
    )
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.text[:500]}")
except Exception as e:
    print(f"Ошибка: {e}")

# Вариант 4: С currency + payment_detail_type
print("\n📦 Вариант 4: С currency + payment_detail_type")
print("-" * 70)

payload4 = {
    "external_id": f"TEST_{int(time.time() * 1000)}_4",
    "amount": 1000,
    "merchant_id": MERCHANT_ID,
    "currency": "rub",
    "payment_detail_type": "card"
}

try:
    response = requests.post(
        f"{BASE_URL}/api/h2h/order",
        json=payload4,
        headers=headers,
        timeout=35
    )
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.text[:500]}")
except Exception as e:
    print(f"Ошибка: {e}")

# Вариант 5: Проверяем, может быть нужен другой endpoint
print("\n📦 Вариант 5: Альтернативные endpoints")
print("-" * 70)

alternative_endpoints = [
    "/api/h2h/orders",
    "/api/h2h/create",
    "/h2h/api/order",
    "/merchant/h2h/order"
]

for endpoint in alternative_endpoints:
    try:
        response = requests.post(
            f"{BASE_URL}{endpoint}",
            json=payload2,
            headers=headers,
            timeout=10
        )
        print(f"{endpoint}: {response.status_code}")
        if response.status_code != 404:
            print(f"  Ответ: {response.text[:200]}")
    except Exception as e:
        print(f"{endpoint}: Ошибка - {e}")

print("\n" + "=" * 70)
print("✅ Тест завершен")
print("=" * 70)
