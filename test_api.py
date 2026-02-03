#!/usr/bin/env python3
"""
Тестовый скрипт для проверки API
"""
import requests
import json

API_URL = "http://localhost:5001"
API_TOKEN = "-3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo"

def test_health():
    """Проверка health endpoint"""
    print("🔍 Проверка health endpoint...")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_create_payment():
    """Тест создания платежа"""
    print("💳 Тест создания платежа...")
    
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'amount': 1000,
        'orderId': f'TEST-{int(requests.get(f"{API_URL}/health").elapsed.total_seconds() * 1000)}'
    }
    
    print(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    
    response = requests.post(
        f"{API_URL}/api/payment",
        json=payload,
        headers=headers,
        timeout=120
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

if __name__ == "__main__":
    print("="*60)
    print("🧪 Тестирование LinkFlow API")
    print("="*60)
    print()
    
    try:
        test_health()
        
        choice = input("Создать тестовый платеж? (y/n): ")
        if choice.lower() == 'y':
            test_create_payment()
        
        print("✅ Тесты завершены")
        
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка: Не удается подключиться к API")
        print("   Убедитесь, что сервер запущен (python start_admin.py)")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
