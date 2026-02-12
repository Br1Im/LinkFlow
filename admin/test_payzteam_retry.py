import requests
import hashlib
import json
import time

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

print("Попытка получить реквизит на 3000 RUB...")
for i in range(5):
    print(f"\nПопытка {i+1}/5...")
    result = create_requisite(3000)
    
    if result.get("success"):
        print("\n✓ Реквизит получен!")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Извлекаем данные карты
        credentials = result["paymentInfo"]["paymentCredentials"]
        card_parts = credentials.split("|")
        card_number = card_parts[0]
        card_owner = card_parts[1]
        
        print(f"\n{'='*60}")
        print(f"Карта: {card_number}")
        print(f"Владелец: {card_owner}")
        print(f"{'='*60}")
        
        # Создаем платеж с этими реквизитами
        print("\nСоздание платежа с полученными реквизитами...")
        payment_data = {
            "amount": 3000,
            "orderId": f"payzteam_test_{int(time.time())}",
            "card_number": card_number,
            "card_owner": card_owner
        }
        
        payment_response = requests.post(
            "http://85.192.56.74/api/payment",
            json=payment_data,
            headers={"Content-Type": "application/json"}
        )
        
        print("\nРезультат создания платежа:")
        print(json.dumps(payment_response.json(), indent=2, ensure_ascii=False))
        break
    else:
        print(f"✗ {result.get('message', 'Ошибка')}")
        if i < 4:
            time.sleep(1)
else:
    print("\n✗ Не удалось получить реквизит после 5 попыток")
