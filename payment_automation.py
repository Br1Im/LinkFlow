from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
import base64
import threading
from dotenv import load_dotenv

load_dotenv()

PROFILE_BASE_PATH = os.path.join(os.getcwd(), "profiles")

if not os.path.exists(PROFILE_BASE_PATH):
    os.makedirs(PROFILE_BASE_PATH)


class WarmBrowser:
    def __init__(self):
        self.driver = None
        self.is_ready = False
        self.card_number = None
        self.owner_name = None
        self.account_phone = None
        self.lock = threading.Lock()
        self.last_activity = 0

    def warmup(self, card_number, owner_name):
        from database import db

        with self.lock:
            if (self.is_ready and self.driver and
                self.card_number == card_number and
                self.owner_name == owner_name):
                print("🔥 Браузер уже прогрет!", flush=True)
                return True

            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
                self.is_ready = False

            accounts = db.get_accounts()
            if not accounts:
                print("❌ Нет аккаунтов для прогрева", flush=True)
                return False

            account = accounts[0]
            profile_path = os.path.join(PROFILE_BASE_PATH, account['profile_path'])

            print(f"\n🔥 ПРОГРЕВ БРАУЗЕРА...", flush=True)
            start_time = time.time()

            try:
                options = webdriver.ChromeOptions()
                options.add_argument(f'--user-data-dir={profile_path}')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-gpu')
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.page_load_strategy = 'eager'

                self.driver = webdriver.Chrome(options=options)
                self.driver.set_page_load_timeout(20)

                self.driver.get('https://1.elecsnet.ru/NotebookFront/services/0mhp/default.aspx?merchantId=36924&fromSegment=')

                wait = WebDriverWait(self.driver, 10)

                try:
                    login_btn = self.driver.find_element(By.CSS_SELECTOR, "a.login[href='main']")
                    print("⚠️ Требуется авторизация...", flush=True)
                    self.driver.execute_script("arguments[0].click();", login_btn)
                    time.sleep(1)

                    popup = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.popup.login")))
                    phone_input = self.driver.find_element(By.CSS_SELECTOR, "div.popup.login #Login_Value")
                    phone_clean = account['phone'].replace("+7", "").replace(" ", "").replace("-", "")
                    phone_input.send_keys(phone_clean)

                    password_input = self.driver.find_element(By.CSS_SELECTOR, "div.popup.login #Password_Value")
                    password_input.send_keys(account['password'])

                    auth_btn = self.driver.find_element(By.CSS_SELECTOR, "div.popup.login #authBtn")
                    self.driver.execute_script("arguments[0].click();", auth_btn)
                    time.sleep(3)

                    self.driver.get('https://1.elecsnet.ru/NotebookFront/services/0mhp/default.aspx?merchantId=36924&fromSegment=')
                    time.sleep(1)
                except:
                    pass

                wait.until(EC.invisibility_of_element_located((By.ID, "loadercontainer")))

                card_input = wait.until(EC.element_to_be_clickable((By.NAME, "requisites.m-36924.f-1")))
                card_input.clear()
                card_input.send_keys(card_number)

                name_input = wait.until(EC.element_to_be_clickable((By.NAME, "requisites.m-36924.f-2")))
                name_input.clear()
                name_input.send_keys(owner_name)

                self.card_number = card_number
                self.owner_name = owner_name
                self.account_phone = account['phone']
                self.is_ready = True
                self.last_activity = time.time()

                elapsed = time.time() - start_time
                print(f"🔥 Браузер прогрет за {elapsed:.1f} сек!", flush=True)
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
        with self.lock:
            if not self.is_ready or not self.driver:
                return {"error": "Браузер не прогрет"}

            start_time = time.time()

            try:
                wait = WebDriverWait(self.driver, 10)


                print(f"[{time.time()-start_time:.1f}s] Заполняю сумму...", flush=True)
                amount_input = wait.until(EC.element_to_be_clickable((By.NAME, "summ.transfer")))
                amount_input.clear()
                amount_input.send_keys(str(amount))


                print(f"[{time.time()-start_time:.1f}s] Ожидаю обработку...", flush=True)
                time.sleep(1)

                try:
                    wait.until(EC.invisibility_of_element_located((By.ID, "loadercontainer")))
                    print(f"[{time.time()-start_time:.1f}s] Loader исчез", flush=True)
                except:
                    print(f"[{time.time()-start_time:.1f}s] Loader не найден", flush=True)
                    pass

                print(f"[{time.time()-start_time:.1f}s] Ищу кнопку Оплатить...", flush=True)
                submit_btn = wait.until(EC.presence_of_element_located((By.NAME, "SubmitBtn")))
                
                print(f"[{time.time()-start_time:.1f}s] Жду активации кнопки...", flush=True)
                for i in range(20):
                    is_disabled = submit_btn.get_attribute("disabled")
                    if not is_disabled:
                        print(f"[{time.time()-start_time:.1f}s] Кнопка активна!", flush=True)
                        break
                    if i % 5 == 0:
                        print(f"[{time.time()-start_time:.1f}s] Кнопка ещё неактивна (попытка {i+1}/20)...", flush=True)
                    time.sleep(0.3)

                print(f"[{time.time()-start_time:.1f}s] Нажимаю Оплатить...", flush=True)
                try:
                    submit_btn.click()
                except:
                    print(f"[{time.time()-start_time:.1f}s] Обычный клик не сработал, пробую JS...", flush=True)
                    self.driver.execute_script("arguments[0].click();", submit_btn)

                print(f"[{time.time()-start_time:.1f}s] Ожидаю QR-код...", flush=True)
                qr_img = wait.until(EC.presence_of_element_located((By.ID, "Image1")))
                qr_code_base64 = qr_img.get_attribute("src")

                payment_link_element = wait.until(EC.presence_of_element_located((By.ID, "LinkMobil")))
                payment_link = payment_link_element.get_attribute("href")

                qr_code_data = qr_code_base64.split(",")[1] if "," in qr_code_base64 else qr_code_base64
                qr_filename = f"qr_{int(time.time())}.png"
                with open(qr_filename, "wb") as f:
                    f.write(base64.b64decode(qr_code_data))

                elapsed = time.time() - start_time

                print(f"\n✅ ПЛАТЁЖ СОЗДАН за {elapsed:.1f} сек!", flush=True)
                print(f"🔗 {payment_link}", flush=True)
                
                result = {
                    "qr_file": qr_filename,
                    "payment_link": payment_link,
                    "elapsed_time": elapsed,
                    "account_used": self.account_phone
                }
                
                try:
                    print("🔄 Возвращаюсь на страницу создания...", flush=True)
                    self.driver.get('https://1.elecsnet.ru/NotebookFront/services/0mhp/default.aspx?merchantId=36924&fromSegment=')
                    time.sleep(2)
                    
                    wait = WebDriverWait(self.driver, 15)
                    wait.until(EC.invisibility_of_element_located((By.ID, "loadercontainer")))
                    
                    card_input = wait.until(EC.element_to_be_clickable((By.NAME, "requisites.m-36924.f-1")))
                    card_input.clear()
                    card_input.send_keys(self.card_number)
                    time.sleep(0.2)
                    
                    name_input = wait.until(EC.element_to_be_clickable((By.NAME, "requisites.m-36924.f-2")))
                    name_input.clear()
                    name_input.send_keys(self.owner_name)
                    
                    print("✅ Браузер готов к следующему платежу!", flush=True)
                    self.is_ready = True
                except Exception as e:
                    print(f"⚠️ Не удалось подготовить к следующему платежу: {e}", flush=True)
                    self.is_ready = False
                
                return result

            except Exception as e:
                elapsed = time.time() - start_time
                print(f"❌ Ошибка: {e}", flush=True)
                self.is_ready = False
                return {"error": str(e), "elapsed_time": elapsed}

    def close(self):

        with self.lock:
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
            self.is_ready = False



warm_browser = WarmBrowser()


def warmup_browser(card_number, owner_name):

    return warm_browser.warmup(card_number, owner_name)


def create_payment_fast(amount):

    return warm_browser.create_payment(amount)


def is_browser_ready():

    return warm_browser.is_ready



def login_account(phone: str, password: str, profile_name: str) -> dict:

    profile_path = os.path.join(PROFILE_BASE_PATH, profile_name)

    print(f"\n{'='*60}", flush=True)
    print(f"🔐 ВХОД В АККАУНТ: {phone}", flush=True)
    print(f"{'='*60}", flush=True)

    options = webdriver.ChromeOptions()
    options.add_argument(f'--user-data-dir={profile_path}')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-blink-features=AutomationControlled')

    driver = None
    start_time = time.time()

    try:
        print(f"[{time.time()-start_time:.1f}s] Запускаю браузер...", flush=True)
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(30)

        print(f"[{time.time()-start_time:.1f}s] Открываю страницу...", flush=True)
        driver.get('https://1.elecsnet.ru/NotebookFront/')

        wait = WebDriverWait(driver, 15)
        time.sleep(2)

        try:
            login_btn = driver.find_element(By.CSS_SELECTOR, "a.login[href='main']")
            print(f"[{time.time()-start_time:.1f}s] Нажимаю кнопку Вход...", flush=True)
            driver.execute_script("arguments[0].click();", login_btn)
            time.sleep(1)

            popup = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.popup.login")))
            phone_input = wait.until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "div.popup.login #Login_Value")
            ))

            phone_clean = phone.replace("+7", "").replace(" ", "").replace("-", "")
            print(f"[{time.time()-start_time:.1f}s] Ввожу телефон: {phone_clean}", flush=True)
            phone_input.clear()
            phone_input.send_keys(phone_clean)

            password_input = driver.find_element(By.CSS_SELECTOR, "div.popup.login #Password_Value")
            print(f"[{time.time()-start_time:.1f}s] Ввожу пароль...", flush=True)
            password_input.clear()
            password_input.send_keys(password)

            print(f"[{time.time()-start_time:.1f}s] Нажимаю Войти...", flush=True)
            auth_btn = driver.find_element(By.CSS_SELECTOR, "div.popup.login #authBtn")
            driver.execute_script("arguments[0].click();", auth_btn)

            print(f"[{time.time()-start_time:.1f}s] Ожидаю завершения входа...", flush=True)
            time.sleep(3)

            driver.get('https://1.elecsnet.ru/NotebookFront/services/0mhp/default.aspx?merchantId=36924&fromSegment=')
            time.sleep(2)

            try:
                driver.find_element(By.CSS_SELECTOR, "a.login[href='main']")
                print(f"[{time.time()-start_time:.1f}s] ❌ Авторизация не удалась", flush=True)
                return {"status": "error", "message": "Авторизация не удалась"}
            except:
                print(f"[{time.time()-start_time:.1f}s] ✅ Авторизация успешна!", flush=True)

        except Exception as e:
            print(f"[{time.time()-start_time:.1f}s] ✅ Уже авторизован", flush=True)

        return {"status": "online", "message": "Вход выполнен успешно"}

    except Exception as e:
        print(f"❌ Ошибка: {e}", flush=True)
        return {"status": "error", "message": str(e)}

    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass


def create_payment_link(card_number, owner_name, amount, account_index=0):

    from database import db

    print(f"\n{'='*60}", flush=True)
    print(f"💳 СОЗДАНИЕ ПЛАТЕЖА", flush=True)
    print(f"{'='*60}", flush=True)

    accounts = db.get_accounts()
    if not accounts:
        return {"error": "Нет доступных аккаунтов"}

    account = accounts[0]
    profile_path = os.path.join(PROFILE_BASE_PATH, account['profile_path'])

    start_time = time.time()

    options = webdriver.ChromeOptions()
    options.add_argument(f'--user-data-dir={profile_path}')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-software-rasterizer')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.page_load_strategy = 'normal'

    driver = None

    try:
        print(f"[{time.time()-start_time:.1f}s] Запускаю браузер...", flush=True)
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(30)

        print(f"[{time.time()-start_time:.1f}s] Открываю страницу...", flush=True)
        driver.get('https://1.elecsnet.ru/NotebookFront/services/0mhp/default.aspx?merchantId=36924&fromSegment=')

        wait = WebDriverWait(driver, 15)

        try:
            login_btn = driver.find_element(By.CSS_SELECTOR, "a.login[href='main']")
            driver.execute_script("arguments[0].click();", login_btn)
            time.sleep(1)

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
            print(f"[{time.time()-start_time:.1f}s] ✅ Авторизован", flush=True)

        wait.until(EC.invisibility_of_element_located((By.ID, "loadercontainer")))

        card_input = wait.until(EC.element_to_be_clickable((By.NAME, "requisites.m-36924.f-1")))
        card_input.clear()
        card_input.send_keys(card_number)

        name_input = wait.until(EC.element_to_be_clickable((By.NAME, "requisites.m-36924.f-2")))
        name_input.clear()
        name_input.send_keys(owner_name)

        amount_input = wait.until(EC.element_to_be_clickable((By.NAME, "summ.transfer")))
        amount_input.clear()
        amount_input.send_keys(str(amount))

        print(f"[{time.time()-start_time:.1f}s] Ожидаю обработку суммы...", flush=True)
        time.sleep(0.5)
        
        for attempt in range(30):
            try:
                loader = driver.find_element(By.ID, "loadercontainer")
                style = loader.get_attribute("style")
                if "display: none" in style or not loader.is_displayed():
                    print(f"[{time.time()-start_time:.1f}s] Loader скрыт", flush=True)
                    break
            except:
                break
            time.sleep(0.2)

        print(f"[{time.time()-start_time:.1f}s] Ожидаю активацию кнопки...", flush=True)
        submit_btn = wait.until(EC.presence_of_element_located((By.NAME, "SubmitBtn")))
        for i in range(30):
            if not submit_btn.get_attribute("disabled"):
                print(f"[{time.time()-start_time:.1f}s] ✅ Кнопка активна!", flush=True)
                break
            time.sleep(0.3)

        print(f"[{time.time()-start_time:.1f}s] Нажимаю Оплатить...", flush=True)
        
        try:
            driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
            time.sleep(0.3)
        except:
            pass
        
        try:
            ActionChains(driver).move_to_element(submit_btn).click().perform()
            print(f"[{time.time()-start_time:.1f}s] Клик выполнен (ActionChains)", flush=True)
        except Exception as e1:
            print(f"[{time.time()-start_time:.1f}s] ActionChains не сработал: {e1}", flush=True)
            try:
                submit_btn.click()
                print(f"[{time.time()-start_time:.1f}s] Клик выполнен (обычный)", flush=True)
            except Exception as e2:
                print(f"[{time.time()-start_time:.1f}s] Обычный клик не сработал: {e2}", flush=True)
                driver.execute_script("arguments[0].click();", submit_btn)
                print(f"[{time.time()-start_time:.1f}s] Клик выполнен (JS)", flush=True)
        
        print(f"[{time.time()-start_time:.1f}s] Ожидаю обработку платежа...", flush=True)
        time.sleep(1.5)
        
        for attempt in range(40):
            try:
                loader = driver.find_element(By.ID, "loadercontainer")
                style = loader.get_attribute("style")
                if "display: none" in style or not loader.is_displayed():
                    print(f"[{time.time()-start_time:.1f}s] Платёж обработан", flush=True)
                    break
                if attempt % 10 == 0 and attempt > 0:
                    print(f"[{time.time()-start_time:.1f}s] Ожидаю... (попытка {attempt+1}/40)", flush=True)
            except:
                break
            time.sleep(0.3)

        print(f"[{time.time()-start_time:.1f}s] Ищу QR-код...", flush=True)
        
        qr_img = None
        for attempt in range(3):
            try:
                qr_img = wait.until(EC.presence_of_element_located((By.ID, "Image1")))
                print(f"[{time.time()-start_time:.1f}s] QR-код найден!", flush=True)
                break
            except Exception as e:
                print(f"[{time.time()-start_time:.1f}s] Попытка {attempt+1}/3: QR не найден - {e}", flush=True)
                if attempt < 2:
                    time.sleep(2)
        
        if not qr_img:
            raise Exception("QR-код не появился после нажатия кнопки")
        
        qr_code_base64 = qr_img.get_attribute("src")

        payment_link_element = wait.until(EC.presence_of_element_located((By.ID, "LinkMobil")))
        payment_link = payment_link_element.get_attribute("href")

        qr_code_data = qr_code_base64.split(",")[1] if "," in qr_code_base64 else qr_code_base64
        qr_filename = f"qr_{int(time.time())}.png"
        with open(qr_filename, "wb") as f:
            f.write(base64.b64decode(qr_code_data))

        elapsed = time.time() - start_time
        print(f"✅ ПЛАТЁЖ СОЗДАН за {elapsed:.1f} сек!", flush=True)

        return {
            "qr_file": qr_filename,
            "payment_link": payment_link,
            "elapsed_time": elapsed,
            "account_used": account['phone']
        }

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Ошибка: {e}", flush=True)
        
        try:
            screenshot_name = f"payment_error_{int(time.time())}.png"
            driver.save_screenshot(screenshot_name)
            print(f"📸 Скриншот: {screenshot_name}", flush=True)
        except:
            pass
        
        return {"error": str(e), "elapsed_time": elapsed}

    finally:
        if driver:
            try:
                print(f"[{time.time()-start_time:.1f}s] Закрываю браузер...", flush=True)
                driver.quit()
            except:
                pass

    print(f"\n{'='*60}", flush=True)
    print(f"💳 СОЗДАНИЕ ПЛАТЕЖА", flush=True)
    print(f"{'='*60}", flush=True)

    accounts = db.get_accounts()
    if not accounts:
        return {"error": "Нет доступных аккаунтов"}

    account = accounts[0]
    profile_path = os.path.join(PROFILE_BASE_PATH, account['profile_path'])

    start_time = time.time()

    options = webdriver.ChromeOptions()
    options.add_argument(f'--user-data-dir={profile_path}')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.page_load_strategy = 'eager'

    driver = None

    try:
        print(f"[{time.time()-start_time:.1f}s] Запускаю браузер...", flush=True)
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(20)

        print(f"[{time.time()-start_time:.1f}s] Открываю страницу...", flush=True)
        driver.get('https://1.elecsnet.ru/NotebookFront/services/0mhp/default.aspx?merchantId=36924&fromSegment=')

        wait = WebDriverWait(driver, 10)


        try:
            login_btn = driver.find_element(By.CSS_SELECTOR, "a.login[href='main']")
            driver.execute_script("arguments[0].click();", login_btn)
            time.sleep(1)

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
            print(f"[{time.time()-start_time:.1f}s] ✅ Авторизован", flush=True)

        wait.until(EC.invisibility_of_element_located((By.ID, "loadercontainer")))


        card_input = wait.until(EC.element_to_be_clickable((By.NAME, "requisites.m-36924.f-1")))
        card_input.clear()
        card_input.send_keys(card_number)

        name_input = wait.until(EC.element_to_be_clickable((By.NAME, "requisites.m-36924.f-2")))
        name_input.clear()
        name_input.send_keys(owner_name)

        amount_input = wait.until(EC.element_to_be_clickable((By.NAME, "summ.transfer")))
        amount_input.clear()
        amount_input.send_keys(str(amount))

        print(f"[{time.time()-start_time:.1f}s] Ожидаю обработку суммы...", flush=True)
        time.sleep(0.5)
        
        for attempt in range(30):
            try:
                loader = driver.find_element(By.ID, "loadercontainer")
                style = loader.get_attribute("style")
                if "display: none" in style or not loader.is_displayed():
                    print(f"[{time.time()-start_time:.1f}s] Loader скрыт", flush=True)
                    break
            except:
                break
            time.sleep(0.2)

        print(f"[{time.time()-start_time:.1f}s] Ожидаю активацию кнопки...", flush=True)
        submit_btn = wait.until(EC.presence_of_element_located((By.NAME, "SubmitBtn")))
        for i in range(30):
            if not submit_btn.get_attribute("disabled"):
                print(f"[{time.time()-start_time:.1f}s] ✅ Кнопка активна!", flush=True)
                break
            time.sleep(0.3)

        print(f"[{time.time()-start_time:.1f}s] Нажимаю Оплатить...", flush=True)
        driver.execute_script("arguments[0].click();", submit_btn)
        
        print(f"[{time.time()-start_time:.1f}s] Ожидаю обработку платежа...", flush=True)
        time.sleep(1)
        
        for attempt in range(50):
            try:
                loader = driver.find_element(By.ID, "loadercontainer")
                style = loader.get_attribute("style")
                if "display: none" in style or not loader.is_displayed():
                    print(f"[{time.time()-start_time:.1f}s] Платёж обработан", flush=True)
                    break
                if attempt % 10 == 0:
                    print(f"[{time.time()-start_time:.1f}s] Ожидаю... (попытка {attempt+1}/50)", flush=True)
            except:
                break
            time.sleep(0.2)

        print(f"[{time.time()-start_time:.1f}s] Ожидаю QR-код...", flush=True)
        wait_long = WebDriverWait(driver, 15)
        qr_img = wait_long.until(EC.presence_of_element_located((By.ID, "Image1")))
        qr_code_base64 = qr_img.get_attribute("src")

        payment_link_element = wait.until(EC.presence_of_element_located((By.ID, "LinkMobil")))
        payment_link = payment_link_element.get_attribute("href")

        qr_code_data = qr_code_base64.split(",")[1] if "," in qr_code_base64 else qr_code_base64
        qr_filename = f"qr_{int(time.time())}.png"
        with open(qr_filename, "wb") as f:
            f.write(base64.b64decode(qr_code_data))

        elapsed = time.time() - start_time
        print(f"✅ ПЛАТЁЖ СОЗДАН за {elapsed:.1f} сек!", flush=True)

        return {
            "qr_file": qr_filename,
            "payment_link": payment_link,
            "elapsed_time": elapsed,
            "account_used": account['phone']
        }

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Ошибка: {e}", flush=True)
        return {"error": str(e), "elapsed_time": elapsed}

    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
