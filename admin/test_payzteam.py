#!/usr/bin/env python3
"""
Тестовый скрипт для проверки PayzTeam API
Запуск: python admin/test_payzteam.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'payment_service'))

import json
import time
import requests
import hashlib

# ============================================
# РЕАЛЬНЫЕ CREDENTIALS
# ============================================
MERCHANT_ID = "747"  # KeyGatePay
API_KEY = "f046a50c7e398bc48124437b612ac7ab"  # API ключ
SECRET_KEY = "aa7c2689-98f2-428f-9c03-93e3835c3b1d"  # Секретный ключ
BASE_URL = "https://payzteam.com"

# ============================================
# Параметры платежа
# ============================================
uuid = f"TEST_{int(time.time())}"
amount = "500.00"
client_email = "test@example.com"
fiat_currency = "rub"
payment_method = "nspk"
language = "ru"
client_ip = "127.0.0.1"
is_intrabank_transfer = False

# ============================================
# Генерация подписи
# ============================================
sign_string = f"{client_email}{uuid}{amount}{fiat_currency}{payment_method}{SECRET_KEY}"
signature = hashlib.sha1(sign_string.encode('utf-8')).hexdigest()

print("=" * 80)
print("🔌 PayzTeam API - ПОЛНЫЙ ДАМП ЗАПРОСА")
print("=" * 80)

# ============================================
# ЗАПРОС
# ============================================
print("\n📤 REQUEST:")
print("-" * 80)

url = f"{BASE_URL}/exchange/create_deal_v2/{MERCHANT_ID}"
print(f"URL: {url}")
print(f"Method: POST")

headers = {
    "Content-Type": "application/json",
    "X-Api-Key": API_KEY
}

print("\nHeaders:")
print(json.dumps(headers, indent=2))

payload = {
    "client": client_email,
    "amount": amount,
    "fiat_currency": fiat_currency,
    "uuid": uuid,
    "language": language,
    "payment_method": payment_method,
    "is_intrabank_transfer": is_intrabank_transfer,
    "ip": client_ip,
    "sign": signature
}

print("\nBody (JSON):")
print(json.dumps(payload, indent=2, ensure_ascii=False))

print("\nПодпись (sign):")
print(f"  Строка для подписи: {sign_string}")
print(f"  SHA1: {signature}")

# ============================================
# ОТПРАВКА ЗАПРОСА
# ============================================
print("\n" + "=" * 80)
print("📡 Отправка запроса...")
print("=" * 80)

try:
    response = requests.post(
        url,
        json=payload,
        headers=headers,
        timeout=30
    )
    
    # ============================================
    # ОТВЕТ
    # ============================================
    print("\n📥 RESPONSE:")
    print("-" * 80)
    print(f"Status Code: {response.status_code}")
    print(f"Status Text: {response.reason}")
    
    print("\nResponse Headers:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")
    
    print("\nResponse Body:")
    try:
        response_json = response.json()
        print(json.dumps(response_json, indent=2, ensure_ascii=False))
    except:
        print(response.text)
    
    print("\n" + "=" * 80)
    
    # ============================================
    # АНАЛИЗ ОТВЕТА
    # ============================================
    if response.status_code == 200 or response.status_code == 201:
        result = response.json()
        if result.get("success"):
            print("✅ Платеж создан успешно!")
            print(f"   ID: {result.get('id')}")
            print(f"   Status: {result.get('status')}")
            
            if "paymentInfo" in result:
                print("\n💳 Информация для оплаты:")
                print(json.dumps(result["paymentInfo"], indent=2, ensure_ascii=False))
        else:
            print(f"❌ Ошибка: {result.get('message', 'Unknown error')}")
    else:
        print(f"❌ HTTP Error: {response.status_code} {response.reason}")
    
except requests.exceptions.RequestException as e:
    print(f"\n❌ Request Exception: {str(e)}")
except Exception as e:
    print(f"\n❌ Error: {str(e)}")

print("\n" + "=" * 80)
