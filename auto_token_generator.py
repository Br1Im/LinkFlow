#!/usr/bin/env python3
"""
Автоматический генератор токенов для multitransfer.ru
Решает checkbox капчу и получает fhptokenid
"""

import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

class AutoTokenGenerator:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None
        self.token = None
        
    def _setup_driver(self):
        """Настройка Chrome драйвера"""
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Включаем логи сети для перехвата токена
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Включаем логи Performance для перехвата запросов
        options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        self.driver = webdriver.Chrome(options=options)
        
    def _solve_checkbox_captcha(self):
        """Решение checkbox капчи (простой клик)"""
        try:
            print("🔍 Ищу checkbox капчу...")
            
            # Ждем появления капчи
            wait = WebDriverWait(self.driver, 10)
            
            # Различные селекторы для checkbox капчи
            checkbox_selectors = [
                "input[type='checkbox']",
                ".captcha-checkbox",
                "[data-testid='captcha-checkbox']",
                ".smart-captcha input",
                ".ya-captcha input",
                "iframe[src*='captcha']"
            ]
            
            checkbox = None
            for selector in checkbox_selectors:
                try:
                    checkbox = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    print(f"✅ Найден checkbox: {selector}")
                    break
                except:
                    continue
            
            if not checkbox:
                # Пробуем найти по iframe (Yandex SmartCaptcha)
                try:
                    iframe = self.driver.find_element(By.CSS_SELECTOR, "iframe[src*='captcha']")
                    self.driver.switch_to.frame(iframe)
                    checkbox = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='checkbox']")))
                    print("✅ Найден checkbox в iframe")
                except:
                    pass
            
            if checkbox:
                # Имитируем человеческий клик
                actions = ActionChains(self.driver)
                actions.move_to_element(checkbox)
                time.sleep(0.5)
                actions.click(checkbox)
                actions.perform()
                
                print("✅ Checkbox капча решена!")
                time.sleep(2)  # Ждем обработки
                
                # Возвращаемся из iframe если были в нем
                try:
                    self.driver.switch_to.default_content()
                except:
                    pass
                    
                return True
            else:
                print("❌ Checkbox капча не найдена")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка решения капчи: {e}")
            return False
    
    def _fill_form(self):
        """Заполнение формы для получения токена"""
        try:
            print("📝 Заполняю форму...")
            
            wait = WebDriverWait(self.driver, 10)
            
            # Сумма
            amount_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-testid='amount-input'], input[name='amount'], input[placeholder*='сумм']")))
            amount_input.clear()
            amount_input.send_keys("110")
            
            # Номер карты получателя
            card_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-testid='card-input'], input[name='card'], input[placeholder*='карт']")))
            card_input.clear()
            card_input.send_keys("9860080323894719")
            
            # Имя получателя
            name_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-testid='name-input'], input[name='name'], input[placeholder*='имя']")))
            name_input.clear()
            name_input.send_keys("Nodir Asadullayev")
            
            print("✅ Форма заполнена")
            time.sleep(1)
            return True
            
        except Exception as e:
            print(f"❌ Ошибка заполнения формы: {e}")
            return False
    
    def _extract_token_from_logs(self):
        """Извлечение токена из логов браузера"""
        try:
            print("🔍 Ищу токен в логах...")
            
            logs = self.driver.get_log('performance')
            
            for log in logs:
                message = json.loads(log['message'])
                
                if message['message']['method'] == 'Network.requestWillBeSent':
                    request = message['message']['params']['request']
                    
                    if 'api.multitransfer.ru' in request.get('url', ''):
                        headers = request.get('headers', {})
                        
                        # Ищем токен в заголовках
                        for header_name, header_value in headers.items():
                            if header_name.lower() in ['fhptokenid', 'fhp-token-id']:
                                self.token = header_value
                                print(f"✅ Токен найден: {self.token[:20]}...")
                                return True
            
            print("❌ Токен не найден в логах")
            return False
            
        except Exception as e:
            print(f"❌ Ошибка извлечения токена: {e}")
            return False
    
    def _trigger_api_request(self):
        """Триггер API запроса для получения токена"""
        try:
            print("🚀 Запускаю API запрос...")
            
            # Ищем кнопку отправки
            wait = WebDriverWait(self.driver, 10)
            
            submit_selectors = [
                "button[type='submit']",
                "button[data-testid='submit']",
                ".submit-button",
                "button:contains('Отправить')",
                "button:contains('Продолжить')"
            ]
            
            submit_button = None
            for selector in submit_selectors:
                try:
                    submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    break
                except:
                    continue
            
            if submit_button:
                submit_button.click()
                print("✅ Форма отправлена")
                time.sleep(3)  # Ждем API запрос
                return True
            else:
                print("❌ Кнопка отправки не найдена")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка отправки формы: {e}")
            return False
    
    def generate_token(self) -> str:
        """Основной метод генерации токена"""
        try:
            print("🚀 Запуск автоматической генерации токена...")
            
            self._setup_driver()
            
            # Открываем страницу
            print("🌐 Открываю multitransfer.ru...")
            self.driver.get("https://multitransfer.ru/transfer/uzbekistan")
            time.sleep(3)
            
            # Заполняем форму
            if not self._fill_form():
                return None
            
            # Решаем капчу
            if not self._solve_checkbox_captcha():
                print("⚠️ Капча не решена, пробую продолжить...")
            
            # Отправляем форму
            if not self._trigger_api_request():
                return None
            
            # Извлекаем токен
            if self._extract_token_from_logs():
                return self.token
            
            print("❌ Не удалось получить токен")
            return None
            
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            return None
            
        finally:
            if self.driver:
                self.driver.quit()
    
    def get_fresh_token(self) -> str:
        """Публичный метод для получения свежего токена"""
        return self.generate_token()

def main():
    """Тест генератора токенов"""
    generator = AutoTokenGenerator(headless=False)  # С GUI для отладки
    token = generator.get_fresh_token()
    
    if token:
        print(f"🎉 УСПЕХ! Токен получен: {token}")
        
        # Сохраняем токен
        with open('fresh_token.txt', 'w') as f:
            f.write(token)
        print("💾 Токен сохранен в fresh_token.txt")
    else:
        print("💥 Не удалось получить токен")

if __name__ == "__main__":
    main()