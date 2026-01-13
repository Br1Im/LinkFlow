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
    Создание платежа с прогретым браузером - МАКСИМАЛЬНАЯ СКОРОСТЬ
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException
    import logging
    
    logger = logging.getLogger(__name__)
    driver = browser_manager.driver
    
    if not driver:
        raise Exception("Прогретый браузер недоступен")
    
    try:
        logger.info(f"[{time.time()-start_time:.1f}s] Используем прогретый браузер...")
        
        # Переходим на страницу оплаты (браузер уже авторизован)
        logger.info(f"[{time.time()-start_time:.1f}s] Переходим на страницу оплаты...")
        driver.get('https://1.elecsnet.ru/NotebookFront/services/0mhp/default.aspx?merchantId=36924&fromSegment=')
        
        # Минимальная задержка - браузер уже прогрет
        time.sleep(0.3)  # Уменьшено с 0.5
        
        # Проверяем авторизацию
        try:
            driver.find_element(By.NAME, "requisites.m-36924.f-1")
            logger.info(f"[{time.time()-start_time:.1f}s] ✅ Браузер авторизован")
        except:
            raise Exception("Браузер потерял авторизацию")
        
        # Заполняем реквизиты - БЫСТРО
        wait = WebDriverWait(driver, 8)  # Уменьшено с 10
        
        logger.info(f"[{time.time()-start_time:.1f}s] Заполняю реквизиты...")
        
        # Карта
        card_input = wait.until(EC.element_to_be_clickable((By.NAME, "requisites.m-36924.f-1")))
        card_input.clear()
        card_input.send_keys(requisite['card_number'])
        
        # Имя
        name_input = wait.until(EC.element_to_be_clickable((By.NAME, "requisites.m-36924.f-2")))
        name_input.clear()
        name_input.send_keys(requisite['owner_name'])
        
        # Сумма
        logger.info(f"[{time.time()-start_time:.1f}s] Заполняю сумму {amount}...")
        amount_input = wait.until(EC.element_to_be_clickable((By.NAME, "summ.transfer")))
        amount_input.clear()
        amount_formatted = f"{int(amount):,}".replace(",", " ")
        amount_input.send_keys(amount_formatted)
        
        # Минимальная задержка для обработки
        time.sleep(0.2)  # Уменьшено с 0.3
        
        # Ждем обработки суммы - АГРЕССИВНАЯ ОПТИМИЗАЦИЯ
        logger.info(f"[{time.time()-start_time:.1f}s] Ждем обработки суммы...")
        for i in range(12):  # Уменьшено с 15
            try:
                loader = driver.find_element(By.ID, "loadercontainer")
                if "display: none" in loader.get_attribute("style") or not loader.is_displayed():
                    logger.info(f"[{time.time()-start_time:.1f}s] Loader исчез после {i} попыток")
                    break
            except:
                break
            time.sleep(0.15)  # Увеличено с 0.1 для стабильности
        
        # Нажимаем Оплатить
        logger.info(f"[{time.time()-start_time:.1f}s] Ищу кнопку Оплатить...")
        submit_btn = wait.until(EC.presence_of_element_located((By.NAME, "SubmitBtn")))
        
        # Ждем активации кнопки - АГРЕССИВНАЯ ОПТИМИЗАЦИЯ
        for i in range(15):  # Уменьшено с 20
            disabled = submit_btn.get_attribute("disabled")
            if not disabled:
                logger.info(f"[{time.time()-start_time:.1f}s] Кнопка активна после {i} попыток")
                break
            time.sleep(0.15)  # Увеличено с 0.1 для стабильности
        
        # Минимальная задержка перед нажатием
        time.sleep(0.3)  # Увеличено с 0.2 для стабильности
        
        # Нажимаем кнопку
        logger.info(f"[{time.time()-start_time:.1f}s] Нажимаю кнопку Оплатить...")
        try:
            submit_btn.click()
            logger.info(f"[{time.time()-start_time:.1f}s] ✓ Кнопка нажата")
        except Exception as e:
            logger.warning(f"Обычный клик не сработал: {e}, пробую JS...")
            driver.execute_script("arguments[0].click();", submit_btn)
            logger.info(f"[{time.time()-start_time:.1f}s] ✓ Кнопка нажата (JS)")
        
        logger.info(f"[{time.time()-start_time:.1f}s] Ожидаю результат...")
        
        # Минимальная задержка для отправки формы
        time.sleep(0.5)
        
        # Ждем результат - ОПТИМИЗАЦИЯ
        for i in range(35):  # Уменьшено с 40
            try:
                # Проверяем URL - если перешли на SBP, значит готово
                current_url = driver.current_url
                if "/SBP/" in current_url or "/sbp/" in current_url.lower():
                    logger.info(f"[{time.time()-start_time:.1f}s] Переход на SBP страницу!")
                    break
                    
                loader = driver.find_element(By.ID, "loadercontainer")
                if "display: none" in loader.get_attribute("style") or not loader.is_displayed():
                    break
            except:
                break
            time.sleep(0.15)  # Увеличено с 0.1 для стабильности
        
        # Минимальная задержка для загрузки результата
        time.sleep(0.3)  # Увеличено с 0.2
        
        current_url = driver.current_url
        logger.info(f"[{time.time()-start_time:.1f}s] Текущий URL: {current_url}")
        
        logger.info(f"[{time.time()-start_time:.1f}s] Ищу результат...")
        
        wait_result = WebDriverWait(driver, 12)  # Уменьшено с 15
        
        # Ищем QR код
        qr_code_base64 = None
        try:
            qr_img = wait_result.until(EC.presence_of_element_located((By.ID, "Image1")))
            qr_code_base64 = qr_img.get_attribute("src")
            logger.info(f"[{time.time()-start_time:.1f}s] QR найден")
        except:
            try:
                qr_img = driver.find_element(By.CSS_SELECTOR, "img[src*='qr'], img[src*='data:image']")
                qr_code_base64 = qr_img.get_attribute("src")
                logger.info(f"[{time.time()-start_time:.1f}s] QR найден альтернативным способом")
            except:
                logger.error(f"[{time.time()-start_time:.1f}s] QR код не найден")
        
        # Ищем ссылку на оплату
        payment_link = None
        try:
            payment_link_element = wait_result.until(EC.presence_of_element_located((By.ID, "LinkMobil")))
            payment_link = payment_link_element.get_attribute("href")
            logger.info(f"[{time.time()-start_time:.1f}s] Ссылка найдена")
        except:
            try:
                payment_link_element = driver.find_element(By.CSS_SELECTOR, "a[href*='qr.nspk.ru'], a[href*='nspk']")
                payment_link = payment_link_element.get_attribute("href")
                logger.info(f"[{time.time()-start_time:.1f}s] Ссылка найдена альтернативным способом")
            except:
                logger.error(f"[{time.time()-start_time:.1f}s] Ссылка не найдена")
        
        if not payment_link or not qr_code_base64:
            raise Exception(f"Не удалось найти элементы результата. URL: {current_url}")
        
        elapsed = time.time() - start_time
        logger.info(f"🚀 Платеж создан за {elapsed:.1f} сек с прогретым браузером!")
        
        return {
            "payment_link": payment_link,
            "qr_base64": qr_code_base64,
            "elapsed_time": elapsed
        }
        
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"❌ Ошибка создания платежа с прогретым браузером: {e}")
        
        # Если прогретый браузер сломался, сбрасываем его состояние
        browser_manager.is_ready = False
        
        return {
            "error": str(e),
            "elapsed_time": elapsed
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
