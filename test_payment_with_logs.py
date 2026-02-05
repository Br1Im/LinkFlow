#!/usr/bin/env python3
"""
Тест создания платежа через API с проверкой логов
"""
import requests
import time
import json

API_URL = "http://localhost:5001"
ADMIN_URL = "http://localhost:5000"
API_TOKEN = "-3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo"

print("🧪 Тест создания платежа с логами\n")

# 1. Создаем платеж
print("1️⃣ Отправляю запрос на создание платежа...")
payload = {
    "amount": 110,
    "orderId": f"TEST-{int(time.time())}"
}

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# Запускаем в отдельном потоке чтобы можно было читать логи
import threading

result = {}
def create_payment():
    try:
        response = requests.post(
            f"{API_URL}/api/payment",
            json=payload,
            headers=headers,
            timeout=120
        )
        result['response'] = response
        result['data'] = response.json()
    except Exception as e:
        result['error'] = str(e)

thread = threading.Thread(target=create_payment)
thread.start()

print("2️⃣ Ожидаю логи в реальном времени...\n")

# Читаем логи каждую секунду
last_log_count = 0
start_time = time.time()

while thread.is_alive():
    try:
        # Читаем логи из админки
        logs_response = requests.get(f"{ADMIN_URL}/api/payment-logs/current", timeout=1)
        if logs_response.status_code == 200:
            logs_data = logs_response.json()
            logs = logs_data.get('logs', [])
            
            # Показываем новые логи
            if len(logs) > last_log_count:
                for log in logs[last_log_count:]:
                    level_icon = {
                        'info': 'ℹ️',
                        'success': '✅',
                        'error': '❌',
                        'warning': '⚠️',
                        'debug': '🔍'
                    }.get(log['level'], '📝')
                    
                    timestamp = log['timestamp'].split('T')[1][:12] if 'T' in log['timestamp'] else ''
                    print(f"[{timestamp}] {level_icon} {log['message'][:100]}")
                
                last_log_count = len(logs)
    except:
        pass
    
    time.sleep(0.5)
    
    # Таймаут 60 секунд
    if time.time() - start_time > 60:
        print("\n⏱️ Таймаут 60 секунд")
        break

thread.join(timeout=5)

print(f"\n3️⃣ Результат:")
if 'data' in result:
    data = result['data']
    print(f"   Success: {data.get('success')}")
    print(f"   Error: {data.get('error', 'N/A')}")
    print(f"   QR Link: {data.get('qr_link', 'N/A')[:50]}...")
    print(f"   Time: {data.get('payment_time', 0):.2f}s")
    
    logs = data.get('logs', [])
    print(f"\n4️⃣ Логи в ответе API: {len(logs)} шт.")
elif 'error' in result:
    print(f"   ❌ Ошибка: {result['error']}")
else:
    print("   ⏱️ Запрос не завершился")

print("\n✅ Тест завершен")
