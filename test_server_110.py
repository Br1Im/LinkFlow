import requests
import json

# Тест без порта (через nginx на порту 80)
url = "http://85.192.56.74/api/create-qr-payment"

data = {
    "amount": 3000
}

print(f"Отправка запроса на {url}")
print(f"Данные: {json.dumps(data, ensure_ascii=False)}\n")

try:
    response = requests.post(url, json=data, timeout=30)
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
except Exception as e:
    print(f"Ошибка: {e}")
    if hasattr(e, 'response'):
        print(f"Текст ответа: {e.response.text}")
