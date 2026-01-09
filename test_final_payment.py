import requests
import json

url = 'http://85.192.56.74:5000/api/payment'
headers = {
    'Authorization': 'Bearer -3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo',
    'Content-Type': 'application/json'
}
data = {
    'amount': 1000,
    'orderId': 'final-real-payment-002'
}

print('🎯 ФИНАЛЬНЫЙ ТЕСТ РЕАЛЬНОГО ПЛАТЕЖА!')
print(f'URL: {url}')
print(f'Data: {data}')

try:
    response = requests.post(url, headers=headers, json=data)
    print(f'Status: {response.status_code}')
    print(f'Response: {response.text}')
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print('🎉 УСПЕХ! РЕАЛЬНЫЙ ПЛАТЕЖ СОЗДАН!')
            print(f'🆔 Order ID: {result.get("orderId")}')
            print(f'🔗 Payment Link: {result.get("qr")}')
            print(f'🏷️  QRC ID: {result.get("qrcId")}')
            
            # Проверяем что это реальная ссылка elecsnet
            qr_link = result.get('qr', '')
            if 'elecsnet.ru' in qr_link or 'qr.nspk.ru' in qr_link:
                print('✅ ЭТО РЕАЛЬНАЯ ССЫЛКА ELECSNET!')
            else:
                print('⚠️  Неизвестный формат ссылки')
        else:
            print(f'❌ Ошибка: {result.get("error")}')
    else:
        print(f'❌ HTTP Error: {response.status_code}')
        
except Exception as e:
    print(f'❌ Exception: {e}')