# -*- coding: utf-8 -*-
"""
Сервис создания платежей с пулом браузеров
ОПТИМИЗИРОВАННАЯ ВЕРСИЯ - 8-12 секунд на платеж
Поддержка распределения нагрузки по аккаунтам и картам
"""

import base64
import time
import os
from browser_manager import browser_pool, browser_manager
from database import db
from config import *

# Флаг использования пула браузеров
USE_BROWSER_POOL = False  # Отключаем пул для стабильности


def initialize_browser_pool():
    """Инициализация пула браузеров"""
    global _pool_initialized
    
    # Проверяем, есть ли уже готовые браузеры в пуле
    status = browser_pool.get_status()
    if status['ready'] > 0:
        print(f"✅ Пул уже готов: {status['ready']}/{status['total']} браузеров", flush=True)
        return True
    
    accounts = db.get_accounts()
    requisites = db.get_requisites()
    
    if not accounts or not requisites:
        print("⚠️ Нет аккаунтов или карт для инициализации пула", flush=True)
        return False
    
    # Инициализируем только если пул пустой
    if status['total'] == 0:
        print(f"🔧 Инициализация пула: {len(accounts)} аккаунтов, {len(requisites)} карт", flush=True)
        browser_pool.initialize(accounts, requisites)
    
    # Прогреваем все браузеры параллельно
    success = browser_pool.warmup_all()
    
    if success:
        print("✅ Пул браузеров инициализирован и прогрет!", flush=True)
    
    return success


def warmup_for_user(user_id):
    """
    Прогрев браузеров (пул или одиночный)
    """
    requisites = db.get_requisites()
    if not requisites:
        return {"error": "Нет реквизитов"}
    
    accounts = db.get_accounts()
    if not accounts:
        return {"error": "Нет аккаунтов"}
    
    if USE_BROWSER_POOL:
        # Используем пул браузеров
        success = initialize_browser_pool()
        return {"success": success, "mode": "pool", "pool_status": browser_pool.get_status()}
    else:
        # Одиночный браузер (обратная совместимость)
        requisite = requisites[0]
        account = accounts[0]
        
        print(f"🔧 Прогрев в SELENIUM режиме...", flush=True)
        success = browser_manager.warmup(
            card_number=requisite['card_number'],
            owner_name=requisite['owner_name'],
            account=account
        )
        
        return {"success": success, "requisite": requisite, "mode": "selenium"}


def create_payment_fast(amount, send_callback=None):
    """
    ОПТИМИЗИРОВАННАЯ функция создания платежа - 10-15 секунд
    Использует прогретый браузер для максимальной скорости
    """
    start_time = time.time()
    
    print(f"⚡ БЫСТРОЕ создание платежа (цель 10-15 сек)...", flush=True)
    
    requisites = db.get_requisites()
    accounts = db.get_accounts()
    
    if not requisites or not accounts:
        return {
            "error": "Нет реквизитов или аккаунтов",
            "elapsed_time": time.time() - start_time,
            "success": False
        }
    
    requisite = requisites[0]
    account = accounts[0]
    
    # Проверяем готовность браузера
    if not browser_manager.is_ready:
        print(f"🔧 Браузер не готов, прогреваю...", flush=True)
        success = browser_manager.warmup(
            card_number=requisite['card_number'],
            owner_name=requisite['owner_name'],
            account=account
        )
        if not success:
            return {
                "error": "Не удалось прогреть браузер",
                "elapsed_time": time.time() - start_time,
                "success": False
            }
    
    # Используем прогретый браузер для максимальной скорости
    print(f"⚡ Используем прогретый браузер...", flush=True)
    result = create_payment_with_warmed_browser(amount, requisite, account, start_time)
    
    # Обработка результата
    if result and result.get('payment_link'):
        # Сохраняем QR код
        qr_base64 = result.get('qr_base64', '')
        if qr_base64:
            try:
                qr_code_data = qr_base64.split(",")[1] if "," in qr_base64 else qr_base64
                qr_filename = f"qr_{int(time.time())}.png"
                
                if not os.path.exists(QR_TEMP_PATH):
                    os.makedirs(QR_TEMP_PATH)
                
                qr_filepath = os.path.join(QR_TEMP_PATH, qr_filename)
                with open(qr_filepath, "wb") as f:
                    f.write(base64.b64decode(qr_code_data))
                
                result["qr_filename"] = qr_filename
                
                # Callback если есть
                if send_callback and callable(send_callback):
                    try:
                        send_callback(result['payment_link'], qr_filepath)
                    except Exception as e:
                        print(f"❌ Ошибка callback: {e}", flush=True)
            except Exception as e:
                print(f"⚠️ Ошибка сохранения QR: {e}", flush=True)
        
        result["success"] = True
        result["mode"] = "ultra_stable"
        
    else:
        if not result:
            result = {}
        result["success"] = False
        result["mode"] = "ultra_stable"
        if not result.get("error"):
            result["error"] = "Неизвестная ошибка создания платежа"
    
    return result


def create_payment_with_warmed_browser(amount, requisite, account, start_time):
    """
    Создание платежа с прогретым браузером
    ОПТИМИЗИРОВАННАЯ + СТАБИЛЬНАЯ ВЕРСИЯ
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.common.exceptions import TimeoutException
    import logging
    
    logger = logging.getLogger(__name__)
    driver = browser_manager.driver
    
    if not driver:
        raise Exception("Прогретый браузер недоступен")
    
    def wait_payment_ready(timeout=12):
        """
        Ждём:
        - исчезновение loader
        - заполнение суммы к зачислению
        - активацию кнопки Оплатить
        """
        end_time = time.time() + timeout
        while time.time() < end_time:
            try:
                loader = driver.find_element(By.ID, "loadercontainer")
                submit_btn = driver.find_element(By.NAME, "SubmitBtn")
                result_sum = driver.find_element(By.ID, "SumResultUsd")
                
                loader_ok = not loader.is_displayed()
                button_ok = submit_btn.get_attribute("disabled") is None
                result_ok = bool(result_sum.get_attribute("value"))
                
                if loader_ok and button_ok and result_ok:
                    return True
            except Exception:
                pass
            time.sleep(0.12)
        return False
    
    try:
        logger.info(f"[{time.time()-start_time:.1f}s] Открываю страницу оплаты")
        driver.get("https://1.elecsnet.ru/NotebookFront/services/0mhp/default.aspx"
                   "?merchantId=36924&fromSegment=")
        
        wait = WebDriverWait(driver, 8)
        
        # Проверка авторизации
        wait.until(lambda d: d.find_element(By.NAME, "requisites.m-36924.f-1"))
        logger.info(f"[{time.time()-start_time:.1f}s] Браузер авторизован")
        
        # Карта
        card_input = driver.find_element(By.NAME, "requisites.m-36924.f-1")
        card_input.clear()
        card_input.send_keys(requisite["card_number"])
        
        # Получатель
        name_input = driver.find_element(By.NAME, "requisites.m-36924.f-2")
        name_input.clear()
        name_input.send_keys(requisite["owner_name"])
        
        # Сумма
        amount_input = driver.find_element(By.NAME, "summ.transfer")
        amount_input.clear()
        amount_formatted = f"{int(amount):,}".replace(",", " ")
        amount_input.send_keys(amount_formatted)
        
        logger.info(f"[{time.time()-start_time:.1f}s] Сумма введена, жду расчёт")
        
        # 🔥 КЛЮЧЕВОЕ МЕСТО
        if not wait_payment_ready(timeout=15):
            raise TimeoutException("Расчёт суммы не завершился")
        
        logger.info(f"[{time.time()-start_time:.1f}s] Сумма рассчитана, нажимаю оплату")
        
        submit_btn = driver.find_element(By.NAME, "SubmitBtn")
        try:
            submit_btn.click()
        except Exception:
            driver.execute_script("arguments[0].click();", submit_btn)
        
        # Ждём переход на SBP
        end = time.time() + 12
        while time.time() < end:
            if "/sbp/" in driver.current_url.lower():
                break
            time.sleep(0.15)
        
        wait_result = WebDriverWait(driver, 10)
        
        qr_code = None
        payment_link = None
        
        try:
            qr_img = wait_result.until(lambda d: d.find_element(By.ID, "Image1"))
            qr_code = qr_img.get_attribute("src")
        except:
            pass
        
        try:
            link_el = wait_result.until(lambda d: d.find_element(By.ID, "LinkMobil"))
            payment_link = link_el.get_attribute("href")
        except:
            pass
        
        if not payment_link or not qr_code:
            raise Exception("Не удалось получить QR или ссылку")
        
        elapsed = time.time() - start_time
        logger.info(f"🚀 Платёж создан за {elapsed:.1f} сек")
        
        return {
            "payment_link": payment_link,
            "qr_base64": qr_code,
            "elapsed_time": elapsed,
        }
        
    except Exception as e:
        browser_manager.is_ready = False
        logger.error(f"❌ Ошибка платежа: {e}")
        return {
            "error": str(e),
            "elapsed_time": time.time() - start_time,
        }


def is_browser_ready():
    """Проверка готовности браузера/пула"""
    if USE_BROWSER_POOL:
        status = browser_pool.get_status()
        return status['ready'] > 0
    return browser_manager.is_ready


def get_pool_status():
    """Получить статус пула браузеров"""
    if USE_BROWSER_POOL:
        return browser_pool.get_status()
    return {"mode": "single", "ready": browser_manager.is_ready}


def close_browser():
    """Закрытие браузеров"""
    if USE_BROWSER_POOL:
        browser_pool.close_all()
    browser_manager.close()
