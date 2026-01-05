# -*- coding: utf-8 -*-
"""
Сервис создания платежей с поддержкой двух режимов:
- HYBRID: Быстрый (API + Selenium) ~1-2 сек
- SELENIUM: Надежный (только Selenium) ~3-5 сек
"""

import base64
import time
import os
from browser_manager import browser_manager
from database import db
from config import *
from payment_modes import mode_manager, PaymentMode

# Импорт гибридного менеджера (опционально)
try:
    from hybrid_payment import hybrid_manager
    HYBRID_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Гибридный режим недоступен: {e}")
    HYBRID_AVAILABLE = False


def warmup_for_user(user_id):
    """
    Прогрев для пользователя (работает для обоих режимов)
    """
    requisites = db.get_requisites()
    if not requisites:
        return {"error": "Нет реквизитов"}
    
    accounts = db.get_accounts()
    if not accounts:
        return {"error": "Нет аккаунтов"}
    
    requisite = requisites[0]
    account = accounts[0]
    
    current_mode = mode_manager.get_mode()
    
    # Гибридный режим: авторизация через Selenium, получение cookies
    if current_mode == PaymentMode.HYBRID and HYBRID_AVAILABLE:
        try:
            print(f"🚀 Прогрев в HYBRID режиме...", flush=True)
            success = hybrid_manager.authorize_and_get_cookies(account)
            
            if success:
                hybrid_manager.card_number = requisite['card_number']
                hybrid_manager.owner_name = requisite['owner_name']
                mode_manager.report_hybrid_success()
                return {"success": True, "requisite": requisite, "mode": "hybrid"}
            else:
                print(f"⚠️ Гибридный режим не удался, переключаюсь на Selenium", flush=True)
                mode_manager.report_hybrid_failure()
                # Fallback на Selenium
        except Exception as e:
            print(f"⚠️ Ошибка гибридного режима: {e}", flush=True)
            mode_manager.report_hybrid_failure()
    
    # Selenium режим (или fallback)
    print(f"🔧 Прогрев в SELENIUM режиме...", flush=True)
    success = browser_manager.warmup(
        card_number=requisite['card_number'],
        owner_name=requisite['owner_name'],
        account=account
    )
    
    return {"success": success, "requisite": requisite, "mode": "selenium"}


def create_payment_fast(amount, send_callback=None):
    """
    Быстрое создание платежа (автоматический выбор режима)
    """
    current_mode = mode_manager.get_mode()
    
    # Попытка создать через гибридный режим
    if current_mode == PaymentMode.HYBRID and HYBRID_AVAILABLE:
        try:
            if hybrid_manager.is_authorized:
                print(f"⚡ Создание платежа в HYBRID режиме...", flush=True)
                
                result = hybrid_manager.create_payment_fast(
                    card_number=hybrid_manager.card_number,
                    owner_name=hybrid_manager.owner_name,
                    amount=amount
                )
                
                if result.get("success"):
                    # Обработка успешного результата
                    qr_base64 = result["qr_base64"]
                    payment_link = result["payment_link"]
                    
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
                    
                    mode_manager.report_hybrid_success()
                    
                    return {
                        "payment_link": payment_link,
                        "qr_base64": qr_base64,
                        "elapsed_time": result["elapsed_time"],
                        "mode": "hybrid"
                    }
                else:
                    print(f"⚠️ Гибридный режим вернул ошибку: {result.get('error')}", flush=True)
                    mode_manager.report_hybrid_failure()
                    # Fallback на Selenium
            else:
                print(f"⚠️ Гибридный режим не авторизован, переключаюсь на Selenium", flush=True)
                # Fallback на Selenium
        except Exception as e:
            print(f"⚠️ Ошибка гибридного режима: {e}", flush=True)
            mode_manager.report_hybrid_failure()
            # Fallback на Selenium
    
    # Selenium режим (или fallback)
    print(f"🔧 Создание платежа в SELENIUM режиме...", flush=True)
    
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
    result["mode"] = "selenium"
    
    return result


def is_browser_ready():
    """Проверка готовности браузера"""
    current_mode = mode_manager.get_mode()
    
    if current_mode == PaymentMode.HYBRID and HYBRID_AVAILABLE:
        return hybrid_manager.is_authorized
    
    return browser_manager.is_ready


def close_browser():
    """Закрытие браузера"""
    browser_manager.close()
    
    if HYBRID_AVAILABLE:
        hybrid_manager.close()
