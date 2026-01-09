# -*- coding: utf-8 -*-
"""
УЛЬТРА-СТАБИЛЬНАЯ версия webhook сервера
Минимальная конфигурация Chrome для максимальной стабильности
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
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins="*", methods=["GET", "POST", "OPTIONS"], 
     allow_headers=["Content-Type", "Authorization"])

db = Database()

def verify_token(token):
    return token == f"Bearer {API_TOKEN}"

def kill_chrome_processes():
    """Убиваем все процессы Chrome для чистого старта"""
    try:
        subprocess.run(['pkill', '-f', 'chrome'], capture_output=True)
        subprocess.run(['pkill', '-f', 'chromedriver'], capture_output=True)
        time.sleep(1)
    except:
        pass

def create_ultra_stable_payment(amount):
    """Создание платежа с ультра-стабильным браузером"""
    driver = None
    start_time = time.time()
    
    try:
        # Убиваем все старые процессы Chrome
        kill_chrome_processes()
        
        # Получаем данные из базы
        requisites = db.get_requisites()
        accounts = db.get_accounts()
        
        if not requisites or not accounts:
            return {"error": "No requisites or accounts configured", "elapsed_time": 0}
        
        requisite = requisites[0]
        account = accounts[0]
        
        logger.info(f"[{time.time()-start_time:.1f}s] Создаю ультра-стабильный браузер...")
        
        # МИНИМАЛЬНАЯ конфигурация Chrome для максимальной стабильности
        options = webdriver.ChromeOptions()
        
        # Основные опции
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        # Отключаем все что может вызвать проблемы (кроме JS)
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')
        # options.add_argument('--disable-javascript')  # НЕ отключаем JS - нужен для elecsnet
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--no-first-run')
        options.add_argument('--no-default-browser-check')
        options.add_argument('--disable-default-apps')
        options.add_argument('--disable-sync')
        options.add_argument('--disable-translate')
        options.add_argument('--disable-background-networking')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-client-side-phishing-detection')
        options.add_argument('--disable-component-extensions-with-background-pages')
        options.add_argument('--disable-ipc-flooding-protection')
        options.add_argument('--single-process')  # Один процесс для стабильности
        options.add_argument('--memory-pressure-off')
        options.add_argument('--max_old_space_size=512')  # Ограничиваем память
        
        # Отключаем логирование
        options.add_argument('--disable-logging')
        options.add_argument('--log-level=3')
        options.add_argument('--silent')
        
        # Экспериментальные опции
        options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Устанавливаем таймауты
        options.page_load_strategy = 'none'  # Не ждем полной загрузки
        
        service = Service('/usr/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(60)  # Увеличиваем таймаут
        
        logger.info(f"[{time.time()-start_time:.1f}s] Открываю elecsnet...")
        
        # Переходим на elecsnet
        driver.get('https://1.elecsnet.ru/NotebookFront/services/0mhp/default.aspx?merchantId=36924&fromSegment=')
        time.sleep(5)  # Больше времени на загрузку
        
        # Простая авторизация без сложной логики
        try:
            logger.info(f"[{time.time()-start_time:.1f}s] Ищу форму авторизации...")
            
            # Ждем появления формы
            wait = WebDriverWait(driver, 30)
            
            # Пробуем найти кнопку входа
            try:
                login_btn = driver.find_element(By.CSS_SELECTOR, "a.login[href='main']")
                logger.info(f"[{time.time()-start_time:.1f}s] Нажимаю вход...")
                login_btn.click()
                time.sleep(3)
                
                # Заполняем форму авторизации
                phone_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#Login_Value")))
                phone_clean = account['phone'].replace("+7", "").replace(" ", "").replace("-", "")
                phone_input.send_keys(phone_clean)
                
                password_input = driver.find_element(By.CSS_SELECTOR, "#Password_Value")
                password_input.send_keys(account['password'])
                
                auth_btn = driver.find_element(By.CSS_SELECTOR, "#authBtn")
                auth_btn.click()
                time.sleep(5)
                
                # Возвращаемся на страницу платежа
                driver.get('https://1.elecsnet.ru/NotebookFront/services/0mhp/default.aspx?merchantId=36924&fromSegment=')
                time.sleep(3)
                
                logger.info(f"[{time.time()-start_time:.1f}s] Авторизация выполнена")
            except:
                logger.info(f"[{time.time()-start_time:.1f}s] Уже авторизован или форма недоступна")
        except Exception as e:
            logger.warning(f"[{time.time()-start_time:.1f}s] Проблема с авторизацией: {e}")
        
        # Заполняем форму платежа
        logger.info(f"[{time.time()-start_time:.1f}s] Заполняю форму...")
        
        wait = WebDriverWait(driver, 30)
        
        # Реквизиты
        try:
            card_input = wait.until(EC.presence_of_element_located((By.NAME, "requisites.m-36924.f-1")))
            card_input.clear()
            card_input.send_keys(requisite['card_number'])
            
            name_input = driver.find_element(By.NAME, "requisites.m-36924.f-2")
            name_input.clear()
            name_input.send_keys(requisite['owner_name'])
            
            # Сумма
            amount_input = driver.find_element(By.NAME, "summ.transfer")
            amount_input.clear()
            amount_formatted = str(int(amount))  # Простое форматирование
            amount_input.send_keys(amount_formatted)
            
            time.sleep(2)
            
            # Кнопка оплатить
            submit_btn = driver.find_element(By.NAME, "SubmitBtn")
            
            # Ждем активации кнопки
            for _ in range(60):  # Больше времени ожидания
                if not submit_btn.get_attribute("disabled"):
                    break
                time.sleep(1)
            
            logger.info(f"[{time.time()-start_time:.1f}s] Нажимаю Оплатить...")
            submit_btn.click()
            
            # Ждем результат дольше
            time.sleep(10)
            
            # Получаем результат
            logger.info(f"[{time.time()-start_time:.1f}s] Получаю результат...")
            
            qr_img = wait.until(EC.presence_of_element_located((By.ID, "Image1")))
            qr_code_base64 = qr_img.get_attribute("src")
            
            payment_link_element = wait.until(EC.presence_of_element_located((By.ID, "LinkMobil")))
            payment_link = payment_link_element.get_attribute("href")
            
            elapsed = time.time() - start_time
            logger.info(f"✅ УЛЬТРА-СТАБИЛЬНЫЙ платеж создан за {elapsed:.1f} сек!")
            
            return {
                "payment_link": payment_link,
                "qr_base64": qr_code_base64,
                "elapsed_time": elapsed
            }
            
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"❌ Ошибка заполнения формы: {e}")
            return {"error": f"Form error: {str(e)}", "elapsed_time": elapsed}
        
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"❌ Критическая ошибка: {e}")
        return {"error": str(e), "elapsed_time": elapsed}
    finally:
        # ВСЕГДА закрываем браузер и убиваем процессы
        if driver:
            try:
                driver.quit()
            except:
                pass
        
        # Убиваем все процессы Chrome для чистоты
        kill_chrome_processes()
        logger.info(f"[{time.time()-start_time:.1f}s] Все процессы очищены")

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
        
        logger.info(f"🚀 УЛЬТРА-СТАБИЛЬНОЕ создание платежа: orderId={order_id}, amount={amount}")
        
        # Создание платежа с ультра-стабильным браузером
        result = create_ultra_stable_payment(amount)
        
        if not result or not result.get('payment_link'):
            error_msg = result.get('error', 'Unknown error') if result else 'No result returned'
            logger.error(f"Ультра-стабильный платеж не удался: {error_msg}")
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
            "method": "ultra_stable_browser",
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
        "mode": "ultra_stable_browser"
    }), 200

if __name__ == '__main__':
    print("🚀 Запуск УЛЬТРА-СТАБИЛЬНОГО webhook сервера...")
    print(f"📡 API endpoint: {SERVER_URL}/api/payment")
    print(f"🔑 Token: {API_TOKEN}")
    print(f"💳 Card: {CARD_NUMBER}")
    print(f"👤 Owner: {CARD_OWNER}")
    print("🛡️  УЛЬТРА-СТАБИЛЬНЫЙ режим - минимальная конфигурация Chrome")
    print("🔄 Полная очистка процессов между запросами")
    print("🌐 CORS включен для всех доменов")
    print("⚡ Готов к любой нагрузке!")
    
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=False)