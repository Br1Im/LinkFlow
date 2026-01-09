#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест curl запроса с вашего ПК
"""

import requests
import json
import time
import uuid

# Настройки
SERVER_URL = "http://85.192.56.74:5000"
API_TOKEN = "-3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo"

def test_curl_from_pc():
    """Тест curl запроса с ПК"""
    
    print("🧪 ТЕСТ CURL ЗАПРОСА С ВАШЕГО ПК")
    print("=" * 50)
    print(f"📡 Сервер: {SERVER_URL}")
    print(f"🔑 Токен: {API_TOKEN}")
    
    # Данные для запроса
    order_id = f"pc-curl-test-{int(time.time())}-{uuid.uuid4().hex[:6]}"
    amount = 100
    
    # Заголовки как в curl
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json',
        'User-Agent': 'curl/7.68.0'  # Имитируем curl
    }
    
    # Данные как в curl
    data = {
        'amount': amount,
        'orderId': order_id
    }
    
    print(f"📋 Order ID: {order_id}")
    print(f"💰 Amount: {amount}")
    print(f"🤖 User-Agent: {headers['User-Agent']}")
    print()
    
    try:
        print("⏳ Отправка curl запроса...")
        start_time = time.time()
        
        response = requests.post(
            f"{SERVER_URL}/api/payment",
            headers=headers,
            json=data,
            timeout=60  # Увеличиваем таймаут для браузера
        )
        
        elapsed = time.time() - start_time
        
        print(f"⏱️ Время ответа: {elapsed:.3f}s")
        print(f"📊 HTTP статус: {response.status_code}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            print("✅ CURL ЗАПРОС УСПЕШЕН!")
            print(f"🆔 Order ID: {result.get('orderId')}")
            print(f"🔗 QRC ID: {result.get('qrcId')}")
            
            payment_link = result.get('qr', '')
            if payment_link:
                print(f"💳 Ссылка для оплаты: {payment_link}")
                
                # Проверяем, что ссылка валидная
                if 'qr.nspk.ru' in payment_link:
                    print("✅ Ссылка NSPK валидная!")
                else:
                    print("⚠️ Ссылка не NSPK формата")
            else:
                print("❌ Ссылка для оплаты НЕ СОЗДАНА")
                
            print(f"⚡ Метод: {result.get('method')}")
            print(f"🚀 CURL совместимый: {result.get('curl_fixed')}")
            
        else:
            print("❌ CURL ЗАПРОС НЕ УДАЛСЯ!")
            try:
                error_data = response.json()
                print(f"📄 Ошибка: {error_data.get('error', 'Unknown error')}")
                print(f"📄 Полный ответ:")
                print(json.dumps(error_data, indent=2, ensure_ascii=False))
            except:
                print(f"📄 Ответ: {response.text}")
                
    except requests.exceptions.Timeout:
        print("❌ ТАЙМАУТ! Сервер не отвечает (браузер долго запускается)")
    except requests.exceptions.ConnectionError:
        print("❌ ОШИБКА СОЕДИНЕНИЯ! Сервер недоступен")
    except Exception as e:
        print(f"❌ НЕОЖИДАННАЯ ОШИБКА: {e}")

if __name__ == "__main__":
    test_curl_from_pc()