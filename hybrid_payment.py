# -*- coding: utf-8 -*-
"""
Гибридное решение: Selenium для авторизации + API для скорости
Скорость создания платежа: ~1 секунда!
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import json
import time
import os
import base64
from typing import Dict, Optional

class HybridPaymentManager:
    """Гибридный менеджер: Selenium + API"""
    
    BASE_URL = "https://1.elecsnet.ru/NotebookFront"
    ELECSNET_URL = f"{BASE_URL}/services/0mhp/default.aspx?merchantId=36924&fromSegment="
    
    def __init__(self):
        self.driver = None
        self.session = requests.Session()
        self.is_authorized = False
        self.card_number = None
        self.owner_name = None
        
    def _cleanup_profile(self, profile_path):
        """Очистка проблемных файлов профиля"""
        try:
            lock_files = [
                'SingletonLock', 'SingletonSocket', 'SingletonCookie',
                'lockfile', 'DevToolsActivePort'
            ]
            
            for lock_file in lock_files:
                lock_path = os.path.join(profile_path, lock_file)
                if os.path.exists(lock_path):
                    try:
                        os.remove(lock_path)
                    except:
                        pass
            
            default_path = os.path.join(profile_path, 'Default')
            if os.path.exists(default_path):
                for lock_file in lock_files:
                    lock_path = os.path.join(default_path, lock_file)
                    if os.path.exists(lock_path):
                        try:
                            os.remove(lock_path)
                        except:
                            pass
        except:
            pass
    
    def _create_driver(self, profile_path):
        """Создание драйвера Chrome"""
        self._cleanup_profile(profile_path)
        
        options = webdriver.ChromeOptions()
        options.add_argument(f'--user-data-dir={profile_path}')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-features=LockProfileCookieDatabase')
        options.add_argument('--disable-site-isolation-trials')
        options.add_argument('--disable-background-networking')
        options.add_argument('--disable-sync')
        options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        options.page_load_strategy = 'eager'
        
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(20)
        return driver
    
    def authorize_and_get_cookies(self, account: Dict) -> bool:
        """Авторизация через Selenium и получение cookies"""
        print(f"🔐 Авторизация через Selenium...", flush=True)
        
        try:
            profile_path = os.path.abspath(os.path.join("profiles", account['profile_path']))
            self.driver = self._create_driver(profile_path)
            
            self.driver.get(self.ELECSNET_URL)
            time.sleep(2)
            
            # Проверка авторизации
            try:
                login_btn = self.driver.find_element(By.CSS_SELECTOR, "a.login[href='main']")
                print("   Выполняю вход...", flush=True)
                
                self.driver.execute_script("arguments[0].click();", login_btn)
                time.sleep(1)
                
                wait = WebDriverWait(self.driver, 10)
                wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.popup.login")))
                
                phone_input = self.driver.find_element(By.CSS_SELECTOR, "div.popup.login #Login_Value")
                phone_clean = account['phone'].replace("+7", "").replace(" ", "").replace("-", "")
                phone_input.send_keys(phone_clean)
                
                password_input = self.driver.find_element(By.CSS_SELECTOR, "div.popup.login #Password_Value")
                password_input.send_keys(account['password'])
                
                auth_btn = self.driver.find_element(By.CSS_SELECTOR, "div.popup.login #authBtn")
                self.driver.execute_script("arguments[0].click();", auth_btn)
                time.sleep(3)
                
                self.driver.get(self.ELECSNET_URL)
                time.sleep(1)
            except:
                print("   Уже авторизован", flush=True)
            
            # Получаем cookies из Selenium
            selenium_cookies = self.driver.get_cookies()
            
            # Переносим cookies в requests.Session
            for cookie in selenium_cookies:
                self.session.cookies.set(
                    cookie['name'],
                    cookie['value'],
                    domain=cookie.get('domain'),
                    path=cookie.get('path')
                )
            
            print(f"   ✅ Cookies получены: {len(selenium_cookies)} шт.", flush=True)
            
            self.is_authorized = True
            
            # Закрываем браузер - он больше не нужен!
            self.driver.quit()
            self.driver = None
            
            return True
            
        except Exception as e:
            print(f"   ❌ Ошибка авторизации: {e}", flush=True)
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
            return False
    
    def _api_request(self, endpoint: str, data: Dict) -> Dict:
        """Универсальный API запрос"""
        url = f"{self.BASE_URL}/services/0mhp/{endpoint}"
        
        headers = {
            "accept": "*/*",
            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "sec-ch-ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-requested-with": "XMLHttpRequest",
            "referer": self.ELECSNET_URL,
            "origin": "https://1.elecsnet.ru"
        }
        
        try:
            response = self.session.post(url, headers=headers, data=data, timeout=10)
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_payment_fast(self, card_number: str, owner_name: str, amount: float) -> Dict:
        """Быстрое создание платежа через API"""
        
        if not self.is_authorized:
            return {"success": False, "error": "Не авторизован"}
        
        start_time = time.time()
        
        # Шаг 1: formatReqId
        amount_formatted = f"{int(amount):,}".replace(",", " ")
        
        format_data = {
            "merchantId": "36924",
            "paymentTool": "205",
            "merchantFields[1]": card_number,
            "merchantFields[2]": owner_name,
            "merchantFields[3]": "Непокрытый Дмитрий Евгеньевич",
            "merchantFields[4]": "03.07.2000",
            "merchantFields[5]": "RU",
            "merchantFields[6]": "1820657875",
            "amount": amount_formatted,
            "bill": "",
            "comment": "",
            "clientId": ""
        }
        
        format_result = self._api_request("formatReqId", format_data)
        
        if not format_result.get("success"):
            return {
                "success": False,
                "error": f"formatReqId: {format_result.get('error')}",
                "elapsed_time": time.time() - start_time
            }
        
        data = format_result["data"]
        reqid = data.get("reqid")
        sign = data.get("sign")
        sign_time = data.get("signTime")
        user_id = data.get("userId", 0)
        ans_id = data.get("ansId", "")
        
        if not reqid or not sign:
            return {
                "success": False,
                "error": "reqid или sign не найдены",
                "elapsed_time": time.time() - start_time
            }
        
        # Шаг 2: logredirect
        amount_formatted_decimal = f"{amount:,.2f}".replace(",", " ")
        
        params_json = {
            "ansId": ans_id,
            "walletId": reqid,
            "amount": amount_formatted_decimal,
            "totalSum": amount_formatted_decimal,
            "comission": "0,00",
            "payment_id": 205,
            "merchant_id": 36924,
            "form_name": "сайт Элекснет;Каталог (05.2015)",
            "merchant_code": "SRX",
            "back_url": f"{self.BASE_URL}/services/0mhp/result",
            "sign": sign,
            "sign_time": sign_time,
            "sender_user_id": user_id,
            "comment": None
        }
        
        redirect_data = {
            "url": "/SBP/default.aspx",
            "paramsJson": json.dumps(params_json, ensure_ascii=False)
        }
        
        redirect_result = self._api_request("logredirect", redirect_data)
        
        if not redirect_result.get("success"):
            return {
                "success": False,
                "error": f"logredirect: {redirect_result.get('error')}",
                "elapsed_time": time.time() - start_time
            }
        
        redirect_response = redirect_result["data"]
        
        # Шаг 3: Получаем QR и ссылку через авторизованную сессию
        sbp_url = f"{self.BASE_URL}/SBP/default.aspx"
        
        try:
            headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "accept-language": "ru-RU,ru;q=0.9",
                "referer": self.ELECSNET_URL,
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = self.session.get(
                sbp_url,
                params=redirect_response.get("params", {}),
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                html = response.text
                
                import re
                qr_match = re.search(r'<img[^>]+id="Image1"[^>]+src="([^"]+)"', html)
                link_match = re.search(r'<a[^>]+id="LinkMobil"[^>]+href="([^"]+)"', html)
                
                if qr_match and link_match:
                    elapsed = time.time() - start_time
                    
                    return {
                        "success": True,
                        "payment_link": link_match.group(1),
                        "qr_base64": qr_match.group(1),
                        "elapsed_time": elapsed
                    }
                else:
                    return {
                        "success": False,
                        "error": "QR или ссылка не найдены в HTML",
                        "elapsed_time": time.time() - start_time
                    }
            else:
                return {
                    "success": False,
                    "error": f"SBP HTTP {response.status_code}",
                    "elapsed_time": time.time() - start_time
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"SBP request: {str(e)}",
                "elapsed_time": time.time() - start_time
            }
    
    def close(self):
        """Закрытие ресурсов"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
        self.session.close()


# Глобальный экземпляр
hybrid_manager = HybridPaymentManager()


def test_hybrid():
    """Тест гибридного решения"""
    print("\n" + "="*60)
    print("🚀 ТЕСТ ГИБРИДНОГО РЕШЕНИЯ")
    print("="*60)
    
    account = {
        "phone": "+79880260334",
        "password": "xowxut-wemhej-3zAsno",
        "profile_path": "profile_79880260334"
    }
    
    # Авторизация (1 раз)
    print("\n1️⃣ АВТОРИЗАЦИЯ")
    if not hybrid_manager.authorize_and_get_cookies(account):
        print("❌ Авторизация не удалась")
        return
    
    print("\n✅ Авторизация успешна! Браузер закрыт.")
    
    # Создание платежей (быстро!)
    for i in range(3):
        print(f"\n2️⃣ ПЛАТЕЖ #{i+1}")
        print("="*60)
        
        result = hybrid_manager.create_payment_fast(
            card_number="9860100125857258",
            owner_name="IZZET SAMEKEEV",
            amount=2000 + i * 100
        )
        
        if result.get("success"):
            print(f"✅ Успех за {result['elapsed_time']:.2f} сек!")
            print(f"🔗 {result['payment_link']}")
        else:
            print(f"❌ Ошибка: {result.get('error')}")
        
        time.sleep(1)
    
    hybrid_manager.close()


if __name__ == "__main__":
    test_hybrid()
