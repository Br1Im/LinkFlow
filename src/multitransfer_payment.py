# -*- coding: utf-8 -*-
"""
Создание платежей через multitransfer.ru
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

try:
    from .mui_helpers import set_mui_input_value, click_mui_element, wait_for_mui_button_enabled
    from .sender_data import SENDER_DATA
except ImportError:
    from mui_helpers import set_mui_input_value, click_mui_element, wait_for_mui_button_enabled
    from sender_data import SENDER_DATA


class MultitransferPayment:
    """Класс для работы с multitransfer.ru"""
    
    def __init__(self, sender_data=None, headless=True, proxy=None, keep_alive=False):
        self.url = "https://multitransfer.ru/transfer/uzbekistan"
        self.driver = None
        self.headless = headless
        self.proxy = proxy
        self.keep_alive = keep_alive  # Держать браузер открытым
        self.is_warmed_up = False  # Флаг прогрева
    
    def _create_driver(self):
        options = webdriver.ChromeOptions()
        
        if self.headless:
            options.add_argument('--headless=new')
        
        if self.proxy:
            options.add_argument(f'--proxy-server={self.proxy}')
            print(f"🌐 Использую прокси: {self.proxy}")
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Определяем путь к Chrome в зависимости от ОС
        import os
        import platform
        
        if platform.system() == 'Linux' and os.path.exists('/usr/bin/google-chrome'):
            options.binary_location = '/usr/bin/google-chrome'
            print("🐧 Используется Linux Chrome")
        elif platform.system() == 'Windows':
            # На Windows webdriver-manager сам найдет Chrome
            print("🪟 Используется Windows Chrome")
        
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        
        # Получаем путь к драйверу
        driver_path = ChromeDriverManager().install()
        
        # Исправляем путь, если он указывает на неправильный файл
        if platform.system() == 'Windows':
            # ChromeDriverManager иногда возвращает путь к THIRD_PARTY_NOTICES
            if 'THIRD_PARTY_NOTICES' in driver_path or not driver_path.endswith('.exe'):
                # Получаем директорию и добавляем правильное имя файла
                driver_dir = os.path.dirname(driver_path)
                driver_path = os.path.join(driver_dir, 'chromedriver.exe')
        
        print(f"📍 ChromeDriver: {driver_path}")
        
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)
        return driver
    
    def login(self, phone=None, password=None):
        print(f"🔧 Инициализация multitransfer.ru...")
        
        self.driver = self._create_driver()
        self.driver.get(self.url)
        
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        print("✅ Страница загружена")
        return True
    
    def warmup(self):
        """Прогрев браузера с предвыбором способа оплаты"""
        if self.is_warmed_up:
            print("✅ Браузер уже прогрет")
            return True
        
        print("🔥 Прогрев браузера и предвыбор способа оплаты...")
        start_time = time.time()
        
        try:
            wait = WebDriverWait(self.driver, 20)
            
            # Вводим минимальную сумму для активации формы
            print("📌 Ввожу минимальную сумму для активации...")
            amount_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='0 RUB']"))
            )
            set_mui_input_value(self.driver, amount_input, 100)
            time.sleep(0.5)
            
            # Открываем способ перевода
            print("📌 Открываю 'Способ перевода'...")
            selectors = [
                "//div[contains(text(),'Способ перевода')]/ancestor::div[contains(@class,'variant-alternative')]",
                "//div[contains(text(),'Способ перевода')]",
                "//*[contains(text(),'Способ перевода')]"
            ]
            
            transfer_block = None
            for selector in selectors:
                try:
                    transfer_block = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except:
                    continue
            
            if transfer_block:
                click_mui_element(self.driver, transfer_block)
                print("✅ Блок способов перевода открыт")
                
                # Выбираем Uzcard / Humo
                print("📌 Предвыбираю Uzcard / Humo...")
                time.sleep(0.5)  # Ждем появления списка
                bank_option = wait.until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        "//*[contains(text(),'Uzcard') or contains(text(),'Humo')]"
                    ))
                )
                click_mui_element(self.driver, bank_option)
                print("✅ Банк предвыбран")
                
                # Закрываем модалку и очищаем состояние
                time.sleep(0.5)
                try:
                    # Нажимаем ESC для закрытия модалки
                    from selenium.webdriver.common.keys import Keys
                    self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                    time.sleep(0.3)
                    
                    # Перезагружаем страницу для чистого состояния
                    print("📌 Перезагружаю страницу для чистого состояния...")
                    self.driver.get(self.url)
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    print("✅ Страница перезагружена")
                except Exception as e:
                    print(f"⚠️ Ошибка при очистке: {e}")
                
                self.is_warmed_up = True
                elapsed = time.time() - start_time
                print(f"✅ Прогрев завершен за {elapsed:.1f}s")
                print("💡 Теперь можно вводить реальную сумму для создания платежа")
                return True
            else:
                print("⚠️ Не удалось прогреть - способ перевода не найден")
                return False
                
        except Exception as e:
            print(f"⚠️ Ошибка прогрева: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def create_payment(self, card_number, owner_name, amount):
        print(f"\n💳 Создание платежа через multitransfer.ru")
        print(f"   Карта: {card_number}")
        print(f"   Владелец: {owner_name}")
        print(f"   Сумма: {amount} руб.")
        
        start_time = time.time()
        step_time = start_time
        
        def log_step(step_name):
            nonlocal step_time
            elapsed = time.time() - step_time
            total = time.time() - start_time
            print(f"⏱️  {step_name}: {elapsed:.1f}s (всего: {total:.1f}s)")
            step_time = time.time()
        
        try:
            wait = WebDriverWait(self.driver, 20)
            
            print("✅ Узбекистан уже выбран (через URL)")
            
            print(f"📌 Ввожу сумму {amount} RUB (React-safe)...")
            amount_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='0 RUB']"))
            )
            
            set_mui_input_value(self.driver, amount_input, amount)
            print("✅ Сумма введена")
            log_step("Ввод суммы")
            
            # Уменьшаем ожидание
            time.sleep(1.0)
            log_step("Ожидание React")
            
            # Если браузер не прогрет, выбираем способ перевода
            if not self.is_warmed_up:
                try:
                    wait.until(EC.element_to_be_clickable((By.ID, "pay")))
                    print("✅ Сумма подтверждена сайтом")
                except:
                    print("⚠️ Кнопка 'Продолжить' не активировалась, но продолжаем")
                
                print("📌 Открываю 'Способ перевода'...")
                transfer_block = None
                
                selectors = [
                    "//div[contains(text(),'Способ перевода')]/ancestor::div[contains(@class,'variant-alternative')]",
                    "//div[contains(text(),'Способ перевода')]",
                    "//*[contains(text(),'Способ перевода')]"
                ]
                
                for selector in selectors:
                    try:
                        transfer_block = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        break
                    except:
                        continue
                
                if not transfer_block:
                    raise Exception("Не удалось найти блок 'Способ перевода'")
                
                click_mui_element(self.driver, transfer_block)
                print("✅ Блок способов перевода открыт")
                log_step("Открытие способа перевода")
                
                print("📌 Выбираю Uzcard / Humo...")
                bank_option = wait.until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        "//*[contains(text(),'Uzcard') or contains(text(),'Humo')]"
                    ))
                )
                click_mui_element(self.driver, bank_option)
                print("✅ Банк выбран")
                log_step("Выбор банка")
            else:
                print("✅ Способ оплаты уже выбран (прогрет)")
                log_step("Пропуск выбора банка")
            
            print("📌 Ожидаю активации кнопки 'Продолжить'...")
            try:
                WebDriverWait(self.driver, 10).until(
                    lambda d: d.find_element(By.ID, "pay").is_enabled()
                )
                print("✅ Кнопка 'Продолжить' активирована")
            except:
                print("⚠️ Кнопка не активировалась, но продолжаем")
            
            # Убираем лишний sleep
            time.sleep(0.5)
            
            print("📌 Нажимаю 'Продолжить'...")
            
            try:
                continue_btn = wait.until(
                    EC.element_to_be_clickable((By.ID, "pay"))
                )
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center', behavior:'instant'});",
                    continue_btn
                )
                continue_btn.click()
                print("✅ Кнопка 'Продолжить' нажата")
                
                WebDriverWait(self.driver, 10).until(lambda d: "sender-details" in d.current_url)
                print("✅ Переход на страницу sender-details")
                log_step("Переход на sender-details")
                
            except Exception as e:
                print(f"⚠️ Ошибка клика по кнопке: {e}")
                try:
                    continue_btn = self.driver.find_element(By.ID, "pay")
                    self.driver.execute_script("arguments[0].click();", continue_btn)
                    print("✅ Кнопка 'Продолжить' нажата (JS)")
                    
                    WebDriverWait(self.driver, 10).until(lambda d: "sender-details" in d.current_url)
                    print("✅ Переход на страницу sender-details")
                    log_step("Переход на sender-details (JS)")
                    
                except Exception as e2:
                    print(f"⚠️ JS клик тоже не сработал: {e2}")
            
            print("📌 Заполняю данные получателя и отправителя...")
            
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "input")))
            time.sleep(0.2)  # Уменьшаем с 0.3 до 0.2
            
            def fill_field_by_label(label_text, value, field_name):
                try:
                    input_elem = wait.until(
                        EC.presence_of_element_located((
                            By.XPATH,
                            f"//label[contains(text(), '{label_text}')]/following-sibling::*//input | //input[@placeholder='{label_text}'] | //input[@aria-label='{label_text}']"
                        ))
                    )
                    wait.until(EC.element_to_be_clickable(input_elem))
                    input_elem.clear()
                    input_elem.send_keys(value)
                    print(f"   ✅ {field_name}: {value}")
                    return True
                except Exception as e:
                    print(f"   ⚠️ Ошибка {field_name}: {e}")
                    return False
            
            def fill_field(name_pattern, value, field_name, retries=2):
                for attempt in range(retries):
                    try:
                        inputs = self.driver.find_elements(By.TAG_NAME, "input")
                        for inp in inputs:
                            try:
                                name_attr = (inp.get_attribute("name") or "")
                                placeholder = (inp.get_attribute("placeholder") or "")
                                aria_label = (inp.get_attribute("aria-label") or "")
                                
                                if (name_pattern.lower() in name_attr.lower() or 
                                    name_pattern.lower() in placeholder.lower() or 
                                    name_pattern.lower() in aria_label.lower()):
                                    
                                    inp.click()
                                    inp.clear()
                                    inp.send_keys(value)
                                    
                                    print(f"   ✅ {field_name}: {value}")
                                    return True
                            except:
                                continue
                        
                        if attempt < retries - 1:
                            time.sleep(0.5)
                        else:
                            return False
                            
                    except Exception as e:
                        if attempt < retries - 1:
                            time.sleep(0.5)
                        else:
                            return False
                return False
            
            def select_country(name_pattern, country_name, field_name):
                try:
                    inputs = self.driver.find_elements(By.TAG_NAME, "input")
                    for inp in inputs:
                        name_attr = (inp.get_attribute("name") or "")
                        if name_pattern in name_attr:
                            self.driver.execute_script(
                                "arguments[0].scrollIntoView({block:'center'});",
                                inp
                            )
                            
                            wait.until(EC.element_to_be_clickable(inp))
                            inp.click()
                            
                            inp.clear()
                            inp.send_keys(country_name)
                            
                            try:
                                option = wait.until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, "li[role='option']"))
                                )
                                option.click()
                                print(f"   ✅ {field_name}: {country_name}")
                                return True
                            except:
                                inp.send_keys(Keys.ENTER)
                                print(f"   ✅ {field_name}: {country_name} (Enter)")
                                return True
                    
                    print(f"   ⚠️ Поле {field_name} не найдено (pattern: {name_pattern})")
                    return False
                except Exception as e:
                    print(f"   ⚠️ Ошибка {field_name}: {e}")
                    return False
            
            fill_field("beneficiaryaccountnumber", card_number, "Номер карты получателя")
            fill_field("beneficiaryaccountnumber", card_number, "Номер карты получателя (повтор)")
            time.sleep(0.2)  # Уменьшаем с 0.3 до 0.2
            fill_field("beneficiary_firstname", owner_name.split()[0], "Имя получателя")
            if len(owner_name.split()) > 1:
                fill_field("beneficiary_lastname", owner_name.split()[1], "Фамилия получателя")
            
            fill_field("sender_documents_series", SENDER_DATA["passport_series"], "Серия паспорта")
            fill_field("sender_documents_number", SENDER_DATA["passport_number"], "Номер паспорта")
            fill_field("issuedate", SENDER_DATA["passport_issue_date"], "Дата выдачи")
            
            select_country("birthPlaceAddress_countryCode", SENDER_DATA["birth_country"], "Страна рождения")
            
            try:
                birth_place_input = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='birthPlaceAddress_full']"))
                )
                
                self.driver.execute_script(
                    f"arguments[0].value = '{SENDER_DATA['birth_place']}';",
                    birth_place_input
                )
                birth_place_input.send_keys(" ")
                birth_place_input.send_keys(Keys.BACKSPACE)
                
                print(f"   ✅ Место рождения: {SENDER_DATA['birth_place']}")
            except Exception as e:
                print(f"   ⚠️ Ошибка заполнения места рождения: {e}")
            
            select_country("registrationAddress_countryCode", SENDER_DATA["registration_country"], "Страна регистрации")
            
            try:
                reg_place_input = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='registrationAddress_full']"))
                )
                
                self.driver.execute_script(
                    f"arguments[0].value = '{SENDER_DATA['registration_place']}';",
                    reg_place_input
                )
                reg_place_input.send_keys(" ")
                reg_place_input.send_keys(Keys.BACKSPACE)
                
                print(f"   ✅ Место регистрации: {SENDER_DATA['registration_place']}")
            except Exception as e:
                print(f"   ⚠️ Ошибка заполнения места регистрации: {e}")
            
            fill_field("sender_firstname", SENDER_DATA["first_name"], "Имя отправителя")
            fill_field("sender_lastname", SENDER_DATA["last_name"], "Фамилия отправителя")
            fill_field("birthdate", SENDER_DATA["birth_date"], "Дата рождения")
            fill_field("phonenumber", SENDER_DATA["phone"], "Телефон")
            
            print("✅ Все данные заполнены")
            log_step("Заполнение данных")
            
            print("📌 Ставлю галочку согласия...")
            try:
                checkbox_container = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='checkbox']"))
                )
                
                if not checkbox_container.is_selected():
                    try:
                        checkbox_container.click()
                        print("✅ Галочка поставлена")
                    except:
                        parent = checkbox_container.find_element(By.XPATH, "./..")
                        parent.click()
                        print("✅ Галочка поставлена")
                else:
                    print("✅ Галочка уже стоит")
                    
            except Exception as e:
                print(f"⚠️ Ошибка с галочкой: {e}")
                try:
                    checkbox_label = self.driver.find_element(By.XPATH, "//span[contains(@class, 'MuiCheckbox')]")
                    checkbox_label.click()
                    print("✅ Галочка поставлена")
                except Exception as e2:
                    print(f"⚠️ Не удалось поставить галочку: {e2}")
            
            print("📌 Нажимаю кнопку 'Продолжить' (id=pay)...")
            try:
                pay_button = wait.until(
                    EC.element_to_be_clickable((By.ID, "pay"))
                )
                pay_button.click()
                print("✅ Кнопка нажата, ожидаю перехода...")
                
                time.sleep(0.5)  # Уменьшаем с 1 до 0.5
                log_step("Нажатие кнопки Продолжить")
                
            except Exception as e:
                print(f"⚠️ Ошибка нажатия кнопки: {e}")
            
            current_url = self.driver.current_url
            
            if "payment" in current_url or "result" in current_url:
                print("✅ Уже на странице оплаты!")
            elif "sender-details" in current_url:
                print("⚠️ Всё ещё на странице sender-details")
                print("📌 Проверяю наличие капчи...")
                try:
                    captcha_iframe = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='smartcaptcha.yandexcloud.net/checkbox']"))
                    )
                    print("⚠️ Обнаружена Yandex SmartCaptcha!")
                    
                    self.driver.switch_to.frame(captcha_iframe)
                    
                    try:
                        checkbox_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.ID, "js-button"))
                        )
                        
                        if checkbox_button:
                            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", checkbox_button)
                            checkbox_button.click()
                            print("✅ Кликнул по чекбоксу капчи")
                            time.sleep(1)  # Уменьшаем с 2 до 1
                            
                            self.driver.switch_to.default_content()
                            print("✅ Капча пройдена!")
                            log_step("Прохождение капчи")
                            
                            # Убираем повторное нажатие - модалка появляется сразу
                            print("📌 Ожидаю модалку 'Проверка данных'...")
                        
                    except Exception as e:
                        print(f"⚠️ Ошибка клика по капче: {e}")
                        self.driver.switch_to.default_content()
                        
                except:
                    print("✅ Капча не обнаружена")
                    
                print("📌 Проверяю наличие модалки 'Проверка данных'...")
                try:
                    # Ждем появления модалки
                    time.sleep(1)
                    
                    # Ищем все кнопки "Продолжить" на странице
                    buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Продолжить')]")
                    
                    if not buttons:
                        # Пробуем альтернативные селекторы
                        buttons = self.driver.find_elements(By.CSS_SELECTOR, "button.MuiButton-sizeLarge")
                    
                    if buttons:
                        # Берем последнюю кнопку (обычно это кнопка в модалке)
                        final_btn = buttons[-1]
                        print(f"✅ Найдено {len(buttons)} кнопок 'Продолжить', кликаю по последней")
                        
                        self.driver.execute_script(
                            "arguments[0].scrollIntoView({block:'center'});",
                            final_btn
                        )
                        time.sleep(0.3)
                        
                        # Кликаем через JS
                        self.driver.execute_script("arguments[0].click();", final_btn)
                        print("✅ Кнопка 'Продолжить' нажата (JS)")
                        
                        # Ждем перехода на страницу оплаты
                        print("📌 Ожидаю перехода на страницу оплаты...")
                        transition_found = False
                        for i in range(40):  # 20 секунд максимум
                            time.sleep(0.5)
                            current = self.driver.current_url
                            if "payment" in current or "result" in current or "/pay/" in current or "finish-transfer" in current:
                                print(f"✅ Переход на страницу оплаты")
                                log_step("Переход на страницу оплаты")
                                transition_found = True
                                break
                        
                        if not transition_found:
                            print(f"⚠️ Не дождались перехода. URL: {self.driver.current_url}")
                    else:
                        print("⚠️ Кнопка 'Продолжить' не найдена")
                    
                except Exception as e:
                    print(f"⚠️ Ошибка с модалкой: {e}")
                    print(f"   Текущий URL: {self.driver.current_url}")
            
            print("📌 Получаю данные платежа...")
            
            qr_base64 = None
            payment_link = self.driver.current_url
            payment_data = {}
            
            try:
                table_rows = self.driver.find_elements(By.CSS_SELECTOR, "tr.MuiTableRow-root")
                for row in table_rows:
                    try:
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if len(cells) == 2:
                            key = cells[0].text.strip()
                            value = cells[1].text.strip()
                            payment_data[key] = value
                    except:
                        continue
                
                if payment_data:
                    print("✅ Данные платежа получены:")
                    for key, value in payment_data.items():
                        print(f"   • {key}: {value}")
                        
            except Exception as e:
                print(f"⚠️ Ошибка извлечения данных: {e}")
            
            try:
                qr_svg = self.driver.find_element(By.CSS_SELECTOR, "svg[viewBox='0 0 37 37']")
                if qr_svg:
                    qr_base64 = self.driver.execute_script("return arguments[0].outerHTML;", qr_svg)
                    print("✅ QR-код найден (SVG)")
            except:
                print("⚠️ QR-код не найден")
            
            log_step("Получение данных платежа")
            
            elapsed = time.time() - start_time
            
            print(f"\n✅ Платеж создан за {elapsed:.1f} сек!")
            print(f"🔗 Ссылка: {payment_link}")
            print(f"\n📊 Распределение времени:")
            print(f"   Общее время: {elapsed:.1f}s")
            
            return {
                "payment_link": payment_link,
                "qr_code": qr_base64,
                "payment_data": payment_data,
                "elapsed_time": elapsed,
                "success": True
            }
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
            return {
                "error": str(e),
                "elapsed_time": elapsed,
                "success": False
            }
    
    def close(self):
        if self.driver:
            try:
                self.driver.quit()
                print("✅ Браузер закрыт")
            except:
                pass
            self.driver = None
