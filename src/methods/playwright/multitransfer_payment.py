#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Playwright-based автоматизация для multitransfer.ru
Быстрее чем Selenium (~30-60 секунд вместо 2 минут)
"""

import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


class MultitransferPayment:
    """Класс для работы с multitransfer.ru через Playwright"""
    
    def __init__(self, sender_data=None, headless=True, skip_bank_selection=True):
        self.url = "https://multitransfer.ru/transfer/uzbekistan?paymentSystem=humo" if skip_bank_selection else "https://multitransfer.ru/transfer/uzbekistan"
        self.headless = headless
        self.skip_bank_selection = skip_bank_selection
        self.playwright = None
        self.browser = None
        self.page = None
        self.sender_data = sender_data
    
    def login(self):
        """Инициализация браузера"""
        print(f"🔧 Инициализация Playwright...")
        
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        
        # Создаём контекст с настройками
        context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36'
        )
        
        self.page = context.new_page()
        self.page.goto(self.url, wait_until='networkidle')
        
        print("✅ Страница загружена")
        return True
    
    def create_payment(self, card_number, owner_name, amount):
        """
        Создание платежа через Playwright
        
        Args:
            card_number: Номер карты получателя
            owner_name: Имя владельца карты
            amount: Сумма платежа
            
        Returns:
            dict: {"payment_link": "...", "success": True/False}
        """
        print(f"\n💳 Создание платежа через Playwright")
        print(f"   Карта: {card_number}")
        print(f"   Владелец: {owner_name}")
        print(f"   Сумма: {amount} руб.")
        
        start_time = time.time()
        
        try:
            # Шаг 1: Ввод суммы
            print("📌 Ввожу сумму...")
            amount_input = self.page.locator("input[placeholder='0 RUB']")
            amount_input.click()
            amount_input.fill(str(amount))
            # Trigger React events
            amount_input.press('Tab')
            time.sleep(2)
            print("✅ Сумма введена")
            
            # Шаг 2: Нажать Продолжить
            print("📌 Нажимаю 'Продолжить'...")
            continue_btn = self.page.locator("#pay")
            continue_btn.click()
            
            # Ждём перехода на sender-details
            self.page.wait_for_url("**/sender-details**", timeout=10000)
            print("✅ Переход на страницу sender-details")
            time.sleep(2)
            
            # Шаг 3: Заполнить данные получателя
            print("📌 Заполняю данные получателя...")
            
            # Номер карты
            self.page.fill("input[name*='beneficiaryAccountNumber']", card_number)
            print(f"   ✅ Номер карты: {card_number}")
            
            # Имя и фамилия получателя
            name_parts = owner_name.split()
            self.page.fill("input[name*='beneficiary_firstName']", name_parts[0])
            print(f"   ✅ Имя получателя: {name_parts[0]}")
            
            if len(name_parts) > 1:
                self.page.fill("input[name*='beneficiary_lastName']", name_parts[1])
                print(f"   ✅ Фамилия получателя: {name_parts[1]}")
            
            # Шаг 4: Заполнить данные отправителя (если есть)
            if self.sender_data:
                print("📌 Заполняю данные отправителя...")
                
                # Паспортные данные
                self.page.fill("input[name*='sender_documents_series']", self.sender_data.get("passport_series", ""))
                self.page.fill("input[name*='sender_documents_number']", self.sender_data.get("passport_number", ""))
                self.page.fill("input[name*='issueDate']", self.sender_data.get("passport_issue_date", ""))
                
                # Место рождения
                self.page.fill("input[name*='birthPlaceAddress_full']", self.sender_data.get("birth_place", ""))
                
                # Место регистрации
                self.page.fill("input[name*='registrationAddress_full']", self.sender_data.get("registration_place", ""))
                
                # Личные данные
                self.page.fill("input[name*='sender_firstName']", self.sender_data.get("first_name", ""))
                self.page.fill("input[name*='sender_lastName']", self.sender_data.get("last_name", ""))
                self.page.fill("input[name*='birthDate']", self.sender_data.get("birth_date", ""))
                self.page.fill("input[name*='phoneNumber']", self.sender_data.get("phone", ""))
                
                print("✅ Данные отправителя заполнены")
            
            # Шаг 5: Поставить галочку согласия
            print("📌 Ставлю галочку согласия...")
            try:
                checkbox = self.page.locator("input[type='checkbox']").first
                checkbox.check()
                print("✅ Галочка поставлена")
            except:
                print("⚠️ Галочка не найдена")
            
            time.sleep(1)
            
            # Шаг 6: Нажать Продолжить
            print("📌 Нажимаю 'Продолжить'...")
            pay_btn = self.page.locator("#pay")
            pay_btn.click()
            time.sleep(3)
            
            # Шаг 7: Обработка капчи (если есть)
            print("📌 Проверяю наличие капчи...")
            try:
                # Ищем iframe с капчей
                captcha_frame = self.page.frame_locator("iframe[src*='smartcaptcha']")
                if captcha_frame:
                    print("⚠️ Обнаружена капча - требуется ручное решение")
                    # В Playwright можно подождать пока пользователь решит капчу
                    time.sleep(10)
            except:
                print("✅ Капча не обнаружена")
            
            # Шаг 8: Нажать финальную кнопку в модалке
            print("📌 Нажимаю финальную кнопку...")
            try:
                final_btn = self.page.locator("button.MuiButton-sizeLarge:has-text('Продолжить')")
                final_btn.click()
                time.sleep(3)
            except:
                print("⚠️ Финальная кнопка не найдена")
            
            # Получаем результат
            payment_link = self.page.url
            elapsed = time.time() - start_time
            
            print(f"✅ Платеж создан за {elapsed:.1f} сек!")
            print(f"🔗 Ссылка: {payment_link}")
            
            return {
                "payment_link": payment_link,
                "elapsed_time": elapsed,
                "success": True
            }
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
            return {
                "error": str(e),
                "elapsed_time": elapsed,
                "success": False
            }
    
    def close(self):
        """Закрытие браузера"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        print("✅ Браузер закрыт")


# Пример использования
if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
    
    from src.sender_data import SENDER_DATA
    from src.config import EXAMPLE_RECIPIENT_DATA
    
    payment = MultitransferPayment(sender_data=SENDER_DATA, headless=True)
    payment.login()
    
    result = payment.create_payment(
        card_number=EXAMPLE_RECIPIENT_DATA["card_number"],
        owner_name=EXAMPLE_RECIPIENT_DATA["owner_name"],
        amount=EXAMPLE_RECIPIENT_DATA["amount"]
    )
    
    payment.close()
    
    print(f"\nРезультат: {result}")
