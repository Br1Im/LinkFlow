# -*- coding: utf-8 -*-
"""
Перехват сетевых запросов при создании платежа
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import json
import os

# Данные для теста
CARD_NUMBER = "9860100125857258"
OWNER_NAME = "IZZET SAMEKEEV"
AMOUNT = 2000
PHONE = "+79880260334"
PASSWORD = "xowxut-wemhej-3zAsno"

ELECSNET_URL = 'https://1.elecsnet.ru/NotebookFront/services/0mhp/default.aspx?merchantId=36924&fromSegment='

def capture_network_requests():
    """Перехват всех сетевых запросов"""
    print("\n" + "="*60)
    print("🔍 ПЕРЕХВАТ СЕТЕВЫХ ЗАПРОСОВ")
    print("="*60)
    
    # Включаем логирование производительности для перехвата запросов
    capabilities = DesiredCapabilities.CHROME.copy()
    capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}
    
    options = webdriver.ChromeOptions()
    profile_path = os.path.abspath("profiles/profile_79880260334")
    options.add_argument(f'--user-data-dir={profile_path}')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    # Добавляем capabilities для логирования
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(20)
    
    try:
        print(f"\n1️⃣ Открываю страницу...", flush=True)
        driver.get(ELECSNET_URL)
        time.sleep(2)
        
        # Проверка авторизации
        try:
            login_btn = driver.find_element(By.CSS_SELECTOR, "a.login[href='main']")
            print("🔐 Требуется авторизация...", flush=True)
            
            driver.execute_script("arguments[0].click();", login_btn)
            time.sleep(1)
            
            wait = WebDriverWait(driver, 10)
            popup = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.popup.login")))
            
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
            print("✅ Авторизация выполнена", flush=True)
        except:
            print("✅ Уже авторизован", flush=True)
        
        wait = WebDriverWait(driver, 15)
        wait.until(EC.invisibility_of_element_located((By.ID, "loadercontainer")))
        
        print(f"\n2️⃣ Заполняю реквизиты...", flush=True)
        card_input = wait.until(EC.element_to_be_clickable((By.NAME, "requisites.m-36924.f-1")))
        card_input.clear()
        card_input.send_keys(CARD_NUMBER)
        
        name_input = wait.until(EC.element_to_be_clickable((By.NAME, "requisites.m-36924.f-2")))
        name_input.clear()
        name_input.send_keys(OWNER_NAME)
        
        print(f"\n3️⃣ Заполняю сумму: {AMOUNT} руб.", flush=True)
        amount_input = wait.until(EC.element_to_be_clickable((By.NAME, "summ.transfer")))
        amount_input.clear()
        amount_input.send_keys(str(AMOUNT))
        
        time.sleep(1)
        
        print(f"\n4️⃣ Нажимаю кнопку Оплатить...", flush=True)
        print("📡 Начинаю перехват запросов...\n", flush=True)
        
        # Очищаем старые логи
        driver.get_log('performance')
        
        submit_btn = wait.until(EC.presence_of_element_located((By.NAME, "SubmitBtn")))
        
        # Ждем активации кнопки
        for _ in range(30):
            if not submit_btn.get_attribute("disabled"):
                break
            time.sleep(0.3)
        
        time.sleep(1)
        driver.execute_script("arguments[0].click();", submit_btn)
        
        print("⏳ Ожидаю ответа (10 секунд)...\n", flush=True)
        time.sleep(10)
        
        # Получаем все логи производительности
        logs = driver.get_log('performance')
        
        print("="*60)
        print("📊 АНАЛИЗ СЕТЕВЫХ ЗАПРОСОВ")
        print("="*60)
        
        requests_found = []
        
        for log in logs:
            try:
                message = json.loads(log['message'])
                method = message.get('message', {}).get('method', '')
                
                # Ищем сетевые запросы
                if method == 'Network.requestWillBeSent':
                    request = message['message']['params']['request']
                    url = request.get('url', '')
                    
                    # Фильтруем только запросы к elecsnet
                    if 'elecsnet.ru' in url and 'services/0mhp' in url:
                        request_method = request.get('method', '')
                        post_data = request.get('postData', '')
                        
                        requests_found.append({
                            'url': url,
                            'method': request_method,
                            'postData': post_data
                        })
                
                # Ищем ответы
                elif method == 'Network.responseReceived':
                    response = message['message']['params']['response']
                    url = response.get('url', '')
                    
                    if 'elecsnet.ru' in url and 'services/0mhp' in url:
                        status = response.get('status', 0)
                        print(f"\n📥 ОТВЕТ: {url}")
                        print(f"   Status: {status}")
                        
            except Exception as e:
                continue
        
        print("\n" + "="*60)
        print("📤 НАЙДЕННЫЕ ЗАПРОСЫ:")
        print("="*60)
        
        for i, req in enumerate(requests_found, 1):
            print(f"\n{i}. {req['method']} {req['url']}")
            if req['postData']:
                print(f"   POST Data: {req['postData'][:200]}...")
        
        # Пытаемся получить результат
        print("\n" + "="*60)
        print("🔗 РЕЗУЛЬТАТ ПЛАТЕЖА:")
        print("="*60)
        
        try:
            qr_img = driver.find_element(By.ID, "Image1")
            qr_src = qr_img.get_attribute("src")
            print(f"\n✅ QR код найден: {qr_src[:100]}...")
            
            payment_link_element = driver.find_element(By.ID, "LinkMobil")
            payment_link = payment_link_element.get_attribute("href")
            print(f"✅ Ссылка найдена: {payment_link}")
            
        except Exception as e:
            print(f"❌ Не удалось получить результат: {e}")
        
        print("\n" + "="*60)
        print("💡 РЕКОМЕНДАЦИЯ:")
        print("="*60)
        print("Найдите POST запрос, который возвращает payment_link и QR код")
        print("Это будет endpoint для быстрого создания платежей через API")
        
        input("\n\nНажмите Enter для закрытия браузера...")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    capture_network_requests()
