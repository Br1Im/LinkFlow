#!/usr/bin/env python3
"""
Тест PayzTeam API через curl
"""
import hashlib
import time
import json
import subprocess

# Параметры
merchant_id = "747"
api_key = "f046a50c7e398bc48124437b612ac7ab"
secret_key = "aa7c2689-98f2-428f-9c03-93e3835c3b1d"

# Данные для запроса
client_email = "test@example.com"
amount = "1000"
fiat_currency = "rub"
uuid = f"test_{int(time.time())}"
language = "ru"
payment_method = "abh_c2c"
client_ip = "127.0.0.1"

# Генерируем подпись
sign_string = f"{client_email}{uuid}{amount}{fiat_currency}{payment_method}{secret_key}"
signature = hashlib.sha1(sign_string.encode('utf-8')).hexdigest()

# Формируем JSON body
body = {
    "client": client_email,
    "amount": amount,
    "fiat_currency": fiat_currency,
    "uuid": uuid,
    "language": language,
    "payment_method": payment_method,
    "is_intrabank_transfer": False,
    "ip": client_ip,
    "sign": signature
}

body_json = json.dumps(body, ensure_ascii=False)

# URL
url = f"https://payzteam.com/exchange/create_deal_v2/{merchant_id}"

print("=" * 80)
print("CURL КОМАНДА ДЛЯ PAYZTEAM API")
print("=" * 80)
print()

# Формируем curl команду
curl_command = f'''curl -X POST "{url}" \\
  -H "Content-Type: application/json" \\
  -H "X-Api-Key: {api_key}" \\
  -d '{body_json}' '''

print("📋 CURL команда:")
print("-" * 80)
print(curl_command)
print()
print("-" * 80)
print()

print("📤 Параметры:")
print(f"   URL: {url}")
print(f"   API Key: {api_key}")
print(f"   UUID: {uuid}")
print(f"   Amount: {amount} {fiat_currency}")
print(f"   Payment Method: {payment_method}")
print()

print("🔐 Подпись:")
print(f"   Строка: {sign_string}")
print(f"   SHA1: {signature}")
print()

print("📦 Body:")
print(json.dumps(body, indent=2, ensure_ascii=False))
print()

print("=" * 80)
print("ВЫПОЛНЯЮ ЗАПРОС...")
print("=" * 80)
print()

# Выполняем curl
try:
    result = subprocess.run(
        ['curl', '-X', 'POST', url,
         '-H', 'Content-Type: application/json',
         '-H', f'X-Api-Key: {api_key}',
         '-d', body_json],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    print("📥 ОТВЕТ:")
    print("-" * 80)
    
    if result.stdout:
        try:
            response_json = json.loads(result.stdout)
            print(json.dumps(response_json, indent=2, ensure_ascii=False))
        except:
            print(result.stdout)
    
    if result.stderr:
        print("\n⚠️ Stderr:")
        print(result.stderr)
    
    print()
    print("-" * 80)
    
except FileNotFoundError:
    print("❌ curl не найден в системе")
    print("   Установите curl или используйте команду выше вручную")
except Exception as e:
    print(f"❌ Ошибка: {e}")

print()
print("=" * 80)
