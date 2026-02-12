import requests
import json
import random

amount = random.randint(1000, 2000)

print(f"Создание платежа на {amount} RUB...")
print("="*60)

payment_data = {
    "amount": amount,
    "orderId": f"local_test_{amount}"
}

response = requests.post(
    "http://localhost:5000/api/payment",
    json=payment_data,
    headers={"Content-Type": "application/json"}
)

result = response.json()

print("\nРезультат:")
print("="*60)

if result.get("success"):
    print(f"✓ Платеж создан успешно!")
    print(f"Order ID: {result['order_id']}")
    print(f"Сумма: {result['amount']} RUB")
    print(f"Время: {result['payment_time']:.2f} сек")
    print(f"\nQR-ссылка:")
    print(result['qr_link'])
else:
    print(f"✗ Ошибка: {result.get('error', 'Неизвестная ошибка')}")
    if 'logs' in result:
        print("\nПоследние логи:")
        for log in result['logs'][-5:]:
            print(f"  [{log['level']}] {log['message']}")
