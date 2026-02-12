import requests
import hashlib
import json
import time
import random

MERCHANT_ID = "747"
API_KEY = "f046a50c7e398bc48124437b612ac7ab"
SECRET_KEY = "aa7c2689-98f2-428f-9c03-93e3835c3b1d"

amount = random.randint(2500, 5000)

print(f"Запрос реквизита на {amount} RUB...")
print("="*60)

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
result = response.json()

print("\nРезультат:")
print("="*60)

if result.get("success"):
    print("✓ Реквизит получен!")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    credentials = result["paymentInfo"]["paymentCredentials"]
    card_parts = credentials.split("|")
    card_number = card_parts[0]
    card_owner = card_parts[1]
    bank = card_parts[2] if len(card_parts) > 2 else "Unknown"
    
    print("\n" + "="*60)
    print("ДАННЫЕ РЕКВИЗИТА:")
    print("="*60)
    print(f"Карта: {card_number}")
    print(f"Владелец: {card_owner}")
    print(f"Банк: {bank}")
    print(f"Сумма: {amount} RUB")
    print("="*60)
else:
    print(f"✗ {result.get('message', 'Ошибка')}")
