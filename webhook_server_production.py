# -*- coding: utf-8 -*-
"""
ПРОДАКШН версия webhook сервера - стабильная работа с curl
Создает новый браузер для каждого запроса
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

# Импорт для создания браузера
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import os
import base64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins="*", methods=["GET", "POST", "OPTIONS"], 
     allow_headers=["Content-Type", "Authorization"])

db = Database()

def verify_token(token):
    return token == f"Bearer {API_TOKEN}"

def create_fresh_payment(amount):
    """Создание платежа с новым браузером для каждого запроса"""
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
        
        logger.info(f"[{time.time()-start_time:.1f}s] Создаю новый браузер...")
        
        # Создаем НОВЫЙ браузер для каждого запроса
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-features=LockProfileCookieDatabase')
        options.add_argument('--disable-site-isolation-trials')
        options.add_argument('--disable-background-networking')
        options.add_argument('--disable-sync')
        options.add_argument('--metrics-recording-only')
        options.add_argument('--disable-default-apps')
        options.add_argument('--no-first-run')
        options.add_argument('--disable-setuid-sandbox')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--no-default-browser-check')
        options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        options.page_load_strategy = 'eager'
        
        service = Service('/usr/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)
        
        logger.info(f"[{time.time()-start_time:.1f}s] Открываю elecsnet...")
        
        # Переходим на elecsnet
        driver.get('https://1.elecsnet.ru/NotebookFront/services/0mhp/default.aspx?merchantId=36924&fromSegment=')
        time.sleep(2)
        
        # Проверяем, нужна ли авторизация
        is_authorized = False
        try:
            # Проверяем наличие кнопки логина
            login_btn = driver.find_element(By.CSS_SELECTOR, "a.login[href='main']")
            logger.info(f"[{time.time()-start_time:.1f}s] Требуется авторизация, выполняю...")
            
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
            
            # Перезагружаем страницу после авторизации
            driver.get('https://1.elecsnet.ru/NotebookFront/services/0mhp/default.aspx?merchantId=36924&fromSegment=')
            time.sleep(2)
            
            # Проверяем успешность авторизации - должна быть форма оплаты
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
        wait = WebDriverWait(driver, 15)
        
        logger.info(f"[{time.time()-start_time:.1f}s] Заполняю реквизиты...")
        
        card_input = wait.until(EC.element_to_be_clickable((By.NAME, "requisites.m-36924.f-1")))
        card_input.clear()
        card_input.send_keys(requisite['card_number'])
        
        name_input = wait.until(EC.element_to_be_clickable((By.NAME, "requisites.m-36924.f-2")))
        name_input.clear()
        name_input.send_keys(requisite['owner_name'])
        
        # Заполняем сумму
        logger.info(f"[{time.time()-start_time:.1f}s] Заполняю сумму...")
        amount_input = wait.until(EC.element_to_be_clickable((By.NAME, "summ.transfer")))
        amount_input.clear()
        amount_formatted = f"{int(amount):,}".replace(",", " ")
        amount_input.send_keys(amount_formatted)
        
        time.sleep(0.5)
        
        # Ждем обработку
        for _ in range(30):
            try:
                loader = driver.find_element(By.ID, "loadercontainer")
                if "display: none" in loader.get_attribute("style") or not loader.is_displayed():
                    break
            except:
                break
            time.sleep(0.2)
        
        # Нажимаем Оплатить
        logger.info(f"[{time.time()-start_time:.1f}s] Нажимаю Оплатить...")
        submit_btn = wait.until(EC.presence_of_element_located((By.NAME, "SubmitBtn")))
        
        # Проверяем состояние кнопки
        logger.info(f"[{time.time()-start_time:.1f}s] Проверяю состояние кнопки...")
        logger.info(f"  - disabled: {submit_btn.get_attribute('disabled')}")
        logger.info(f"  - class: {submit_btn.get_attribute('class')}")
        logger.info(f"  - displayed: {submit_btn.is_displayed()}")
        logger.info(f"  - enabled: {submit_btn.is_enabled()}")
        
        # Ждем активации кнопки
        for i in range(30):
            disabled = submit_btn.get_attribute("disabled")
            if not disabled:
                logger.info(f"[{time.time()-start_time:.1f}s] Кнопка активна после {i} попыток")
                break
            time.sleep(0.3)
        else:
            logger.warning(f"[{time.time()-start_time:.1f}s] Кнопка все еще disabled!")
        
        time.sleep(1)
        
        # Пробуем разные способы нажатия
        logger.info(f"[{time.time()-start_time:.1f}s] Пробую нажать кнопку...")
        try:
            # Способ 1: JavaScript click
            driver.execute_script("arguments[0].click();", submit_btn)
            logger.info(f"[{time.time()-start_time:.1f}s] ✓ JavaScript click выполнен")
        except Exception as e1:
            logger.error(f"JavaScript click failed: {e1}")
            try:
                # Способ 2: обычный click
                submit_btn.click()
                logger.info(f"[{time.time()-start_time:.1f}s] ✓ Обычный click выполнен")
            except Exception as e2:
                logger.error(f"Regular click failed: {e2}")
                # Способ 3: submit формы
                try:
                    form = driver.find_element(By.TAG_NAME, "form")
                    form.submit()
                    logger.info(f"[{time.time()-start_time:.1f}s] ✓ Form submit выполнен")
                except Exception as e3:
                    logger.error(f"Form submit failed: {e3}")
                    raise Exception("Не удалось нажать кнопку Оплатить")
        
        logger.info(f"[{time.time()-start_time:.1f}s] Ожидаю результат...")
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
        
        # Дополнительное ожидание для загрузки результата
        time.sleep(2)
        
        # Логируем текущий URL для отладки
        current_url = driver.current_url
        logger.info(f"[{time.time()-start_time:.1f}s] Текущий URL: {current_url}")
        
        # Получаем данные - пробуем разные селекторы
        logger.info(f"[{time.time()-start_time:.1f}s] Получаю данные...")
        
        # Пробуем найти QR код по разным селекторам
        qr_img = None
        qr_code_base64 = None
        try:
            qr_img = wait.until(EC.presence_of_element_located((By.ID, "Image1")))
            qr_code_base64 = qr_img.get_attribute("src")
            logger.info(f"[{time.time()-start_time:.1f}s] QR найден по ID=Image1")
        except:
            try:
                # Пробуем найти по тегу img с src содержащим qr или base64
                qr_img = driver.find_element(By.CSS_SELECTOR, "img[src*='qr'], img[src*='data:image']")
                qr_code_base64 = qr_img.get_attribute("src")
                logger.info(f"[{time.time()-start_time:.1f}s] QR найден по CSS селектору")
            except:
                logger.error(f"[{time.time()-start_time:.1f}s] QR код не найден")
        
        # Пробуем найти ссылку на оплату по разным селекторам
        payment_link = None
        try:
            payment_link_element = wait.until(EC.presence_of_element_located((By.ID, "LinkMobil")))
            payment_link = payment_link_element.get_attribute("href")
            logger.info(f"[{time.time()-start_time:.1f}s] Ссылка найдена по ID=LinkMobil")
        except:
            try:
                # Пробуем найти ссылку содержащую qr.nspk.ru
                payment_link_element = driver.find_element(By.CSS_SELECTOR, "a[href*='qr.nspk.ru'], a[href*='nspk']")
                payment_link = payment_link_element.get_attribute("href")
                logger.info(f"[{time.time()-start_time:.1f}s] Ссылка найдена по CSS селектору")
            except:
                logger.error(f"[{time.time()-start_time:.1f}s] Ссылка на оплату не найдена")
        
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
                logger.info(f"[{time.time()-start_time:.1f}s] Делаю скриншот ошибки...")
                screenshot = driver.get_screenshot_as_base64()
                screenshot_base64 = f"data:image/png;base64,{screenshot}"
                
                # Также сохраняем HTML страницы
                page_source = driver.page_source[:5000]  # Первые 5000 символов
                
                logger.info(f"[{time.time()-start_time:.1f}s] Скриншот сохранен")
            except Exception as screenshot_error:
                logger.error(f"Не удалось сделать скриншот: {screenshot_error}")
        
        return {
            "error": str(e), 
            "elapsed_time": elapsed,
            "screenshot": screenshot_base64,
            "page_source": page_source
        }
    finally:
        # ВСЕГДА закрываем браузер
        if driver:
            try:
                driver.quit()
                logger.info(f"[{time.time()-start_time:.1f}s] Браузер закрыт")
            except:
                pass

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
        
        # Проверка минимальной и максимальной суммы для elecsnet.ru
        if amount < 1000:
            return jsonify({"success": False, "error": "Amount must be at least 1000 (minimum for elecsnet.ru)"}), 400
        
        if amount > 100000:
            return jsonify({"success": False, "error": "Amount must not exceed 100000 (maximum for elecsnet.ru)"}), 400
        
        existing_order = db.get_order_by_id(order_id)
        if existing_order:
            return jsonify({"success": False, "error": "Order already exists"}), 409
        
        logger.info(f"🚀 ПРОДАКШН создание платежа: orderId={order_id}, amount={amount}")
        
        # Создание платежа с новым браузером
        result = create_fresh_payment(amount)
        
        if not result or not result.get('payment_link'):
            error_msg = result.get('error', 'Unknown error') if result else 'No result returned'
            screenshot = result.get('screenshot') if result else None
            page_source = result.get('page_source') if result else None
            
            logger.error(f"Продакшн платеж не удался: {error_msg}")
            
            error_response = {
                "success": False, 
                "error": f"Payment creation failed: {error_msg}"
            }
            
            # Добавляем скриншот если есть
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
            "method": "production_fresh_browser",
            "elapsed_time": result.get('elapsed_time', 0)
        }
        
        db.save_order(order_data)
        
        logger.info(f"✅ ПРОДАКШН платеж создан: orderId={order_id}, qrcId={qrc_id}, время={result.get('elapsed_time', 0):.1f}s")
        
        return jsonify({
            "success": True,
            "orderId": order_id,
            "qrcId": qrc_id,
            "qr": result.get('payment_link', ''),
            "production_mode": True,
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
        "mode": "production_fresh_browser"
    }), 200

if __name__ == '__main__':
    print("🚀 Запуск ПРОДАКШН webhook сервера...")
    print(f"📡 API endpoint: {SERVER_URL}/api/payment")
    print(f"🔑 Token: {API_TOKEN}")
    print(f"💳 Card: {CARD_NUMBER}")
    print(f"👤 Owner: {CARD_OWNER}")
    print("🔄 Новый браузер для каждого запроса - МАКСИМАЛЬНАЯ СТАБИЛЬНОСТЬ")
    print("🌐 CORS включен для всех доменов")
    print("⚡ Готов к продакшн нагрузке!")
    
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=False)