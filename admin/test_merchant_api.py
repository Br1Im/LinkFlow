#!/usr/bin/env python3
"""
Тест Merchant API - альтернатива H2H API
"""

import requests
import time
import random

BASE_URL = "https://liberty.top"
ACCESS_TOKEN = "dtpf8uupsbhumevz4pz2jebrqzqmv62o"
MERCHANT_ID = "d5c17c6c-dc40-428a-80e5-2ca01af99f68"

headers = {
    'Accept': 'application/json',
    'Access-Token': ACCESS_TOKEN,
    'X-Max-Wait-Ms': '30000'
}

print("=" * 70)
print("🔄 Тест Merchant API - 10 запросов от 1000 до 5000 RUB")
print("=" * 70)
print(f"📍 API URL: {BASE_URL}")
print(f"🔑 Merchant ID: {MERCHANT_ID}")
print("=" * 70)

# Генерируем 10 случайных сумм от 1000 до 5000
amounts = [random.randint(1000, 5000) for _ in range(10)]

results = []

for i, amount in enumerate(amounts, 1):
    print(f"\n{'='*70}")
    print(f"📦 Запрос #{i}/10 - Сумма: {amount} RUB")
    print(f"{'='*70}")
    
    external_id = f"TEST_{int(time.time() * 1000)}_{i}"
    
    payload = {
        "external_id": external_id,
        "amount": amount,
        "merchant_id": MERCHANT_ID,
        "currency": "rub",
        "payment_detail_type": "card"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/merchant/order",
            json=payload,
            headers=headers,
            timeout=35
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("success"):
                order_data = data["data"]
                
                print(f"✅ Успешно!")
                print(f"   Order ID: {order_data.get('order_id')}")
                print(f"   External ID: {order_data.get('external_id')}")
                print(f"   Сумма к оплате: {order_data.get('amount')} {order_data.get('currency').upper()}")
                print(f"   Платежный метод: {order_data.get('payment_gateway_name')}")
                print(f"   Статус: {order_data.get('status')} / {order_data.get('sub_status')}")
                print(f"   Истекает: {order_data.get('expires_at')}")
                print(f"   Платежная ссылка: {order_data.get('payment_link')}")
                
                # Получаем детали через GET запрос
                order_id = order_data.get('order_id')
                detail_response = requests.get(
                    f"{BASE_URL}/api/merchant/order/{order_id}",
                    headers=headers,
                    timeout=10
                )
                
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    if detail_data.get("success"):
                        print(f"   📇 Детали заказа получены")
                
                results.append({
                    'success': True,
                    'amount': amount,
                    'order_id': order_data.get('order_id'),
                    'payment_gateway': order_data.get('payment_gateway_name')
                })
            else:
                error = data.get('message', 'Unknown error')
                print(f"❌ Ошибка: {error}")
                results.append({
                    'success': False,
                    'amount': amount,
                    'error': error
                })
        else:
            print(f"❌ HTTP {response.status_code}: {response.text[:200]}")
            results.append({
                'success': False,
                'amount': amount,
                'error': f"HTTP {response.status_code}"
            })
    
    except Exception as e:
        print(f"❌ Исключение: {e}")
        results.append({
            'success': False,
            'amount': amount,
            'error': str(e)
        })
    
    # Небольшая задержка между запросами
    if i < 10:
        time.sleep(0.5)

# Итоговая статистика
print(f"\n{'='*70}")
print("📊 ИТОГОВАЯ СТАТИСТИКА")
print(f"{'='*70}")

successful = sum(1 for r in results if r['success'])
failed = len(results) - successful

print(f"✅ Успешных запросов: {successful}/10")
print(f"❌ Неудачных запросов: {failed}/10")

if successful > 0:
    print(f"\n📋 Успешные заказы:")
    for i, r in enumerate([r for r in results if r['success']], 1):
        print(f"   {i}. {r['amount']} RUB - {r['payment_gateway']}")

if failed > 0:
    print(f"\n⚠️ Неудачные заказы:")
    for i, r in enumerate([r for r in results if not r['success']], 1):
        print(f"   {i}. {r['amount']} RUB - {r.get('error', 'Unknown error')}")

print(f"\n{'='*70}")
print("✅ Тест завершен")
print(f"{'='*70}")
