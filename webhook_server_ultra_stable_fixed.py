# -*- coding: utf-8 -*-
"""
УЛЬТРА СТАБИЛЬНАЯ версия webhook сервера - исправлена проблема с падением браузера
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import uuid
import time
from datetime import datetime
from database import Database
from webhook_config import API_TOKEN, CARD_NUMBER, CARD_OWNER, SERVER_HOST, SERVER_PORT, SERVER_URL
import logging
import subprocess
import os
import signal

# Импорт для создания браузера
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, WebDriverException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins="*", methods=["GET", "POST", "OPTIONS"], 
     allow_headers=["Content-Type", "Authorization"])

db = Database()

def verify_token(token):
    return token == f"Bearer {API_TOKEN}"

def kill_chrome_processes():
    """Убиваем все процессы Chrome перед запуском"""
    try:
        # Для Linux
        subprocess.run(['pkill', '-f', 'chrome'], capture_output=True, timeout=5)
        subprocess.run(['pkill', '-f', 'chromium'], capture_output=True, timeout=5)
        time.sleep(1)
    except:
        try:
            # Для Windows (если вдруг)
            subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], capture_output=True, timeout=5)
            time.sleep(1)
        except:
            pass

def create_ultra_stable_driver():
    """Создание максимально стабильного Chrome драйвера"""
    
    # Убиваем все процессы Chrome
    kill_chrome_processes()
    
    options = webdriver.ChromeOptions()
    
    # КРИТИЧЕСКИ ВАЖНЫЕ настройки для стабильности
    options.add_argument('--headless=new')  # Новый headless режим
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--disable-setuid-sandbox')
    
    # Отключаем все что может вызвать проблемы
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-plugins')
    options.add_argument('--disable-images')
    options.add_argument('--disable-javascript')  # Отключаем JS для стабильности
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-features=VizDisplayCompositor')
    options.add_argument('--disable-features=LockProfileCookieDatabase')
    options.add_argument('--disable-site-isolation-trials')
    options.add_argument('--disable-background-networking')
    options.add_argument('--disable-sync')
    options.add_argument('--disable-default-apps')
    options.add_argument('--disable-background-timer-throttling')
    options.add_argument('--disable-backgrounding-occluded-windows')
    options.add_argument('--disable-renderer-backgrounding')
    options.add_argument('--disable-field-trial-config')
    options.add_argument('--disable-ipc-flooding-protection')
    
    # Память и производительность
    options.add_argument('--memory-pressure-off')
    options.add_argument('--max_old_space_size=4096')
    options.add_argument('--single-process')  # Один процесс для стабильности
    
    # Размер окна
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--start-maximized')
    
    # Отключаем логи и автоматизацию
    options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Быстрая загрузка страниц
    options.page_load_strategy = 'eager'
    
    # Создаем временную директорию для профиля
    import tempfile
    temp_dir = tempfile.mkdtemp()
    options.add_argument(f'--user-data-dir={temp_dir}')
    
    try:
        # Пробуем создать драйвер с Service
        service = Service('/usr/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=options)
    except:
        try:
            # Если не получилось, пробуем без Service
            driver = webdriver.Chrome(options=options)
        except Exception as e:
            logger.error(f"Не удалось создать Chrome драйвер: {e}")
            raise
    
    # Устанавливаем таймауты
    driver.set_page_load_timeout(60)
    driver.implicitly_wait(10)
    
    return driver

def create_payment_ultra_stable(amount):
    """Создание платежа с максимальной стабильностью"""
    driver = None
    start_time = time.time()
    
    try:
        # Получаем данные из базы
        requisites = db.get_requisites()
        accounts = db.get_accounts()
        
        if not requisites or not accounts:
            return {"error": "No requisites or accounts configured", "elapsed_time": 0}
        
        requisite = requisites[0]
        account = accounts[0]
        
        logger.info(f"[{time.time()-start_time:.1f}s] Создаю ультра-стабильный браузер...")
        
        # Создаем драйвер
        driver = create_ultra_stable_driver()
        
        logger.info(f"[{time.time()-start_time:.1f}s] Браузер создан, открываю elecsnet...")
        
        # Переходим на elecsnet с повторными попытками
        max_retries = 3
        for attempt in range(max_retries):
            try:
                driver.get('https://1.elecsnet.ru/NotebookFront/services/0mhp/default.aspx?merchantId=36924&fromSegment=')
                logger.info(f"[{time.time()-start_time:.1f}s] Страница загружена (попытка {attempt + 1})")
                break
            except Exception as e:
                logger.warning(f"Попытка {attempt + 1} не удалась: {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2)
        
        time.sleep(3)  # Даем время на загрузку
        
        # Проверяем, нужна ли авторизация
        is_authorized = False
        try:
            # Ищем кнопку логина
            login_btn = driver.find_element(By.CSS_SELECTOR, "a.login[href='main']")
            logger.info(f"[{time.time()-start_time:.1f}s] Требуется авторизация...")
            
            # Включаем JavaScript для авторизации
            driver.execute_script("document.querySelector('a.login[href=\"main\"]').click();")
            time.sleep(2)
            
            wait = WebDriverWait(driver, 15)
            popup = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.popup.login")))
            
            phone_input = driver.find_element(By.CSS_SELECTOR, "div.popup.login #Login_Value")
            phone_clean = account['phone'].replace("+7", "").replace(" ", "").replace("-", "")
            phone_input.send_keys(phone_clean)
            
            password_input = driver.find_element(By.CSS_SELECTOR, "div.popup.login #Password_Value")
            password_input.send_keys(account['password'])
            
            auth_btn = driver.find_element(By.CSS_SELECTOR, "div.popup.login #authBtn")
            driver.execute_script("arguments[0].click();", auth_btn)
            time.sleep(5)
            
            # Перезагружаем страницу после авторизации
            driver.get('https://1.elecsnet.ru/NotebookFront/services/0mhp/default.aspx?merchantId=36924&fromSegment=')
            time.sleep(3)
            
            # Проверяем успешность авторизации
            try:
                driver.find_element(By.NAME, "requisites.m-36924.f-1")
                is_authorized = True
                logger.info(f"[{time.time()-start_time:.1f}s] ✅ Авторизация успешна")
            except:
                raise Exception("Авторизация не удалась - форма оплаты не найдена")
                
        except Exception as auth_error:
            if "форма оплаты не найдена" in str(auth_error):
                raise auth_error
            # Если кнопки логина нет, проверяем наличие формы
            try:
                driver.find_element(By.NAME, "requisites.m-36924.f-1")
                is_authorized = True
                logger.info(f"[{time.time()-start_time:.1f}s] ✅ Уже авторизован")
            except:
                raise Exception("Не авторизован и не удалось авторизоваться")
        
        if not is_authorized:
            raise Exception("Авторизация не выполнена")
        
        # Заполняем реквизиты
        wait = WebDriverWait(driver, 20)
        
        logger.info(f"[{time.time()-start_time:.1f}s] Заполняю реквизиты...")
        
        # Ждем загрузки формы
        card_input = wait.until(EC.element_to_be_clickable((By.NAME, "requisites.m-36924.f-1")))
        card_input.clear()
        card_input.send_keys(requisite['card_number'])
        
        name_input = wait.until(EC.element_to_be_clickable((By.NAME, "requisites.m-36924.f-2")))
        name_input.clear()
        name_input.send_keys(requisite['owner_name'])
        
        # Заполняем сумму
        logger.info(f"[{time.time()-start_time:.1f}s] Заполняю сумму {amount}...")
        amount_input = wait.until(EC.element_to_be_clickable((By.NAME, "summ.transfer")))
        amount_input.clear()
        amount_formatted = f"{int(amount):,}".replace(",", " ")
        amount_input.send_keys(amount_formatted)
        
        time.sleep(2)  # Даем время на обработку
        
        # Ждем обработку суммы
        for _ in range(30):
            try:
                loader = driver.find_element(By.ID, "loadercontainer")
                if "display: none" in loader.get_attribute("style") or not loader.is_displayed():
                    break
            except:
                break
            time.sleep(0.5)
        
        # Нажимаем Оплатить
        logger.info(f"[{time.time()-start_time:.1f}s] Ищу кнопку Оплатить...")
        submit_btn = wait.until(EC.presence_of_element_located((By.NAME, "SubmitBtn")))
        
        # Ждем активации кнопки
        for i in range(40):
            disabled = submit_btn.get_attribute("disabled")
            if not disabled:
                logger.info(f"[{time.time()-start_time:.1f}s] Кнопка активна после {i} попыток")
                break
            time.sleep(0.5)
        else:
            logger.warning(f"[{time.time()-start_time:.1f}s] Кнопка все еще disabled, но продолжаю...")
        
        time.sleep(2)
        
        # Нажимаем кнопку
        logger.info(f"[{time.time()-start_time:.1f}s] Нажимаю кнопку Оплатить...")
        try:
            # Включаем JavaScript для нажатия
            driver.execute_script("arguments[0].click();", submit_btn)
            logger.info(f"[{time.time()-start_time:.1f}s] ✓ Кнопка нажата")
        except Exception as e:
            logger.error(f"Ошибка нажатия кнопки: {e}")
            # Пробуем альтернативный способ
            try:
                driver.execute_script("document.querySelector('input[name=\"SubmitBtn\"]').click();")
                logger.info(f"[{time.time()-start_time:.1f}s] ✓ Альтернативное нажатие")
            except Exception as e2:
                raise Exception(f"Не удалось нажать кнопку: {e}, {e2}")
        
        logger.info(f"[{time.time()-start_time:.1f}s] Ожидаю результат...")
        time.sleep(5)  # Увеличиваем время ожидания
        
        # Ждем результат с увеличенным таймаутом
        for _ in range(60):
            try:
                loader = driver.find_element(By.ID, "loadercontainer")
                if "display: none" in loader.get_attribute("style") or not loader.is_displayed():
                    break
            except:
                break
            time.sleep(1)
        
        # Дополнительное ожидание
        time.sleep(3)
        
        # Логируем текущий URL
        current_url = driver.current_url
        logger.info(f"[{time.time()-start_time:.1f}s] Текущий URL: {current_url}")
        
        # Получаем данные с увеличенным таймаутом
        logger.info(f"[{time.time()-start_time:.1f}s] Ищу результат...")
        
        wait_result = WebDriverWait(driver, 30)
        
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
        logger.info(f"✅ Платеж создан за {elapsed:.1f} сек!")
        
        return {
            "payment_link": payment_link,
            "qr_base64": qr_code_base64,
            "elapsed_time": elapsed
        }
        
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"❌ Ошибка создания платежа: {e}")
        
        # Делаем скриншот при ошибке
        screenshot_base64 = None
        page_source = None
        if driver:
            try:
                logger.info(f"[{elapsed:.1f}s] Делаю скриншот ошибки...")
                screenshot = driver.get_screenshot_as_base64()
                screenshot_base64 = f"data:image/png;base64,{screenshot}"
                
                page_source = driver.page_source[:3000]
                logger.info(f"[{elapsed:.1f}s] Скриншот сохранен")
            except Exception as screenshot_error:
                logger.error(f"Не удалось сделать скриншот: {screenshot_error}")
        
        return {
            "error": str(e), 
            "elapsed_time": elapsed,
            "screenshot": screenshot_base64,
            "page_source_preview": page_source
        }
    finally:
        # ВСЕГДА закрываем браузер
        if driver:
            try:
                driver.quit()
                logger.info(f"[{time.time()-start_time:.1f}s] Браузер закрыт")
            except:
                pass
            
            # Убиваем процессы Chrome для полной очистки
            kill_chrome_processes()

@app.route('/api/payment', methods=['POST', 'OPTIONS'])
def create_payment():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        # Проверка авторизации
        auth_header = request.headers.get('Authorization')
        if not auth_header or not verify_token(auth_header):
            return jsonify({"success": False, "error": "Unauthorized"}), 401
        
        if request.content_type != 'application/json':
            return jsonify({"success": False, "error": "Content-Type must be application/json"}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Invalid JSON"}), 400
        
        amount = data.get('amount')
        order_id = data.get('orderId')
        
        if not amount or not order_id:
            return jsonify({"success": False, "error": "Missing required fields: amount, orderId"}), 400
        
        if not isinstance(amount, (int, float)) or amount <= 0:
            return jsonify({"success": False, "error": "Amount must be a positive number"}), 400
        
        # Проверка минимальной и максимальной суммы
        if amount < 1000:
            return jsonify({"success": False, "error": "Amount must be at least 1000"}), 400
        
        if amount > 100000:
            return jsonify({"success": False, "error": "Amount must not exceed 100000"}), 400
        
        existing_order = db.get_order_by_id(order_id)
        if existing_order:
            return jsonify({"success": False, "error": "Order already exists"}), 409
        
        logger.info(f"🚀 УЛЬТРА-СТАБИЛЬНОЕ создание платежа: orderId={order_id}, amount={amount}")
        
        # Создание платежа
        result = create_payment_ultra_stable(amount)
        
        if not result or not result.get('payment_link'):
            error_msg = result.get('error', 'Unknown error') if result else 'No result returned'
            screenshot = result.get('screenshot') if result else None
            page_source = result.get('page_source_preview') if result else None
            
            logger.error(f"Ультра-стабильный платеж не удался: {error_msg}")
            
            error_response = {
                "success": False, 
                "error": f"Payment creation failed: {error_msg}"
            }
            
            if screenshot:
                error_response["screenshot"] = screenshot
                error_response["debug_info"] = "Screenshot available - check screenshot field"
            
            if page_source:
                error_response["page_source_preview"] = page_source
            
            return jsonify(error_response), 500
        
        # Генерация уникального QRC ID
        qrc_id = f"QR{int(time.time())}{uuid.uuid4().hex[:8].upper()}"
        
        # Сохранение заказа в базу данных
        order_data = {
            "order_id": order_id,
            "qrc_id": qrc_id,
            "amount": amount,
            "payment_link": result.get('payment_link', ''),
            "qr_base64": result.get('qr_base64', ''),
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "method": "ultra_stable_fixed",
            "elapsed_time": result.get('elapsed_time', 0)
        }
        
        db.save_order(order_data)
        
        logger.info(f"✅ УЛЬТРА-СТАБИЛЬНЫЙ платеж создан: orderId={order_id}, qrcId={qrc_id}, время={result.get('elapsed_time', 0):.1f}s")
        
        return jsonify({
            "success": True,
            "orderId": order_id,
            "qrcId": qrc_id,
            "qr": result.get('payment_link', ''),
            "ultra_stable_mode": True,
            "elapsed_time": result.get('elapsed_time', 0)
        }), 200
        
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {str(e)}")
        return jsonify({"success": False, "error": "Internal server error"}), 500

@app.route('/api/status/<order_id>', methods=['GET', 'OPTIONS'])
def get_payment_status(order_id):
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not verify_token(auth_header):
            return jsonify({"success": False, "error": "Unauthorized"}), 401
        
        order = db.get_order_by_id(order_id)
        if not order:
            return jsonify({"success": False, "error": "Order not found"}), 404
        
        return jsonify({
            "success": True,
            "orderId": order['order_id'],
            "status": order['status'],
            "amount": order['amount'],
            "createdAt": order['created_at']
        }), 200
        
    except Exception as e:
        logger.error(f"Ошибка получения статуса: {str(e)}")
        return jsonify({"success": False, "error": "Internal server error"}), 500

@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health_check():
    if request.method == 'OPTIONS':
        return '', 200
        
    return jsonify({
        "success": True,
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "mode": "ultra_stable_fixed"
    }), 200

if __name__ == '__main__':
    print("🚀 Запуск УЛЬТРА-СТАБИЛЬНОГО webhook сервера (ИСПРАВЛЕНО)...")
    print(f"📡 API endpoint: {SERVER_URL}/api/payment")
    print(f"🔑 Token: {API_TOKEN}")
    print(f"💳 Card: {CARD_NUMBER}")
    print(f"👤 Owner: {CARD_OWNER}")
    print("🛡️ Максимальная стабильность Chrome")
    print("🔧 Исправлены проблемы с падением браузера")
    print("🌐 CORS включен для всех доменов")
    print("⚡ Готов к работе!")
    
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=False)