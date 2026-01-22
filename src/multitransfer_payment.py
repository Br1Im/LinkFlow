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
    # Для запуска вне пакета
    from mui_helpers import set_mui_input_value, click_mui_element, wait_for_mui_button_enabled
    from sender_data import SENDER_DATA


class MultitransferPayment:
    """Класс для работы с multitransfer.ru"""
    
    def __init__(self, sender_data=None, headless=True):
        self.url = "https://multitransfer.ru/"
        self.driver = None
        self.headless = headless
    
    def _create_driver(self):
        """Создание Chrome драйвера"""
        options = webdriver.ChromeOptions()
        
        if self.headless:
            options.add_argument('--headless=new')
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Для Docker
        import os
        if os.path.exists('/usr/bin/google-chrome'):
            options.binary_location = '/usr/bin/google-chrome'
        
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)
        return driver
    
    def login(self, phone=None, password=None):
        """
        Инициализация (авторизация не требуется для multitransfer.ru)
        """
        print(f"🔧 Инициализация multitransfer.ru...")
        
        self.driver = self._create_driver()
        self.driver.get(self.url)
        time.sleep(2)
        
        print("✅ Страница загружена")
        return True
    
    def create_payment(self, card_number, owner_name, amount):
        """
        Создание платежа (React-safe версия)
        
        Args:
            card_number: Номер карты получателя (Узбекистан)
            owner_name: Имя владельца карты
            amount: Сумма платежа в рублях
            
        Returns:
            dict: {"payment_link": "...", "qr_base64": "..."}
        """
        print(f"\n💳 Создание платежа через multitransfer.ru")
        print(f"   Карта: {card_number}")
        print(f"   Владелец: {owner_name}")
        print(f"   Сумма: {amount} руб.")
        
        start_time = time.time()
        
        try:
            wait = WebDriverWait(self.driver, 20)
            
            # Шаг 1: Выбрать страну "Узбекистан"
            print("📌 Выбираю Узбекистан...")
            country_selector = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".variant-alternative.css-c8d8yl"))
            )
            country_selector.click()
            time.sleep(0.3)
            
            uzbekistan = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'variant-alternative') and contains(., 'Узбекистан')]"))
            )
            uzbekistan.click()
            time.sleep(0.5)
            print("✅ Узбекистан выбран")
            
            # Шаг 2: Ввод суммы через send_keys (React-safe)
            print(f"📌 Ввожу сумму {amount} RUB (React-safe)...")
            amount_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='0 RUB']"))
            )
            
            # Один раз вводим сумму посимвольно
            set_mui_input_value(self.driver, amount_input, amount)
            print("✅ Сумма введена")
            
            # Ждём пока React обработает (ВАЖНО: только здесь 3 секунды!)
            time.sleep(3)
            
            # Шаг 3: Ждём активации кнопки "Продолжить"
            print("📌 Ожидаю подтверждения суммы React...")
            if wait_for_mui_button_enabled(self.driver, "pay", timeout=5):
                print("✅ Сумма подтверждена сайтом")
            else:
                print("⚠️ Кнопка 'Продолжить' не активировалась, но продолжаем")
            
            # Шаг 4: Открыть блок "Способ перевода"
            print("📌 Открываю 'Способ перевода'...")
            transfer_block = wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//div[contains(text(),'Способ перевода')]/ancestor::div[contains(@class,'variant-alternative')]"
                ))
            )
            click_mui_element(self.driver, transfer_block)
            print("✅ Блок способов перевода открыт")
            time.sleep(0.5)
            
            # Шаг 5: Выбрать Uzcard / Humo по тексту
            print("📌 Выбираю Uzcard / Humo...")
            bank_option = wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//*[contains(text(),'Uzcard') or contains(text(),'Humo')]"
                ))
            )
            click_mui_element(self.driver, bank_option)
            print("✅ Банк выбран")
            time.sleep(2)  # Ждём пока React обработает выбор банка
            
            # Шаг 6: Нажать кнопку "Продолжить" (НЕ заполняем данные карты!)
            print("📌 Нажимаю 'Продолжить'...")
            
            # Ищем кнопку "Продолжить" по ID
            try:
                continue_btn = wait.until(
                    EC.element_to_be_clickable((By.ID, "pay"))
                )
                # Прокручиваем к кнопке
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center', behavior:'instant'});",
                    continue_btn
                )
                time.sleep(0.5)
                # Пробуем обычный клик
                continue_btn.click()
                print("✅ Кнопка 'Продолжить' нажата")
                
                # Ждём перехода на страницу sender-details
                wait.until(lambda d: "sender-details" in d.current_url)
                print("✅ Переход на страницу sender-details")
                time.sleep(2)  # Ждём полной загрузки формы
                
            except Exception as e:
                print(f"⚠️ Ошибка клика по кнопке: {e}")
                # Пробуем JS клик
                try:
                    continue_btn = self.driver.find_element(By.ID, "pay")
                    self.driver.execute_script("arguments[0].click();", continue_btn)
                    print("✅ Кнопка 'Продолжить' нажата (JS)")
                    
                    # Ждём перехода на страницу sender-details
                    wait.until(lambda d: "sender-details" in d.current_url)
                    print("✅ Переход на страницу sender-details")
                    time.sleep(2)
                    
                except Exception as e2:
                    print(f"⚠️ JS клик тоже не сработал: {e2}")
            
            # Шаг 7: Заполнить данные получателя на странице sender-details
            print("📌 Заполняю данные получателя и отправителя...")
            time.sleep(1)  # Ждём загрузки формы
            
            # Функция для поиска и заполнения поля
            def fill_field(name_pattern, value, field_name):
                try:
                    inputs = self.driver.find_elements(By.TAG_NAME, "input")
                    for inp in inputs:
                        name_attr = (inp.get_attribute("name") or "").lower()
                        if name_pattern in name_attr:
                            inp.clear()
                            inp.send_keys(value)
                            print(f"   ✅ {field_name}: {value}")
                            time.sleep(0.2)
                            return True
                    return False
                except Exception as e:
                    print(f"   ⚠️ Ошибка {field_name}: {e}")
                    return False
            
            # Функция для выбора страны из MUI Autocomplete
            def select_country(name_pattern, country_name, field_name):
                try:
                    # Ищем input с нужным name
                    inputs = self.driver.find_elements(By.TAG_NAME, "input")
                    for inp in inputs:
                        name_attr = (inp.get_attribute("name") or "")
                        if name_pattern in name_attr:
                            # Прокручиваем к полю
                            self.driver.execute_script(
                                "arguments[0].scrollIntoView({block:'center'});",
                                inp
                            )
                            time.sleep(0.3)
                            
                            # Кликаем на поле для фокуса
                            inp.click()
                            time.sleep(0.3)
                            
                            # Очищаем и вводим название страны
                            inp.clear()
                            time.sleep(0.1)
                            inp.send_keys(country_name)
                            time.sleep(0.8)  # Ждём появления списка
                            
                            # Ищем выпадающий список
                            try:
                                # Ждём появления опций
                                option = wait.until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, "li[role='option']"))
                                )
                                time.sleep(0.2)
                                # Кликаем на первую опцию
                                option.click()
                                print(f"   ✅ {field_name}: {country_name}")
                                time.sleep(0.3)
                                return True
                            except:
                                # Если не нашли список, пробуем нажать Enter
                                inp.send_keys(Keys.ENTER)
                                print(f"   ✅ {field_name}: {country_name} (Enter)")
                                time.sleep(0.3)
                                return True
                    
                    print(f"   ⚠️ Поле {field_name} не найдено (pattern: {name_pattern})")
                    return False
                except Exception as e:
                    print(f"   ⚠️ Ошибка {field_name}: {e}")
                    return False
            
            # Заполняем данные получателя
            fill_field("beneficiaryaccountnumber", card_number, "Номер карты получателя")
            fill_field("beneficiary_firstname", owner_name.split()[0], "Имя получателя")
            if len(owner_name.split()) > 1:
                fill_field("beneficiary_lastname", owner_name.split()[1], "Фамилия получателя")
            
            # Заполняем паспортные данные отправителя
            fill_field("sender_documents_series", SENDER_DATA["passport_series"], "Серия паспорта")
            fill_field("sender_documents_number", SENDER_DATA["passport_number"], "Номер паспорта")
            fill_field("issuedate", SENDER_DATA["passport_issue_date"], "Дата выдачи")
            
            # Страна рождения (MUI Autocomplete)
            select_country("birthPlaceAddress_countryCode", SENDER_DATA["birth_country"], "Страна рождения")
            
            # Место рождения
            fill_field("birthplaceaddress_full", SENDER_DATA["birth_place"], "Место рождения")
            
            # Страна регистрации (MUI Autocomplete)
            select_country("registrationAddress_countryCode", SENDER_DATA["registration_country"], "Страна регистрации")
            
            # Место регистрации
            fill_field("registrationaddress_full", SENDER_DATA["registration_place"], "Место регистрации")
            
            # Личные данные отправителя
            fill_field("sender_firstname", SENDER_DATA["first_name"], "Имя отправителя")
            fill_field("sender_lastname", SENDER_DATA["last_name"], "Фамилия отправителя")
            fill_field("birthdate", SENDER_DATA["birth_date"], "Дата рождения")
            fill_field("phonenumber", SENDER_DATA["phone"], "Телефон")
            
            print("✅ Все данные заполнены")
            time.sleep(1)
            
            # Шаг 8: Поставить галочку согласия
            print("📌 Ставлю галочку согласия...")
            try:
                checkbox = self.driver.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
                if not checkbox.is_selected():
                    checkbox.click()
                    print("✅ Галочка поставлена")
                    time.sleep(0.5)
            except Exception as e:
                print(f"⚠️ Ошибка с галочкой: {e}")
            
            # Шаг 9: Нажать кнопку "Продолжить" (появится капча)
            print("📌 Нажимаю кнопку 'Продолжить' (id=pay)...")
            try:
                pay_button = wait.until(
                    EC.element_to_be_clickable((By.ID, "pay"))
                )
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});",
                    pay_button
                )
                time.sleep(0.5)
                pay_button.click()
                print("✅ Кнопка нажата, ожидаю появления капчи...")
                time.sleep(2)
            except Exception as e:
                print(f"⚠️ Ошибка нажатия кнопки: {e}")
            
            # Шаг 10: Решаем капчу если появилась
            print("📌 Проверяю наличие капчи...")
            try:
                # Ищем iframe с капчей
                captcha_iframe = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='smartcaptcha.yandexcloud.net/checkbox']"))
                )
                print("⚠️ Обнаружена Yandex SmartCaptcha!")
                
                # Переключаемся на iframe
                self.driver.switch_to.frame(captcha_iframe)
                time.sleep(1)
                
                # Ищем кнопку чекбокса и кликаем
                try:
                    # Ищем кнопку по ID или классу
                    checkbox_button = None
                    try:
                        checkbox_button = self.driver.find_element(By.ID, "js-button")
                    except:
                        checkbox_button = self.driver.find_element(By.CLASS_NAME, "CheckboxCaptcha-Button")
                    
                    if checkbox_button:
                        # Прокручиваем к кнопке
                        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", checkbox_button)
                        time.sleep(0.5)
                        
                        # Кликаем
                        checkbox_button.click()
                        print("✅ Кликнул по чекбоксу капчи")
                        time.sleep(5)  # Увеличиваем ожидание для появления модалки
                        
                        # Возвращаемся в основной контекст
                        self.driver.switch_to.default_content()
                        
                        print("✅ Капча пройдена!")
                    
                except Exception as e:
                    print(f"⚠️ Ошибка клика по капче: {e}")
                    self.driver.switch_to.default_content()
                    time.sleep(5)
                    
            except:
                print("✅ Капча не обнаружена")
                
            time.sleep(2)  # Дополнительное ожидание появления модалки
            
            # Шаг 9: Нажать кнопку "Продолжить" в модалке "Проверка данных"
            print("📌 Нажимаю кнопку 'Продолжить' в модалке...")
            try:
                # Ждём появления модалки с проверкой данных
                # Ищем именно большую кнопку внизу (sizeLarge), а не крестик
                final_btn = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.MuiButton-sizeLarge[buttontext='Продолжить']"))
                )
                print("✅ Модалка 'Проверка данных' появилась")
                
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});",
                    final_btn
                )
                time.sleep(0.5)
                
                # Пробуем обычный клик
                try:
                    final_btn.click()
                    print("✅ Кнопка 'Продолжить' нажата")
                except:
                    # Если не сработал, пробуем JS клик
                    self.driver.execute_script("arguments[0].click();", final_btn)
                    print("✅ Кнопка 'Продолжить' нажата (JS)")
                
                # Ждём перехода на страницу payment
                try:
                    wait.until(lambda d: "payment" in d.current_url or "result" in d.current_url, timeout=10)
                    print("✅ Переход на страницу оплаты")
                except:
                    print("⚠️ Не дождались перехода на страницу оплаты")
                
                time.sleep(3)
            except Exception as e:
                print(f"⚠️ Ошибка нажатия кнопки в модалке: {e}")
            
            # Шаг 10: Получить результат со страницы оплаты
            print("📌 Получаю данные платежа...")
            
            qr_base64 = None
            payment_link = self.driver.current_url
            payment_data = {}
            
            # Извлекаем данные из таблицы
            try:
                # Ищем все строки таблицы
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
            
            # Поиск QR-кода (SVG)
            try:
                qr_svg = self.driver.find_element(By.CSS_SELECTOR, "svg[viewBox='0 0 37 37']")
                if qr_svg:
                    # Получаем outerHTML SVG
                    qr_base64 = self.driver.execute_script("return arguments[0].outerHTML;", qr_svg)
                    print("✅ QR-код найден (SVG)")
            except:
                print("⚠️ QR-код не найден")
            
            elapsed = time.time() - start_time
            
            # ПАУЗА ДЛЯ ПРОСМОТРА
            print(f"\n⏸️  ПАУЗА 60 СЕКУНД - Проверяй все заполненные данные!")
            print(f"   URL: {self.driver.current_url}")
            time.sleep(60)
            
            print(f"✅ Платеж создан за {elapsed:.1f} сек!")
            print(f"🔗 Ссылка: {payment_link}")
            
            return {
                "payment_link": payment_link,
                "qr_code": qr_base64,  # SVG QR-кода
                "payment_data": payment_data,  # Детали платежа
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
        """Закрытие браузера"""
        if self.driver:
            try:
                self.driver.quit()
                print("✅ Браузер закрыт")
            except:
                pass
            self.driver = None
