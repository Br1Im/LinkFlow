import requests
import json

url = 'http://85.192.56.74:5000/api/payment'
headers = {
    'Authorization': 'Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo',
    'Content-Type': 'application/json'
}
data = {
    'amount': 100,
    'orderId': 'curl-test-002'
}

print('🧪 Тестируем тот же запрос что и curl...')
print(f'URL: {url}')
print(f'Headers: {headers}')
print(f'Data: {data}')

try:
    response = requests.post(url, headers=headers, json=data)
    print(f'Status: {response.status_code}')
    print(f'Response: {response.text}')
    
    if response.status_code == 200:
        result = response.json()
        print('✅ УСПЕХ через Python!')
        print(f'QR: {result.get("qr")}')
    else:
        print(f'❌ Ошибка: {response.status_code}')
        
except Exception as e:
    print(f'❌ Exception: {e}')