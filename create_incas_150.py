#!/usr/bin/env python3
"""
Создание реквизитов INCAS на сумму 150 рублей
"""
import requests
import json
import uuid
from datetime import datetime

def create_incas_150():
    # INCAS API конфигурация
    API_URL = "https://gate.incas.world/v1"
    BEARER_TOKEN = "atFC7Ia7YJTwrMJ0sqHvlnr34"
    
    amount = 150
    
    # Генерируем уникальные ID
    payment_id = f"payment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    order_id = f"order_{uuid.uuid4().hex[:16]}"

    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }

    # Данные запроса для получения реквизитов P2P карты
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
            "type": "p2psbp",
            "object": {}
        }
    }

    url = f"{API_URL}/payments/{payment_id}"
    
    print("💳 Создание реквизитов INCAS на 150 рублей")
    print(f"🔑 Токен: {BEARER_TOKEN}")
    print(f"💰 Сумма: {amount} RUB")
    print(f"📤 PUT {url}")
    print(f"🆔 Order ID: {order_id}")
    print("="*60)

    try:
        response = requests.put(url, headers=headers, json=payload, timeout=30)
        
        print(f"📥 HTTP Status: {response.status_code}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            data = response.json()
            print("📄 Response:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if response.status_code == 200 and 'object' in data:
                obj = data['object']
                payment_data = obj.get('paymentData', {}).get('object', {})
                
                card_number = payment_data.get('credentials')
                card_owner = payment_data.get('description')
                bank = payment_data.get('bank')
                
                print("\n✅ УСПЕХ! Реквизиты созданы:")
                print(f"💳 Карта: {card_number}")
                print(f"👤 Владелец: {card_owner}")
                print(f"🏦 Банк: {bank}")
                print(f"💰 Сумма: {amount} RUB")
                print(f"🆔 Payment ID: {payment_id}")
                print(f"🆔 Order ID: {order_id}")
                
                return {
                    'success': True,
                    'card_number': card_number,
                    'card_owner': card_owner,
                    'bank': bank,
                    'amount': amount,
                    'payment_id': payment_id,
                    'order_id': order_id
                }
                
            else:
                print("\n❌ Ошибка или реквизиты не получены")
                return {'success': False, 'error': 'No requisites received'}
        else:
            print(f"Raw response: {response.text}")
            return {'success': False, 'error': 'Invalid response format'}
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return {'success': False, 'error': str(e)}

if __name__ == "__main__":
    print("🚀 Запуск создания реквизитов INCAS на 150 рублей...")
    result = create_incas_150()
    
    print("\n" + "="*60)
    if result['success']:
        print("🎉 РЕКВИЗИТЫ УСПЕШНО СОЗДАНЫ!")
        print("Готовы к использованию для оплаты 150 рублей.")
    else:
        print("💥 ОШИБКА СОЗДАНИЯ РЕКВИЗИТОВ!")
        print(f"Причина: {result.get('error', 'Unknown error')}")