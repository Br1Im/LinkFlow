# -*- coding: utf-8 -*-
"""
╨б╨╛╨╖╨┤╨░╨╜╨╕╨╡ ╨┐╨╗╨░╤В╨╡╨╢╨╡╨╣ ╤З╨╡╤А╨╡╨╖ multitransfer.ru
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
    # ╨Ф╨╗╤П ╨╖╨░╨┐╤Г╤Б╨║╨░ ╨▓╨╜╨╡ ╨┐╨░╨║╨╡╤В╨░
    from mui_helpers import set_mui_input_value, click_mui_element, wait_for_mui_button_enabled
    from sender_data import SENDER_DATA


class MultitransferPayment:
    """╨Ъ╨╗╨░╤Б╤Б ╨┤╨╗╤П ╤А╨░╨▒╨╛╤В╤Л ╤Б multitransfer.ru"""
    
    def __init__(self):
        self.url = "https://multitransfer.ru/"
        self.driver = None
    
    def _create_driver(self):
        """╨б╨╛╨╖╨┤╨░╨╜╨╕╨╡ Chrome ╨┤╤А╨░╨╣╨▓╨╡╤А╨░"""
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless=new')  # ╨Ю╤В╨║╨╗╤О╤З╨╡╨╜╨╛ ╨┤╨╗╤П ╨╛╤В╨╗╨░╨┤╨║╨╕
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(30)
        return driver
    
    def login(self, phone=None, password=None):
        """
        ╨Ш╨╜╨╕╤Ж╨╕╨░╨╗╨╕╨╖╨░╤Ж╨╕╤П (╨░╨▓╤В╨╛╤А╨╕╨╖╨░╤Ж╨╕╤П ╨╜╨╡ ╤В╤А╨╡╨▒╤Г╨╡╤В╤Б╤П ╨┤╨╗╤П multitransfer.ru)
        """
        print(f"ЁЯФз ╨Ш╨╜╨╕╤Ж╨╕╨░╨╗╨╕╨╖╨░╤Ж╨╕╤П multitransfer.ru...")
        
        self.driver = self._create_driver()
        self.driver.get(self.url)
        time.sleep(2)
        
        print("тЬЕ ╨б╤В╤А╨░╨╜╨╕╤Ж╨░ ╨╖╨░╨│╤А╤Г╨╢╨╡╨╜╨░")
        return True
    
    def create_payment(self, card_number, owner_name, amount):
        """
        ╨б╨╛╨╖╨┤╨░╨╜╨╕╨╡ ╨┐╨╗╨░╤В╨╡╨╢╨░ (React-safe ╨▓╨╡╤А╤Б╨╕╤П)
        
        Args:
            card_number: ╨Э╨╛╨╝╨╡╤А ╨║╨░╤А╤В╤Л ╨┐╨╛╨╗╤Г╤З╨░╤В╨╡╨╗╤П (╨г╨╖╨▒╨╡╨║╨╕╤Б╤В╨░╨╜)
            owner_name: ╨Ш╨╝╤П ╨▓╨╗╨░╨┤╨╡╨╗╤М╤Ж╨░ ╨║╨░╤А╤В╤Л
            amount: ╨б╤Г╨╝╨╝╨░ ╨┐╨╗╨░╤В╨╡╨╢╨░ ╨▓ ╤А╤Г╨▒╨╗╤П╤Е
            
        Returns:
            dict: {"payment_link": "...", "qr_base64": "..."}
        """
        print(f"\nЁЯТ│ ╨б╨╛╨╖╨┤╨░╨╜╨╕╨╡ ╨┐╨╗╨░╤В╨╡╨╢╨░ ╤З╨╡╤А╨╡╨╖ multitransfer.ru")
        print(f"   ╨Ъ╨░╤А╤В╨░: {card_number}")
        print(f"   ╨Т╨╗╨░╨┤╨╡╨╗╨╡╤Ж: {owner_name}")
        print(f"   ╨б╤Г╨╝╨╝╨░: {amount} ╤А╤Г╨▒.")
        
        start_time = time.time()
        
        try:
            wait = WebDriverWait(self.driver, 20)
            
            # ╨и╨░╨│ 1: ╨Т╤Л╨▒╤А╨░╤В╤М ╤Б╤В╤А╨░╨╜╤Г "╨г╨╖╨▒╨╡╨║╨╕╤Б╤В╨░╨╜" - ╨┐╤А╨╛╤Б╤В╨╛ ╨┐╨╡╤А╨╡╨╣╨┤╤С╨╝ ╨┐╨╛ URL
            print("ЁЯУМ ╨Т╤Л╨▒╨╕╤А╨░╤О ╨г╨╖╨▒╨╡╨║╨╕╤Б╤В╨░╨╜...")
            self.driver.get("https://multitransfer.ru/uzbekistan")
            time.sleep(5)  # ╨г╨▓╨╡╨╗╨╕╤З╨╕╨▓╨░╨╡╨╝ ╨╛╨╢╨╕╨┤╨░╨╜╨╕╨╡ ╨╖╨░╨│╤А╤Г╨╖╨║╨╕ React
            print("тЬЕ ╨г╨╖╨▒╨╡╨║╨╕╤Б╤В╨░╨╜ ╨▓╤Л╨▒╤А╨░╨╜")
            
            # ╨и╨░╨│ 2: ╨Т╨▓╨╛╨┤ ╤Б╤Г╨╝╨╝╤Л ╤З╨╡╤А╨╡╨╖ send_keys (React-safe)
            print(f"ЁЯУМ ╨Т╨▓╨╛╨╢╤Г ╤Б╤Г╨╝╨╝╤Г {amount} RUB (React-safe)...")
            # ╨Я╤А╨╛╨▒╤Г╨╡╨╝ ╤А╨░╨╖╨╜╤Л╨╡ ╤Б╨╡╨╗╨╡╨║╤В╨╛╤А╤Л
            amount_input = None
            selectors = [
                "input[placeholder='0 RUB']",
                "input[placeholder*='RUB']",
                "input[type='text'][inputmode='decimal']",
                ".money-input input"
            ]
            
            for selector in selectors:
                try:
                    amount_input = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue
            
            if not amount_input:
                raise Exception("╨Э╨╡ ╤Г╨┤╨░╨╗╨╛╤Б╤М ╨╜╨░╨╣╤В╨╕ ╨┐╨╛╨╗╨╡ ╨▓╨▓╨╛╨┤╨░ ╤Б╤Г╨╝╨╝╤Л")
            
            # ╨Ю╨┤╨╕╨╜ ╤А╨░╨╖ ╨▓╨▓╨╛╨┤╨╕╨╝ ╤Б╤Г╨╝╨╝╤Г ╨┐╨╛╤Б╨╕╨╝╨▓╨╛╨╗╤М╨╜╨╛
            set_mui_input_value(self.driver, amount_input, amount)
            print("тЬЕ ╨б╤Г╨╝╨╝╨░ ╨▓╨▓╨╡╨┤╨╡╨╜╨░")
            
            # ╨Ц╨┤╤С╨╝ ╨┐╨╛╨║╨░ React ╨╛╨▒╤А╨░╨▒╨╛╤В╨░╨╡╤В (╨Т╨Р╨Ц╨Э╨Ю: ╤В╨╛╨╗╤М╨║╨╛ ╨╖╨┤╨╡╤Б╤М 3 ╤Б╨╡╨║╤Г╨╜╨┤╤Л!)
            time.sleep(3)
            
            # ╨и╨░╨│ 3: ╨Ц╨┤╤С╨╝ ╨░╨║╤В╨╕╨▓╨░╤Ж╨╕╨╕ ╨║╨╜╨╛╨┐╨║╨╕ "╨Я╤А╨╛╨┤╨╛╨╗╨╢╨╕╤В╤М"
            print("ЁЯУМ ╨Ю╨╢╨╕╨┤╨░╤О ╨┐╨╛╨┤╤В╨▓╨╡╤А╨╢╨┤╨╡╨╜╨╕╤П ╤Б╤Г╨╝╨╝╤Л React...")
            if wait_for_mui_button_enabled(self.driver, "pay", timeout=5):
                print("тЬЕ ╨б╤Г╨╝╨╝╨░ ╨┐╨╛╨┤╤В╨▓╨╡╤А╨╢╨┤╨╡╨╜╨░ ╤Б╨░╨╣╤В╨╛╨╝")
            else:
                print("тЪая╕П ╨Ъ╨╜╨╛╨┐╨║╨░ '╨Я╤А╨╛╨┤╨╛╨╗╨╢╨╕╤В╤М' ╨╜╨╡ ╨░╨║╤В╨╕╨▓╨╕╤А╨╛╨▓╨░╨╗╨░╤Б╤М, ╨╜╨╛ ╨┐╤А╨╛╨┤╨╛╨╗╨╢╨░╨╡╨╝")
            
            # ╨и╨░╨│ 4: ╨Ю╤В╨║╤А╤Л╤В╤М ╨▒╨╗╨╛╨║ "╨б╨┐╨╛╤Б╨╛╨▒ ╨┐╨╡╤А╨╡╨▓╨╛╨┤╨░"
            print("ЁЯУМ ╨Ю╤В╨║╤А╤Л╨▓╨░╤О '╨б╨┐╨╛╤Б╨╛╨▒ ╨┐╨╡╤А╨╡╨▓╨╛╨┤╨░'...")
            transfer_block = wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//div[contains(text(),'╨б╨┐╨╛╤Б╨╛╨▒ ╨┐╨╡╤А╨╡╨▓╨╛╨┤╨░')]/ancestor::div[contains(@class,'variant-alternative')]"
                ))
            )
            click_mui_element(self.driver, transfer_block)
            print("тЬЕ ╨С╨╗╨╛╨║ ╤Б╨┐╨╛╤Б╨╛╨▒╨╛╨▓ ╨┐╨╡╤А╨╡╨▓╨╛╨┤╨░ ╨╛╤В╨║╤А╤Л╤В")
            time.sleep(0.5)
            
            # ╨и╨░╨│ 5: ╨Т╤Л╨▒╤А╨░╤В╤М Uzcard / Humo ╨┐╨╛ ╤В╨╡╨║╤Б╤В╤Г
            print("ЁЯУМ ╨Т╤Л╨▒╨╕╤А╨░╤О Uzcard / Humo...")
            bank_option = wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//*[contains(text(),'Uzcard') or contains(text(),'Humo')]"
                ))
            )
            click_mui_element(self.driver, bank_option)
            print("тЬЕ ╨С╨░╨╜╨║ ╨▓╤Л╨▒╤А╨░╨╜")
            time.sleep(2)  # ╨Ц╨┤╤С╨╝ ╨┐╨╛╨║╨░ React ╨╛╨▒╤А╨░╨▒╨╛╤В╨░╨╡╤В ╨▓╤Л╨▒╨╛╤А ╨▒╨░╨╜╨║╨░
            
            # ╨и╨░╨│ 6: ╨Э╨░╨╢╨░╤В╤М ╨║╨╜╨╛╨┐╨║╤Г "╨Я╤А╨╛╨┤╨╛╨╗╨╢╨╕╤В╤М" (╨Э╨Х ╨╖╨░╨┐╨╛╨╗╨╜╤П╨╡╨╝ ╨┤╨░╨╜╨╜╤Л╨╡ ╨║╨░╤А╤В╤Л!)
            print("ЁЯУМ ╨Э╨░╨╢╨╕╨╝╨░╤О '╨Я╤А╨╛╨┤╨╛╨╗╨╢╨╕╤В╤М'...")
            
            # ╨Ш╤Й╨╡╨╝ ╨║╨╜╨╛╨┐╨║╤Г "╨Я╤А╨╛╨┤╨╛╨╗╨╢╨╕╤В╤М" ╨┐╨╛ ID
            try:
                continue_btn = wait.until(
                    EC.element_to_be_clickable((By.ID, "pay"))
                )
                # ╨Я╤А╨╛╨║╤А╤Г╤З╨╕╨▓╨░╨╡╨╝ ╨║ ╨║╨╜╨╛╨┐╨║╨╡
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center', behavior:'instant'});",
                    continue_btn
                )
                time.sleep(0.5)
                # ╨Я╤А╨╛╨▒╤Г╨╡╨╝ ╨╛╨▒╤Л╤З╨╜╤Л╨╣ ╨║╨╗╨╕╨║
                continue_btn.click()
                print("тЬЕ ╨Ъ╨╜╨╛╨┐╨║╨░ '╨Я╤А╨╛╨┤╨╛╨╗╨╢╨╕╤В╤М' ╨╜╨░╨╢╨░╤В╨░")
                
                # ╨Ц╨┤╤С╨╝ ╨┐╨╡╤А╨╡╤Е╨╛╨┤╨░ ╨╜╨░ ╤Б╤В╤А╨░╨╜╨╕╤Ж╤Г sender-details
                wait.until(lambda d: "sender-details" in d.current_url)
                print("тЬЕ ╨Я╨╡╤А╨╡╤Е╨╛╨┤ ╨╜╨░ ╤Б╤В╤А╨░╨╜╨╕╤Ж╤Г sender-details")
                time.sleep(2)  # ╨Ц╨┤╤С╨╝ ╨┐╨╛╨╗╨╜╨╛╨╣ ╨╖╨░╨│╤А╤Г╨╖╨║╨╕ ╤Д╨╛╤А╨╝╤Л
                
            except Exception as e:
                print(f"тЪая╕П ╨Ю╤И╨╕╨▒╨║╨░ ╨║╨╗╨╕╨║╨░ ╨┐╨╛ ╨║╨╜╨╛╨┐╨║╨╡: {e}")
                # ╨Я╤А╨╛╨▒╤Г╨╡╨╝ JS ╨║╨╗╨╕╨║
                try:
                    continue_btn = self.driver.find_element(By.ID, "pay")
                    self.driver.execute_script("arguments[0].click();", continue_btn)
                    print("тЬЕ ╨Ъ╨╜╨╛╨┐╨║╨░ '╨Я╤А╨╛╨┤╨╛╨╗╨╢╨╕╤В╤М' ╨╜╨░╨╢╨░╤В╨░ (JS)")
                    
                    # ╨Ц╨┤╤С╨╝ ╨┐╨╡╤А╨╡╤Е╨╛╨┤╨░ ╨╜╨░ ╤Б╤В╤А╨░╨╜╨╕╤Ж╤Г sender-details
                    wait.until(lambda d: "sender-details" in d.current_url)
                    print("тЬЕ ╨Я╨╡╤А╨╡╤Е╨╛╨┤ ╨╜╨░ ╤Б╤В╤А╨░╨╜╨╕╤Ж╤Г sender-details")
                    time.sleep(2)
                    
                except Exception as e2:
                    print(f"тЪая╕П JS ╨║╨╗╨╕╨║ ╤В╨╛╨╢╨╡ ╨╜╨╡ ╤Б╤А╨░╨▒╨╛╤В╨░╨╗: {e2}")
            
            # ╨и╨░╨│ 7: ╨Ч╨░╨┐╨╛╨╗╨╜╨╕╤В╤М ╨┤╨░╨╜╨╜╤Л╨╡ ╨┐╨╛╨╗╤Г╤З╨░╤В╨╡╨╗╤П ╨╜╨░ ╤Б╤В╤А╨░╨╜╨╕╤Ж╨╡ sender-details
            print("ЁЯУМ ╨Ч╨░╨┐╨╛╨╗╨╜╤П╤О ╨┤╨░╨╜╨╜╤Л╨╡ ╨┐╨╛╨╗╤Г╤З╨░╤В╨╡╨╗╤П ╨╕ ╨╛╤В╨┐╤А╨░╨▓╨╕╤В╨╡╨╗╤П...")
            time.sleep(1)  # ╨Ц╨┤╤С╨╝ ╨╖╨░╨│╤А╤Г╨╖╨║╨╕ ╤Д╨╛╤А╨╝╤Л
            
            # ╨д╤Г╨╜╨║╤Ж╨╕╤П ╨┤╨╗╤П ╨┐╨╛╨╕╤Б╨║╨░ ╨╕ ╨╖╨░╨┐╨╛╨╗╨╜╨╡╨╜╨╕╤П ╨┐╨╛╨╗╤П
            def fill_field(name_pattern, value, field_name):
                try:
                    inputs = self.driver.find_elements(By.TAG_NAME, "input")
                    for inp in inputs:
                        name_attr = (inp.get_attribute("name") or "").lower()
                        if name_pattern in name_attr:
                            inp.clear()
                            inp.send_keys(value)
                            print(f"   тЬЕ {field_name}: {value}")
                            time.sleep(0.2)
                            return True
                    return False
                except Exception as e:
                    print(f"   тЪая╕П ╨Ю╤И╨╕╨▒╨║╨░ {field_name}: {e}")
                    return False
            
            # ╨д╤Г╨╜╨║╤Ж╨╕╤П ╨┤╨╗╤П ╨▓╤Л╨▒╨╛╤А╨░ ╤Б╤В╤А╨░╨╜╤Л ╨╕╨╖ MUI Autocomplete
            def select_country(name_pattern, country_name, field_name):
                try:
                    # ╨Ш╤Й╨╡╨╝ input ╤Б ╨╜╤Г╨╢╨╜╤Л╨╝ name
                    inputs = self.driver.find_elements(By.TAG_NAME, "input")
                    for inp in inputs:
                        name_attr = (inp.get_attribute("name") or "")
                        if name_pattern in name_attr:
                            # ╨Я╤А╨╛╨║╤А╤Г╤З╨╕╨▓╨░╨╡╨╝ ╨║ ╨┐╨╛╨╗╤О
                            self.driver.execute_script(
                                "arguments[0].scrollIntoView({block:'center'});",
                                inp
                            )
                            time.sleep(0.3)
                            
                            # ╨Ъ╨╗╨╕╨║╨░╨╡╨╝ ╨╜╨░ ╨┐╨╛╨╗╨╡ ╨┤╨╗╤П ╤Д╨╛╨║╤Г╤Б╨░
                            inp.click()
                            time.sleep(0.3)
                            
                            # ╨Ю╤З╨╕╤Й╨░╨╡╨╝ ╨╕ ╨▓╨▓╨╛╨┤╨╕╨╝ ╨╜╨░╨╖╨▓╨░╨╜╨╕╨╡ ╤Б╤В╤А╨░╨╜╤Л
                            inp.clear()
                            time.sleep(0.1)
                            inp.send_keys(country_name)
                            time.sleep(0.8)  # ╨Ц╨┤╤С╨╝ ╨┐╨╛╤П╨▓╨╗╨╡╨╜╨╕╤П ╤Б╨┐╨╕╤Б╨║╨░
                            
                            # ╨Ш╤Й╨╡╨╝ ╨▓╤Л╨┐╨░╨┤╨░╤О╤Й╨╕╨╣ ╤Б╨┐╨╕╤Б╨╛╨║
                            try:
                                # ╨Ц╨┤╤С╨╝ ╨┐╨╛╤П╨▓╨╗╨╡╨╜╨╕╤П ╨╛╨┐╤Ж╨╕╨╣
                                option = wait.until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, "li[role='option']"))
                                )
                                time.sleep(0.2)
                                # ╨Ъ╨╗╨╕╨║╨░╨╡╨╝ ╨╜╨░ ╨┐╨╡╤А╨▓╤Г╤О ╨╛╨┐╤Ж╨╕╤О
                                option.click()
                                print(f"   тЬЕ {field_name}: {country_name}")
                                time.sleep(0.3)
                                return True
                            except:
                                # ╨Х╤Б╨╗╨╕ ╨╜╨╡ ╨╜╨░╤И╨╗╨╕ ╤Б╨┐╨╕╤Б╨╛╨║, ╨┐╤А╨╛╨▒╤Г╨╡╨╝ ╨╜╨░╨╢╨░╤В╤М Enter
                                inp.send_keys(Keys.ENTER)
                                print(f"   тЬЕ {field_name}: {country_name} (Enter)")
                                time.sleep(0.3)
                                return True
                    
                    print(f"   тЪая╕П ╨Я╨╛╨╗╨╡ {field_name} ╨╜╨╡ ╨╜╨░╨╣╨┤╨╡╨╜╨╛ (pattern: {name_pattern})")
                    return False
                except Exception as e:
                    print(f"   тЪая╕П ╨Ю╤И╨╕╨▒╨║╨░ {field_name}: {e}")
                    return False
            
            # ╨Ч╨░╨┐╨╛╨╗╨╜╤П╨╡╨╝ ╨┤╨░╨╜╨╜╤Л╨╡ ╨┐╨╛╨╗╤Г╤З╨░╤В╨╡╨╗╤П
            fill_field("beneficiaryaccountnumber", card_number, "╨Э╨╛╨╝╨╡╤А ╨║╨░╤А╤В╤Л ╨┐╨╛╨╗╤Г╤З╨░╤В╨╡╨╗╤П")
            fill_field("beneficiary_firstname", owner_name.split()[0], "╨Ш╨╝╤П ╨┐╨╛╨╗╤Г╤З╨░╤В╨╡╨╗╤П")
            if len(owner_name.split()) > 1:
                fill_field("beneficiary_lastname", owner_name.split()[1], "╨д╨░╨╝╨╕╨╗╨╕╤П ╨┐╨╛╨╗╤Г╤З╨░╤В╨╡╨╗╤П")
            
            # ╨Ч╨░╨┐╨╛╨╗╨╜╤П╨╡╨╝ ╨┐╨░╤Б╨┐╨╛╤А╤В╨╜╤Л╨╡ ╨┤╨░╨╜╨╜╤Л╨╡ ╨╛╤В╨┐╤А╨░╨▓╨╕╤В╨╡╨╗╤П
            fill_field("sender_documents_series", SENDER_DATA["passport_series"], "╨б╨╡╤А╨╕╤П ╨┐╨░╤Б╨┐╨╛╤А╤В╨░")
            fill_field("sender_documents_number", SENDER_DATA["passport_number"], "╨Э╨╛╨╝╨╡╤А ╨┐╨░╤Б╨┐╨╛╤А╤В╨░")
            fill_field("issuedate", SENDER_DATA["passport_issue_date"], "╨Ф╨░╤В╨░ ╨▓╤Л╨┤╨░╤З╨╕")
            
            # ╨б╤В╤А╨░╨╜╨░ ╤А╨╛╨╢╨┤╨╡╨╜╨╕╤П (MUI Autocomplete)
            select_country("birthPlaceAddress_countryCode", SENDER_DATA["birth_country"], "╨б╤В╤А╨░╨╜╨░ ╤А╨╛╨╢╨┤╨╡╨╜╨╕╤П")
            
            # ╨Ь╨╡╤Б╤В╨╛ ╤А╨╛╨╢╨┤╨╡╨╜╨╕╤П
            fill_field("birthplaceaddress_full", SENDER_DATA["birth_place"], "╨Ь╨╡╤Б╤В╨╛ ╤А╨╛╨╢╨┤╨╡╨╜╨╕╤П")
            
            # ╨б╤В╤А╨░╨╜╨░ ╤А╨╡╨│╨╕╤Б╤В╤А╨░╤Ж╨╕╨╕ (MUI Autocomplete)
            select_country("registrationAddress_countryCode", SENDER_DATA["registration_country"], "╨б╤В╤А╨░╨╜╨░ ╤А╨╡╨│╨╕╤Б╤В╤А╨░╤Ж╨╕╨╕")
            
            # ╨Ь╨╡╤Б╤В╨╛ ╤А╨╡╨│╨╕╤Б╤В╤А╨░╤Ж╨╕╨╕
            fill_field("registrationaddress_full", SENDER_DATA["registration_place"], "╨Ь╨╡╤Б╤В╨╛ ╤А╨╡╨│╨╕╤Б╤В╤А╨░╤Ж╨╕╨╕")
            
            # ╨Ы╨╕╤З╨╜╤Л╨╡ ╨┤╨░╨╜╨╜╤Л╨╡ ╨╛╤В╨┐╤А╨░╨▓╨╕╤В╨╡╨╗╤П
            fill_field("sender_firstname", SENDER_DATA["first_name"], "╨Ш╨╝╤П ╨╛╤В╨┐╤А╨░╨▓╨╕╤В╨╡╨╗╤П")
            fill_field("sender_lastname", SENDER_DATA["last_name"], "╨д╨░╨╝╨╕╨╗╨╕╤П ╨╛╤В╨┐╤А╨░╨▓╨╕╤В╨╡╨╗╤П")
            fill_field("birthdate", SENDER_DATA["birth_date"], "╨Ф╨░╤В╨░ ╤А╨╛╨╢╨┤╨╡╨╜╨╕╤П")
            fill_field("phonenumber", SENDER_DATA["phone"], "╨в╨╡╨╗╨╡╤Д╨╛╨╜")
            
            print("тЬЕ ╨Т╤Б╨╡ ╨┤╨░╨╜╨╜╤Л╨╡ ╨╖╨░╨┐╨╛╨╗╨╜╨╡╨╜╤Л")
            time.sleep(1)
            
            # ╨и╨░╨│ 8: ╨Я╨╛╤Б╤В╨░╨▓╨╕╤В╤М ╨│╨░╨╗╨╛╤З╨║╤Г ╤Б╨╛╨│╨╗╨░╤Б╨╕╤П
            print("ЁЯУМ ╨б╤В╨░╨▓╨╗╤О ╨│╨░╨╗╨╛╤З╨║╤Г ╤Б╨╛╨│╨╗╨░╤Б╨╕╤П...")
            try:
                checkbox = self.driver.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
                if not checkbox.is_selected():
                    checkbox.click()
                    print("тЬЕ ╨У╨░╨╗╨╛╤З╨║╨░ ╨┐╨╛╤Б╤В╨░╨▓╨╗╨╡╨╜╨░")
                    time.sleep(0.5)
            except Exception as e:
                print(f"тЪая╕П ╨Ю╤И╨╕╨▒╨║╨░ ╤Б ╨│╨░╨╗╨╛╤З╨║╨╛╨╣: {e}")
            
            # ╨и╨░╨│ 9: ╨Э╨░╨╢╨░╤В╤М ╨║╨╜╨╛╨┐╨║╤Г "╨Я╤А╨╛╨┤╨╛╨╗╨╢╨╕╤В╤М" (╨┐╨╛╤П╨▓╨╕╤В╤Б╤П ╨║╨░╨┐╤З╨░)
            print("ЁЯУМ ╨Э╨░╨╢╨╕╨╝╨░╤О ╨║╨╜╨╛╨┐╨║╤Г '╨Я╤А╨╛╨┤╨╛╨╗╨╢╨╕╤В╤М' (id=pay)...")
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
                print("тЬЕ ╨Ъ╨╜╨╛╨┐╨║╨░ ╨╜╨░╨╢╨░╤В╨░, ╨╛╨╢╨╕╨┤╨░╤О ╨┐╨╛╤П╨▓╨╗╨╡╨╜╨╕╤П ╨║╨░╨┐╤З╨╕...")
                time.sleep(2)
            except Exception as e:
                print(f"тЪая╕П ╨Ю╤И╨╕╨▒╨║╨░ ╨╜╨░╨╢╨░╤В╨╕╤П ╨║╨╜╨╛╨┐╨║╨╕: {e}")
            
            # ╨и╨░╨│ 10: ╨а╨╡╤И╨░╨╡╨╝ ╨║╨░╨┐╤З╤Г ╨╡╤Б╨╗╨╕ ╨┐╨╛╤П╨▓╨╕╨╗╨░╤Б╤М
            print("ЁЯУМ ╨Я╤А╨╛╨▓╨╡╤А╤П╤О ╨╜╨░╨╗╨╕╤З╨╕╨╡ ╨║╨░╨┐╤З╨╕...")
            try:
                # ╨Ш╤Й╨╡╨╝ iframe ╤Б ╨║╨░╨┐╤З╨╡╨╣
                captcha_iframe = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='smartcaptcha.yandexcloud.net/checkbox']"))
                )
                print("тЪая╕П ╨Ю╨▒╨╜╨░╤А╤Г╨╢╨╡╨╜╨░ Yandex SmartCaptcha!")
                
                # ╨Я╨╡╤А╨╡╨║╨╗╤О╤З╨░╨╡╨╝╤Б╤П ╨╜╨░ iframe
                self.driver.switch_to.frame(captcha_iframe)
                time.sleep(1)
                
                # ╨Ш╤Й╨╡╨╝ ╨║╨╜╨╛╨┐╨║╤Г ╤З╨╡╨║╨▒╨╛╨║╤Б╨░ ╨╕ ╨║╨╗╨╕╨║╨░╨╡╨╝
                try:
                    # ╨Ш╤Й╨╡╨╝ ╨║╨╜╨╛╨┐╨║╤Г ╨┐╨╛ ID ╨╕╨╗╨╕ ╨║╨╗╨░╤Б╤Б╤Г
                    checkbox_button = None
                    try:
                        checkbox_button = self.driver.find_element(By.ID, "js-button")
                    except:
                        checkbox_button = self.driver.find_element(By.CLASS_NAME, "CheckboxCaptcha-Button")
                    
                    if checkbox_button:
                        # ╨Я╤А╨╛╨║╤А╤Г╤З╨╕╨▓╨░╨╡╨╝ ╨║ ╨║╨╜╨╛╨┐╨║╨╡
                        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", checkbox_button)
                        time.sleep(0.5)
                        
                        # ╨Ъ╨╗╨╕╨║╨░╨╡╨╝
                        checkbox_button.click()
                        print("тЬЕ ╨Ъ╨╗╨╕╨║╨╜╤Г╨╗ ╨┐╨╛ ╤З╨╡╨║╨▒╨╛╨║╤Б╤Г ╨║╨░╨┐╤З╨╕")
                        time.sleep(5)  # ╨г╨▓╨╡╨╗╨╕╤З╨╕╨▓╨░╨╡╨╝ ╨╛╨╢╨╕╨┤╨░╨╜╨╕╨╡ ╨┤╨╗╤П ╨┐╨╛╤П╨▓╨╗╨╡╨╜╨╕╤П ╨╝╨╛╨┤╨░╨╗╨║╨╕
                        
                        # ╨Т╨╛╨╖╨▓╤А╨░╤Й╨░╨╡╨╝╤Б╤П ╨▓ ╨╛╤Б╨╜╨╛╨▓╨╜╨╛╨╣ ╨║╨╛╨╜╤В╨╡╨║╤Б╤В
                        self.driver.switch_to.default_content()
                        
                        print("тЬЕ ╨Ъ╨░╨┐╤З╨░ ╨┐╤А╨╛╨╣╨┤╨╡╨╜╨░!")
                    
                except Exception as e:
                    print(f"тЪая╕П ╨Ю╤И╨╕╨▒╨║╨░ ╨║╨╗╨╕╨║╨░ ╨┐╨╛ ╨║╨░╨┐╤З╨╡: {e}")
                    self.driver.switch_to.default_content()
                    time.sleep(5)
                    
            except:
                print("тЬЕ ╨Ъ╨░╨┐╤З╨░ ╨╜╨╡ ╨╛╨▒╨╜╨░╤А╤Г╨╢╨╡╨╜╨░")
                
            time.sleep(2)  # ╨Ф╨╛╨┐╨╛╨╗╨╜╨╕╤В╨╡╨╗╤М╨╜╨╛╨╡ ╨╛╨╢╨╕╨┤╨░╨╜╨╕╨╡ ╨┐╨╛╤П╨▓╨╗╨╡╨╜╨╕╤П ╨╝╨╛╨┤╨░╨╗╨║╨╕
            
            # ╨и╨░╨│ 9: ╨Э╨░╨╢╨░╤В╤М ╨║╨╜╨╛╨┐╨║╤Г "╨Я╤А╨╛╨┤╨╛╨╗╨╢╨╕╤В╤М" ╨▓ ╨╝╨╛╨┤╨░╨╗╨║╨╡ "╨Я╤А╨╛╨▓╨╡╤А╨║╨░ ╨┤╨░╨╜╨╜╤Л╤Е"
            print("ЁЯУМ ╨Э╨░╨╢╨╕╨╝╨░╤О ╨║╨╜╨╛╨┐╨║╤Г '╨Я╤А╨╛╨┤╨╛╨╗╨╢╨╕╤В╤М' ╨▓ ╨╝╨╛╨┤╨░╨╗╨║╨╡...")
            try:
                # ╨Ц╨┤╤С╨╝ ╨┐╨╛╤П╨▓╨╗╨╡╨╜╨╕╤П ╨╝╨╛╨┤╨░╨╗╨║╨╕ ╤Б ╨┐╤А╨╛╨▓╨╡╤А╨║╨╛╨╣ ╨┤╨░╨╜╨╜╤Л╤Е
                # ╨Ш╤Й╨╡╨╝ ╨╕╨╝╨╡╨╜╨╜╨╛ ╨▒╨╛╨╗╤М╤И╤Г╤О ╨║╨╜╨╛╨┐╨║╤Г ╨▓╨╜╨╕╨╖╤Г (sizeLarge), ╨░ ╨╜╨╡ ╨║╤А╨╡╤Б╤В╨╕╨║
                final_btn = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.MuiButton-sizeLarge[buttontext='╨Я╤А╨╛╨┤╨╛╨╗╨╢╨╕╤В╤М']"))
                )
                print("тЬЕ ╨Ь╨╛╨┤╨░╨╗╨║╨░ '╨Я╤А╨╛╨▓╨╡╤А╨║╨░ ╨┤╨░╨╜╨╜╤Л╤Е' ╨┐╨╛╤П╨▓╨╕╨╗╨░╤Б╤М")
                
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});",
                    final_btn
                )
                time.sleep(0.5)
                
                # ╨Я╤А╨╛╨▒╤Г╨╡╨╝ ╨╛╨▒╤Л╤З╨╜╤Л╨╣ ╨║╨╗╨╕╨║
                try:
                    final_btn.click()
                    print("тЬЕ ╨Ъ╨╜╨╛╨┐╨║╨░ '╨Я╤А╨╛╨┤╨╛╨╗╨╢╨╕╤В╤М' ╨╜╨░╨╢╨░╤В╨░")
                except:
                    # ╨Х╤Б╨╗╨╕ ╨╜╨╡ ╤Б╤А╨░╨▒╨╛╤В╨░╨╗, ╨┐╤А╨╛╨▒╤Г╨╡╨╝ JS ╨║╨╗╨╕╨║
                    self.driver.execute_script("arguments[0].click();", final_btn)
                    print("тЬЕ ╨Ъ╨╜╨╛╨┐╨║╨░ '╨Я╤А╨╛╨┤╨╛╨╗╨╢╨╕╤В╤М' ╨╜╨░╨╢╨░╤В╨░ (JS)")
                
                # ╨Ц╨┤╤С╨╝ ╨┐╨╡╤А╨╡╤Е╨╛╨┤╨░ ╨╜╨░ ╤Б╤В╤А╨░╨╜╨╕╤Ж╤Г payment
                try:
                    wait.until(lambda d: "payment" in d.current_url or "result" in d.current_url, timeout=10)
                    print("тЬЕ ╨Я╨╡╤А╨╡╤Е╨╛╨┤ ╨╜╨░ ╤Б╤В╤А╨░╨╜╨╕╤Ж╤Г ╨╛╨┐╨╗╨░╤В╤Л")
                except:
                    print("тЪая╕П ╨Э╨╡ ╨┤╨╛╨╢╨┤╨░╨╗╨╕╤Б╤М ╨┐╨╡╤А╨╡╤Е╨╛╨┤╨░ ╨╜╨░ ╤Б╤В╤А╨░╨╜╨╕╤Ж╤Г ╨╛╨┐╨╗╨░╤В╤Л")
                
                time.sleep(3)
            except Exception as e:
                print(f"тЪая╕П ╨Ю╤И╨╕╨▒╨║╨░ ╨╜╨░╨╢╨░╤В╨╕╤П ╨║╨╜╨╛╨┐╨║╨╕ ╨▓ ╨╝╨╛╨┤╨░╨╗╨║╨╡: {e}")
            
            # ╨и╨░╨│ 10: ╨Я╨╛╨╗╤Г╤З╨╕╤В╤М ╤А╨╡╨╖╤Г╨╗╤М╤В╨░╤В ╤Б╨╛ ╤Б╤В╤А╨░╨╜╨╕╤Ж╤Л ╨╛╨┐╨╗╨░╤В╤Л
            print("ЁЯУМ ╨Я╨╛╨╗╤Г╤З╨░╤О ╨┤╨░╨╜╨╜╤Л╨╡ ╨┐╨╗╨░╤В╨╡╨╢╨░...")
            
            qr_base64 = None
            payment_link = self.driver.current_url
            payment_data = {}
            
            # ╨Ш╨╖╨▓╨╗╨╡╨║╨░╨╡╨╝ ╨┤╨░╨╜╨╜╤Л╨╡ ╨╕╨╖ ╤В╨░╨▒╨╗╨╕╤Ж╤Л
            try:
                # ╨Ш╤Й╨╡╨╝ ╨▓╤Б╨╡ ╤Б╤В╤А╨╛╨║╨╕ ╤В╨░╨▒╨╗╨╕╤Ж╤Л
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
                    print("тЬЕ ╨Ф╨░╨╜╨╜╤Л╨╡ ╨┐╨╗╨░╤В╨╡╨╢╨░ ╨┐╨╛╨╗╤Г╤З╨╡╨╜╤Л:")
                    for key, value in payment_data.items():
                        print(f"   тАв {key}: {value}")
                        
            except Exception as e:
                print(f"тЪая╕П ╨Ю╤И╨╕╨▒╨║╨░ ╨╕╨╖╨▓╨╗╨╡╤З╨╡╨╜╨╕╤П ╨┤╨░╨╜╨╜╤Л╤Е: {e}")
            
            # ╨Я╨╛╨╕╤Б╨║ QR-╨║╨╛╨┤╨░ (SVG)
            try:
                qr_svg = self.driver.find_element(By.CSS_SELECTOR, "svg[viewBox='0 0 37 37']")
                if qr_svg:
                    # ╨Я╨╛╨╗╤Г╤З╨░╨╡╨╝ outerHTML SVG
                    qr_base64 = self.driver.execute_script("return arguments[0].outerHTML;", qr_svg)
                    print("тЬЕ QR-╨║╨╛╨┤ ╨╜╨░╨╣╨┤╨╡╨╜ (SVG)")
            except:
                print("тЪая╕П QR-╨║╨╛╨┤ ╨╜╨╡ ╨╜╨░╨╣╨┤╨╡╨╜")
            
            elapsed = time.time() - start_time
            
            # ╨Я╨Р╨г╨Ч╨Р ╨Ф╨Ы╨п ╨Я╨а╨Ю╨б╨Ь╨Ю╨в╨а╨Р
            print(f"\nтП╕я╕П  ╨Я╨Р╨г╨Ч╨Р 60 ╨б╨Х╨Ъ╨г╨Э╨Ф - ╨Я╤А╨╛╨▓╨╡╤А╤П╨╣ ╨▓╤Б╨╡ ╨╖╨░╨┐╨╛╨╗╨╜╨╡╨╜╨╜╤Л╨╡ ╨┤╨░╨╜╨╜╤Л╨╡!")
            print(f"   URL: {self.driver.current_url}")
            time.sleep(60)
            
            print(f"тЬЕ ╨Я╨╗╨░╤В╨╡╨╢ ╤Б╨╛╨╖╨┤╨░╨╜ ╨╖╨░ {elapsed:.1f} ╤Б╨╡╨║!")
            print(f"ЁЯФЧ ╨б╤Б╤Л╨╗╨║╨░: {payment_link}")
            
            return {
                "payment_link": payment_link,
                "qr_code": qr_base64,  # SVG QR-╨║╨╛╨┤╨░
                "payment_data": payment_data,  # ╨Ф╨╡╤В╨░╨╗╨╕ ╨┐╨╗╨░╤В╨╡╨╢╨░
                "elapsed_time": elapsed,
                "success": True
            }
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"тЭМ ╨Ю╤И╨╕╨▒╨║╨░: {e}")
            import traceback
            traceback.print_exc()
            return {
                "error": str(e),
                "elapsed_time": elapsed,
                "success": False
            }
    
    def close(self):
        """╨Ч╨░╨║╤А╤Л╤В╨╕╨╡ ╨▒╤А╨░╤Г╨╖╨╡╤А╨░"""
        if self.driver:
            try:
                self.driver.quit()
                print("тЬЕ ╨С╤А╨░╤Г╨╖╨╡╤А ╨╖╨░╨║╤А╤Л╤В")
            except:
                pass
            self.driver = None
