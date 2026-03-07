#!/usr/bin/env python3
"""
INCAS API клиент для получения реквизитов
"""

import requests
import json
import uuid
from datetime import datetime

def get_incas_requisite(amount):
    """
    Получает реквизиты от INCAS API
    
    Args:
        amount: Сумма платежа в рублях
        
    Returns:
        dict: {'card_number': str, 'card_owner': str} или None при ошибке
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
        
        print(f"[INCAS] Запрос реквизитов для суммы {amount} RUB...")
        
        response = requests.put(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            
            if 'object' in data:
                obj = data['object']
                payment_data = obj.get('paymentData', {}).get('object', {})
                
                card_number = payment_data.get('credentials')
                card_owner = payment_data.get('description')
                
                if card_number and card_owner:
                    print(f"[INCAS] ✅ Реквизиты получены: {card_owner} ({card_number})")
                    return {
                        'card_number': card_number,
                        'card_owner': card_owner
                    }
                else:
                    print(f"[INCAS] ❌ Реквизиты не найдены в ответе")
                    return None
            else:
                print(f"[INCAS] ❌ Неверный формат ответа")
                return None
        else:
            print(f"[INCAS] ❌ HTTP {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        print(f"[INCAS] ❌ Таймаут запроса")
        return None
    except requests.exceptions.ConnectionError:
        print(f"[INCAS] ❌ Ошибка соединения")
        return None
    except Exception as e:
        print(f"[INCAS] ❌ Ошибка: {e}")
        return None

if __name__ == "__main__":
    # Тест
    result = get_incas_requisite(1000)
    print("Результат:", result)