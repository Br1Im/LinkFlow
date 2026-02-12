import requests
import hashlib
import json
import time
import random

MERCHANT_ID = "747"
API_KEY = "f046a50c7e398bc48124437b612ac7ab"
SECRET_KEY = "aa7c2689-98f2-428f-9c03-93e3835c3b1d"

def create_requisite(amount):
    client = "test@example.com"
    uuid = f"TEST_{int(time.time() * 1000)}"
    amount_str = f"{amount:.2f}"
    fiat_currency = "rub"
    payment_method = "abh_c2c"
    
    sign_string = f"{client}{uuid}{amount_str}{fiat_currency}{payment_method}{SECRET_KEY}"
    signature = hashlib.sha1(sign_string.encode('utf-8')).hexdigest()
    
    url = f"https://payzteam.com/exchange/create_deal_v2/{MERCHANT_ID}"
    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": API_KEY
    }
    payload = {
        "client": client,
        "amount": amount_str,
        "fiat_currency": fiat_currency,
        "uuid": uuid,
        "language": "ru",
        "payment_method": payment_method,
        "is_intrabank_transfer": False,
        "ip": "127.0.0.1",
        "sign": signature
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

print("Создание 5 реквизитов PayzTeam...")
print("="*60)

results = []

# 4 платежа от 1000 до 5000
for i in range(4):
    amount = random.randint(1000, 5000)
    print(f"\nЗапрос #{i+1}: {amount} RUB")
    result = create_requisite(amount)
    results.append(result)
    
    if result.get("success"):
        print(f"✓ Успех: {result['paymentInfo']['paymentCredentials']}")
    else:
        print(f"✗ {result.get('message', 'Ошибка')}")
    
    time.sleep(0.5)

# 5-й платеж на 2500
print(f"\nЗапрос #5: 2500 RUB")
result = create_requisite(2500)
results.append(result)

if result.get("success"):
    print(f"✓ Успех: {result['paymentInfo']['paymentCredentials']}")
    
    # Извлекаем данные карты из последнего реквизита
    credentials = result["paymentInfo"]["paymentCredentials"]
    card_parts = credentials.split("|")
    card_number = card_parts[0]
    card_owner = card_parts[1]
    
    print("\n" + "="*60)
    print("ПОСЛЕДНИЙ РЕКВИЗИТ (для создания платежа):")
    print("="*60)
    print(f"Карта: {card_number}")
    print(f"Владелец: {card_owner}")
    print(f"Сумма: 2500 RUB")
    print("="*60)
    
    # Добавляем карту в базу данных
    print("\nДобавление карты в базу данных...")
    add_response = requests.post(
        "http://85.192.56.74/api/beneficiaries",
        json={
            "card_number": card_number,
            "card_owner": card_owner
        },
        headers={"Content-Type": "application/json"}
    )
    
    if add_response.status_code == 200:
        print("✓ Карта добавлена в базу")
        time.sleep(2)
        
        # Создаем платеж с этой картой
        print("\nСоздание платежа с реквизитом...")
        payment_data = {
            "amount": 2500,
            "orderId": f"payzteam_final_{int(time.time())}",
            "card_number": card_number,
            "card_owner": card_owner
        }
        
        payment_response = requests.post(
            "http://85.192.56.74/api/payment",
            json=payment_data,
            headers={"Content-Type": "application/json"}
        )
        
        print("\n" + "="*60)
        print("РЕЗУЛЬТАТ СОЗДАНИЯ ПЛАТЕЖА:")
        print("="*60)
        payment_result = payment_response.json()
        
        if payment_result.get("success"):
            print(f"✓ Платеж создан успешно!")
            print(f"Order ID: {payment_result['order_id']}")
            print(f"Сумма: {payment_result['amount']} RUB")
            print(f"Время: {payment_result['payment_time']:.2f} сек")
            print(f"QR-ссылка: {payment_result['qr_link']}")
        else:
            print(f"✗ Ошибка: {payment_result.get('error', 'Неизвестная ошибка')}")
            if 'logs' in payment_result:
                print("\nЛоги:")
                for log in payment_result['logs'][-3:]:
                    print(f"  {log['level']}: {log['message']}")
    else:
        print(f"✗ Ошибка добавления карты: {add_response.text}")
else:
    print(f"✗ {result.get('message', 'Ошибка')}")

print("\n" + "="*60)
print("ИТОГИ:")
print("="*60)
success_count = sum(1 for r in results if r.get("success"))
print(f"Успешных реквизитов: {success_count}/5")
