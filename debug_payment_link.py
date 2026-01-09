#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Отладка проблемы с поиском ссылки на оплату
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import subprocess

def kill_chrome_processes():
    """Убиваем все процессы Chrome"""
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], capture_output=True, timeout=5)
        subprocess.run(['taskkill', '/F', '/IM', 'chromedriver.exe'], capture_output=True, timeout=5)
        time.sleep(0.5)
    except:
        pass

def create_debug_driver():
    """Создание драйвера для отладки"""
    kill_chrome_processes()
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.page_load_strategy = 'eager'
    
    # Создаем временную директорию для профиля
    import tempfile
    temp_dir = tempfile.mkdtemp()
    options.add_argument(f'--user-data-dir={temp_dir}')
    
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(5)
    
    return driver

def debug_payment_creation():
    """Отладка создания платежа с детальным логированием"""
    driver = None
    
    try:
        print("🔍 Начинаю отладку создания платежа...")
        
        # Данные для тестирования
        card_number = "9860100126186921"
        owner_name = "AVAZBEK ISAQOV"
        amount = 5000
        
        # Данные аккаунта (нужно получить из базы)
        from bot.database import Database
        db = Database()
        
        accounts = db.get_accounts()
        if not accounts:
            print("❌ Нет аккаунтов в базе данных")
            return
        
        account = accounts[0]
        print(f"📱 Используем аккаунт: {account['phone']}")
        
        driver = create_debug_driver()
        
        print("📖 Открываю elecsnet...")
        driver.get('https://1.elecsnet.ru/NotebookFront/services/0mhp/default.aspx?merchantId=36924&fromSegment=')
        time.sleep(2)
        
        # Авторизация если нужна
        try:
            login_btn = driver.find_element(By.CSS_SELECTOR, "a.login[href='main']")
            print("🔐 Выполняю авторизацию...")
            
            driver.execute_script("arguments[0].click();", login_btn)
            time.sleep(1)
            
            wait = WebDriverWait(driver, 10)
            popup = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.popup.login")))
            
            phone_input = driver.find_element(By.CSS_SELECTOR, "div.popup.login #Login_Value")
            phone_clean = account['phone'].replace("+7", "").replace(" ", "").replace("-", "")
            phone_input.send_keys(phone_clean)
            
            password_input = driver.find_element(By.CSS_SELECTOR, "div.popup.login #Password_Value")
            password_input.send_keys(account['password'])
            
            auth_btn = driver.find_element(By.CSS_SELECTOR, "div.popup.login #authBtn")
            driver.execute_script("arguments[0].click();", auth_btn)
            time.sleep(3)
            
            driver.get('https://1.elecsnet.ru/NotebookFront/services/0mhp/default.aspx?merchantId=36924&fromSegment=')
            time.sleep(2)
            print("✅ Авторизация выполнена")
        except:
            print("✅ Уже авторизован")
        
        # Заполняем реквизиты
        wait = WebDriverWait(driver, 15)
        
        print("📝 Заполняю реквизиты...")
        card_input = wait.until(EC.element_to_be_clickable((By.NAME, "requisites.m-36924.f-1")))
        card_input.clear()
        card_input.send_keys(card_number)
        
        name_input = wait.until(EC.element_to_be_clickable((By.NAME, "requisites.m-36924.f-2")))
        name_input.clear()
        name_input.send_keys(owner_name)
        
        # Заполняем сумму
        print(f"💰 Заполняю сумму {amount}...")
        amount_input = wait.until(EC.element_to_be_clickable((By.NAME, "summ.transfer")))
        amount_input.clear()
        amount_formatted = f"{int(amount):,}".replace(",", " ")
        amount_input.send_keys(amount_formatted)
        
        time.sleep(1)
        
        # Ждем обработку суммы
        for _ in range(20):
            try:
                loader = driver.find_element(By.ID, "loadercontainer")
                if "display: none" in loader.get_attribute("style") or not loader.is_displayed():
                    break
            except:
                break
            time.sleep(0.2)
        
        # Нажимаем кнопку
        print("🚀 Нажимаю Оплатить...")
        submit_btn = wait.until(EC.presence_of_element_located((By.NAME, "SubmitBtn")))
        
        # Ждем активации кнопки
        for i in range(20):
            disabled = submit_btn.get_attribute("disabled")
            if not disabled:
                print(f"✅ Кнопка активна после {i} попыток")
                break
            time.sleep(0.3)
        
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", submit_btn)
        
        print("⏳ Ожидаю результат...")
        time.sleep(3)
        
        # Ждем результат
        for _ in range(50):
            try:
                loader = driver.find_element(By.ID, "loadercontainer")
                if "display: none" in loader.get_attribute("style") or not loader.is_displayed():
                    break
            except:
                break
            time.sleep(0.5)
        
        time.sleep(2)  # Дополнительное ожидание
        
        print("🔍 Анализирую страницу результата...")
        
        # Логируем текущий URL и заголовок
        current_url = driver.current_url
        page_title = driver.title
        print(f"📍 URL: {current_url}")
        print(f"📄 Title: {page_title}")
        
        # Ищем QR код
        print("\n🔍 Поиск QR кода...")
        qr_found = False
        qr_selectors = [
            (By.ID, "Image1"),
            (By.CSS_SELECTOR, "img[src*='qr']"),
            (By.CSS_SELECTOR, "img[src*='data:image']"),
            (By.CSS_SELECTOR, "img[alt*='QR']"),
            (By.CSS_SELECTOR, "img[id*='qr']"),
            (By.CSS_SELECTOR, "img[class*='qr']")
        ]
        
        for selector_type, selector in qr_selectors:
            try:
                qr_img = driver.find_element(selector_type, selector)
                qr_src = qr_img.get_attribute("src")
                if qr_src and len(qr_src) > 50:
                    print(f"✅ QR найден: {selector} -> {qr_src[:100]}...")
                    qr_found = True
                    break
                else:
                    print(f"⚠️ QR пустой: {selector}")
            except:
                print(f"❌ QR не найден: {selector}")
        
        # Ищем ссылку на оплату
        print("\n🔍 Поиск ссылки на оплату...")
        link_found = False
        link_selectors = [
            (By.ID, "LinkMobil"),
            (By.CSS_SELECTOR, "a[href*='qr.nspk.ru']"),
            (By.CSS_SELECTOR, "a[href*='nspk']"),
            (By.CSS_SELECTOR, "a[href*='qr']"),
            (By.CSS_SELECTOR, "a[id*='Link']"),
            (By.CSS_SELECTOR, "a[class*='link']"),
            (By.CSS_SELECTOR, "a[href*='elecsnet']"),
            (By.XPATH, "//a[contains(@href, 'qr')]"),
            (By.XPATH, "//a[contains(text(), 'Оплатить')]"),
            (By.XPATH, "//a[contains(@id, 'Link')]")
        ]
        
        for selector_type, selector in link_selectors:
            try:
                link_element = driver.find_element(selector_type, selector)
                href = link_element.get_attribute("href")
                if href and len(href) > 10:
                    print(f"✅ Ссылка найдена: {selector} -> {href}")
                    link_found = True
                    break
                else:
                    print(f"⚠️ Пустая ссылка: {selector}")
            except:
                print(f"❌ Ссылка не найдена: {selector}")
        
        # Логируем все ссылки на странице
        print("\n🔍 Все ссылки на странице:")
        try:
            all_links = driver.find_elements(By.TAG_NAME, "a")
            print(f"Найдено {len(all_links)} ссылок:")
            for i, link in enumerate(all_links[:15]):  # Показываем первые 15
                href = link.get_attribute("href") or "нет href"
                link_id = link.get_attribute("id") or "нет id"
                link_class = link.get_attribute("class") or "нет class"
                text = link.text[:50] if link.text else "нет текста"
                print(f"   {i+1:2d}. href={href[:80]:<80} id={link_id:<15} class={link_class:<20} text={text}")
        except Exception as e:
            print(f"Ошибка получения ссылок: {e}")
        
        # Логируем все изображения
        print("\n🔍 Все изображения на странице:")
        try:
            all_images = driver.find_elements(By.TAG_NAME, "img")
            print(f"Найдено {len(all_images)} изображений:")
            for i, img in enumerate(all_images[:10]):  # Показываем первые 10
                src = img.get_attribute("src") or "нет src"
                img_id = img.get_attribute("id") or "нет id"
                img_class = img.get_attribute("class") or "нет class"
                alt = img.get_attribute("alt") or "нет alt"
                print(f"   {i+1:2d}. src={src[:80]:<80} id={img_id:<15} class={img_class:<20} alt={alt}")
        except Exception as e:
            print(f"Ошибка получения изображений: {e}")
        
        # Сохраняем скриншот
        try:
            screenshot_path = "debug_screenshot.png"
            driver.save_screenshot(screenshot_path)
            print(f"\n📸 Скриншот сохранен: {screenshot_path}")
        except Exception as e:
            print(f"Ошибка сохранения скриншота: {e}")
        
        # Сохраняем HTML
        try:
            html_path = "debug_page_source.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print(f"📄 HTML сохранен: {html_path}")
        except Exception as e:
            print(f"Ошибка сохранения HTML: {e}")
        
        print(f"\n📊 Результат отладки:")
        print(f"   QR код: {'✅ найден' if qr_found else '❌ не найден'}")
        print(f"   Ссылка: {'✅ найдена' if link_found else '❌ не найдена'}")
        
        if not link_found:
            print("\n🔧 Рекомендации:")
            print("   1. Проверьте HTML файл debug_page_source.html")
            print("   2. Проверьте скриншот debug_screenshot.png")
            print("   3. Возможно изменилась структура страницы")
            print("   4. Попробуйте увеличить время ожидания")
        
    except Exception as e:
        print(f"❌ Ошибка отладки: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
        kill_chrome_processes()

if __name__ == "__main__":
    debug_payment_creation()