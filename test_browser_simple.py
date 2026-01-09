#!/usr/bin/env python3
"""
Простой тест браузера на сервере
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os

def test_browser():
    print("🧪 Тестируем браузер на сервере...")
    
    try:
        # Создаем опции для сервера
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--remote-debugging-port=9222')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--single-process')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-web-security')
        
        print("🚀 Запускаем Chrome...")
        from selenium.webdriver.chrome.service import Service
        service = Service('/usr/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)
        
        print("🌐 Переходим на elecsnet...")
        driver.get('https://1.elecsnet.ru/NotebookFront/services/0mhp/default.aspx?merchantId=36924&fromSegment=')
        
        print("⏳ Ждем загрузки...")
        time.sleep(5)
        
        print(f"📄 Заголовок страницы: {driver.title}")
        print(f"🔗 URL: {driver.current_url}")
        
        # Проверяем есть ли кнопка входа
        try:
            login_btn = driver.find_element(By.CSS_SELECTOR, "a.login[href='main']")
            print("✅ Кнопка входа найдена")
        except:
            print("❌ Кнопка входа не найдена")
        
        driver.quit()
        print("✅ Тест браузера прошел успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка браузера: {e}")
        return False

if __name__ == '__main__':
    test_browser()