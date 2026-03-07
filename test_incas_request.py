#!/usr/bin/env python3
"""
Тест запроса к INCAS для получения номера карты и имени владельца
"""

import requests
import json
import uuid
from datetime import datetime

def get_incas_card_data(amount=1000):
    """
    Получает данные карты от INCAS API
    """
    try:
        # INCAS API конфигурация
        API_URL = "https://gate.incas.world/v1"
        BEARER_TOKEN = "axLhH837yWpg3lzfs3tShn3KV"
        
        # Генерируем уникальные ID
        payment_id = f"payment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        order_id = f"order_{uuid.uuid4().hex[:16]}"

        headers = {
            "Authorization": f"Bearer {BEARER_TOKEN}",
            "Content-Type": "application/json"
        }

        # Данные запроса
        payload = {
            "orderId": order_id,
            "description": f"Payment {amount} RUB",
            "autoConfirm": False,
            "returnUrl": "https://your-site.com/return",
            "callbackUrl": "https://webhook.site/unique-url",
            "customer": {
                "ip": "123.123.123.123",
                "email": "test@example.com",
                "fullName": "Test User",
                "phone": "79001234567"
            },
            "amount": {
                "value": f"{amount:.2f}",
                "currency": "RUB"
            },
            "paymentData": {
                "type": "p2pcard",
                "object": {}
            }
        }

        url = f"{API_URL}/payments/{payment_id}"
        
        print(f"🔄 Отправляю запрос к INCAS...")
        print(f"📤 URL: {url}")
        print(f"💰 Сумма: {amount} RUB")
        print("="*60)
        
        response = requests.put(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )

        print(f"📥 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("📄 Полный ответ:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if 'object' in data:
                obj = data['object']
                payment_data = obj.get('paymentData', {}).get('object', {})
                
                card_number = payment_data.get('credentials')
                card_owner = payment_data.get('description')
                
                print("\n" + "="*60)
                if card_number and card_owner:
                    print("✅ ДАННЫЕ КАРТЫ ПОЛУЧЕНЫ:")
                    print(f"💳 Номер карты: {card_number}")
                    print(f"👤 Владелец: {card_owner}")
                    return {
                        'card_number': card_number,
                        'card_owner': card_owner
                    }
                else:
                    print("❌ Данные карты не найдены в ответе")
                    print(f"   credentials: {payment_data.get('credentials')}")
                    print(f"   description: {payment_data.get('description')}")
                    return None
            else:
                print("❌ Поле 'object' не найдено в ответе")
                return None
        else:
            print(f"❌ Ошибка HTTP {response.status_code}")
            print(f"📄 Response: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ Таймаут запроса (30 сек)")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка соединения с INCAS")
        return None
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return None

if __name__ == "__main__":
    result = get_incas_card_data(150)
    if result:
        print(f"\n🎉 Успешно получены данные карты!")
    else:
        print(f"\n💥 Не удалось получить данные карты")