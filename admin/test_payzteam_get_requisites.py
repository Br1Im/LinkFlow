#!/usr/bin/env python3
"""
Тестовый скрипт для получения реквизитов через PayzTeam API
"""
import sys
sys.path.insert(0, 'payment_service')

from payzteam_api import PayzTeamAPI
import json

def test_get_requisites():
    """Тестируем получение реквизитов"""
    
    # Инициализируем API с ключами
    api = PayzTeamAPI(
        merchant_id="747",
        api_key="f046a50c7e398bc48124437b612ac7ab",
        secret_key="aa7c2689-98f2-428f-9c03-93e3835c3b1d"
    )
    
    print("=" * 60)
    print("ТЕСТ: Получение реквизитов через PayzTeam API")
    print("=" * 60)
    print()
    
    # Параметры для создания сделки
    params = {
        "client_email": "test@example.com",
        "amount": 1000,
        "fiat_currency": "rub",
        "uuid": "test_" + str(int(__import__('time').time())),
        "language": "ru",
        "payment_method": "abh_c2c",  # трансгран карта v2
        "client_ip": "127.0.0.1"
    }
    
    print("📤 Отправляю запрос на создание сделки...")
    print(f"   Сумма: {params['amount']} {params['fiat_currency']}")
    print(f"   Метод: {params['payment_method']}")
    print(f"   UUID: {params['uuid']}")
    print()
    
    # Показываем что будет отправлено
    print("📋 Параметры запроса:")
    print("-" * 60)
    for key, value in params.items():
        print(f"   {key}: {value}")
    print()
    
    # Генерируем подпись вручную чтобы показать
    import hashlib
    sign_string = f"{params['client_email']}{params['uuid']}{params['amount']}{params['fiat_currency']}{params['payment_method']}aa7c2689-98f2-428f-9c03-93e3835c3b1d"
    signature = hashlib.sha1(sign_string.encode('utf-8')).hexdigest()
    
    print("🔐 Подпись:")
    print(f"   Строка для подписи: {sign_string}")
    print(f"   SHA1: {signature}")
    print()
    
    print("🌐 Запрос:")
    print(f"   URL: https://payzteam.com/exchange/create_deal_v2/747")
    print(f"   Method: POST")
    print(f"   Headers: X-Api-Key: f046a50c7e398bc48124437b612ac7ab")
    print()
    
    # Создаем сделку
    result = api.create_deal(**params)
    
    print("=" * 60)
    print("📥 ОТВЕТ ОТ API:")
    print("=" * 60)
    print()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print()
    
    if result.get('success'):
        print("✅ Сделка создана успешно!")
        print()
        
        payment_info = result.get('paymentInfo', {})
        if payment_info:
            print("💳 РЕКВИЗИТЫ ДЛЯ ОПЛАТЫ:")
            print("-" * 60)
            
            # Выводим все поля из paymentInfo
            for key, value in payment_info.items():
                print(f"   {key}: {value}")
            
            print()
            
            # ID сделки для проверки статуса
            deal_id = result.get('id')
            if deal_id:
                print(f"🔑 ID сделки: {deal_id}")
                print()
                print("Для проверки статуса используйте:")
                print(f"   api.get_payment_status({deal_id})")
                print()
                print("Для отмены:")
                print(f"   api.cancel_payment({deal_id})")
    else:
        print("❌ Ошибка при создании сделки")
        if 'error' in result:
            print(f"   Ошибка: {result['error']}")
    
    print()
    print("=" * 60)

if __name__ == '__main__':
    test_get_requisites()
