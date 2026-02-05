#!/usr/bin/env python3
"""
Тест создания платежа на 500₽ через админ-панель
"""

import requests
import time

ADMIN_URL = 'http://localhost:5000'

def test_payment_500():
    """Тестирует создание платежа на 500₽"""
    print("=" * 70)
    print("ТЕСТ: Создание платежа на 500₽")
    print("=" * 70)
    
    payload = {'amount': 500}
    
    print(f"\n📤 Отправка запроса на создание платежа...")
    print(f"   Сумма: {payload['amount']}₽")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f'{ADMIN_URL}/api/create-payment',
            json=payload,
            timeout=120
        )
        
        elapsed = time.time() - start_time
        
        print(f"\n⏱️  Время выполнения: {elapsed:.2f}s")
        print(f"📊 Статус ответа: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"\n✅ УСПЕХ!")
            print(f"   Order ID: {data.get('order_id')}")
            print(f"   Сумма: {data.get('amount')}₽")
            print(f"   Время генерации: {data.get('generation_time', 0):.2f}s")
            
            if data.get('qr_link'):
                qr_link = data['qr_link']
                print(f"   QR-ссылка: {qr_link[:80]}...")
            
            return True
        else:
            data = response.json()
            print(f"\n❌ ОШИБКА!")
            print(f"   Сообщение: {data.get('error', 'Unknown error')}")
            
            return False
            
    except Exception as e:
        print(f"\n❌ ИСКЛЮЧЕНИЕ: {e}")
        return False


if __name__ == "__main__":
    success = test_payment_500()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ ТЕСТ ПРОЙДЕН")
    else:
        print("❌ ТЕСТ НЕ ПРОЙДЕН")
    print("=" * 70)
