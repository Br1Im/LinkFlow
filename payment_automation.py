# -*- coding: utf-8 -*-
"""
Автоматизация платежей через Selenium
Оставлена только функция авторизации для обратной совместимости
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from config import *


def login_account(phone: str, password: str, profile_name: str) -> dict:
    """
    Вход в аккаунт elecsnet.ru
    
    Args:
        phone: Номер телефона
        password: Пароль
        profile_name: Имя профиля браузера
    
    Returns:
        dict: {"status": "online"/"error", "message": "..."}
    """
    profile_path = os.path.join(PROFILE_BASE_PATH, profile_name)
    
    print(f"\n{'='*60}", flush=True)
    print(f"🔐 ВХОД В АККАУНТ: {phone}", flush=True)
    print(f"{'='*60}", flush=True)
    
    options = webdriver.ChromeOptions()
    options.add_argument(f'--user-data-dir={profile_path}')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    driver = None
    start_time = time.time()
    
    try:
        print(f"[{time.time()-start_time:.1f}s] Запускаю браузер...", flush=True)
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(BROWSER_TIMEOUT)
        
        print(f"[{time.time()-start_time:.1f}s] Открываю страницу...", flush=True)
        driver.get(ELECSNET_BASE_URL)
        
        wait = WebDriverWait(driver, ELEMENT_WAIT_TIMEOUT)
        time.sleep(2)
        
        try:
            login_btn = driver.find_element(By.CSS_SELECTOR, "a.login[href='main']")
            print(f"[{time.time()-start_time:.1f}s] Нажимаю кнопку Вход...", flush=True)
            driver.execute_script("arguments[0].click();", login_btn)
            time.sleep(1)
            
            popup = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.popup.login")))
            phone_input = wait.until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "div.popup.login #Login_Value")
            ))
            
            phone_clean = phone.replace("+7", "").replace(" ", "").replace("-", "")
            print(f"[{time.time()-start_time:.1f}s] Ввожу телефон: {phone_clean}", flush=True)
            phone_input.clear()
            phone_input.send_keys(phone_clean)
            
            password_input = driver.find_element(By.CSS_SELECTOR, "div.popup.login #Password_Value")
            print(f"[{time.time()-start_time:.1f}s] Ввожу пароль...", flush=True)
            password_input.clear()
            password_input.send_keys(password)
            
            print(f"[{time.time()-start_time:.1f}s] Нажимаю Войти...", flush=True)
            auth_btn = driver.find_element(By.CSS_SELECTOR, "div.popup.login #authBtn")
            driver.execute_script("arguments[0].click();", auth_btn)
            
            print(f"[{time.time()-start_time:.1f}s] Ожидаю завершения входа...", flush=True)
            time.sleep(3)
            
            driver.get(ELECSNET_URL)
            time.sleep(2)
            
            try:
                driver.find_element(By.CSS_SELECTOR, "a.login[href='main']")
                print(f"[{time.time()-start_time:.1f}s] ❌ Авторизация не удалась", flush=True)
                return {"status": "error", "message": "Авторизация не удалась"}
            except:
                print(f"[{time.time()-start_time:.1f}s] ✅ Авторизация успешна!", flush=True)
        
        except Exception as e:
            print(f"[{time.time()-start_time:.1f}s] ✅ Уже авторизован", flush=True)
        
        return {"status": "online", "message": "Вход выполнен успешно"}
    
    except Exception as e:
        print(f"❌ Ошибка: {e}", flush=True)
        return {"status": "error", "message": str(e)}
    
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
