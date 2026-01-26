#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Перехват HTTP-запросов используя готовый Selenium скрипт
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import json
import time

# Импортируем данные
from src.sender_data import SENDER_DATA
from src.config import EXAMPLE_RECIPIENT_DATA


# Копируем функцию set_mui_input_value
def set_mui_input_value(driver, element, value):
    """React-safe установка значения в MUI controlled input"""
    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        time.sleep(0.2)
        element.click()
        time.sleep(0.2)
        element.send_keys(Keys.CONTROL + "a")
        time.sleep(0.1)
        element.send_keys(Keys.BACKSPACE)
        time.sleep(0.2)
        for char in str(value):
            element.send_keys(char)
            time.sleep(0.08)
        driver.execute_script("""
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
        """, element)
        time.sleep(0.3)
        driver.execute_script("document.body.click()")
        time.sleep(0.2)
        return True
    except Exception as e:
        print(f"   ⚠️ Ошибка set_mui_input_value: {e}")
        return False


def capture_payment_requests():
    """
    Создаёт платёж через Selenium и перехватывает все HTTP запросы
    """
    print("🔍 Запуск перехвата с полным созданием платежа...")
    
    # Настройка Chrome
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    # ВАЖНО: Включаем логирование сетевых запросов
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    captured_requests = []
    
    try:
        # Открываем страницу
        url = "https://multitransfer.ru/transfer/uzbekistan?paymentSystem=humo"
        print(f"\n📌 Открываю {url}...")
        driver.get(url)
        time.sleep(3)
        
        wait = WebDriverWait(driver, 20)
        
        # Шаг 1: Ввод суммы
        print("📌 Ввожу сумму 500 RUB...")
        amount_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='0 RUB']"))
        )
        set_mui_input_value(driver, amount_input, 500)
        print("✅ Сумма введена")
        time.sleep(5)
        
        # Шаг 2: Нажать Продолжить
        print("📌 Нажимаю 'Продолжить'...")
        try:
            continue_btn = wait.until(EC.element_to_be_clickable((By.ID, "pay")))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", continue_btn)
            time.sleep(0.5)
            continue_btn.click()
            print("✅ Кнопка нажата")
            
            # Ждём перехода
            wait.until(lambda d: "sender-details" in d.current_url)
            print("✅ Переход на страницу sender-details")
            time.sleep(3)
        except Exception as e:
            print(f"⚠️ Ошибка: {e}")
        
        # Шаг 3: Заполнить данные (частично, чтобы увидеть запросы)
        print("📌 Заполняю данные...")
        
        def fill_field(name_pattern, value):
            try:
                inputs = driver.find_elements(By.TAG_NAME, "input")
                for inp in inputs:
                    name_attr = (inp.get_attribute("name") or "").lower()
                    if name_pattern in name_attr:
                        inp.clear()
                        inp.send_keys(value)
                        time.sleep(0.2)
                        return True
                return False
            except:
                return False
        
        # Заполняем основные поля
        fill_field("beneficiaryaccountnumber", EXAMPLE_RECIPIENT_DATA["card_number"])
        fill_field("beneficiary_firstname", EXAMPLE_RECIPIENT_DATA["owner_name"].split()[0])
        fill_field("beneficiary_lastname", EXAMPLE_RECIPIENT_DATA["owner_name"].split()[1])
        fill_field("sender_firstname", SENDER_DATA["first_name"])
        fill_field("sender_lastname", SENDER_DATA["last_name"])
        
        print("✅ Данные заполнены")
        time.sleep(3)
        
        # Теперь анализируем перехваченные запросы
        print("\n🔍 Анализирую перехваченные запросы...")
        logs = driver.get_log('performance')
        
        for entry in logs:
            try:
                log = json.loads(entry['message'])['message']
                
                # Фильтруем сетевые запросы
                if log['method'] == 'Network.requestWillBeSent':
                    request = log['params']['request']
                    url = request['url']
                    
                    # Интересуют запросы к API
                    if 'multitransfer.ru' in url and (
                        '/api/' in url or 
                        'graphql' in url or
                        '/transfer/' in url and request['method'] in ['POST', 'PUT', 'PATCH']
                    ):
                        captured_requests.append({
                            'url': url,
                            'method': request['method'],
                            'headers': request.get('headers', {}),
                            'postData': request.get('postData', None),
                            'timestamp': entry['timestamp']
                        })
                        
                        print(f"\n✅ Перехвачен запрос:")
                        print(f"   URL: {url}")
                        print(f"   Method: {request['method']}")
                        if request.get('postData'):
                            data_preview = request['postData'][:300]
                            print(f"   Data: {data_preview}...")
                
                # Смотрим ответы
                elif log['method'] == 'Network.responseReceived':
                    response = log['params']['response']
                    url = response['url']
                    
                    if 'multitransfer.ru' in url and (
                        '/api/' in url or 
                        'graphql' in url
                    ):
                        print(f"\n📥 Ответ от: {url}")
                        print(f"   Status: {response['status']}")
                        
            except Exception as e:
                continue
        
        # Сохраняем результаты
        output_file = 'captured_requests.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(captured_requests, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Сохранено {len(captured_requests)} запросов в {output_file}")
        
        # Статистика
        print("\n📊 Статистика:")
        methods = {}
        for req in captured_requests:
            method = req['method']
            methods[method] = methods.get(method, 0) + 1
        
        for method, count in methods.items():
            print(f"   {method}: {count} запросов")
        
        # Показываем уникальные эндпоинты
        print("\n📋 Уникальные эндпоинты:")
        endpoints = set()
        for req in captured_requests:
            from urllib.parse import urlparse
            parsed = urlparse(req['url'])
            endpoint = f"{req['method']} {parsed.path}"
            endpoints.add(endpoint)
        
        for endpoint in sorted(endpoints):
            print(f"   {endpoint}")
        
        return captured_requests
        
    finally:
        driver.quit()


if __name__ == "__main__":
    print("="*80)
    print("🔍 Перехват HTTP-запросов с полным созданием платежа")
    print("="*80)
    
    requests = capture_payment_requests()
    
    print("\n" + "="*80)
    print("✅ Готово! Проверь файл captured_requests.json")
    print("\nТеперь запусти: python3 src/methods/requests_api/analyze_api.py")
    print("="*80)
