#!/usr/bin/env python3
"""
Тест API сервера напрямую с хоста
Проверяет оба эндпоинта и все режимы requisite_api
"""

import requests
import json
import time

# Тестируем локально на сервере
API_BASE = "http://localhost:5001"

def test_endpoint(endpoint, payload, description):
    """Тестирует один эндпоинт"""
    print(f"\n{'='*60}")
    print(f"ТЕСТ: {description}")
    print(f"Эндпоинт: {endpoint}")
    print(f"Payload: {json.dumps(payload, ensure_ascii=False)}")
    print(f"{'='*60}")
    
    try:
        start = time.time()
        response = requests.post(
            f"{API_BASE}{endpoint}",
            json=payload,
            timeout=120
        )
        elapsed = time.time() - start
        
        print(f"\nStatus: {response.status_code}")
        print(f"Time: {elapsed:.2f}s")
        print(f"\nResponse:")
        
        try:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if data.get('success'):
                print(f"\n✅ УСПЕХ!")
                print(f"QR: {data.get('qr_link', 'N/A')[:80]}...")
                print(f"Карта: {data.get('card_number', 'N/A')}")
                print(f"Владелец: {data.get('card_owner', 'N/A')}")
                print(f"Источник: {data.get('requisite_source', 'N/A')}")
            else:
                print(f"\n❌ ОШИБКА: {data.get('error', 'Unknown')}")
                if 'card_number' in data:
                    print(f"Карта: {data.get('card_number', 'N/A')}")
                    print(f"Владелец: {data.get('card_owner', 'N/A')}")
                if 'logs' in data:
                    print(f"\nЛоги ({len(data['logs'])}):")
                    for log in data['logs'][-5:]:
                        print(f"  [{log.get('level', 'info')}] {log.get('message', '')}")
        except:
            print(response.text[:500])
            
    except requests.exceptions.Timeout:
        print(f"\n⏱️ ТАЙМАУТ после 120 секунд")
    except Exception as e:
        print(f"\n❌ ИСКЛЮЧЕНИЕ: {e}")


def main():
    print("="*60)
    print("ТЕСТИРОВАНИЕ API СЕРВЕРА")
    print("="*60)
    
    # Проверяем health
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        print(f"\nHealth check: {response.json()}")
    except Exception as e:
        print(f"\n❌ Health check failed: {e}")
        print("API сервер не запущен или недоступен!")
        return
    
    # Тест 1: /api/payment с auto режимом
    test_endpoint(
        "/api/payment",
        {"amount": 1100},
        "Эндпоинт /api/payment, auto режим (по умолчанию)"
    )
    
    time.sleep(2)
    
    # Тест 2: /api/create-payment с auto режимом
    test_endpoint(
        "/api/create-payment",
        {"amount": 1200},
        "Эндпоинт /api/create-payment, auto режим (по умолчанию)"
    )
    
    time.sleep(2)
    
    # Тест 3: /api/create-payment с h2h режимом
    test_endpoint(
        "/api/create-payment",
        {"amount": 1300, "requisite_api": "h2h"},
        "Эндпоинт /api/create-payment, только H2H API"
    )
    
    time.sleep(2)
    
    # Тест 4: /api/create-payment с payzteam режимом
    test_endpoint(
        "/api/create-payment",
        {"amount": 1400, "requisite_api": "payzteam"},
        "Эндпоинт /api/create-payment, только PayzTeam API"
    )
    
    print(f"\n{'='*60}")
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
