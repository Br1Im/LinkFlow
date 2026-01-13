# -*- coding: utf-8 -*-
"""
Менеджер браузера с пулом и распределением нагрузки
ОПТИМИЗИРОВАННАЯ ВЕРСИЯ - 8-12 секунд на платеж
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import threading
from config import *


class BrowserInstance:
    """Один экземпляр браузера для конкретного аккаунта/карты"""
    
    def __init__(self, account, card):
        self.driver = None
        self.is_ready = False
        self.account = account
        self.card = card
        self.lock = threading.Lock()
        self.last_activity = 0
        self.payment_count = 0
    
    def _create_driver(self):
        """Создание драйвера Chrome (КАК В РАБОЧЕМ КОДЕ)"""
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        from selenium.webdriver.chrome.service import Service as ChromeService
        import subprocess
        
        # АГРЕССИВНАЯ очистка всех Chrome процессов перед запуском
        try:
            # Убиваем все процессы Chrome/ChromeDriver принудительно
            subprocess.run(['pkill', '-9', '-f', 'chrome'], capture_output=True, timeout=10)
            subprocess.run(['pkill', '-9', '-f', 'chromium'], capture_output=True, timeout=10)
            subprocess.run(['pkill', '-9', '-f', 'chromedriver'], capture_output=True, timeout=10)
            
            # Очищаем временные файлы и сокеты
            subprocess.run(['rm', '-rf', '/tmp/.com.google.Chrome.*'], capture_output=True, timeout=5)
            subprocess.run(['rm', '-rf', '/tmp/chrome_*'], capture_output=True, timeout=5)
            subprocess.run(['rm', '-rf', '/tmp/.org.chromium.*'], capture_output=True, timeout=5)
            
            # Ждем полной очистки
            time.sleep(2)
            print("🧹 Агрессивная очистка Chrome процессов завершена", flush=True)
        except Exception as e:
            print(f"⚠️ Ошибка очистки процессов: {e}", flush=True)
        
        options = ChromeOptions()
        
        # МАКСИМАЛЬНО СТАБИЛЬНЫЕ опции для Docker
        # options.add_argument('--headless=new')  # Отключаем headless - используем Xvfb
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-setuid-sandbox')
        
        # КРИТИЧНО для стабильности в Docker
        options.add_argument('--single-process')  # Один процесс - меньше конфликтов
        options.add_argument('--no-zygote')       # Отключаем zygote процесс
        options.add_argument('--disable-dev-tools')
        options.add_argument('--disable-crash-reporter')
        options.add_argument('--disable-in-process-stack-traces')
        options.add_argument('--disable-logging')
        options.add_argument('--log-level=3')     # Минимум логов
        options.add_argument('--silent')
        
        # Память и производительность - УЛУЧШЕНО
        options.add_argument('--memory-pressure-off')
        options.add_argument('--max_old_space_size=3072')  # Увеличено до 3GB
        options.add_argument('--aggressive-cache-discard')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        
        # Отключаем всё что может вызвать проблемы
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-features=LockProfileCookieDatabase')
        options.add_argument('--disable-site-isolation-trials')
        options.add_argument('--disable-background-networking')
        options.add_argument('--disable-sync')
        options.add_argument('--disable-default-apps')
        options.add_argument('--disable-field-trial-config')
        options.add_argument('--disable-ipc-flooding-protection')
        
        # Размер окна
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--start-maximized')
        
        # Отключаем логи и автоматизацию
        options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Быстрая загрузка страниц
        options.page_load_strategy = 'eager'
        
        try:
            service = ChromeService('/usr/bin/chromedriver')  # Как в git!
            driver = webdriver.Chrome(service=service, options=options)
        except:
            try:
                driver = webdriver.Chrome(options=options)
            except Exception as e:
                print(f"❌ Не удалось создать Chrome драйвер: {e}", flush=True)
                raise
        
        driver.set_page_load_timeout(60)
        driver.implicitly_wait(10)
        return driver
    
    def warmup(self):
        """Прогрев браузера"""
        with self.lock:
            if self.is_ready and self.driver:
                return True
            
            try:
                print(f"🔥 Прогрев браузера для {self.account['phone']}...", flush=True)
                start = time.time()
                
                self.driver = self._create_driver()
                print(f"  📌 Драйвер создан, загружаю {ELECSNET_URL}...", flush=True)
                self.driver.get(ELECSNET_URL)
                print(f"  📌 Страница загружена за {time.time()-start:.1f}s", flush=True)
                
                # Авторизация
                try:
                    login_btn = self.driver.find_element(By.CSS_SELECTOR, ".login")
                    self.driver.execute_script("arguments[0].click();", login_btn)
                    print(f"  📌 Кнопка входа нажата", flush=True)
                    time.sleep(2)
                    
                    phone_input = self.driver.find_element(By.ID, "Login_Value")
                    password_input = self.driver.find_element(By.ID, "Password_Value")
                    auth_btn = self.driver.find_element(By.ID, "authBtn")
                    
                    phone_clean = self.account['phone'].replace("+7", "").replace(" ", "").replace("-", "")
                    self.driver.execute_script("""
                        arguments[0].value = arguments[2];
                        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                        arguments[1].value = arguments[3];
                        arguments[1].dispatchEvent(new Event('input', { bubbles: true }));
                    """, phone_input, password_input, phone_clean, self.account['password'])
                    
                    time.sleep(0.5)
                    self.driver.execute_script("arguments[0].click();", auth_btn)
                    print(f"  📌 Авторизация отправлена", flush=True)
                    time.sleep(3)
                    self.driver.get(ELECSNET_URL)
                    time.sleep(1)
                except Exception as auth_err:
                    print(f"  ⚠️ Авторизация пропущена: {auth_err}", flush=True)
                
                # Ждем загрузки
                print(f"  📌 Ожидание загрузки страницы...", flush=True)
                wait = WebDriverWait(self.driver, 20)
                wait.until(EC.invisibility_of_element_located((By.ID, "loadercontainer")))
                print(f"  📌 Лоадер скрыт", flush=True)
                
                # Заполняем реквизиты
                card_input = wait.until(EC.presence_of_element_located((By.NAME, "requisites.m-36924.f-1")))
                name_input = wait.until(EC.presence_of_element_located((By.NAME, "requisites.m-36924.f-2")))
                print(f"  📌 Поля найдены, заполняю реквизиты...", flush=True)
                
                self.driver.execute_script("""
                    arguments[0].value = arguments[2];
                    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                    arguments[1].value = arguments[3];
                    arguments[1].dispatchEvent(new Event('input', { bubbles: true }));
                """, card_input, name_input, self.card['card_number'], self.card['owner_name'])
                
                self.is_ready = True
                self.last_activity = time.time()
                print(f"✅ Браузер прогрет за {time.time()-start:.1f}s", flush=True)
                return True
                
            except Exception as e:
                print(f"❌ Ошибка прогрева: {e}", flush=True)
                if self.driver:
                    try:
                        self.driver.quit()
                    except:
                        pass
                    self.driver = None
                self.is_ready = False
                return False

    def create_payment(self, amount):
        """Создание платежа (ТОЧНО КАК В РАБОЧЕМ GIT КОДЕ)"""
        start_time = time.time()
        driver = None
        
        try:
            print(f"[{time.time()-start_time:.1f}s] Создаю ультра-стабильный браузер...", flush=True)
            
            # Создаём свежий браузер
            driver = self._create_driver()
            
            print(f"[{time.time()-start_time:.1f}s] Браузер создан, открываю elecsnet...", flush=True)
            
            # Переходим на elecsnet с повторными попытками
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    driver.get(ELECSNET_URL)
                    print(f"[{time.time()-start_time:.1f}s] Страница загружена (попытка {attempt + 1})", flush=True)
                    break
                except Exception as e:
                    print(f"Попытка {attempt + 1} не удалась: {e}", flush=True)
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(2)
            
            time.sleep(3)
            
            # Проверяем, нужна ли авторизация
            is_authorized = False
            try:
                login_btn = driver.find_element(By.CSS_SELECTOR, "a.login[href='main']")
                print(f"[{time.time()-start_time:.1f}s] Требуется авторизация...", flush=True)
                
                driver.execute_script("document.querySelector('a.login[href=\"main\"]').click();")
                time.sleep(2)
                
                wait = WebDriverWait(driver, 15)
                popup = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.popup.login")))
                
                phone_input = driver.find_element(By.CSS_SELECTOR, "div.popup.login #Login_Value")
                phone_clean = self.account['phone'].replace("+7", "").replace(" ", "").replace("-", "")
                phone_input.send_keys(phone_clean)
                
                password_input = driver.find_element(By.CSS_SELECTOR, "div.popup.login #Password_Value")
                password_input.send_keys(self.account['password'])
                
                auth_btn = driver.find_element(By.CSS_SELECTOR, "div.popup.login #authBtn")
                driver.execute_script("arguments[0].click();", auth_btn)
                time.sleep(5)
                
                # Перезагружаем страницу после авторизации
                driver.get(ELECSNET_URL)
                time.sleep(3)
                
                # Проверяем успешность авторизации
                try:
                    driver.find_element(By.NAME, "requisites.m-36924.f-1")
                    is_authorized = True
                    print(f"[{time.time()-start_time:.1f}s] ✅ Авторизация успешна", flush=True)
                except:
                    raise Exception("Авторизация не удалась - форма оплаты не найдена")
                    
            except Exception as auth_error:
                if "форма оплаты не найдена" in str(auth_error):
                    raise auth_error
                # Если кнопки логина нет, проверяем наличие формы
                try:
                    driver.find_element(By.NAME, "requisites.m-36924.f-1")
                    is_authorized = True
                    print(f"[{time.time()-start_time:.1f}s] ✅ Уже авторизован", flush=True)
                except:
                    raise Exception("Не авторизован и не удалось авторизоваться")
            
            if not is_authorized:
                raise Exception("Авторизация не выполнена")
            
            # Заполняем реквизиты (КАК В GIT)
            wait = WebDriverWait(driver, 20)
            
            print(f"[{time.time()-start_time:.1f}s] Заполняю реквизиты...", flush=True)
            
            # Ждем загрузки формы
            card_input = wait.until(EC.element_to_be_clickable((By.NAME, "requisites.m-36924.f-1")))
            card_input.clear()
            card_input.send_keys(self.card['card_number'])
            
            name_input = wait.until(EC.element_to_be_clickable((By.NAME, "requisites.m-36924.f-2")))
            name_input.clear()
            name_input.send_keys(self.card['owner_name'])
            
            # Заполняем сумму (КАК В GIT)
            print(f"[{time.time()-start_time:.1f}s] Заполняю сумму {amount}...", flush=True)
            amount_input = wait.until(EC.element_to_be_clickable((By.NAME, "summ.transfer")))
            amount_input.clear()
            amount_formatted = f"{int(amount):,}".replace(",", " ")
            amount_input.send_keys(amount_formatted)
            
            time.sleep(2)  # Даем время на обработку
            
            # Ждем обработки суммы
            for _ in range(30):
                try:
                    loader = driver.find_element(By.ID, "loadercontainer")
                    if "display: none" in loader.get_attribute("style") or not loader.is_displayed():
                        break
                except:
                    break
                time.sleep(0.5)
            
            # Нажимаем Оплатить
            print(f"[{time.time()-start_time:.1f}s] Ищу кнопку Оплатить...", flush=True)
            submit_btn = wait.until(EC.presence_of_element_located((By.NAME, "SubmitBtn")))
            
            # Ждем активации кнопки
            for i in range(40):
                disabled = submit_btn.get_attribute("disabled")
                if not disabled:
                    print(f"[{time.time()-start_time:.1f}s] Кнопка активна после {i} попыток", flush=True)
                    break
                time.sleep(0.5)
            else:
                print(f"[{time.time()-start_time:.1f}s] Кнопка все еще disabled, но продолжаю...", flush=True)
            
            time.sleep(2)
            
            # Нажимаем кнопку
            print(f"[{time.time()-start_time:.1f}s] Нажимаю кнопку Оплатить...", flush=True)
            try:
                # Включаем JavaScript для нажатия
                driver.execute_script("arguments[0].click();", submit_btn)
                print(f"[{time.time()-start_time:.1f}s] ✓ Кнопка нажата", flush=True)
            except Exception as e:
                print(f"Ошибка нажатия кнопки: {e}", flush=True)
                # Пробуем альтернативный способ
                try:
                    driver.execute_script("document.querySelector('input[name=\"SubmitBtn\"]').click();")
                    print(f"[{time.time()-start_time:.1f}s] ✓ Альтернативное нажатие", flush=True)
                except Exception as e2:
                    raise Exception(f"Не удалось нажать кнопку: {e}, {e2}")
            
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
            print(f"[{time.time()-start_time:.1f}s] Текущий URL: {current_url}", flush=True)
            
            # Получаем данные с увеличенным таймаутом
            print(f"[{time.time()-start_time:.1f}s] Ищу результат...", flush=True)
            
            wait_result = WebDriverWait(driver, 30)
            
            # Ищем QR код
            qr_code_base64 = None
            try:
                qr_img = wait_result.until(EC.presence_of_element_located((By.ID, "Image1")))
                qr_code_base64 = qr_img.get_attribute("src")
                print(f"[{time.time()-start_time:.1f}s] QR найден", flush=True)
            except:
                try:
                    qr_img = driver.find_element(By.CSS_SELECTOR, "img[src*='qr'], img[src*='data:image']")
                    qr_code_base64 = qr_img.get_attribute("src")
                    print(f"[{time.time()-start_time:.1f}s] QR найден альтернативным способом", flush=True)
                except:
                    print(f"[{time.time()-start_time:.1f}s] QR код не найден", flush=True)
            
            # Ищем ссылку на оплату
            payment_link = None
            try:
                payment_link_element = wait_result.until(EC.presence_of_element_located((By.ID, "LinkMobil")))
                payment_link = payment_link_element.get_attribute("href")
                print(f"[{time.time()-start_time:.1f}s] Ссылка найдена", flush=True)
            except:
                try:
                    payment_link_element = driver.find_element(By.CSS_SELECTOR, "a[href*='qr.nspk.ru'], a[href*='nspk']")
                    payment_link = payment_link_element.get_attribute("href")
                    print(f"[{time.time()-start_time:.1f}s] Ссылка найдена альтернативным способом", flush=True)
                except:
                    print(f"[{time.time()-start_time:.1f}s] Ссылка не найдена", flush=True)
            
            if not payment_link or not qr_code_base64:
                raise Exception(f"Не удалось найти элементы результата. URL: {current_url}")
            
            elapsed = time.time() - start_time
            print(f"✅ Платеж создан за {elapsed:.1f} сек!", flush=True)
            
            return {
                "payment_link": payment_link,
                "qr_base64": qr_code_base64,
                "elapsed_time": elapsed
            }
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ Ошибка создания платежа: {e}", flush=True)
            
            # Делаем скриншот при ошибке
            screenshot_base64 = None
            page_source = None
            if driver:
                try:
                    print(f"[{elapsed:.1f}s] Делаю скриншот ошибки...", flush=True)
                    screenshot = driver.get_screenshot_as_base64()
                    screenshot_base64 = f"data:image/png;base64,{screenshot}"
                    
                    page_source = driver.page_source[:3000]
                    print(f"[{elapsed:.1f}s] Скриншот сохранен", flush=True)
                except Exception as screenshot_error:
                    print(f"Не удалось сделать скриншот: {screenshot_error}", flush=True)
            
            return {
                "error": str(e),
                "elapsed_time": elapsed,
                "screenshot": screenshot_base64,
                "page_source_preview": page_source
            }
        finally:
            # АГРЕССИВНОЕ закрытие браузера и очистка процессов
            if driver:
                try:
                    # Сначала пытаемся закрыть нормально
                    driver.quit()
                    print(f"[{time.time()-start_time:.1f}s] Браузер закрыт", flush=True)
                except Exception as e:
                    print(f"[{time.time()-start_time:.1f}s] Ошибка закрытия браузера: {e}", flush=True)
                
                # ПРИНУДИТЕЛЬНО убиваем все процессы Chrome
                try:
                    import subprocess
                    subprocess.run(['pkill', '-9', '-f', 'chrome'], capture_output=True, timeout=10)
                    subprocess.run(['pkill', '-9', '-f', 'chromium'], capture_output=True, timeout=10)
                    subprocess.run(['pkill', '-9', '-f', 'chromedriver'], capture_output=True, timeout=10)
                    
                    # Очищаем временные файлы
                    subprocess.run(['rm', '-rf', '/tmp/.com.google.Chrome.*'], capture_output=True, timeout=5)
                    subprocess.run(['rm', '-rf', '/tmp/chrome_*'], capture_output=True, timeout=5)
                    
                    print(f"[{time.time()-start_time:.1f}s] Chrome процессы принудительно убиты", flush=True)
                except Exception as cleanup_error:
                    print(f"[{time.time()-start_time:.1f}s] Ошибка очистки: {cleanup_error}", flush=True)
            
            start_time = time.time()
            
            try:
                wait = WebDriverWait(self.driver, 15)
                
                # Заполняем сумму
                print(f"  📌 Заполняю сумму: {amount}", flush=True)
                amount_input = wait.until(EC.presence_of_element_located((By.NAME, "summ.transfer")))
                amount_formatted = f"{int(amount):,}".replace(",", " ")
                
                # Очищаем и заполняем поле
                self.driver.execute_script("""
                    var input = arguments[0];
                    input.focus();
                    input.value = '';
                    input.value = arguments[1];
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                    input.dispatchEvent(new Event('blur', { bubbles: true }));
                """, amount_input, amount_formatted)
                
                # Проверяем что сумма заполнена
                filled_value = amount_input.get_attribute('value')
                print(f"  📌 Сумма заполнена: {filled_value}", flush=True)
                
                # Ждем обработки (сбалансировано)
                time.sleep(1.5)
                
                # Ждем лоадер (сбалансировано)
                print(f"  📌 Ожидание лоадера...", flush=True)
                for i in range(15):  # Увеличено с 10 до 15
                    try:
                        loader = self.driver.find_element(By.ID, "loadercontainer")
                        if "display: none" in loader.get_attribute("style") or not loader.is_displayed():
                            break
                    except:
                        break
                    time.sleep(0.3)  # Увеличено с 0.2 до 0.3
                
                # Ждем кнопку
                print(f"  📌 Поиск кнопки отправки...", flush=True)
                submit_btn = wait.until(EC.presence_of_element_located((By.NAME, "SubmitBtn")))
                
                # Ждем активации кнопки (оптимизировано)
                print(f"  📌 Ожидание активации кнопки...", flush=True)
                btn_enabled = False
                for i in range(20):  # Уменьшено с 30 до 20
                    try:
                        disabled = submit_btn.get_attribute("disabled")
                        enabled = submit_btn.is_enabled()
                        if i % 5 == 0:
                            print(f"  📌 Кнопка: disabled={disabled}, enabled={enabled}", flush=True)
                        if not disabled and enabled:
                            btn_enabled = True
                            break
                        submit_btn = self.driver.find_element(By.NAME, "SubmitBtn")
                    except Exception as e:
                        print(f"  ⚠️ Ошибка проверки кнопки: {e}", flush=True)
                    time.sleep(0.2)  # Уменьшено с 0.3 до 0.2
                
                if not btn_enabled:
                    print(f"  ⚠️ Кнопка не активировалась, пробую нажать всё равно", flush=True)
                
                # Клик
                print(f"  📌 Нажимаю кнопку отправки...", flush=True)
                
                # Сначала закрываем возможные popup'ы
                try:
                    popups = self.driver.find_elements(By.CSS_SELECTOR, ".modal-close, .close, [data-dismiss='modal'], .popup-close")
                    for popup in popups:
                        if popup.is_displayed():
                            popup.click()
                            print(f"  📌 Закрыт popup", flush=True)
                            time.sleep(0.5)
                except:
                    pass
                
                try:
                    # Прокручиваем к кнопке
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)
                    time.sleep(0.3)  # Уменьшено с 0.5
                    
                    # Сохраняем скриншот перед кликом
                    self.driver.save_screenshot('/tmp/before_click.png')
                    print(f"  📌 Скриншот перед кликом сохранён", flush=True)
                    
                    # Проверяем наличие ошибок на странице
                    try:
                        errors = self.driver.find_elements(By.CSS_SELECTOR, ".error, .alert-danger, .validation-error, [class*='error']")
                        if errors:
                            for err in errors:
                                if err.is_displayed():
                                    print(f"  ⚠️ Ошибка на странице: {err.text[:100]}", flush=True)
                    except:
                        pass
                    
                    # Логируем состояние формы
                    try:
                        form_html = self.driver.execute_script("""
                            var form = document.querySelector('form');
                            if (form) {
                                var inputs = form.querySelectorAll('input, select, textarea');
                                var data = {};
                                inputs.forEach(function(input) {
                                    if (input.name) {
                                        data[input.name] = {
                                            value: input.value,
                                            disabled: input.disabled,
                                            required: input.required,
                                            valid: input.checkValidity ? input.checkValidity() : 'unknown'
                                        };
                                    }
                                });
                                return JSON.stringify(data);
                            }
                            return 'No form found';
                        """)
                        print(f"  📌 Состояние формы: {form_html[:200]}", flush=True)
                    except Exception as e:
                        print(f"  ⚠️ Не удалось получить состояние формы: {e}", flush=True)
                    
                    # Пробуем разные способы клика
                    # Способ 1: JavaScript click с удалением overlay
                    self.driver.execute_script("""
                        // Удаляем возможные overlay
                        var overlays = document.querySelectorAll('.overlay, .modal-backdrop, .loader');
                        overlays.forEach(function(el) { el.style.display = 'none'; });
                        
                        // Кликаем
                        arguments[0].click();
                    """, submit_btn)
                    print(f"  📌 JS клик выполнен", flush=True)
                    time.sleep(1.5)  # Увеличено с 1 до 1.5
                    
                    # Проверяем изменился ли URL
                    current = self.driver.current_url
                    print(f"  📌 URL после клика: {current[:80]}", flush=True)
                    
                    if "SBP" not in current and "sbp" not in current.lower() and "default.aspx" in current:
                        print(f"  📌 Страница не изменилась, пробую submit формы...", flush=True)
                        # Способ 2: Submit формы
                        try:
                            forms = self.driver.find_elements(By.TAG_NAME, "form")
                            for form in forms:
                                try:
                                    form.submit()
                                    time.sleep(1)
                                    break
                                except:
                                    pass
                        except:
                            pass
                    
                    # Проверяем ещё раз
                    current = self.driver.current_url
                    if "SBP" not in current and "sbp" not in current.lower() and "default.aspx" in current:
                        print(f"  📌 Submit не сработал, пробую ActionChains...", flush=True)
                        # Способ 3: ActionChains
                        from selenium.webdriver.common.action_chains import ActionChains
                        actions = ActionChains(self.driver)
                        actions.move_to_element(submit_btn).click().perform()
                        
                except Exception as e:
                    print(f"  ⚠️ Ошибка клика: {e}", flush=True)
                    try:
                        submit_btn.click()
                    except:
                        pass
                
                # Ждем перехода - СБАЛАНСИРОВАНО
                print(f"  📌 Ожидание перехода на страницу QR...", flush=True)
                for i in range(50):  # Увеличено с 30 до 50
                    current_url = self.driver.current_url
                    if "SBP/default.aspx" in current_url or "sbp" in current_url.lower():
                        print(f"  📌 Переход на QR страницу: {current_url}", flush=True)
                        break
                    if i % 10 == 0:
                        print(f"  📌 Ожидание... URL: {current_url[:80]}", flush=True)
                    time.sleep(0.4)  # Увеличено с 0.2 до 0.4
                
                # Ждем загрузки QR - СБАЛАНСИРОВАНО
                print(f"  📌 Ожидание загрузки QR кода...", flush=True)
                time.sleep(2)  # Увеличено с 1 до 2
                
                # Получаем данные
                payment_link = None
                qr_code_base64 = None
                
                print(f"  📌 Поиск QR кода по ID Image1...", flush=True)
                wait_result = WebDriverWait(self.driver, 12)  # Увеличено с 10 до 12
                try:
                    qr_img = wait_result.until(EC.presence_of_element_located((By.ID, "Image1")))
                    qr_code_base64 = qr_img.get_attribute("src")
                    print(f"  📌 QR найден по ID", flush=True)
                except:
                    try:
                        qr_img = self.driver.find_element(By.CSS_SELECTOR, "img[src*='qr'], img[src*='data:image']")
                        qr_code_base64 = qr_img.get_attribute("src")
                        print(f"  📌 QR найден альтернативным способом", flush=True)
                    except Exception as e:
                        print(f"  ⚠️ QR код не найден: {str(e)[:100]}", flush=True)
                
                print(f"  📌 Поиск ссылки по ID LinkMobil...", flush=True)
                try:
                    payment_link_element = wait_result.until(EC.presence_of_element_located((By.ID, "LinkMobil")))
                    payment_link = payment_link_element.get_attribute("href")
                    print(f"  📌 Ссылка найдена по ID", flush=True)
                except:
                    try:
                        payment_link_element = self.driver.find_element(By.CSS_SELECTOR, "a[href*='qr.nspk.ru'], a[href*='nspk']")
                        payment_link = payment_link_element.get_attribute("href")
                        print(f"  📌 Ссылка найдена альтернативным способом", flush=True)
                    except Exception as e:
                        print(f"  ⚠️ Ссылка не найдена через элементы: {str(e)[:100]}", flush=True)
                        # Пробуем найти в page_source
                        try:
                            import re
                            page_source = self.driver.page_source
                            # Ищем ссылку на qr.nspk.ru
                            match = re.search(r'https://qr\.nspk\.ru/[A-Z0-9]+\?[^"\'<>\s]+', page_source)
                            if match:
                                payment_link = match.group(0)
                                print(f"  📌 Ссылка найдена в HTML: {payment_link[:60]}...", flush=True)
                            else:
                                print(f"  ⚠️ Ссылка не найдена в HTML", flush=True)
                        except Exception as html_error:
                            print(f"  ⚠️ Ошибка поиска в HTML: {str(html_error)[:100]}", flush=True)
                
                if not payment_link or not qr_code_base64:
                    # Сохраняем скриншот для диагностики
                    try:
                        self.driver.save_screenshot('/tmp/debug_payment.png')
                        print(f"  📌 Скриншот сохранён: /tmp/debug_payment.png", flush=True)
                        print(f"  📌 Текущий URL: {self.driver.current_url}", flush=True)
                        print(f"  📌 Заголовок: {self.driver.title}", flush=True)
                    except:
                        pass
                    raise Exception(f"Не удалось получить данные платежа. Link: {payment_link}, QR: {qr_code_base64 is not None}")
                
                elapsed = time.time() - start_time
                self.payment_count += 1
                self.last_activity = time.time()
                
                # Подготовка к следующему - СБАЛАНСИРОВАНО
                try:
                    print(f"  📌 Возврат на форму...", flush=True)
                    self.driver.get(ELECSNET_URL)
                    time.sleep(1)  # Увеличено с 0.5 до 1
                    
                    # Проверка лоадера
                    for _ in range(8):  # Увеличено с 5 до 8
                        try:
                            loader = self.driver.find_element(By.ID, "loadercontainer")
                            if "display: none" in loader.get_attribute("style") or not loader.is_displayed():
                                break
                        except:
                            break
                        time.sleep(0.2)  # Увеличено с 0.1 до 0.2
                    
                    card_input = WebDriverWait(self.driver, 5).until(  # Увеличено с 3 до 5
                        EC.presence_of_element_located((By.NAME, "requisites.m-36924.f-1")))
                    name_input = self.driver.find_element(By.NAME, "requisites.m-36924.f-2")
                    
                    # Быстрое заполнение через JS
                    self.driver.execute_script("""
                        arguments[0].value = arguments[2];
                        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                        arguments[1].value = arguments[3];
                        arguments[1].dispatchEvent(new Event('input', { bubbles: true }));
                    """, card_input, name_input, self.card['card_number'], self.card['owner_name'])
                    print(f"  📌 Форма готова к следующему платежу", flush=True)
                    
                    self.is_ready = True
                except:
                    self.is_ready = False
                
                return {
                    "payment_link": payment_link,
                    "qr_base64": qr_code_base64,
                    "elapsed_time": elapsed,
                    "account_used": self.account['phone'],
                    "card_used": self.card['card_number']
                }
                
            except Exception as e:
                self.is_ready = False
                return {"error": str(e), "elapsed_time": time.time() - start_time}
    
    def close(self):
        """Закрытие браузера"""
        with self.lock:
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
            self.is_ready = False


class BrowserPool:
    """Пул браузеров с распределением нагрузки"""
    
    def __init__(self):
        self.instances = []  # Список BrowserInstance
        self.lock = threading.Lock()
        self.round_robin_index = 0
    
    def initialize(self, accounts, cards):
        """Инициализация пула браузеров"""
        with self.lock:
            # Закрываем старые
            for inst in self.instances:
                inst.close()
            self.instances = []
            
            # Создаем комбинации аккаунт+карта
            if not accounts or not cards:
                print("⚠️ Нет аккаунтов или карт для инициализации пула", flush=True)
                return False
            
            # Распределяем карты по аккаунтам
            for i, card in enumerate(cards):
                account = accounts[i % len(accounts)]
                inst = BrowserInstance(account, card)
                self.instances.append(inst)
                print(f"📦 Создан экземпляр: {account['phone']} + {card['card_number'][-4:]}", flush=True)
            
            return True
    
    def warmup_all(self):
        """Прогрев всех браузеров параллельно"""
        if not self.instances:
            return False
        
        threads = []
        for inst in self.instances:
            t = threading.Thread(target=inst.warmup)
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join(timeout=60)
        
        ready_count = sum(1 for inst in self.instances if inst.is_ready)
        print(f"✅ Прогрето {ready_count}/{len(self.instances)} браузеров", flush=True)
        return ready_count > 0
    
    def get_best_instance(self):
        """Получить лучший доступный экземпляр (round-robin)"""
        with self.lock:
            if not self.instances:
                return None
            
            # Ищем готовый экземпляр по round-robin
            for _ in range(len(self.instances)):
                inst = self.instances[self.round_robin_index]
                self.round_robin_index = (self.round_robin_index + 1) % len(self.instances)
                
                if inst.is_ready and not inst.lock.locked():
                    return inst
            
            # Если все заняты, возвращаем первый готовый
            for inst in self.instances:
                if inst.is_ready:
                    return inst
            
            return None
    
    def create_payment(self, amount):
        """Создание платежа через лучший доступный браузер"""
        inst = self.get_best_instance()
        
        if not inst:
            # Пробуем прогреть первый экземпляр
            if self.instances:
                self.instances[0].warmup()
                inst = self.instances[0]
            else:
                return {"error": "Нет доступных браузеров"}
        
        return inst.create_payment(amount)
    
    def get_status(self):
        """Статус пула"""
        return {
            "total": len(self.instances),
            "ready": sum(1 for inst in self.instances if inst.is_ready),
            "instances": [
                {
                    "account": inst.account['phone'],
                    "card": inst.card['card_number'][-4:],
                    "ready": inst.is_ready,
                    "payments": inst.payment_count
                }
                for inst in self.instances
            ]
        }
    
    def close_all(self):
        """Закрытие всех браузеров"""
        for inst in self.instances:
            inst.close()
        self.instances = []


# Глобальные экземпляры
browser_pool = BrowserPool()

# Обратная совместимость - одиночный менеджер
class BrowserManager:
    """Обратная совместимость с одиночным браузером"""
    
    def __init__(self):
        self.driver = None
        self.is_ready = False
        self.card_number = None
        self.owner_name = None
        self.account_phone = None
        self.lock = threading.Lock()
        self._warmup_in_progress = False
        self._instance = None
    
    def warmup(self, card_number, owner_name, account):
        """Прогрев через пул или одиночный экземпляр"""
        if self._warmup_in_progress:
            for _ in range(90):
                if not self._warmup_in_progress:
                    break
                time.sleep(0.5)
            if self.is_ready:
                return True
        
        with self.lock:
            if self._warmup_in_progress:
                return False
            
            self._warmup_in_progress = True
            
            try:
                # Создаем одиночный экземпляр
                card = {'card_number': card_number, 'owner_name': owner_name}
                self._instance = BrowserInstance(account, card)
                
                if self._instance.warmup():
                    self.driver = self._instance.driver
                    self.is_ready = True
                    self.card_number = card_number
                    self.owner_name = owner_name
                    self.account_phone = account['phone']
                    return True
                return False
            finally:
                self._warmup_in_progress = False
    
    def create_payment(self, amount, callback=None):
        """Создание платежа"""
        if not self._instance or not self._instance.is_ready:
            return {"error": "Браузер не прогрет"}
        
        result = self._instance.create_payment(amount)
        
        # Обновляем состояние
        self.is_ready = self._instance.is_ready
        self.driver = self._instance.driver
        
        # Callback
        if callback and result.get('payment_link'):
            callback(result['payment_link'], result.get('qr_base64', ''))
        
        # Добавляем success флаг
        if result.get('payment_link'):
            result['success'] = True
        
        return result
    
    def close(self):
        """Закрытие"""
        if self._instance:
            self._instance.close()
        self.is_ready = False
        self.driver = None


    def warmup_full(self, card_number, owner_name, account):
        """
        ПОЛНЫЙ прогрев браузера с авторизацией и предзаполненными реквизитами
        Браузер остается на странице оплаты, готовый принять только сумму
        """
        if self._warmup_in_progress:
            for _ in range(90):
                if not self._warmup_in_progress:
                    break
                time.sleep(0.5)
            if self.is_ready:
                return True
        
        with self.lock:
            if self._warmup_in_progress:
                return False
            
            self._warmup_in_progress = True
            
            try:
                print(f"🔥 ПОЛНЫЙ ПРОГРЕВ браузера для {account['phone']}...", flush=True)
                start = time.time()
                
                # Создаем драйвер
                from selenium.webdriver.chrome.options import Options as ChromeOptions
                from selenium.webdriver.chrome.service import Service as ChromeService
                import subprocess
                
                # Убиваем старые процессы
                try:
                    subprocess.run(['pkill', '-f', 'chrome'], capture_output=True, timeout=5)
                    subprocess.run(['pkill', '-f', 'chromium'], capture_output=True, timeout=5)
                    time.sleep(1)
                except:
                    pass
                
                options = ChromeOptions()
                # ОТКЛЮЧАЕМ headless - используем виртуальный дисплей Xvfb
                # options.add_argument('--headless=new')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-gpu')
                options.add_argument('--disable-software-rasterizer')
                options.add_argument('--disable-setuid-sandbox')
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_argument('--disable-extensions')
                options.add_argument('--disable-plugins')
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
                options.add_argument('--memory-pressure-off')
                options.add_argument('--max_old_space_size=4096')
                # БЕЗОПАСНЫЕ ОПТИМИЗАЦИИ
                options.add_argument('--disable-logging')
                options.add_argument('--disable-notifications')
                options.add_argument('--disable-popup-blocking')
                options.add_argument('--window-size=1920,1080')
                options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
                options.add_experimental_option('useAutomationExtension', False)
                
                try:
                    service = ChromeService('/usr/bin/chromedriver')
                    self.driver = webdriver.Chrome(service=service, options=options)
                except:
                    try:
                        self.driver = webdriver.Chrome(options=options)
                    except Exception as e:
                        print(f"❌ Не удалось создать Chrome драйвер: {e}", flush=True)
                        raise
                
                # ОПТИМИЗИРОВАННЫЕ ТАЙМАУТЫ ДЛЯ СКОРОСТИ
                self.driver.set_page_load_timeout(60)  # Возвращаем стандартное значение для стабильности
                self.driver.implicitly_wait(10)  # Возвращаем стандартное значение для стабильности
                
                print(f"[{time.time()-start:.1f}s] 📌 Драйвер создан (HEADLESS + ОПТИМИЗАЦИИ), загружаю {ELECSNET_URL}...", flush=True)
                self.driver.get(ELECSNET_URL)
                print(f"[{time.time()-start:.1f}s] 📌 Страница загружена", flush=True)
                
                # Авторизация
                try:
                    login_btn = self.driver.find_element(By.CSS_SELECTOR, ".login")
                    self.driver.execute_script("arguments[0].click();", login_btn)
                    print(f"[{time.time()-start:.1f}s] 📌 Кнопка входа нажата", flush=True)
                    time.sleep(2)
                    
                    phone_input = self.driver.find_element(By.ID, "Login_Value")
                    password_input = self.driver.find_element(By.ID, "Password_Value")
                    auth_btn = self.driver.find_element(By.ID, "authBtn")
                    
                    phone_clean = account['phone'].replace("+7", "").replace(" ", "").replace("-", "")
                    self.driver.execute_script("""
                        arguments[0].value = arguments[2];
                        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                        arguments[1].value = arguments[3];
                        arguments[1].dispatchEvent(new Event('input', { bubbles: true }));
                    """, phone_input, password_input, phone_clean, account['password'])
                    
                    time.sleep(0.5)
                    self.driver.execute_script("arguments[0].click();", auth_btn)
                    print(f"[{time.time()-start:.1f}s] 📌 Авторизация отправлена", flush=True)
                    time.sleep(3)
                    
                    # Переходим на страницу оплаты
                    self.driver.get('https://1.elecsnet.ru/NotebookFront/services/0mhp/default.aspx?merchantId=36924&fromSegment=')
                    time.sleep(1)
                    
                except Exception as auth_err:
                    print(f"[{time.time()-start:.1f}s] ⚠️ Авторизация пропущена: {auth_err}", flush=True)
                
                # Ждем загрузки страницы оплаты
                print(f"[{time.time()-start:.1f}s] 📌 Ожидание загрузки страницы оплаты...", flush=True)
                wait = WebDriverWait(self.driver, 20)
                wait.until(EC.invisibility_of_element_located((By.ID, "loadercontainer")))
                print(f"[{time.time()-start:.1f}s] 📌 Лоадер скрыт", flush=True)
                
                # Заполняем реквизиты и оставляем браузер готовым
                card_input = wait.until(EC.presence_of_element_located((By.NAME, "requisites.m-36924.f-1")))
                name_input = wait.until(EC.presence_of_element_located((By.NAME, "requisites.m-36924.f-2")))
                print(f"[{time.time()-start:.1f}s] 📌 Поля найдены, заполняю реквизиты...", flush=True)
                
                self.driver.execute_script("""
                    arguments[0].value = arguments[2];
                    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                    arguments[1].value = arguments[3];
                    arguments[1].dispatchEvent(new Event('input', { bubbles: true }));
                """, card_input, name_input, card_number, owner_name)
                
                # Сохраняем данные
                self.card_number = card_number
                self.owner_name = owner_name
                self.account_phone = account['phone']
                self.is_ready = True
                
                elapsed = time.time() - start
                print(f"🚀 БРАУЗЕР ПОЛНОСТЬЮ ПРОГРЕТ ЗА {elapsed:.1f}s! Готов к мгновенным платежам!", flush=True)
                return True
                
            except Exception as e:
                print(f"❌ Ошибка полного прогрева: {e}", flush=True)
                if self.driver:
                    try:
                        self.driver.quit()
                    except:
                        pass
                    self.driver = None
                self.is_ready = False
                return False
            finally:
                self._warmup_in_progress = False
    
    def check_auth(self):
        """Проверка актуальности авторизации"""
        if not self.driver or not self.is_ready:
            return False
        
        try:
            # Проверяем что мы на правильной странице и авторизованы
            current_url = self.driver.current_url
            if "elecsnet.ru" not in current_url:
                return False
            
            # Проверяем наличие полей формы (признак авторизации)
            try:
                self.driver.find_element(By.NAME, "requisites.m-36924.f-1")
                self.driver.find_element(By.NAME, "requisites.m-36924.f-2")
                self.driver.find_element(By.NAME, "summ.transfer")
                return True
            except:
                return False
                
        except Exception as e:
            print(f"⚠️ Ошибка проверки авторизации: {e}", flush=True)
            return False
    
    def refresh_auth(self):
        """Обновление авторизации без полного перезапуска браузера"""
        if not self.driver:
            return False
        
        try:
            print("🔄 Обновление авторизации...", flush=True)
            
            # Переходим на главную страницу
            self.driver.get(ELECSNET_URL)
            time.sleep(2)
            
            # Проверяем нужна ли авторизация
            try:
                login_btn = self.driver.find_element(By.CSS_SELECTOR, ".login")
                print("📌 Требуется повторная авторизация", flush=True)
                
                # Получаем данные аккаунта из базы
                from database import db
                accounts = db.get_accounts()
                if not accounts:
                    return False
                
                account = accounts[0]  # Используем первый аккаунт
                
                self.driver.execute_script("arguments[0].click();", login_btn)
                time.sleep(2)
                
                phone_input = self.driver.find_element(By.ID, "Login_Value")
                password_input = self.driver.find_element(By.ID, "Password_Value")
                auth_btn = self.driver.find_element(By.ID, "authBtn")
                
                phone_clean = account['phone'].replace("+7", "").replace(" ", "").replace("-", "")
                self.driver.execute_script("""
                    arguments[0].value = arguments[2];
                    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                    arguments[1].value = arguments[3];
                    arguments[1].dispatchEvent(new Event('input', { bubbles: true }));
                """, phone_input, password_input, phone_clean, account['password'])
                
                time.sleep(0.5)
                self.driver.execute_script("arguments[0].click();", auth_btn)
                time.sleep(3)
                
            except:
                print("📌 Авторизация не требуется", flush=True)
            
            # Переходим на страницу оплаты и восстанавливаем реквизиты
            self.driver.get('https://1.elecsnet.ru/NotebookFront/services/0mhp/default.aspx?merchantId=36924&fromSegment=')
            time.sleep(1)
            
            wait = WebDriverWait(self.driver, 15)
            wait.until(EC.invisibility_of_element_located((By.ID, "loadercontainer")))
            
            # Заполняем реквизиты заново
            card_input = wait.until(EC.presence_of_element_located((By.NAME, "requisites.m-36924.f-1")))
            name_input = wait.until(EC.presence_of_element_located((By.NAME, "requisites.m-36924.f-2")))
            
            self.driver.execute_script("""
                arguments[0].value = arguments[2];
                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                arguments[1].value = arguments[3];
                arguments[1].dispatchEvent(new Event('input', { bubbles: true }));
            """, card_input, name_input, self.card_number, self.owner_name)
            
            print("✅ Авторизация обновлена", flush=True)
            return True
            
        except Exception as e:
            print(f"❌ Ошибка обновления авторизации: {e}", flush=True)
            self.is_ready = False
            return False


browser_manager = BrowserManager()

def check_chrome_driver_alive(driver):
    """Проверяет что Chrome Driver еще жив и отвечает"""
    try:
        # Простая проверка - получаем текущий URL
        current_url = driver.current_url
        return True
    except Exception as e:
        print(f"❌ Chrome Driver недоступен: {e}", flush=True)
        return False

def safe_screenshot(driver, path, description=""):
    """Безопасное создание скриншота с проверкой состояния Chrome Driver"""
    try:
        if not check_chrome_driver_alive(driver):
            print(f"⚠️ Не могу сделать скриншот {description} - Chrome Driver недоступен", flush=True)
            return False
        
        driver.save_screenshot(path)
        print(f"📸 Скриншот {description} сохранен: {path}", flush=True)
        return True
    except Exception as e:
        print(f"⚠️ Ошибка скриншота {description}: {e}", flush=True)
        return False

def restart_chrome_if_needed(driver):
    """Проверяет состояние Chrome Driver и перезапускает при необходимости"""
    if not check_chrome_driver_alive(driver):
        print("🔄 Chrome Driver потерян, требуется перезапуск", flush=True)
        return False
    return True