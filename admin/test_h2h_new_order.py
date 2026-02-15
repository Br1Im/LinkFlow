#!/usr/bin/env python3
import requests, json, time

BASE_URL = 'https://api.liberty.top'
ACCESS_TOKEN = 'dtpf8uupsbhumevz4pz2jebrqzqmv62o'
MERCHANT_ID = 'd5c17c6c-dc40-428a-80e5-2ca01af99f68'

headers = {
    'Accept': 'application/json',
    'Access-Token': ACCESS_TOKEN,
    'Content-Type': 'application/json',
    'X-Max-Wait-Ms': '30000'
}

ext_id = f'TEST_NEW_{int(time.time())}'
payload = {
    'amount': 2500,
    'currency': 'rub',
    'client_id': None,
    'payer_bank': None,
    'external_id': ext_id,
    'merchant_id': MERCHANT_ID,
    'callback_url': '',
    'payment_detail_type': 'card'
}

print(f'External ID: {ext_id}')
response = requests.post(f'{BASE_URL}/api/h2h/order', json=payload, headers=headers, timeout=35)
result = response.json()

if result.get('success'):
    pd = result['data']['payment_detail']
    print(f'✅ Карта: {pd["detail"]}')
    print(f'✅ Владелец: {pd["initials"]}')
else:
    print(f'❌ Ошибка: {result}')
