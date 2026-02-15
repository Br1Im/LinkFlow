#!/usr/bin/env python3
"""
Простая проверка: работает ли API вообще
"""

import requests
import json

print("Проверка API сервера на localhost:5001")
print("="*60)

# 1. Health check
print("\n1. Health check:")
try:
    r = requests.get("http://localhost:5001/health", timeout=5)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
except Exception as e:
    print(f"   ❌ ОШИБКА: {e}")
    print("\n   API сервер не запущен!")
    print("   Запустите: cd admin && python api_server.py")
    exit(1)

# 2. Простой запрос
print("\n2. Тестовый запрос на создание платежа (1000₽):")
try:
    r = requests.post(
        "http://localhost:5001/api/create-payment",
        json={"amount": 1000},
        timeout=120
    )
    print(f"   Status: {r.status_code}")
    data = r.json()
    
    if data.get('success'):
        print(f"   ✅ УСПЕХ!")
        print(f"   QR: {data.get('qr_link', 'N/A')[:60]}...")
    else:
        print(f"   ❌ ОШИБКА: {data.get('error')}")
        
    print(f"\n   Полный ответ:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
except Exception as e:
    print(f"   ❌ ИСКЛЮЧЕНИЕ: {e}")

print("\n" + "="*60)
