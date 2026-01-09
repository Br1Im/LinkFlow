#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест CURL совместимости webhook сервера
"""

import requests
import json
import time
import uuid

# Настройки
SERVER_URL = "http://85.192.56.74:5000"
API_TOKEN = "-3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo"

def test_curl_request():
    """Тест запроса аналогичного curl"""
    
    print("🧪 Тестирование CURL совместимости...")
    print(f"📡 Сервер: {SERVER_URL}")
    print(f"🔑 Токен: {API_TOKEN}")
    
    # Данные для запроса
    order_id = f"curl-test-{int(time.time())}-{uuid.uuid4().hex[:6]}"
    amount = 100
    
    # Заголовки как в curl
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # Данные как в curl
    data = {
        'amount': amount,
        'orderId': order_id
    }
    
    print(f"📋 Order ID: {order_id}")
    print(f"💰 Amount: {amount}")
    print()
    
    try:
        print("⏳ Отправка запроса...")
        start_time = time.time()
        
        response = requests.post(
            f"{SERVER_URL}/api/payment",
            headers=headers,
            json=data,
            timeout=30
        )
        
        elapsed = time.time() - start_time
        
        print(f"⏱️ Время ответа: {elapsed:.3f}s")
        print(f"📊 Статус: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ УСПЕХ!")
            print(f"🆔 Order ID: {result.get('orderId')}")
            print(f"🔗 QRC ID: {result.get('qrcId')}")
            print(f"💳 Ссылка: {result.get('qr')}")
            print(f"⚡ Метод: {result.get('method')}")
            print(f"🚀 CURL совместимый: {result.get('curl_compatible')}")
            
            # Проверяем, что ссылка валидная
            payment_link = result.get('qr', '')
            if 'qr.nspk.ru' in payment_link:
                print("✅ Ссылка NSPK валидная!")
            else:
                print("⚠️ Ссылка не NSPK формата")
                
        else:
            print("❌ ОШИБКА!")
            try:
                error_data = response.json()
                print(f"📄 Ошибка: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"📄 Ответ: {response.text}")
                
    except requests.exceptions.Timeout:
        print("❌ ТАЙМАУТ! Сервер не отвечает")
    except requests.exceptions.ConnectionError:
        print("❌ ОШИБКА СОЕДИНЕНИЯ! Сервер недоступен")
    except Exception as e:
        print(f"❌ НЕОЖИДАННАЯ ОШИБКА: {e}")

def test_health_check():
    """Тест health check"""
    print("\n🏥 Тестирование Health Check...")
    
    try:
        response = requests.get(f"{SERVER_URL}/api/health", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Сервер здоров!")
            print(f"📊 Статус: {result.get('status')}")
            print(f"🔧 Режим: {result.get('mode')}")
            print(f"⚡ Функции: {', '.join(result.get('features', []))}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Health check error: {e}")

if __name__ == "__main__":
    print("🚀 ТЕСТ CURL СОВМЕСТИМОСТИ")
    print("=" * 50)
    
    # Тест health check
    test_health_check()
    
    # Тест создания платежа
    test_curl_request()
    
    print("\n" + "=" * 50)
    print("✅ Тестирование завершено!")