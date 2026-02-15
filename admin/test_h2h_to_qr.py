#!/usr/bin/env python3
"""
Тест: получение реквизитов от H2H API и генерация QR-ссылки через Multitransfer
"""

import sys
import os
import json
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'payment_service'))

from h2h_api import H2HAPI
from requisite_config import get_h2h_config

# Импортируем payment_service для генерации QR
import asyncio
from payment_service import PaymentService

async def test_h2h_to_qr():
    """Тест полного цикла: H2H API → QR-ссылка"""
    
    config = get_h2h_config()
    
    print("="*70)
    print("ТЕСТ: H2H API → MULTITRANSFER QR")
    print("="*70)
    
    # Шаг 1: Получаем реквизиты от H2H API
    print("\n[Шаг 1] Получение реквизитов от H2H API...")
    print(f"  Base URL: {config['base_url']}")
    print(f"  Merchant ID: {config['merchant_id']}")
    
    api = H2HAPI(
        base_url=config['base_url'],
        access_token=config['access_token']
    )
    
    amount = 2500
    external_id = f"H2H_QR_TEST_{int(time.time())}"
    
    print(f"  Сумма: {amount} RUB")
    print(f"  External ID: {external_id}")
    
    result = api.create_order(
        external_id=external_id,
        amount=amount,
        merchant_id=config['merchant_id'],
        currency="rub",
        payment_detail_type="card"
    )
    
    if not result.get("success"):
        error_msg = result.get('details', {}).get('message', result.get('error', 'Unknown error'))
        print(f"\n❌ Ошибка получения реквизитов: {error_msg}")
        return
    
    data = result["data"]
    payment_detail = data.get("payment_detail", {})
    
    card_number = payment_detail.get('detail')
    card_owner = payment_detail.get('initials')
    order_id = data.get('order_id')
    
    print(f"\n✅ Реквизиты получены:")
    print(f"  Order ID: {order_id}")
    print(f"  Карта: {card_number}")
    print(f"  Владелец: {card_owner}")
    print(f"  Gateway: {data.get('payment_gateway_name')} ({data.get('payment_gateway')})")
    
    # Шаг 2: Генерируем QR-ссылку через Multitransfer
    print(f"\n[Шаг 2] Генерация QR-ссылки через Multitransfer...")
    
    payment_service = PaymentService()
    
    try:
        # Запускаем браузер
        print("  Запуск браузера...")
        await payment_service.start(headless=True)
        
        # Создаем платеж с реквизитами от H2H API
        print(f"  Создание платежа с реквизитами от H2H API...")
        payment_result = await payment_service.create_payment_link(
            amount=amount,
            card_number=card_number,
            owner_name=card_owner
        )
        
        if payment_result.get('success'):
            print(f"\n✅ QR-ссылка успешно создана!")
            print(f"  QR Link: {payment_result.get('qr_link')}")
            print(f"  Время генерации: {payment_result.get('time'):.2f}s")
            print(f"  Step 1: {payment_result.get('step1_time'):.2f}s")
            print(f"  Step 2: {payment_result.get('step2_time'):.2f}s")
            
            print(f"\n{'='*70}")
            print("ИТОГ:")
            print(f"{'='*70}")
            print(f"H2H Order ID: {order_id}")
            print(f"Карта: {card_number}")
            print(f"Владелец: {card_owner}")
            print(f"QR-ссылка: {payment_result.get('qr_link')}")
            print(f"{'='*70}")
        else:
            print(f"\n❌ Ошибка создания QR-ссылки: {payment_result.get('error')}")
            
    finally:
        # Останавливаем браузер
        await payment_service.stop()

if __name__ == "__main__":
    asyncio.run(test_h2h_to_qr())
