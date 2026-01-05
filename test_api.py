# -*- coding: utf-8 -*-
"""
Тест прямых API запросов к elecsnet.ru
"""

import requests
import json

# Данные для теста
CARD_NUMBER = "9860100125857258"
OWNER_NAME = "IZZET SAMEKEEV"
AMOUNT = 2000

# URL endpoints
BASE_URL = "https://1.elecsnet.ru/NotebookFront"
CALC_COMMISSION_URL = f"{BASE_URL}/services/0mhp/CalcCommission"
GET_MERCHANT_INFO_URL = f"{BASE_URL}/services/0mhp/GetMerchantInfo"

# Headers из браузера
headers = {
    "accept": "*/*",
    "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "sec-ch-ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-requested-with": "XMLHttpRequest",
    "referer": "https://1.elecsnet.ru/NotebookFront/services/0mhp/default.aspx?merchantId=36924&fromSegment=",
    "origin": "https://1.elecsnet.ru"
}

def test_calc_commission():
    """Тест расчета комиссии"""
    print("\n" + "="*60)
    print("1️⃣ ТЕСТ: Расчет комиссии")
    print("="*60)
    
    session = requests.Session()
    
    data = {
        "summ": str(AMOUNT),
        "merchantId": "36924",
        "paymentToolId": "205",
        "isExternal": "false"
    }
    
    try:
        response = session.post(
            CALC_COMMISSION_URL,
            headers=headers,
            data=data,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("isSuccess"):
                print("✅ Расчет комиссии работает!")
                return session, result
            else:
                print("❌ isSuccess = false")
                return None, None
        else:
            print(f"❌ Ошибка HTTP: {response.status_code}")
            return None, None
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None, None

def test_get_merchant_info(session):
    """Тест получения информации о мерчанте"""
    print("\n" + "="*60)
    print("2️⃣ ТЕСТ: Получение информации о платеже")
    print("="*60)
    
    if not session:
        print("❌ Нет сессии, пропускаем тест")
        return False
    
    data = {
        "merchantId": "36924",
        "paymentTool": "205",
        "merchantFields[1]": CARD_NUMBER,
        "merchantFields[2]": OWNER_NAME,
        "merchantFields[3]": "Непокрытый Дмитрий Евгеньевич",
        "merchantFields[4]": "03.07.2000",
        "merchantFields[5]": "RU",
        "merchantFields[6]": "1820657875",
        "amount": str(AMOUNT)
    }
    
    try:
        response = session.post(
            GET_MERCHANT_INFO_URL,
            headers=headers,
            data=data,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("isSuccess"):
                print("✅ Получение информации работает!")
                return True
            else:
                print("❌ isSuccess = false")
                return False
        else:
            print(f"❌ Ошибка HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_create_payment(session):
    """Тест создания платежа (получение ссылки и QR)"""
    print("\n" + "="*60)
    print("3️⃣ ТЕСТ: Создание платежа")
    print("="*60)
    
    if not session:
        print("❌ Нет сессии, пропускаем тест")
        return False
    
    # Возможные endpoints для создания платежа
    possible_endpoints = [
        f"{BASE_URL}/services/0mhp/CreatePayment",
        f"{BASE_URL}/services/0mhp/GeneratePayment",
        f"{BASE_URL}/services/0mhp/SubmitPayment",
        f"{BASE_URL}/services/0mhp/ProcessPayment",
    ]
    
    data = {
        "merchantId": "36924",
        "paymentTool": "205",
        "merchantFields[1]": CARD_NUMBER,
        "merchantFields[2]": OWNER_NAME,
        "merchantFields[3]": "Непокрытый Дмитрий Евгеньевич",
        "merchantFields[4]": "03.07.2000",
        "merchantFields[5]": "RU",
        "merchantFields[6]": "1820657875",
        "amount": str(AMOUNT),
        "summ.transfer": str(AMOUNT)
    }
    
    print("⚠️ Нужно найти правильный endpoint для создания платежа")
    print("Проверьте в браузере Network tab, какой запрос создает ссылку")
    print("\nВозможные варианты:")
    for endpoint in possible_endpoints:
        print(f"  - {endpoint}")
    
    return False

def main():
    print("\n🧪 ТЕСТИРОВАНИЕ API ЗАПРОСОВ К ELECSNET.RU")
    print("="*60)
    print(f"Карта: {CARD_NUMBER}")
    print(f"Владелец: {OWNER_NAME}")
    print(f"Сумма: {AMOUNT} руб.")
    
    # Тест 1: Расчет комиссии
    session, commission_result = test_calc_commission()
    
    if not session:
        print("\n❌ РЕЗУЛЬТАТ: API запросы НЕ работают без авторизации")
        print("Нужно использовать Selenium для получения cookies")
        return False
    
    # Тест 2: Получение информации
    merchant_info_ok = test_get_merchant_info(session)
    
    # Тест 3: Создание платежа
    payment_ok = test_create_payment(session)
    
    if merchant_info_ok:
        print("\n✅ РЕЗУЛЬТАТ: API запросы работают!")
        print("Можно использовать requests вместо Selenium")
        print("Скорость увеличится в 10 раз!")
        print("\n⚠️ НУЖНО: Найти endpoint для создания платежа")
        print("Откройте браузер, создайте платеж и посмотрите в Network tab")
        print("Какой запрос возвращает payment_link и QR код")
        return True
    else:
        print("\n❌ РЕЗУЛЬТАТ: API запросы НЕ работают полностью")
        print("Нужна авторизация через Selenium")
        return False

if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n💡 СЛЕДУЮЩИЙ ШАГ:")
        print("Нужно получить cookies из авторизованного браузера Selenium")
        print("и использовать их для requests запросов")
