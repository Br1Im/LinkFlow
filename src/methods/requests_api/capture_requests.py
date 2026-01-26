#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для перехвата HTTP-запросов к multitransfer.ru
Используется для reverse engineering API
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import json
import time
import sys
import os

# Добавляем путь к src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

def capture_network_requests():
    """
    Перехватывает все HTTP запросы при создании платежа
    """
    print("🔍 Запуск перехвата HTTP-запросов...")
    
    # Настройка Chrome для логирования сетевых запросов
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')  # Headless режим
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    captured_requests = []
    
    try:
        # Открываем страницу
        print("\n📌 Открываю https://multitransfer.ru/transfer/uzbekistan...")
        driver.get("https://multitransfer.ru/transfer/uzbekistan?paymentSystem=humo")
        time.sleep(3)
        
        print("📌 Автоматически создаю платёж для перехвата запросов...")
        
        # Импортируем данные
        from src.sender_data import SENDER_DATA
        from src.config import EXAMPLE_RECIPIENT_DATA
        
        # Вводим сумму
        print("   Ввожу сумму...")
        amount_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='0 RUB']"))
        )
        amount_input.click()
        time.sleep(0.2)
        for char in str(500):
            amount_input.send_keys(char)
            time.sleep(0.05)
        time.sleep(2)
        
        # Нажимаем Продолжить
        print("   Нажимаю Продолжить...")
        try:
            continue_btn = driver.find_element(By.ID, "pay")
            driver.execute_script("arguments[0].click();", continue_btn)
            time.sleep(3)
        except:
            pass
        
        print("   Ожидаю загрузки формы...")
        time.sleep(5)
        
        print("\n🔍 Анализирую перехваченные запросы...")
        # Получаем логи производительности
        logs = driver.get_log('performance')
        
        for entry in logs:
            try:
                log = json.loads(entry['message'])['message']
                
                # Фильтруем только сетевые запросы
                if log['method'] == 'Network.requestWillBeSent':
                    request = log['params']['request']
                    url = request['url']
                    
                    # Интересуют только запросы к multitransfer.ru API
                    if 'multitransfer.ru' in url and ('/api/' in url or '/transfer/' in url or 'graphql' in url):
                        captured_requests.append({
                            'url': url,
                            'method': request['method'],
                            'headers': request.get('headers', {}),
                            'postData': request.get('postData', None)
                        })
                        
                        print(f"\n✅ Перехвачен запрос:")
                        print(f"   URL: {url}")
                        print(f"   Method: {request['method']}")
                        if request.get('postData'):
                            print(f"   Data: {request['postData'][:200]}...")
                
                # Также смотрим ответы
                elif log['method'] == 'Network.responseReceived':
                    response = log['params']['response']
                    url = response['url']
                    
                    if 'multitransfer.ru' in url and ('/api/' in url or '/transfer/' in url or 'graphql' in url):
                        print(f"\n📥 Ответ от: {url}")
                        print(f"   Status: {response['status']}")
                        
            except Exception as e:
                continue
        
        # Сохраняем результаты
        output_file = 'captured_requests.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(captured_requests, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Сохранено {len(captured_requests)} запросов в {output_file}")
        
        # Выводим краткую статистику
        print("\n📊 Статистика:")
        methods = {}
        for req in captured_requests:
            method = req['method']
            methods[method] = methods.get(method, 0) + 1
        
        for method, count in methods.items():
            print(f"   {method}: {count} запросов")
        
        return captured_requests
        
    finally:
        driver.quit()


if __name__ == "__main__":
    print("="*60)
    print("🔍 Перехват HTTP-запросов к multitransfer.ru")
    print("="*60)
    
    requests = capture_network_requests()
    
    print("\n" + "="*60)
    print("✅ Готово! Проверь файл captured_requests.json")
    print("="*60)
