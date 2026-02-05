#!/usr/bin/env python3
"""
Финальный тест создания платежа с логами
"""
import requests
import time

API_URL = "http://localhost:5001"
ADMIN_URL = "http://localhost:5000"
API_TOKEN = "-3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo"

print("🧪 Финальный тест создания платежа\n")

# Создаем платеж с указанием реквизитов
print("1️⃣ Отправляю запрос на создание платежа...")
payload = {
    "amount": 110,
    "orderId": f"TEST-{int(time.time())}",
    "card_number": "9860080323894719",
    "card_owner": "Nodir Asadullayev"
}

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# Запускаем в отдельном потоке
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

print("2️⃣ Читаю логи в реальном времени...\n")

# Читаем логи
last_log_count = 0
start_time = time.time()

while thread.is_alive():
    try:
        logs_response = requests.get(f"{ADMIN_URL}/api/payment-logs/current", timeout=1)
        if logs_response.status_code == 200:
            logs_data = logs_response.json()
            logs = logs_data.get('logs', [])
            
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
                    message = log['message'][:120]
                    print(f"[{timestamp}] {level_icon} {message}")
                
                last_log_count = len(logs)
    except:
        pass
    
    time.sleep(0.5)
    
    if time.time() - start_time > 60:
        print("\n⏱️ Таймаут 60 секунд")
        break

thread.join(timeout=5)

print(f"\n3️⃣ Результат:")
if 'data' in result:
    data = result['data']
    print(f"   Success: {data.get('success')}")
    if not data.get('success'):
        print(f"   Error: {data.get('error', 'N/A')}")
    else:
        print(f"   QR Link: {data.get('qr_link', 'N/A')[:60]}...")
    print(f"   Time: {data.get('payment_time', 0):.2f}s")
    
    logs = data.get('logs', [])
    print(f"\n4️⃣ Всего логов: {len(logs)}")
    
    if logs:
        print(f"\n   Первые 5 логов:")
        for i, log in enumerate(logs[:5], 1):
            print(f"   {i}. [{log['level']}] {log['message'][:80]}")
        
        print(f"\n   Последние 5 логов:")
        for i, log in enumerate(logs[-5:], len(logs)-4):
            print(f"   {i}. [{log['level']}] {log['message'][:80]}")
elif 'error' in result:
    print(f"   ❌ Ошибка: {result['error']}")
else:
    print("   ⏱️ Запрос не завершился")

print("\n✅ Тест завершен")
