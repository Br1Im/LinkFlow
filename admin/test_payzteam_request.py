#!/usr/bin/env python3
"""
Тестовый запрос к PayzTeam API для проверки структуры ответа
Пробуем разные варианты запросов
"""

import requests
import hashlib
import json

# Конфигурация мерчанта
MERCHANT_ID = "747"
API_KEY = "your_api_key_here"  # Замените на реальный API ключ из "Мой магазин" -> "Ключи"
SECRET_KEY = "your_secret_key_here"  # Замените на реальный секретный ключ

def generate_signature(params, secret_key):
    """Генерация подписи для запроса"""
    sorted_params = sorted(params.items())
    sign_string = ""
    for key, value in sorted_params:
        if value is not None and value != "":
            sign_string += f"{key}={value}&"
    sign_string += secret_key
    signature = hashlib.md5(sign_string.encode('utf-8')).hexdigest()
    return signature

def test_request(url, params, headers, method="POST"):
    """Тестовый запрос"""
    print("=" * 60)
    print(f"ЗАПРОС: {method} {url}")
    print("=" * 60)
    print(f"\nЗаголовки:")
    print(json.dumps(headers, indent=2))
    print(f"\nПараметры:")
    print(json.dumps(params, indent=2, ensure_ascii=False))
    print("\n" + "=" * 60)
    
    try:
        if method == "POST":
            response = requests.post(url, json=params, headers=headers, timeout=30)
        else:
            response = requests.get(url, params=params, headers=headers, timeout=30)
        
        print(f"Статус: {response.status_code}")
        print(f"\nОтвет:")
        try:
            result = response.json()
            print(json.dumps(result, indent=2, ensure_ascii=False))
        except:
            print(response.text)
        print("=" * 60 + "\n")
        return response
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("=" * 60 + "\n")
        return None

# Параметры платежа
params = {
    "merchant_id": MERCHANT_ID,
    "amount": "1000.00",
    "order_id": "TEST_ORDER_12345",
    "currency": "RUB",
    "description": "Тестовый платеж",
}

# Генерируем подпись
signature = generate_signature(params, SECRET_KEY)
params["sign"] = signature

print("\n" + "=" * 60)
print("ТЕСТИРОВАНИЕ PAYZTEAM API")
print("=" * 60)
print(f"Merchant ID: {MERCHANT_ID}\n")

# Вариант 1: Стандартный API с Bearer токеном
print("\n### ВАРИАНТ 1: Стандартный API (Bearer Token) ###\n")
test_request(
    "https://payzteam.com/api/payment/create",
    params,
    {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
)

# Вариант 2: API ключ в параметрах
print("\n### ВАРИАНТ 2: API ключ в параметрах ###\n")
params_with_key = params.copy()
params_with_key["api_key"] = API_KEY
test_request(
    "https://payzteam.com/api/payment/create",
    params_with_key,
    {"Content-Type": "application/json"}
)

# Вариант 3: H2H API endpoint
print("\n### ВАРИАНТ 3: H2H API endpoint ###\n")
test_request(
    "https://payzteam.com/payment-api/create",
    params,
    {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
)

# Вариант 4: Form data вместо JSON
print("\n### ВАРИАНТ 4: Form data (application/x-www-form-urlencoded) ###\n")
try:
    response = requests.post(
        "https://payzteam.com/api/payment/create",
        data=params,
        headers={"Authorization": f"Bearer {API_KEY}"},
        timeout=30
    )
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.text}")
except Exception as e:
    print(f"❌ Ошибка: {e}")

print("\n" + "=" * 60)
print("ЗАВЕРШЕНО")
print("=" * 60)
