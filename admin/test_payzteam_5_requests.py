#!/usr/bin/env python3
"""
Отправка 5 запросов в PayzTeam с разными суммами
Суммы: 500, 550, 600, 700, 900 рублей
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'payment_service'))

import json
import time
import requests
import hashlib

# ============================================
# РЕАЛЬНЫЕ CREDENTIALS
# ============================================
MERCHANT_ID = "747"  # KeyGatePay
API_KEY = "f046a50c7e398bc48124437b612ac7ab"
SECRET_KEY = "aa7c2689-98f2-428f-9c03-93e3835c3b1d"
BASE_URL = "https://payzteam.com"

# ============================================
# Суммы для тестирования
# ============================================
AMOUNTS = ["500.00", "550.00", "600.00", "700.00", "900.00"]

def create_payment(amount, index):
    """Создание платежа с указанной суммой"""
    
    uuid = f"TEST_{int(time.time())}_{index}"
    client_email = "test@example.com"
    fiat_currency = "rub"
    payment_method = "nspk"
    language = "ru"
    client_ip = "127.0.0.1"
    is_intrabank_transfer = False
    
    # Генерация подписи
    sign_string = f"{client_email}{uuid}{amount}{fiat_currency}{payment_method}{SECRET_KEY}"
    signature = hashlib.sha1(sign_string.encode('utf-8')).hexdigest()
    
    print(f"\n{'='*80}")
    print(f"📤 ЗАПРОС #{index + 1} - Сумма: {amount} RUB")
    print(f"{'='*80}")
    
    url = f"{BASE_URL}/exchange/create_deal_v2/{MERCHANT_ID}"
    
    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": API_KEY
    }
    
    payload = {
        "client": client_email,
        "amount": amount,
        "fiat_currency": fiat_currency,
        "uuid": uuid,
        "language": language,
        "payment_method": payment_method,
        "is_intrabank_transfer": is_intrabank_transfer,
        "ip": client_ip,
        "sign": signature
    }
    
    print(f"UUID: {uuid}")
    print(f"Сумма: {amount} RUB")
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"\n📥 ОТВЕТ:")
        print(f"Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if result.get("success"):
                print(f"\n✅ Платеж создан успешно!")
                print(f"   ID: {result.get('id')}")
                print(f"   Status: {result.get('status')}")
                return True, result
            else:
                print(f"\n❌ Ошибка: {result.get('message', 'Unknown error')}")
                return False, result
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(response.text)
            return False, None
            
    except Exception as e:
        print(f"\n❌ Ошибка: {str(e)}")
        return False, None

# ============================================
# ОСНОВНОЙ КОД
# ============================================
if __name__ == "__main__":
    print("🚀 Запуск тестирования PayzTeam API")
    print(f"Количество запросов: {len(AMOUNTS)}")
    print(f"Суммы: {', '.join(AMOUNTS)} RUB")
    
    results = []
    
    for i, amount in enumerate(AMOUNTS):
        success, result = create_payment(amount, i)
        results.append({
            "amount": amount,
            "success": success,
            "result": result
        })
        
        # Пауза между запросами
        if i < len(AMOUNTS) - 1:
            print(f"\n⏳ Пауза 2 секунды перед следующим запросом...")
            time.sleep(2)
    
    # ============================================
    # ИТОГОВАЯ СТАТИСТИКА
    # ============================================
    print(f"\n{'='*80}")
    print("📊 ИТОГОВАЯ СТАТИСТИКА")
    print(f"{'='*80}")
    
    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful
    
    print(f"\nВсего запросов: {len(results)}")
    print(f"✅ Успешных: {successful}")
    print(f"❌ Неудачных: {failed}")
    
    print(f"\n{'='*80}")
    print("ДЕТАЛИ:")
    print(f"{'='*80}")
    
    for i, r in enumerate(results):
        status = "✅" if r["success"] else "❌"
        print(f"{status} Запрос #{i+1}: {r['amount']} RUB - {'Успешно' if r['success'] else 'Ошибка'}")
        if r["success"] and r["result"]:
            print(f"   ID: {r['result'].get('id')}")
    
    print(f"\n{'='*80}")
