# -*- coding: utf-8 -*-
"""
Создание платежей через multitransfer.ru (рабочая версия)
"""

import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

try:
    from .config import EXAMPLE_SENDER_DATA, DEFAULT_COUNTRY, DEFAULT_BANK
except ImportError:
    from config import EXAMPLE_SENDER_DATA, DEFAULT_COUNTRY, DEFAULT_BANK


class MultitransferPayment:
    """Класс для работы с multitransfer.ru"""
    
    def __init__(self, sender_data=None, headless=True):
        self.url = "https://multitransfer.ru/"
        self.driver = None
        self.sender_data = sender_data or EXAMPLE_SENDER_DATA
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
        if os.path.exists('/usr/bin/google-chrome'):
            options.binary_location = '/usr/bin/google-chrome'
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)
        return driver
    
    def login(self):
        """Инициализация"""
        print(f"🔧 Инициализация multitransfer.ru...")
        
        self.driver = self._create_driver()
        self.driver.get(self.url)
        time.sleep(2)
        
        print("✅ Страница загружена, готов к созданию платежей")
        return True
    
    def create_payment(self, card_number, owner_name, amount):
        """Создание платежа"""
        print(f"\n💳 Создание платежа")
        print(f"   Карта: {card_number}")
        print(f"   Владелец: {owner_name}")
        print(f"   Сумма: {amount} RUB")
        
        start_time = time.time()
        
        try:
            wait = WebDriverWait(self.driver, 30)  # Увеличил с 20 до 30
            
            # Делаем скриншот начальной страницы
            try:
                self.driver.save_screenshot("/app/screenshots/step_0_start.png")
                print("📸 Скриншот: step_0_start.png")
            except:
                pass
            
            # Шаг 1: Выбрать страну "Узбекистан"
            print("📌 Выбираю Узбекистан...")
            time.sleep(2)  # Даём странице загрузиться
            
            try:
                country_selector = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".variant-alternative"))
                )
            except:
                # Пробуем другой селектор
                country_selector = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'variant-alternative')]"))
                )
            
            country_selector.click()
            time.sleep(0.5)
            
            try:
                self.driver.save_screenshot("/app/screenshots/step_1_country_opened.png")
            except:
                pass
            
            uzbekistan = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(., 'Узбекистан')]"))
            )
            uzbekistan.click()
            time.sleep(0.5)
            print("✅ Узбекистан выбран")
            
            try:
                self.driver.save_screenshot("/app/screenshots/step_2_country_selected.png")
            except:
                pass
            
            # Шаг 2: Ввод суммы
            print(f"📌 Ввожу сумму {amount} RUB...")
            
            # Пробуем разные селекторы для поля суммы
            amount_input = None
            try:
                amount_input = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='RUB']"))
                )
            except:
                try:
                    amount_input = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text'][placeholder*='0']"))
                    )
                except:
                    # Ищем любое input поле для суммы
                    inputs = self.driver.find_elements(By.TAG_NAME, "input")
                    for inp in inputs:
                        placeholder = (inp.get_attribute("placeholder") or "").lower()
                        if "rub" in placeholder or "руб" in placeholder or placeholder == "0":
                            amount_input = inp
                            break
            
            if not amount_input:
                raise Exception("Не удалось найти поле для ввода суммы")
            
            try:
                self.driver.save_screenshot("/app/screenshots/step_3_before_amount.png")
            except:
                pass
            
            # Очищаем и вводим сумму посимвольно для React
            amount_input.click()
            amount_input.clear()
            time.sleep(0.2)
            
            for char in str(amount):
                amount_input.send_keys(char)
                time.sleep(0.05)
            
            # Триггерим React события
            self.driver.execute_script("""
                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
            """, amount_input)
            
            print("✅ Сумма введена")
            time.sleep(3)  # Ждём React
            
            # Шаг 3: Открыть блок "Способ перевода"
            print("📌 Открываю 'Способ перевода'...")
            transfer_block = wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//div[contains(text(),'Способ перевода')]/ancestor::div[contains(@class,'variant-alternative')]"
                ))
            )
            transfer_block.click()
            print("✅ Блок способов перевода открыт")
            time.sleep(0.5)
            
            # Шаг 4: Выбрать Uzcard / Humo
            print("📌 Выбираю Uzcard / Humo...")
            try:
                # Пробуем разные способы найти банк
                bank_option = None
                try:
                    # Способ 1: По тексту Uzcard
                    bank_option = wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//*[contains(text(),'Uzcard')]"))
                    )
                except:
                    try:
                        # Способ 2: По тексту Humo
                        bank_option = wait.until(
                            EC.element_to_be_clickable((By.XPATH, "//*[contains(text(),'Humo')]"))
                        )
                    except:
                        # Способ 3: По любому элементу с обоими текстами
                        bank_option = wait.until(
                            EC.element_to_be_clickable((By.XPATH, "//*[contains(text(),'Uzcard') or contains(text(),'Humo') or contains(text(),'UZCARD') or contains(text(),'HUMO')]"))
                        )
                
                if bank_option:
                    bank_option.click()
                    print("✅ Банк выбран")
                    time.sleep(2)
            except Exception as e:
                print(f"⚠️ Не удалось выбрать банк автоматически: {e}")
                print("⚠️ Продолжаю без выбора банка...")
            
            # Шаг 5: Ввести номер карты и имя владельца НА ПЕРВОЙ СТРАНИЦЕ
            print("📌 Ввожу номер карты...")
            try:
                card_input = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[name*='beneficiary'], input[placeholder*='карт']"))
                )
                card_input.clear()
                card_input.send_keys(card_number)
                print(f"✅ Номер карты введён: {card_number}")
                time.sleep(0.5)
            except Exception as e:
                print(f"⚠️ Не удалось ввести карту на первой странице: {e}")
            
            print("📌 Ввожу имя владельца...")
            try:
                # Ищем поля для имени и фамилии
                name_parts = owner_name.split()
                inputs = self.driver.find_elements(By.TAG_NAME, "input")
                
                for inp in inputs:
                    placeholder = (inp.get_attribute("placeholder") or "").lower()
                    name_attr = (inp.get_attribute("name") or "").lower()
                    
                    if "имя" in placeholder or "firstname" in name_attr or "name" in placeholder:
                        inp.clear()
                        inp.send_keys(name_parts[0] if len(name_parts) > 0 else owner_name)
                        print(f"✅ Имя введено: {name_parts[0] if len(name_parts) > 0 else owner_name}")
                        time.sleep(0.3)
                        break
                
                for inp in inputs:
                    placeholder = (inp.get_attribute("placeholder") or "").lower()
                    name_attr = (inp.get_attribute("name") or "").lower()
                    
                    if "фамилия" in placeholder or "lastname" in name_attr or "surname" in placeholder:
                        if len(name_parts) > 1:
                            inp.clear()
                            inp.send_keys(name_parts[1])
                            print(f"✅ Фамилия введена: {name_parts[1]}")
                            time.sleep(0.3)
                        break
            except Exception as e:
                print(f"⚠️ Не удалось ввести имя на первой странице: {e}")
            
            time.sleep(1)
            
            # Шаг 6: Нажать кнопку "Продолжить"
            print("📌 Нажимаю 'Продолжить'...")
            continue_btn = wait.until(EC.element_to_be_clickable((By.ID, "pay")))
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", continue_btn)
            time.sleep(0.5)
            
            try:
                continue_btn.click()
            except:
                self.driver.execute_script("arguments[0].click();", continue_btn)
            
            print("✅ Кнопка 'Продолжить' нажата")
            
            # Ждём перехода на страницу sender-details
            wait.until(lambda d: "sender-details" in d.current_url)
            print("✅ Переход на страницу sender-details")
            time.sleep(2)
            
            # Шаг 7: Заполнить данные отправителя (данные получателя уже введены)
            print("📌 Заполняю данные отправителя...")
            self._fill_sender_data()
            
            # Шаг 8: Галочка согласия
            print("📌 Ставлю галочку согласия...")
            try:
                checkbox = self.driver.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
                if not checkbox.is_selected():
                    checkbox.click()
                    time.sleep(0.3)
            except:
                pass
            
            # Шаг 9: Нажимаем "Продолжить"
            print("📌 Нажимаю 'Продолжить' (отправка данных)...")
            pay_button = wait.until(EC.element_to_be_clickable((By.ID, "pay")))
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", pay_button)
            time.sleep(0.3)
            pay_button.click()
            time.sleep(2)
            
            # Шаг 10: Обрабатываем капчу если есть
            self._handle_captcha(wait)
            
            # Шаг 11: Нажимаем финальную кнопку в модалке
            print("📌 Нажимаю финальную кнопку...")
            try:
                final_btn = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.MuiButton-sizeLarge[buttontext='Продолжить']"))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", final_btn)
                time.sleep(0.3)
                final_btn.click()
                print("✅ Финальная кнопка нажата")
                
                wait.until(lambda d: "payment" in d.current_url or "result" in d.current_url, timeout=10)
                time.sleep(2)
            except Exception as e:
                print(f"⚠️ Ошибка финальной кнопки: {e}")
            
            # Получаем результат
            payment_link = self.driver.current_url
            elapsed = time.time() - start_time
            
            print(f"✅ Платеж создан за {elapsed:.1f} сек!")
            print(f"🔗 Ссылка: {payment_link}")
            
            return {
                "payment_link": payment_link,
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
    
    def _fill_recipient_data(self, card_number, owner_name):
        """Заполнение данных получателя"""
        self._fill_field("beneficiaryaccountnumber", card_number)
        name_parts = owner_name.split()
        if len(name_parts) > 0:
            self._fill_field("beneficiary_firstname", name_parts[0])
        if len(name_parts) > 1:
            self._fill_field("beneficiary_lastname", name_parts[1])
    
    def _fill_sender_data(self):
        """Заполнение данных отправителя"""
        self._fill_field("sender_documents_series", self.sender_data["passport_series"])
        self._fill_field("sender_documents_number", self.sender_data["passport_number"])
        self._fill_field("issuedate", self.sender_data["passport_issue_date"])
        self._select_country("birthPlaceAddress_countryCode", self.sender_data["birth_country"])
        self._fill_field("birthplaceaddress_full", self.sender_data["birth_place"])
        self._select_country("registrationAddress_countryCode", self.sender_data["registration_country"])
        self._fill_field("registrationaddress_full", self.sender_data["registration_place"])
        self._fill_field("sender_firstname", self.sender_data["first_name"])
        self._fill_field("sender_lastname", self.sender_data["last_name"])
        self._fill_field("birthdate", self.sender_data["birth_date"])
        self._fill_field("phonenumber", self.sender_data["phone"])
    
    def _fill_field(self, name_pattern, value):
        """Заполнение поля по паттерну имени"""
        try:
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            for inp in inputs:
                name_attr = (inp.get_attribute("name") or "").lower()
                if name_pattern.lower() in name_attr:
                    inp.clear()
                    inp.send_keys(value)
                    time.sleep(0.1)
                    return True
            return False
        except:
            return False
    
    def _select_country(self, name_pattern, country_name):
        """Выбор страны из MUI Autocomplete"""
        try:
            wait = WebDriverWait(self.driver, 10)
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            for inp in inputs:
                name_attr = (inp.get_attribute("name") or "")
                if name_pattern in name_attr:
                    self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", inp)
                    time.sleep(0.2)
                    inp.click()
                    time.sleep(0.2)
                    inp.clear()
                    time.sleep(0.1)
                    inp.send_keys(country_name)
                    time.sleep(0.5)
                    
                    try:
                        option = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li[role='option']")))
                        time.sleep(0.1)
                        option.click()
                        time.sleep(0.2)
                        return True
                    except:
                        inp.send_keys(Keys.ENTER)
                        time.sleep(0.2)
                        return True
            return False
        except:
            return False
    
    def _handle_captcha(self, wait):
        """Обработка капчи"""
        print("📌 Проверяю капчу...")
        try:
            captcha_iframe = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='smartcaptcha.yandexcloud.net/checkbox']"))
            )
            print("⚠️ Обнаружена капча!")
            
            self.driver.switch_to.frame(captcha_iframe)
            time.sleep(0.5)
            
            try:
                checkbox_button = self.driver.find_element(By.ID, "js-button")
                checkbox_button.click()
                print("✅ Капча пройдена")
                time.sleep(3)
            except:
                pass
            
            self.driver.switch_to.default_content()
            time.sleep(1)
        except:
            print("✅ Капча не обнаружена")
    
    def close(self):
        """Закрытие браузера"""
        if self.driver:
            try:
                self.driver.quit()
                print("✅ Браузер закрыт")
            except:
                pass
            self.driver = None
