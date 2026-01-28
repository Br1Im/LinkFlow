#!/usr/bin/env python3
"""
ПОЛНАЯ АВТОМАТИЗАЦИЯ с решением SmartCaptcha через 2captcha
"""

import requests
import time
from multitransfer_api import MultitransferAPI

class FullAutomation:
    def __init__(self, api_key_2captcha: str):
        self.api_key_2captcha = api_key_2captcha
        self.session = requests.Session()
        
    def solve_smartcaptcha(self) -> str:
        """Решение Yandex SmartCaptcha через 2captcha"""
        print("🧩 Решаю SmartCaptcha через 2captcha...")
        
        # Параметры SmartCaptcha из HAR файла
        sitekey = "ysc1_DAo8nFPdNCMHkAwYxIUJFxW5IIJd3ITGArZehXxO9a0ea6f8"
        pageurl = "https://multitransfer.ru/transfer/uzbekistan/sender-details"
        
        # Отправляем капчу в 2captcha
        submit_url = "http://2captcha.com/in.php"
        submit_data = {
            'key': self.api_key_2captcha,
            'method': 'yandex',
            'sitekey': sitekey,
            'pageurl': pageurl,
            'json': 1
        }
        
        try:
            response = requests.post(submit_url, data=submit_data)
            result = response.json()
            
            if result.get('status') == 1:
                captcha_id = result['request']
                print(f"✅ Капча отправлена, ID: {captcha_id}")
                
                # Ждем решения
                result_url = "http://2captcha.com/res.php"
                
                for attempt in range(60):  # Максимум 10 минут
                    time.sleep(10)
                    
                    result_response = requests.get(result_url, params={
                        'key': self.api_key_2captcha,
                        'action': 'get',
                        'id': captcha_id,
                        'json': 1
                    })
                    
                    result_data = result_response.json()
                    
                    if result_data.get('status') == 0:
                        if result_data.get('request') == 'CAPCHA_NOT_READY':
                            print(f"⏳ Ждем решения... ({attempt + 1}/60)")
                            continue
                        else:
                            print(f"❌ Ошибка 2captcha: {result_data.get('request')}")
                            return None
                    elif result_data.get('status') == 1:
                        token = result_data['request']
                        print(f"✅ Капча решена!")
                        print(f"🔑 Токен: {token[:30]}...")
                        return token
                
                print("❌ Таймаут решения капчи")
                return None
            else:
                print(f"❌ Ошибка отправки капчи: {result}")
                return None
                
        except Exception as e:
            print(f"❌ Ошибка 2captcha: {e}")
            return None
    
    def create_qr_payment(self, card_number: str, recipient_name: str, amount: float) -> str:
        """Создание QR-платежа с автоматическим решением капчи"""
        print(f"🎯 Создаю QR-платеж: {amount} RUB → {card_number}")
        
        # Получаем токен через решение капчи
        token = self.solve_smartcaptcha()
        
        if not token:
            print("❌ Не удалось получить токен")
            return None
        
        # Используем API с токеном
        api = MultitransferAPI(token)
        
        try:
            qr_link = api.create_qr_payment(card_number, recipient_name, amount)
            return qr_link
        except Exception as e:
            print(f"❌ Ошибка создания платежа: {e}")
            return None

def main():
    """Тест полной автоматизации"""
    print("🚀 ПОЛНАЯ АВТОМАТИЗАЦИЯ С 2CAPTCHA")
    print("="*50)
    
    # API ключ 2captcha
    api_key = input("Введи API ключ 2captcha: ").strip()
    
    if not api_key:
        print("❌ API ключ не введен")
        print("💡 Получи ключ на https://2captcha.com")
        return
    
    automation = FullAutomation(api_key)
    
    # Создаем QR-платеж
    qr_link = automation.create_qr_payment(
        card_number="9860080323894719",
        recipient_name="Nodir Asadullayev",
        amount=110
    )
    
    if qr_link:
        print(f"🎉 УСПЕХ! QR-ссылка: {qr_link}")
        
        with open('automated_result.txt', 'w') as f:
            f.write(f"QR Link: {qr_link}\n")
        
        print("💾 Результат сохранен в automated_result.txt")
        print("✅ ПОЛНАЯ АВТОМАТИЗАЦИЯ РАБОТАЕТ!")
    else:
        print("❌ Не удалось создать QR-ссылку")

if __name__ == "__main__":
    main()