# -*- coding: utf-8 -*-
"""
Простой способ найти endpoint - анализ JavaScript на странице
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import re

CARD_NUMBER = "9860100125857258"
OWNER_NAME = "IZZET SAMEKEEV"
PHONE = "+79880260334"
PASSWORD = "xowxut-wemhej-3zAsno"
ELECSNET_URL = 'https://1.elecsnet.ru/NotebookFront/services/0mhp/default.aspx?merchantId=36924&fromSegment='

def find_payment_endpoint():
    print("\n" + "="*60)
    print("🔍 ПОИСК ENDPOINT ДЛЯ СОЗДАНИЯ ПЛАТЕЖА")
    print("="*60)
    
    options = webdriver.ChromeOptions()
    profile_path = os.path.abspath("profiles/profile_79880260334")
    options.add_argument(f'--user-data-dir={profile_path}')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(20)
    
    try:
        print(f"\n1️⃣ Открываю страницу...", flush=True)
        driver.get(ELECSNET_URL)
        time.sleep(2)
        
        # Авторизация если нужно
        try:
            login_btn = driver.find_element(By.CSS_SELECTOR, "a.login[href='main']")
            print("🔐 Авторизация...", flush=True)
            driver.execute_script("arguments[0].click();", login_btn)
            time.sleep(1)
            
            wait = WebDriverWait(driver, 10)
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.popup.login")))
            
            phone_input = driver.find_element(By.CSS_SELECTOR, "div.popup.login #Login_Value")
            phone_clean = PHONE.replace("+7", "").replace(" ", "").replace("-", "")
            phone_input.send_keys(phone_clean)
            
            password_input = driver.find_element(By.CSS_SELECTOR, "div.popup.login #Password_Value")
            password_input.send_keys(PASSWORD)
            
            auth_btn = driver.find_element(By.CSS_SELECTOR, "div.popup.login #authBtn")
            driver.execute_script("arguments[0].click();", auth_btn)
            time.sleep(3)
            
            driver.get(ELECSNET_URL)
            time.sleep(1)
        except:
            pass
        
        print(f"\n2️⃣ Анализирую JavaScript на странице...", flush=True)
        
        # Получаем весь HTML
        page_source = driver.page_source
        
        # Ищем все упоминания services/0mhp/
        endpoints = re.findall(r'services/0mhp/(\w+)', page_source)
        unique_endpoints = list(set(endpoints))
        
        print(f"\n📋 Найденные endpoints:")
        for endpoint in unique_endpoints:
            print(f"   - services/0mhp/{endpoint}")
        
        # Ищем JavaScript функции с ajax/fetch
        print(f"\n3️⃣ Ищу AJAX запросы в JavaScript...", flush=True)
        
        # Получаем все скрипты
        scripts = driver.find_elements(By.TAG_NAME, "script")
        
        ajax_calls = []
        for script in scripts:
            script_content = script.get_attribute('innerHTML')
            if script_content and 'ajax' in script_content.lower():
                # Ищем паттерны ajax вызовов
                ajax_patterns = re.findall(r'\$\.ajax\({[^}]+url:\s*["\']([^"\']+)["\']', script_content)
                ajax_calls.extend(ajax_patterns)
        
        if ajax_calls:
            print(f"\n📡 Найденные AJAX вызовы:")
            for call in set(ajax_calls):
                print(f"   - {call}")
        
        # Проверяем кнопку Submit
        print(f"\n4️⃣ Анализирую кнопку Оплатить...", flush=True)
        
        wait = WebDriverWait(driver, 15)
        wait.until(EC.invisibility_of_element_located((By.ID, "loadercontainer")))
        
        submit_btn = driver.find_element(By.NAME, "SubmitBtn")
        
        # Получаем все атрибуты кнопки
        print(f"\n🔘 Атрибуты кнопки SubmitBtn:")
        print(f"   - id: {submit_btn.get_attribute('id')}")
        print(f"   - name: {submit_btn.get_attribute('name')}")
        print(f"   - onclick: {submit_btn.get_attribute('onclick')}")
        print(f"   - type: {submit_btn.get_attribute('type')}")
        
        # Ищем форму
        try:
            form = driver.find_element(By.TAG_NAME, "form")
            print(f"\n📝 Атрибуты формы:")
            print(f"   - action: {form.get_attribute('action')}")
            print(f"   - method: {form.get_attribute('method')}")
            print(f"   - id: {form.get_attribute('id')}")
        except:
            print(f"\n⚠️ Форма не найдена")
        
        # Проверяем все возможные endpoints
        print(f"\n5️⃣ Тестирую возможные endpoints...", flush=True)
        
        possible_endpoints = [
            'CreatePayment',
            'GeneratePayment', 
            'SubmitPayment',
            'ProcessPayment',
            'MakePayment',
            'InitPayment',
            'GetPaymentLink',
            'GenerateQR'
        ]
        
        print(f"\n🧪 Возможные варианты для тестирования:")
        for endpoint in possible_endpoints:
            url = f"https://1.elecsnet.ru/NotebookFront/services/0mhp/{endpoint}"
            print(f"   - {url}")
        
        print("\n" + "="*60)
        print("💡 СЛЕДУЮЩИЕ ШАГИ:")
        print("="*60)
        print("1. Откройте DevTools (F12) → Network")
        print("2. Создайте платеж вручную")
        print("3. Найдите POST запрос после нажатия 'Оплатить'")
        print("4. Скопируйте:")
        print("   - URL запроса")
        print("   - Request Payload")
        print("   - Response")
        
        input("\n\nНажмите Enter для закрытия...")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    find_payment_endpoint()
