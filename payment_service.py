# -*- coding: utf-8 -*-
"""
Сервис создания платежей
"""

import base64
import time
import os
from browser_manager import browser_manager
from database import db
from config import *


def warmup_for_user(user_id):
    """
    Прогрев браузера для пользователя
    Вызывается когда пользователь начинает вводить сумму
    """
    requisites = db.get_requisites()
    if not requisites:
        return {"error": "Нет реквизитов"}
    
    accounts = db.get_accounts()
    if not accounts:
        return {"error": "Нет аккаунтов"}
    
    requisite = requisites[0]
    account = accounts[0]
    
    success = browser_manager.warmup(
        card_number=requisite['card_number'],
        owner_name=requisite['owner_name'],
        account=account
    )
    
    return {"success": success, "requisite": requisite}


def create_payment_fast(amount, send_callback=None):
    """
    Быстрое создание платежа в прогретом браузере
    
    send_callback(payment_link, qr_file_path) - вызывается СРАЗУ при получении данных
    """
    
    def internal_callback(payment_link, qr_base64):
        """Внутренний callback для обработки данных"""
        # Сохраняем QR
        qr_code_data = qr_base64.split(",")[1] if "," in qr_base64 else qr_base64
        qr_filename = f"qr_{int(time.time())}.png"
        
        if not os.path.exists(QR_TEMP_PATH):
            os.makedirs(QR_TEMP_PATH)
        
        qr_filepath = os.path.join(QR_TEMP_PATH, qr_filename)
        with open(qr_filepath, "wb") as f:
            f.write(base64.b64decode(qr_code_data))
        
        # СРАЗУ отправляем в бота
        if send_callback:
            send_callback(payment_link, qr_filepath)
    
    # Создаем платеж с callback
    result = browser_manager.create_payment(amount, callback=internal_callback)
    
    return result


def is_browser_ready():
    """Проверка готовности браузера"""
    return browser_manager.is_ready


def close_browser():
    """Закрытие браузера"""
    browser_manager.close()
