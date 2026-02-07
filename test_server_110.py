import requests
import json

# Тест на сервере через порт 80 (nginx)
url = "http://85.192.56.74/api/payment"

headers = {
    "Authorization": "Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo",
    "Content-Type": "application/json"
}

data = {
    "amount": 110,
    "orderId": "test_110_external",
    "card_number": "9860080323894719",
    "card_owner": "Nodir Asadullayev"
}

print("=" * 70)
print("ТЕСТ: Создание платежа на 110₽ (через nginx, порт 80)")
print("=" * 70)
print()

print("📤 Отправка запроса...")
print(f"   URL: {url}")
print(f"   Сумма: {data['amount']}₽")
print()

try:
    response = requests.post(url, json=data, headers=headers, timeout=120)
    
    print(f"📊 Статус: {response.status_code}")
    print()
    
    if response.status_code in [200, 201]:
        result = response.json()
        print("✅ УСПЕХ!")
        print(f"   QR-ссылка: {result.get('qr_link', 'НЕТ')}")
        print(f"   Время: {result.get('payment_time', result.get('time', 0)):.2f}s")
        print(f"   Stage 1: {result.get('step1_time', 0):.2f}s")
        print(f"   Stage 2: {result.get('step2_time', 0):.2f}s")
        print()
        
        # Логи
        if 'logs' in result and result['logs']:
            print("📋 Последние 10 логов:")
            for log in result['logs'][-10:]:
                print(f"   {log}")
    else:
        print("❌ ОШИБКА!")
        print(f"   Ответ: {response.text[:500]}")
        
except Exception as e:
    print(f"❌ ИСКЛЮЧЕНИЕ: {e}")

print()
print("=" * 70)
