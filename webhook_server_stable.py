# -*- coding: utf-8 -*-
"""
Стабильная версия webhook сервера - перезапускает браузер для каждого запроса
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

# Импорт для создания одноразового браузера
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins="*", methods=["GET", "POST", "OPTIONS"], 
     allow_headers=["Content-Type", "Authorization"])

db = Database()

def verify_token(token):
    return token == f"Bearer {API_TOKEN}"

def create_single_use_payment(amount):
    """Создание платежа с одноразовым браузером"""
    driver = None
    try:
        # Получаем данные из базы
        requisites = db.get_requisites()
        accounts = db.get_accounts()
        
        if not requisites or not accounts:
            return {"error": "No requisites or accounts configured"}
        
        requisite = requisites[0]
        account = accounts[0]
        
        # Создаем одноразовый браузер
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--remote-debugging-port=9223')  # Другой порт
        options.add_argument('--disable-crash-reporter')
        options.add_argument('--disable-logging')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-plugins-discovery')
        options.add_argument('--disable-translate')
        options.add_argument('--hide-scrollbars')
        options.add_argument('--mute-audio')
        options.add_argument('--disable-in-process-stack-traces')
        options.add_argument('--disable-dev-tools')
        options.add_argument('--memory-pressure-off')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--disable-ipc-flooding-protection')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-setuid-sandbox')
        options.add_argument('--disable-web-security')
        options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        service = Service('/usr/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)
        
        start_time = time.time()
        
        # Переходим на elecsnet
        driver.get('https://1.elecsnet.ru/NotebookFront/services/0mhp/default.aspx?merchantId=36924&fromSegment=')
        time.sleep(2)
        
        # Авторизация если нужна
        try:
            login_btn = driver.find_element(By.CSS_SELECTOR, "a.login[href='main']")
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
            time.sleep(1)
        except:
            pass  # Уже авторизован
        
        # Заполняем реквизиты
        wait = WebDriverWait(driver, 15)
        
        card_input = wait.until(EC.element_to_be_clickable((By.NAME, "requisites.m-36924.f-1")))
        card_input.clear()
        card_input.send_keys(requisite['card_number'])
        
        name_input = wait.until(EC.element_to_be_clickable((By.NAME, "requisites.m-36924.f-2")))
        name_input.clear()
        name_input.send_keys(requisite['owner_name'])
        
        # Заполняем сумму
        amount_input = wait.until(EC.element_to_be_clickable((By.NAME, "summ.transfer")))
        amount_input.clear()
        amount_formatted = f"{int(amount):,}".replace(",", " ")
        amount_input.send_keys(amount_formatted)
        
        time.sleep(0.5)
        
        # Нажимаем Оплатить
        submit_btn = wait.until(EC.presence_of_element_located((By.NAME, "SubmitBtn")))
        
        # Ждем активации кнопки
        for _ in range(30):
            if not submit_btn.get_attribute("disabled"):
                break
            time.sleep(0.3)
        
        time.sleep(1)
        driver.execute_script("arguments[0].click();", submit_btn)
        time.sleep(2)
        
        # Ждем результат
        for _ in range(40):
            try:
                loader = driver.find_element(By.ID, "loadercontainer")
                if "display: none" in loader.get_attribute("style") or not loader.is_displayed():
                    break
            except:
                break
            time.sleep(0.3)
        
        # Получаем данные
        qr_img = wait.until(EC.presence_of_element_located((By.ID, "Image1")))
        qr_code_base64 = qr_img.get_attribute("src")
        
        payment_link_element = wait.until(EC.presence_of_element_located((By.ID, "LinkMobil")))
        payment_link = payment_link_element.get_attribute("href")
        
        elapsed = time.time() - start_time
        
        return {
            "payment_link": payment_link,
            "qr_base64": qr_code_base64,
            "elapsed_time": elapsed
        }
        
    except Exception as e:
        elapsed = time.time() - start_time if 'start_time' in locals() else 0
        return {"error": str(e), "elapsed_time": elapsed}
    finally:
        if driver:
            try:
                driver.quit()
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
        
        existing_order = db.get_order_by_id(order_id)
        if existing_order:
            return jsonify({"success": False, "error": "Order already exists"}), 409
        
        logger.info(f"Creating STABLE payment: orderId={order_id}, amount={amount}")
        
        # Создание платежа с одноразовым браузером
        result = create_single_use_payment(amount)
        
        if not result or not result.get('payment_link'):
            error_msg = result.get('error', 'Unknown error') if result else 'No result returned'
            logger.error(f"Stable payment failed: {error_msg}")
            return jsonify({"success": False, "error": f"Payment creation failed: {error_msg}"}), 500
        
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
            "method": "stable_single_use_browser",
            "elapsed_time": result.get('elapsed_time', 0)
        }
        
        db.save_order(order_data)
        
        logger.info(f"STABLE payment created successfully: orderId={order_id}, qrcId={qrc_id}")
        
        return jsonify({
            "success": True,
            "orderId": order_id,
            "qrcId": qrc_id,
            "qr": result.get('payment_link', ''),
            "stable_mode": True
        }), 200
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
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
        logger.error(f"Error getting status: {str(e)}")
        return jsonify({"success": False, "error": "Internal server error"}), 500

@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health_check():
    if request.method == 'OPTIONS':
        return '', 200
        
    return jsonify({
        "success": True,
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "mode": "stable_single_use_browser"
    }), 200

if __name__ == '__main__':
    print("🚀 Запуск СТАБИЛЬНОГО webhook сервера...")
    print(f"📡 API endpoint: {SERVER_URL}/api/payment")
    print(f"🔑 Token: {API_TOKEN}")
    print(f"💳 Card: {CARD_NUMBER}")
    print(f"👤 Owner: {CARD_OWNER}")
    print("🔄 Одноразовый браузер для каждого запроса")
    print("🌐 CORS включен для всех доменов")
    
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=False)