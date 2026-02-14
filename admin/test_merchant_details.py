#!/usr/bin/env python3
"""
Тест получения полных деталей заказа через Merchant API
Проверяем, возвращаются ли реквизиты (номер карты, ФИО)
"""

import requests
import time
import json

BASE_URL = "https://liberty.top"
ACCESS_TOKEN = "dtpf8uupsbhumevz4pz2jebrqzqmv62o"
MERCHANT_ID = "d5c17c6c-dc40-428a-80e5-2ca01af99f68"

headers = {
    'Accept': 'application/json',
    'Access-Token': ACCESS_TOKEN,
    'X-Max-Wait-Ms': '30000'
}

print("=" * 70)
print("🔍 Тест получения реквизитов через Merchant API")
print("=" * 70)

# Создаем заказ
external_id = f"TEST_{int(time.time() * 1000)}"

payload = {
    "external_id": external_id,
    "amount": 2000,
    "merchant_id": MERCHANT_ID,
    "currency": "rub",
    "payment_detail_type": "card"
}

print(f"\n📦 Создаем заказ: {external_id}")
print(f"Сумма: 2000 RUB")
print("-" * 70)

try:
    response = requests.post(
        f"{BASE_URL}/api/merchant/order",
        json=payload,
        headers=headers,
        timeout=35
    )
    
    print(f"Статус: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        print("\n✅ ПОЛНЫЙ ОТВЕТ ПРИ СОЗДАНИИ:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        if data.get("success"):
            order_data = data["data"]
            order_id = order_data.get('order_id')
            
            # Проверяем, есть ли payment_detail в ответе
            if 'payment_detail' in order_data:
                print("\n🎉 РЕКВИЗИТЫ НАЙДЕНЫ В ОТВЕТЕ СОЗДАНИЯ!")
                detail = order_data['payment_detail']
                print(f"   Номер карты: {detail.get('detail')}")
                print(f"   ФИО: {detail.get('initials')}")
                print(f"   Тип: {detail.get('detail_type')}")
            else:
                print("\n⚠️ payment_detail НЕ найден в ответе создания")
            
            # Ждем немного, чтобы система обработала заказ
            print(f"\n⏳ Ждем 3 секунды для обработки заказа...")
            time.sleep(3)
            
            # Получаем детали заказа через GET
            print(f"\n📥 Получаем детали заказа: {order_id}")
            print("-" * 70)
            
            detail_response = requests.get(
                f"{BASE_URL}/api/merchant/order/{order_id}",
                headers=headers,
                timeout=10
            )
            
            print(f"Статус: {detail_response.status_code}")
            
            if detail_response.status_code == 200:
                detail_data = detail_response.json()
                
                print("\n✅ ПОЛНЫЙ ОТВЕТ GET ЗАПРОСА:")
                print(json.dumps(detail_data, indent=2, ensure_ascii=False))
                
                if detail_data.get("success"):
                    order_info = detail_data["data"]
                    
                    # Проверяем, есть ли payment_detail в GET ответе
                    if 'payment_detail' in order_info:
                        print("\n🎉 РЕКВИЗИТЫ НАЙДЕНЫ В GET ОТВЕТЕ!")
                        detail = order_info['payment_detail']
                        print(f"   Номер карты: {detail.get('detail')}")
                        print(f"   ФИО: {detail.get('initials')}")
                        print(f"   Тип: {detail.get('detail_type')}")
                    else:
                        print("\n⚠️ payment_detail НЕ найден в GET ответе")
                        print("\n📋 Доступные поля:")
                        for key in order_info.keys():
                            print(f"   - {key}")
            
            # Пробуем получить через external_id
            print(f"\n📥 Получаем через external_id: {external_id}")
            print("-" * 70)
            
            ext_response = requests.get(
                f"{BASE_URL}/api/merchant/order/{MERCHANT_ID}/{external_id}",
                headers=headers,
                timeout=10
            )
            
            print(f"Статус: {ext_response.status_code}")
            
            if ext_response.status_code == 200:
                ext_data = ext_response.json()
                
                if ext_data.get("success"):
                    ext_order = ext_data["data"]
                    
                    if 'payment_detail' in ext_order:
                        print("\n🎉 РЕКВИЗИТЫ НАЙДЕНЫ!")
                        detail = ext_order['payment_detail']
                        print(f"   Номер карты: {detail.get('detail')}")
                        print(f"   ФИО: {detail.get('initials')}")
                    else:
                        print("\n⚠️ payment_detail НЕ найден")
    else:
        print(f"❌ Ошибка: {response.text}")

except Exception as e:
    print(f"❌ Исключение: {e}")

print("\n" + "=" * 70)
print("✅ Тест завершен")
print("=" * 70)
