#!/usr/bin/env python3
"""
Простой тест H2H API - один запрос с детальной информацией
"""

import requests
import json

BASE_URL = "https://api.liberty.top"
ACCESS_TOKEN = "dtpf8uupsbhumevz4pz2jebrqzqmv62o"
MERCHANT_ID = "d5c17c6c-dc40-428a-80e5-2ca01af99f68"

print("=" * 70)
print("🔍 Тест H2H API")
print("=" * 70)
print(f"URL: {BASE_URL}/api/h2h/order")
print(f"Merchant ID: {MERCHANT_ID}")
print("=" * 70)

headers = {
    'Accept': 'application/json',
    'Access-Token': ACCESS_TOKEN,
    'Content-Type': 'application/json',
    'X-Max-Wait-Ms': '30000'
}

payload = {
    "external_id": "TEST_H2H_001",
    "amount": 1000,
    "merchant_id": MERCHANT_ID,
    "currency": "rub",
    "payment_detail_type": "card"
}

print("\n📤 Отправляем запрос:")
print(json.dumps(payload, indent=2, ensure_ascii=False))
print("\n📋 Заголовки:")
for key, value in headers.items():
    if key == 'Access-Token':
        print(f"   {key}: {value[:20]}...")
    else:
        print(f"   {key}: {value}")

try:
    response = requests.post(
        f"{BASE_URL}/api/h2h/order",
        json=payload,
        headers=headers,
        timeout=35
    )
    
    print(f"\n📥 Ответ сервера:")
    print(f"   Статус: {response.status_code}")
    print(f"   Заголовки ответа: {dict(response.headers)}")
    
    print(f"\n📄 Тело ответа:")
    try:
        response_json = response.json()
        print(json.dumps(response_json, indent=2, ensure_ascii=False))
    except:
        print(response.text)
    
    if response.status_code == 404:
        print("\n" + "=" * 70)
        print("❌ ОШИБКА 404: Endpoint не найден")
        print("=" * 70)
        print("\n💡 Возможные причины:")
        print("   1. У вашего мерчанта нет доступа к H2H API")
        print("   2. H2H API требует активации от администратора")
        print("   3. Неправильный URL (но документация указывает именно этот)")
        print("\n📧 Что делать:")
        print("   Свяжитесь с администратором Liberty.top:")
        print(f"   - Merchant ID: {MERCHANT_ID}")
        print("   - Запрос: Активировать доступ к H2H API")
        print("   - Endpoint: POST /api/h2h/order")
    
    elif response.status_code == 401:
        print("\n❌ ОШИБКА 401: Проблема с авторизацией")
        print("   Проверьте Access-Token")
    
    elif response.status_code == 422:
        print("\n❌ ОШИБКА 422: Ошибка валидации")
        print("   Проверьте параметры запроса")
    
    elif response.status_code == 200:
        print("\n✅ УСПЕХ! H2H API работает!")

except Exception as e:
    print(f"\n❌ Исключение: {e}")

print("\n" + "=" * 70)
