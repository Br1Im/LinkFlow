# -*- coding: utf-8 -*-
"""
Тестирование webhook API
"""

import requests
import json
import time
from webhook_config import API_TOKEN, SERVER_URL

def test_create_payment():
    """Тест создания платежа"""
    print("🧪 Тестирование создания платежа...")
    
    url = f"{SERVER_URL}/api/payment"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "amount": 1000,
        "orderId": f"test-order-{int(time.time())}"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"📊 Статус: {response.status_code}")
        print(f"📄 Ответ: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Успех!")
            print(f"🆔 Order ID: {result.get('orderId')}")
            print(f"🔗 QR Link: {result.get('qr')}")
            return result.get('orderId')
        else:
            print(f"❌ Ошибка: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Исключение: {e}")
        return None

def test_get_status(order_id):
    """Тест получения статуса"""
    if not order_id:
        return
        
    print(f"\n🧪 Тестирование получения статуса для {order_id}...")
    
    url = f"{SERVER_URL}/api/status/{order_id}"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"📊 Статус: {response.status_code}")
        print(f"📄 Ответ: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Успех!")
            print(f"🆔 Order ID: {result.get('orderId')}")
            print(f"📊 Status: {result.get('status')}")
            print(f"💰 Amount: {result.get('amount')}")
        else:
            print(f"❌ Ошибка: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Исключение: {e}")

def test_health():
    """Тест health check"""
    print("\n🧪 Тестирование health check...")
    
    url = f"{SERVER_URL}/api/health"
    
    try:
        response = requests.get(url, timeout=10)
        
        print(f"📊 Статус: {response.status_code}")
        print(f"📄 Ответ: {response.text}")
        
        if response.status_code == 200:
            print(f"✅ Сервер работает!")
        else:
            print(f"❌ Ошибка: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Исключение: {e}")

def test_unauthorized():
    """Тест неавторизованного запроса"""
    print("\n🧪 Тестирование неавторизованного запроса...")
    
    url = f"{SERVER_URL}/api/payment"
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "amount": 1000,
        "orderId": "test-unauthorized"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        print(f"📊 Статус: {response.status_code}")
        print(f"📄 Ответ: {response.text}")
        
        if response.status_code == 401:
            print(f"✅ Авторизация работает корректно!")
        else:
            print(f"❌ Неожиданный статус: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Исключение: {e}")

if __name__ == "__main__":
    print("="*60)
    print("🧪 ТЕСТИРОВАНИЕ WEBHOOK API")
    print("="*60)
    print(f"🌐 Server URL: {SERVER_URL}")
    print(f"🔑 Token: {API_TOKEN[:20]}...")
    print("="*60)
    
    # Тест health check
    test_health()
    
    # Тест неавторизованного запроса
    test_unauthorized()
    
    # Тест создания платежа
    order_id = test_create_payment()
    
    # Тест получения статуса
    test_get_status(order_id)
    
    print("\n" + "="*60)
    print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("="*60)