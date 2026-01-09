import requests
import json

url = 'http://85.192.56.74:5000/api/payment'
headers = {
    'Authorization': 'Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo',
    'Content-Type': 'application/json'
}
data = {
    'amount': 1000,
    'orderId': 'real-payment-test-001'
}

print('🚀 Тестируем РЕАЛЬНОЕ создание платежа...')
print(f'URL: {url}')
print(f'Data: {data}')

try:
    response = requests.post(url, headers=headers, json=data)
    print(f'Status: {response.status_code}')
    print(f'Response: {response.text}')
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print('✅ УСПЕХ! Платеж создан')
            print(f'🆔 Order ID: {result.get("orderId")}')
            print(f'🔗 Payment Link: {result.get("qr")}')
            if 'test_mode' not in result:
                print('🎉 ЭТО РЕАЛЬНЫЙ ПЛАТЕЖ!')
            else:
                print('⚠️  Это тестовый режим')
        else:
            print(f'❌ Ошибка: {result.get("error")}')
    else:
        print(f'❌ HTTP Error: {response.status_code}')
        
except Exception as e:
    print(f'❌ Exception: {e}')