#!/usr/bin/env python3
"""
Диагностика H2H API - проверка доступности endpoints
"""

import requests

BASE_URL = "https://liberty.top"
ACCESS_TOKEN = "dtpf8uupsbhumevz4pz2jebrqzqmv62o"

headers = {
    'Accept': 'application/json',
    'Access-Token': ACCESS_TOKEN
}

print("=" * 70)
print("🔍 Диагностика H2H API")
print("=" * 70)
print(f"📍 BASE URL: {BASE_URL}")
print(f"🔑 ACCESS TOKEN: {ACCESS_TOKEN[:20]}...")
print("=" * 70)

# Проверяем базовые endpoints
endpoints_to_test = [
    "/api/currencies",
    "/api/payment-gateways",
    "/api/h2h/order",
    "/api/merchant/order"
]

for endpoint in endpoints_to_test:
    url = f"{BASE_URL}{endpoint}"
    print(f"\n🔗 Проверяем: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   ✅ Статус: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   📦 Ответ: {str(data)[:200]}...")
            except:
                print(f"   📦 Ответ (не JSON): {response.text[:200]}...")
        elif response.status_code == 404:
            print(f"   ❌ Endpoint не найден")
        elif response.status_code == 401:
            print(f"   ❌ Ошибка авторизации - проверьте токен")
        elif response.status_code == 405:
            print(f"   ⚠️ Метод не разрешен (возможно нужен POST)")
        else:
            print(f"   ⚠️ Ответ: {response.text[:200]}")
    
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

print("\n" + "=" * 70)
print("✅ Диагностика завершена")
print("=" * 70)
