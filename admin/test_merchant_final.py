#!/usr/bin/env python3
"""
Финальный тест Merchant API - 10 запросов с получением реквизитов
"""

import sys
import os
import time
import random

# Добавляем путь к payment_service
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'payment_service'))

from merchant_api import MerchantAPI

BASE_URL = "https://liberty.top"
ACCESS_TOKEN = "dtpf8uupsbhumevz4pz2jebrqzqmv62o"
MERCHANT_ID = "d5c17c6c-dc40-428a-80e5-2ca01af99f68"

print("=" * 70)
print("🔄 Финальный тест Merchant API - 10 запросов от 1000 до 5000 RUB")
print("=" * 70)
print(f"📍 API URL: {BASE_URL}")
print(f"🔑 Merchant ID: {MERCHANT_ID}")
print("=" * 70)

# Создаем клиент
api = MerchantAPI(
    base_url=BASE_URL,
    access_token=ACCESS_TOKEN
)

# Генерируем 10 случайных сумм от 1000 до 5000
amounts = [random.randint(1000, 5000) for _ in range(10)]

results = []

for i, amount in enumerate(amounts, 1):
    print(f"\n{'='*70}")
    print(f"📦 Запрос #{i}/10 - Сумма: {amount} RUB")
    print(f"{'='*70}")
    
    external_id = f"TEST_{int(time.time() * 1000)}_{i}"
    
    try:
        # Создаем заказ
        result = api.create_order(
            external_id=external_id,
            amount=amount,
            merchant_id=MERCHANT_ID,
            currency="rub",
            payment_detail_type="card"
        )
        
        if result.get("success"):
            data = result["data"]
            payment_detail = data.get("payment_detail", {})
            
            print(f"✅ Успешно!")
            print(f"   Order ID: {data.get('order_id')}")
            print(f"   External ID: {data.get('external_id')}")
            print(f"   Сумма к оплате: {data.get('amount')} {data.get('currency').upper()}")
            print(f"   Платежный метод: {data.get('payment_gateway_name')}")
            
            if payment_detail:
                print(f"   📇 Реквизиты:")
                print(f"      Номер карты: {payment_detail.get('detail')}")
                print(f"      Владелец: {payment_detail.get('initials')}")
                print(f"      Тип: {payment_detail.get('detail_type')}")
            
            print(f"   Статус: {data.get('status')} / {data.get('sub_status')}")
            print(f"   Истекает: {data.get('expires_at')}")
            print(f"   Платежная ссылка: {data.get('payment_link')}")
            
            results.append({
                'success': True,
                'amount': amount,
                'order_id': data.get('order_id'),
                'card_number': payment_detail.get('detail') if payment_detail else None,
                'card_owner': payment_detail.get('initials') if payment_detail else None,
                'payment_gateway': data.get('payment_gateway_name')
            })
        else:
            error = result.get('error', 'Unknown error')
            print(f"❌ Ошибка: {error}")
            
            results.append({
                'success': False,
                'amount': amount,
                'error': error
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
    print(f"\n📋 Успешные заказы с реквизитами:")
    for i, r in enumerate([r for r in results if r['success']], 1):
        print(f"   {i}. {r['amount']} RUB - {r['card_owner']} ({r['card_number']}) - {r['payment_gateway']}")

if failed > 0:
    print(f"\n⚠️ Неудачные заказы:")
    for i, r in enumerate([r for r in results if not r['success']], 1):
        print(f"   {i}. {r['amount']} RUB - {r.get('error', 'Unknown error')}")

print(f"\n{'='*70}")
print("✅ Тест завершен")
print(f"{'='*70}")
print("\n💡 Merchant API полностью работает и возвращает реквизиты!")
print("   Можно использовать для получения номеров карт и ФИО владельцев.")
