# -*- coding: utf-8 -*-
"""
Менеджер браузера с прогревом
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import threading
from config import *


class BrowserManager:
    """Управление прогретым браузером"""
    
    def __init__(self):
        self.driver = None
        self.is_ready = False
        self.card_number = None
        self.owner_name = None
        self.account_phone = None
        self.lock = threading.Lock()
        self.last_activity = 0
    
    def _create_driver(self, profile_path):
        """Создание драйвера Chrome"""
        options = webdriver.ChromeOptions()
        options.add_argument(f'--user-data-dir={profile_path}')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.page_load_strategy = 'eager'
        
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
        return driver
    
    def _login_if_needed(self, driver, account):
        """Авторизация если требуется"""
        try:
            login_btn = driver.find_element(By.CSS_SELECTOR, "a.login[href='main']")
            print("🔐 Выполняю авторизацию...", flush=True)
            
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
            
            driver.get(ELECSNET_URL)
            time.sleep(1)
            print("✅ Авторизация выполнена", flush=True)
        except:
            print("✅ Уже авторизован", flush=True)
    
    def warmup(self, card_number, owner_name, account):
        """Прогрев браузера с заполнением данных"""
        with self.lock:
            # Если уже прогрет с теми же данными
            if (self.is_ready and self.driver and 
                self.card_number == card_number and 
                self.owner_name == owner_name):
                print("🔥 Браузер уже прогрет!", flush=True)
                return True
            
            # Закрываем старый браузер
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
                self.is_ready = False
            
            print(f"\n🔥 ПРОГРЕВ БРАУЗЕРА...", flush=True)
            start_time = time.time()
            
            try:
                profile_path = os.path.join(PROFILE_BASE_PATH, account['profile_path'])
                self.driver = self._create_driver(profile_path)
                
                print(f"[{time.time()-start_time:.1f}s] Открываю страницу...", flush=True)
                self.driver.get(ELECSNET_URL)
                
                self._login_if_needed(self.driver, account)
                
                wait = WebDriverWait(self.driver, ELEMENT_WAIT_TIMEOUT)
                wait.until(EC.invisibility_of_element_located((By.ID, "loadercontainer")))
                
                print(f"[{time.time()-start_time:.1f}s] Заполняю реквизиты...", flush=True)
                card_input = wait.until(EC.element_to_be_clickable((By.NAME, "requisites.m-36924.f-1")))
                card_input.clear()
                card_input.send_keys(card_number)
                
                name_input = wait.until(EC.element_to_be_clickable((By.NAME, "requisites.m-36924.f-2")))
                name_input.clear()
                name_input.send_keys(owner_name)
                
                self.card_number = card_number
                self.owner_name = owner_name
                self.account_phone = account['phone']
                self.is_ready = True
                self.last_activity = time.time()
                
                elapsed = time.time() - start_time
                print(f"🔥 Браузер прогрет за {elapsed:.1f} сек!", flush=True)
                return True
                
            except Exception as e:
                print(f"❌ Ошибка прогрева: {e}", flush=True)
                if self.driver:
                    try:
                        self.driver.quit()
                    except:
                        pass
                    self.driver = None
                self.is_ready = False
                return False
    
    def create_payment(self, amount, callback=None):
        """
        Создание платежа в прогретом браузере
        callback(payment_link, qr_base64) - вызывается сразу при получении данных
        """
        with self.lock:
            if not self.is_ready or not self.driver:
                return {"error": "Браузер не прогрет"}
            
            start_time = time.time()
            
            try:
                wait = WebDriverWait(self.driver, ELEMENT_WAIT_TIMEOUT)
                
                print(f"[{time.time()-start_time:.1f}s] Заполняю сумму...", flush=True)
                amount_input = wait.until(EC.element_to_be_clickable((By.NAME, "summ.transfer")))
                amount_input.clear()
                amount_input.send_keys(str(amount))
                
                # Ждем обработку
                time.sleep(0.5)
                for _ in range(30):
                    try:
                        loader = self.driver.find_element(By.ID, "loadercontainer")
                        if "display: none" in loader.get_attribute("style") or not loader.is_displayed():
                            break
                    except:
                        break
                    time.sleep(0.2)
                
                print(f"[{time.time()-start_time:.1f}s] Нажимаю Оплатить...", flush=True)
                submit_btn = wait.until(EC.presence_of_element_located((By.NAME, "SubmitBtn")))
                
                # Ждем активации кнопки
                for _ in range(30):
                    if not submit_btn.get_attribute("disabled"):
                        break
                    time.sleep(0.3)
                
                # Финальное ожидание loader
                time.sleep(1)
                for _ in range(20):
                    try:
                        loader = self.driver.find_element(By.ID, "loadercontainer")
                        if "display: none" in loader.get_attribute("style") and not loader.is_displayed():
                            break
                    except:
                        break
                    time.sleep(0.3)
                
                self.driver.execute_script("arguments[0].click();", submit_btn)
                
                print(f"[{time.time()-start_time:.1f}s] Ожидаю результат...", flush=True)
                time.sleep(2)
                
                # Ждем исчезновения loader
                for _ in range(40):
                    try:
                        loader = self.driver.find_element(By.ID, "loadercontainer")
                        if "display: none" in loader.get_attribute("style") or not loader.is_displayed():
                            break
                    except:
                        break
                    time.sleep(0.3)
                
                print(f"[{time.time()-start_time:.1f}s] Получаю данные...", flush=True)
                qr_img = wait.until(EC.presence_of_element_located((By.ID, "Image1")))
                qr_code_base64 = qr_img.get_attribute("src")
                
                payment_link_element = wait.until(EC.presence_of_element_located((By.ID, "LinkMobil")))
                payment_link = payment_link_element.get_attribute("href")
                
                elapsed = time.time() - start_time
                print(f"✅ Платёж создан за {elapsed:.1f} сек!", flush=True)
                
                # СРАЗУ вызываем callback для отправки в бота
                if callback:
                    print(f"[{elapsed:.1f}s] 🚀 Отправляю в бота...", flush=True)
                    callback(payment_link, qr_code_base64)
                
                # Подготовка к следующему платежу
                try:
                    print(f"[{elapsed:.1f}s] Подготовка к следующему...", flush=True)
                    self.driver.get(ELECSNET_URL)
                    time.sleep(1)
                    
                    wait.until(EC.invisibility_of_element_located((By.ID, "loadercontainer")))
                    
                    card_input = wait.until(EC.element_to_be_clickable((By.NAME, "requisites.m-36924.f-1")))
                    card_input.clear()
                    card_input.send_keys(self.card_number)
                    
                    name_input = wait.until(EC.element_to_be_clickable((By.NAME, "requisites.m-36924.f-2")))
                    name_input.clear()
                    name_input.send_keys(self.owner_name)
                    
                    print("✅ Готов к следующему платежу!", flush=True)
                    self.is_ready = True
                except Exception as e:
                    print(f"⚠️ Не удалось подготовить: {e}", flush=True)
                    self.is_ready = False
                
                return {
                    "payment_link": payment_link,
                    "qr_base64": qr_code_base64,
                    "elapsed_time": elapsed,
                    "account_used": self.account_phone
                }
                
            except Exception as e:
                elapsed = time.time() - start_time
                print(f"❌ Ошибка: {e}", flush=True)
                self.is_ready = False
                return {"error": str(e), "elapsed_time": elapsed}
    
    def close(self):
        """Закрытие браузера"""
        with self.lock:
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
            self.is_ready = False


# Глобальный экземпляр
browser_manager = BrowserManager()
