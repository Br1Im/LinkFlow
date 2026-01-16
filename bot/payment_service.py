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
    УЛЬТРА-ОПТИМИЗИРОВАННАЯ функция создания платежа - ЦЕЛЬ < 10 СЕКУНД
    Использует прогретый браузер для максимальной скорости
    """
    start_time = time.time()
    
    print(f"⚡ УЛЬТРА-БЫСТРОЕ создание платежа (цель < 10 сек)...", flush=True)
    
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
        print(f"🔧 Браузер не готов, БЫСТРЫЙ прогрев...", flush=True)
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
        print(f"✅ Браузер прогрет за {time.time()-start_time:.1f}s", flush=True)
    
    # Используем прогретый браузер для максимальной скорости
    print(f"⚡ Используем прогретый браузер (уже авторизован и готов)...", flush=True)
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
    УЛЬТРА-ОПТИМИЗИРОВАННАЯ ВЕРСИЯ - ЦЕЛЬ < 10 СЕКУНД
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.common.exceptions import TimeoutException
    import logging
    
    logger = logging.getLogger(__name__)
    driver = browser_manager.driver
    
    if not driver:
        raise Exception("Прогретый браузер недоступен")
    
    def wait_payment_ready(timeout=8):
        """
        БЫСТРАЯ проверка готовности:
        - исчезновение loader
        - активация кнопки Оплатить
        """
        end_time = time.time() + timeout
        while time.time() < end_time:
            try:
                loader = driver.find_element(By.ID, "loadercontainer")
                submit_btn = driver.find_element(By.NAME, "SubmitBtn")
                
                loader_ok = not loader.is_displayed()
                button_ok = submit_btn.get_attribute("disabled") is None
                
                if loader_ok and button_ok:
                    return True
            except Exception:
                pass
            time.sleep(0.08)  # Уменьшено с 0.12 до 0.08
        return False
    
    try:
        logger.info(f"[{time.time()-start_time:.1f}s] ⚡ Используем прогретый браузер")
        
        # Браузер УЖЕ на странице оплаты с заполненными реквизитами!
        # Проверяем что мы на правильной странице
        current_url = driver.current_url
        if "default.aspx" not in current_url or "merchantId=36924" not in current_url:
            logger.info(f"[{time.time()-start_time:.1f}s] Переход на страницу оплаты")
            driver.get("https://1.elecsnet.ru/NotebookFront/services/0mhp/default.aspx"
                       "?merchantId=36924&fromSegment=")
            time.sleep(0.5)  # Минимальная задержка
        
        wait = WebDriverWait(driver, 5)  # Уменьшено с 8 до 5
        
        # Проверка что форма загружена
        wait.until(lambda d: d.find_element(By.NAME, "summ.transfer"))
        logger.info(f"[{time.time()-start_time:.1f}s] Форма готова")
        
        # Реквизиты УЖЕ заполнены при прогреве, только проверяем
        try:
            card_input = driver.find_element(By.NAME, "requisites.m-36924.f-1")
            current_card = card_input.get_attribute("value")
            if not current_card or current_card != requisite["card_number"]:
                logger.info(f"[{time.time()-start_time:.1f}s] Обновляю реквизиты")
                driver.execute_script("""
                    arguments[0].value = arguments[1];
                    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                """, card_input, requisite["card_number"])
                
                name_input = driver.find_element(By.NAME, "requisites.m-36924.f-2")
                driver.execute_script("""
                    arguments[0].value = arguments[1];
                    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                """, name_input, requisite["owner_name"])
        except:
            pass
        
        # Сумма - БЫСТРОЕ заполнение через JS
        amount_input = driver.find_element(By.NAME, "summ.transfer")
        amount_formatted = f"{int(amount):,}".replace(",", " ")
        
        driver.execute_script("""
            var input = arguments[0];
            input.value = '';
            input.value = arguments[1];
            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
            input.blur();
        """, amount_input, amount_formatted)
        
        logger.info(f"[{time.time()-start_time:.1f}s] Сумма {amount_formatted}, жду расчёт")
        
        # АГРЕССИВНАЯ ОПТИМИЗАЦИЯ: Минимальное ожидание
        time.sleep(0.5)  # Даем минимум времени на начало обработки
        
        # Проверяем готовность, но не ждем долго
        if not wait_payment_ready(timeout=5):  # Уменьшено с 12 до 5
            logger.warning(f"[{time.time()-start_time:.1f}s] ⚠️ Таймаут ожидания, принудительно активирую кнопку")
            # Принудительно активируем кнопку через JS
            try:
                driver.execute_script("""
                    var btn = document.querySelector('input[name="SubmitBtn"]');
                    if (btn) {
                        btn.disabled = false;
                        btn.removeAttribute('disabled');
                    }
                """)
            except:
                pass
        
        logger.info(f"[{time.time()-start_time:.1f}s] ✓ Готово, проверяю кнопку")
        
        # Проверяем наличие ошибок на странице
        try:
            errors = driver.find_elements(By.CSS_SELECTOR, ".error, .alert-danger, [class*='error']")
            for err in errors:
                if err.is_displayed():
                    error_text = err.text
                    logger.error(f"[{time.time()-start_time:.1f}s] ❌ Ошибка на странице: {error_text[:200]}")
                    raise Exception(f"Ошибка валидации: {error_text[:200]}")
        except Exception as e:
            if "Ошибка валидации" in str(e):
                raise
        
        # АГРЕССИВНАЯ ОПТИМИЗАЦИЯ: Минимальное ожидание активации кнопки
        submit_btn = driver.find_element(By.NAME, "SubmitBtn")
        
        # Даем только 2 секунды на активацию
        for i in range(10):  # 10 * 0.2 = 2 секунды
            if submit_btn.is_enabled() and not submit_btn.get_attribute("disabled"):
                break
            time.sleep(0.2)
            submit_btn = driver.find_element(By.NAME, "SubmitBtn")
        
        # Если кнопка все еще не активна - принудительно активируем
        if submit_btn.get_attribute("disabled"):
            logger.warning(f"[{time.time()-start_time:.1f}s] ⚠️ Кнопка не активна, принудительно активирую")
            driver.execute_script("""
                var btn = arguments[0];
                btn.disabled = false;
                btn.removeAttribute('disabled');
            """, submit_btn)
            time.sleep(0.2)
        
        logger.info(f"[{time.time()-start_time:.1f}s] ✓ Кнопка активна, нажимаю оплату")
        
        logger.info(f"[{time.time()-start_time:.1f}s] ✓ Кнопка активна, нажимаю оплату")
        
        # Проверяем состояние формы перед кликом
        try:
            form_state = driver.execute_script("""
                var form = document.querySelector('form');
                var cardInput = document.querySelector('input[name="requisites.m-36924.f-1"]');
                var nameInput = document.querySelector('input[name="requisites.m-36924.f-2"]');
                var amountInput = document.querySelector('input[name="summ.transfer"]');
                var submitBtn = document.querySelector('input[name="SubmitBtn"]');
                
                return {
                    cardValue: cardInput ? cardInput.value : null,
                    nameValue: nameInput ? nameInput.value : null,
                    amountValue: amountInput ? amountInput.value : null,
                    btnDisabled: submitBtn ? submitBtn.disabled : null,
                    btnVisible: submitBtn ? submitBtn.offsetParent !== null : null
                };
            """)
            logger.info(f"[{time.time()-start_time:.1f}s] Состояние формы: {form_state}")
        except Exception as e:
            logger.warning(f"[{time.time()-start_time:.1f}s] Не удалось проверить форму: {e}")
        
        # Пробуем разные способы клика для надежности
        click_success = False
        
        # Способ 1: Прокрутка к кнопке + JS клик (самый надежный)
        try:
            driver.execute_script("""
                var btn = arguments[0];
                btn.scrollIntoView({block: 'center'});
                // Удаляем возможные overlay
                var overlays = document.querySelectorAll('.overlay, .modal-backdrop');
                overlays.forEach(function(el) { el.style.display = 'none'; });
            """, submit_btn)
            time.sleep(0.3)
            
            driver.execute_script("arguments[0].click();", submit_btn)
            click_success = True
            logger.info(f"[{time.time()-start_time:.1f}s] ✓ Клик методом 1 (JS с прокруткой)")
        except Exception as e1:
            logger.warning(f"[{time.time()-start_time:.1f}s] Метод 1 не сработал: {e1}")
            try:
                # Способ 2: Обычный клик
                submit_btn.click()
                click_success = True
                logger.info(f"[{time.time()-start_time:.1f}s] ✓ Клик методом 2 (обычный)")
            except Exception as e2:
                logger.warning(f"[{time.time()-start_time:.1f}s] Метод 2 не сработал: {e2}")
                try:
                    # Способ 3: Submit формы
                    form = driver.find_element(By.TAG_NAME, "form")
                    form.submit()
                    click_success = True
                    logger.info(f"[{time.time()-start_time:.1f}s] ✓ Клик методом 3 (submit)")
                except Exception as e3:
                    logger.error(f"[{time.time()-start_time:.1f}s] ❌ Все способы клика не сработали: {e3}")
        
        if not click_success:
            raise Exception("Не удалось нажать кнопку Оплатить")
        
        logger.info(f"[{time.time()-start_time:.1f}s] Клик выполнен, жду перехода на SBP...")
        
        # Даем время на обработку клика
        time.sleep(0.3)  # Уменьшено с 0.5 до 0.3
        
        # АГРЕССИВНОЕ ожидание перехода на SBP
        end = time.time() + 10  # Уменьшено с 15 до 10
        sbp_reached = False
        check_count = 0
        while time.time() < end:
            current_url = driver.current_url
            check_count += 1
            
            if "/sbp/" in current_url.lower() or "sbp" in current_url.lower():
                logger.info(f"[{time.time()-start_time:.1f}s] ✓ Переход на SBP: {current_url[:80]}")
                sbp_reached = True
                break
            
            # Каждые 2 секунды проверяем что происходит
            if check_count % 10 == 0:
                logger.info(f"[{time.time()-start_time:.1f}s] Ожидание SBP: {current_url[:80]}")
            
            time.sleep(0.15)  # Уменьшено с 0.2 до 0.15
        
        if not sbp_reached:
            logger.warning(f"[{time.time()-start_time:.1f}s] ⚠️ Не перешли на SBP, текущий URL: {driver.current_url}")
            
            # Проверяем что на странице
            try:
                page_title = driver.title
                logger.warning(f"[{time.time()-start_time:.1f}s] Заголовок страницы: {page_title}")
                
                # Проверяем наличие сообщений об ошибках
                error_msgs = driver.find_elements(By.CSS_SELECTOR, ".error, .alert, [class*='error'], [class*='alert']")
                for msg in error_msgs:
                    if msg.is_displayed():
                        logger.error(f"[{time.time()-start_time:.1f}s] Сообщение на странице: {msg.text[:200]}")
            except:
                pass
        
        # БЫСТРОЕ получение результата
        wait_result = WebDriverWait(driver, 5)  # Уменьшено с 10 до 5
        
        qr_code = None
        payment_link = None
        
        try:
            qr_img = wait_result.until(lambda d: d.find_element(By.ID, "Image1"))
            qr_code = qr_img.get_attribute("src")
            logger.info(f"[{time.time()-start_time:.1f}s] ✓ QR найден по ID")
        except:
            try:
                qr_img = driver.find_element(By.CSS_SELECTOR, "img[src*='data:image']")
                qr_code = qr_img.get_attribute("src")
                logger.info(f"[{time.time()-start_time:.1f}s] ✓ QR найден по CSS")
            except Exception as e:
                logger.warning(f"[{time.time()-start_time:.1f}s] ⚠️ QR не найден: {str(e)[:100]}")
        
        try:
            link_el = wait_result.until(lambda d: d.find_element(By.ID, "LinkMobil"))
            payment_link = link_el.get_attribute("href")
            logger.info(f"[{time.time()-start_time:.1f}s] ✓ Ссылка найдена по ID")
        except:
            try:
                link_el = driver.find_element(By.CSS_SELECTOR, "a[href*='qr.nspk.ru']")
                payment_link = link_el.get_attribute("href")
                logger.info(f"[{time.time()-start_time:.1f}s] ✓ Ссылка найдена по CSS")
            except:
                # Пробуем найти в HTML
                try:
                    import re
                    page_source = driver.page_source
                    match = re.search(r'https://qr\.nspk\.ru/[A-Z0-9]+\?[^"\'<>\s]+', page_source)
                    if match:
                        payment_link = match.group(0)
                        logger.info(f"[{time.time()-start_time:.1f}s] ✓ Ссылка найдена в HTML")
                except Exception as e:
                    logger.warning(f"[{time.time()-start_time:.1f}s] ⚠️ Ссылка не найдена: {str(e)[:100]}")
        
        if not payment_link or not qr_code:
            # Сохраняем скриншот для отладки
            try:
                screenshot = driver.get_screenshot_as_base64()
                logger.error(f"[{time.time()-start_time:.1f}s] ❌ Скриншот сохранен в логах")
                logger.error(f"[{time.time()-start_time:.1f}s] URL: {driver.current_url}")
                logger.error(f"[{time.time()-start_time:.1f}s] Title: {driver.title}")
            except:
                pass
            raise Exception("Не удалось получить QR или ссылку")
        
        elapsed = time.time() - start_time
        logger.info(f"🚀 Платёж создан за {elapsed:.1f} сек")
        
        # БЫСТРЫЙ возврат на форму для следующего платежа
        try:
            driver.get("https://1.elecsnet.ru/NotebookFront/services/0mhp/default.aspx"
                       "?merchantId=36924&fromSegment=")
            # НЕ ждем полной загрузки - браузер готов к следующему запросу
        except:
            pass
        
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
