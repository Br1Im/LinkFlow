import requests
import hashlib
import json

MERCHANT_ID = "747"
API_KEY = "f046a50c7e398bc48124437b612ac7ab"
SECRET_KEY = "aa7c2689-98f2-428f-9c03-93e3835c3b1d"

import time

client = "test@example.com"
uuid = f"TEST_{int(time.time())}"
amount = "1500.00"
fiat_currency = "rub"
payment_method = "abh_c2c"

sign_string = f"{client}{uuid}{amount}{fiat_currency}{payment_method}{SECRET_KEY}"
signature = hashlib.sha1(sign_string.encode('utf-8')).hexdigest()

url = f"https://payzteam.com/exchange/create_deal_v2/{MERCHANT_ID}"
headers = {
    "Content-Type": "application/json",
    "X-Api-Key": API_KEY
}
payload = {
    "client": client,
    "amount": amount,
    "fiat_currency": fiat_currency,
    "uuid": uuid,
    "language": "ru",
    "payment_method": payment_method,
    "is_intrabank_transfer": False,
    "ip": "127.0.0.1",
    "sign": signature
}

response = requests.post(url, json=payload, headers=headers)
print(json.dumps(response.json(), indent=2))
