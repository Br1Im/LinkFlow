# -*- coding: utf-8 -*-
"""
Сервис создания платежей через multitransfer.ru
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService

logger = logging.getLogger(__name__)

MULTITRANSFER_URL = "https://multitransfer.ru/"


class MultiTransferManager:
    """Менеджер для работы с multitransfer.ru"""
    
    def __init__(self):
        self.driver = None
        self.is_ready = False
    
    def _create_driver(self):
        """Создание драйвера Chrome"""
        options = ChromeOptions()
        
        # Опции для локального тестирования
        # options.add_argument('--headless=new')  # Закомментировано для отладки
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        try:
            # Для Windows
            driver = webdriver.Chrome(options=options)
        except Exception as e:
            logger.error(f"❌ Не удалось создать Chrome драйвер: {e}")
            raise
        
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        return driver
    
    def initialize(self):
        """Инициализация браузера"""
        try:
            print(f"🔧 Инициализация MultiTransfer браузера...", flush=True)
            start = time.time()
            
            self.driver = self._create_driver()
            print(f"  📌 Драйвер создан, загружаю {MULTITRANSFER_URL}...", flush=True)
            
            self.driver.get(MULTITRANSFER_URL)
            print(f"  📌 Страница загружена за {time.time()-start:.1f}s", flush=True)
            
            self.is_ready = True
            print(f"✅ MultiTransfer браузер готов за {time.time()-start:.1f}s", flush=True)
            return True
            
        except Exception as e:
            print(f"❌ Ошибка инициализации: {e}", flush=True)
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
            self.is_ready = False
            return False
    
    def create_payment(self, amount, card_number, owner_name):
        """
        Создание платежа через multitransfer.ru
        
        Args:
            amount: Сумма платежа (в рублях)
            card_number: Номер карты получателя
            owner_name: Имя владельца карты
            
        Returns:
            dict: Результат с payment_link и qr_base64
        """
        start_time = time.time()
        
        if not self.is_ready or not self.driver:
            raise Exception("Браузер не инициализирован")
        
        try:
            print(f"🚀 Создание платежа через MultiTransfer...", flush=True)
            print(f"  Сумма: {amount} RUB", flush=True)
            print(f"  Карта: {card_number}", flush=True)
            print(f"  Владелец: {owner_name}", flush=True)
            
            wait = WebDriverWait(self.driver, 20)
            
            # Шаг 1: Выбрать страну "Узбекистан"
            print(f"  📌 Выбираю страну Узбекистан...", flush=True)
            try:
                # Клик на блок выбора страны (там где Азербайджан по умолчанию)
                country_block = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".variant-alternative.css-c8d8yl"))
                )
                country_block.click()
                time.sleep(1)
                
                # Ищем Узбекистан в выпадающем списке
                uzbekistan = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Узбекистан')]"))
                )
                uzbekistan.click()
                print(f"  ✅ Узбекистан выбран", flush=True)
                time.sleep(1)
            except Exception as e:
                print(f"  ⚠️ Не удалось выбрать страну (возможно уже выбран): {e}", flush=True)
            
            # Шаг 2: Ввести сумму отправления
            print(f"  📌 Ввожу сумму {amount} RUB...", flush=True)
            amount_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='0 RUB']"))
            )
            amount_input.click()
            amount_input.clear()
            amount_input.send_keys(str(amount))
            print(f"  ✅ Сумма введена, жду пересчета...", flush=True)
            time.sleep(3)  # Ждем пересчета
            
            # Шаг 3: Нажать кнопку "Продолжить" на главной странице
            print(f"  📌 Ищу кнопку Продолжить на главной странице...", flush=True)
            try:
                # Ждем пока кнопка станет активной (disabled снимется)
                pay_btn_found = False
                for i in range(30):
                    try:
                        pay_btn = self.driver.find_element(By.ID, "pay")
                        is_disabled = pay_btn.get_attribute("disabled")
                        btn_text = pay_btn.text
                        
                        if i % 5 == 0:  # Выводим статус каждые 2.5 секунды
                            print(f"  📌 Кнопка '{btn_text}': disabled={is_disabled}", flush=True)
                        
                        if not is_disabled:
                            print(f"  📌 Кнопка Продолжить активна! Нажимаю...", flush=True)
                            # Сохраняем скриншот перед кликом
                            try:
                                self.driver.save_screenshot("before_continue_click.png")
                            except:
                                pass
                            
                            self.driver.execute_script("arguments[0].click();", pay_btn)
                            time.sleep(5)
                            print(f"  ✅ Кнопка Продолжить нажата", flush=True)
                            print(f"  📌 Новый URL: {self.driver.current_url}", flush=True)
                            pay_btn_found = True
                            break
                    except Exception as e:
                        if i == 0:
                            print(f"  ⚠️ Кнопка #pay не найдена: {e}", flush=True)
                    time.sleep(0.5)
                
                if not pay_btn_found:
                    print(f"  ⚠️ Кнопка Продолжить так и не активировалась", flush=True)
                    # Сохраняем скриншот
                    try:
                        self.driver.save_screenshot("button_not_active.png")
                        print(f"  📌 Скриншот: button_not_active.png", flush=True)
                    except:
                        pass
                    
            except Exception as e:
                print(f"  ⚠️ Ошибка с кнопкой Продолжить: {e}", flush=True)
            
            # Шаг 4: Теперь должна открыться страница со списком банков
            print(f"  📌 Ищу список банков на новой странице...", flush=True)
            time.sleep(2)
            
            try:
                # Ищем все карточки банков
                bank_cards = self.driver.find_elements(By.CSS_SELECTOR, ".home.css-1lvwieb, div[role='button'][aria-label*='банк']")
                print(f"  📌 Найдено {len(bank_cards)} банков", flush=True)
                
                if len(bank_cards) > 0:
                    # Ищем Uzcard/Humo - последний в списке
                    humo_card = None
                    for card in bank_cards:
                        try:
                            aria_label = card.get_attribute("aria-label") or ""
                            card_text = card.text
                            if "Uzcard" in aria_label or "Humo" in aria_label or "Uzcard" in card_text or "Humo" in card_text:
                                humo_card = card
                                print(f"  📌 Найден банк Uzcard/Humo", flush=True)
                                break
                        except:
                            continue
                    
                    if not humo_card:
                        # Если не нашли по имени, берем последний
                        humo_card = bank_cards[-1]
                        print(f"  📌 Выбираю последний банк в списке", flush=True)
                    
                    # Прокручиваем к карточке и кликаем
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", humo_card)
                    time.sleep(0.5)
                    humo_card.click()
                    time.sleep(3)
                    print(f"  ✅ Банк Uzcard/Humo выбран", flush=True)
                    print(f"  📌 URL после выбора банка: {self.driver.current_url}", flush=True)
                else:
                    print(f"  ⚠️ Банки не найдены на странице", flush=True)
                    
            except Exception as e:
                print(f"  ❌ Ошибка выбора банка: {e}", flush=True)
                raise
            
            # Шаг 5: Заполнить данные карты на следующей странице
            print(f"  📌 Жду загрузки формы...", flush=True)
            time.sleep(3)
            
            # Сохраняем скриншот для отладки
            try:
                self.driver.save_screenshot("after_bank_selection.png")
                print(f"  📌 Скриншот сохранен: after_bank_selection.png", flush=True)
                print(f"  📌 Текущий URL: {self.driver.current_url}", flush=True)
            except:
                pass
            
            print(f"  📌 Ищу поля для ввода данных...", flush=True)
            
            # Ищем все input поля на странице
            all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
            print(f"  📌 Найдено {len(all_inputs)} input полей", flush=True)
            for i, inp in enumerate(all_inputs[:10]):
                try:
                    placeholder = inp.get_attribute("placeholder") or ""
                    name = inp.get_attribute("name") or ""
                    inp_type = inp.get_attribute("type") or ""
                    inputmode = inp.get_attribute("inputmode") or ""
                    print(f"    Input {i+1}: type={inp_type}, inputmode={inputmode}, name={name}, placeholder={placeholder}", flush=True)
                except:
                    pass
            
            # Ищем поле номера карты - обычно это поле с inputmode="numeric" или placeholder содержит "карт"
            card_input = None
            for inp in all_inputs:
                try:
                    placeholder = (inp.get_attribute("placeholder") or "").lower()
                    inputmode = inp.get_attribute("inputmode") or ""
                    inp_type = inp.get_attribute("type") or ""
                    
                    if inputmode == "numeric" or "карт" in placeholder or "card" in placeholder or inp_type == "tel":
                        card_input = inp
                        print(f"  📌 Поле карты найдено: placeholder={placeholder}, inputmode={inputmode}", flush=True)
                        break
                except:
                    continue
            
            if card_input:
                card_input.clear()
                card_input.send_keys(card_number)
                print(f"  ✅ Номер карты введен", flush=True)
                time.sleep(1)
            else:
                print(f"  ⚠️ Поле карты не найдено", flush=True)
            
            # Ищем поле имени владельца - обычно это текстовое поле после поля карты
            name_input = None
            for inp in all_inputs:
                try:
                    placeholder = (inp.get_attribute("placeholder") or "").lower()
                    inp_type = inp.get_attribute("type") or ""
                    
                    if inp != card_input and (inp_type == "text" and ("имя" in placeholder or "владелец" in placeholder or "name" in placeholder or "фио" in placeholder)):
                        name_input = inp
                        print(f"  📌 Поле имени найдено: placeholder={placeholder}", flush=True)
                        break
                except:
                    continue
            
            # Если не нашли по placeholder, берем второе текстовое поле
            if not name_input:
                text_inputs = [inp for inp in all_inputs if inp.get_attribute("type") == "text" and inp != card_input]
                if len(text_inputs) > 0:
                    name_input = text_inputs[0]
                    print(f"  📌 Поле имени найдено (второе текстовое поле)", flush=True)
            
            if name_input:
                name_input.clear()
                name_input.send_keys(owner_name)
                print(f"  ✅ Имя владельца введено", flush=True)
                time.sleep(1)
            else:
                print(f"  ⚠️ Поле имени не найдено", flush=True)
            
            # Шаг 6: Найти и нажать кнопку отправки
            print(f"  📌 Ищу кнопку отправки формы...", flush=True)
            time.sleep(2)
            
            # Ищем все кнопки на странице
            all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
            print(f"  📌 Найдено {len(all_buttons)} кнопок", flush=True)
            
            submit_btn = None
            for btn in all_buttons:
                try:
                    btn_text = btn.text.lower()
                    btn_type = btn.get_attribute("type") or ""
                    if "создать" in btn_text or "оплатить" in btn_text or "продолжить" in btn_text or btn_type == "submit":
                        print(f"  📌 Найдена кнопка: {btn.text} (type={btn_type})", flush=True)
                        submit_btn = btn
                        break
                except:
                    continue
            
            if submit_btn:
                self.driver.execute_script("arguments[0].click();", submit_btn)
                print(f"  ✅ Кнопка отправки нажата", flush=True)
                time.sleep(3)
            else:
                print(f"  ⚠️ Кнопка отправки не найдена", flush=True)
            
            # Шаг 6: Получить ссылку и QR код
            print(f"  📌 Получаю ссылку и QR код...", flush=True)
            time.sleep(2)
            
            # Ищем QR код
            qr_img = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "img[alt*='QR'], img[src*='qr'], canvas"))
            )
            qr_base64 = qr_img.get_attribute("src")
            
            # Ищем ссылку на оплату
            payment_link = None
            try:
                link_element = self.driver.find_element(By.CSS_SELECTOR, "a[href*='pay'], a[href*='payment']")
                payment_link = link_element.get_attribute("href")
            except:
                # Если ссылка не найдена, пробуем получить из текущего URL
                payment_link = self.driver.current_url
            
            elapsed = time.time() - start_time
            print(f"✅ Платеж создан за {elapsed:.1f}s", flush=True)
            print(f"  Ссылка: {payment_link}", flush=True)
            
            return {
                "payment_link": payment_link,
                "qr_base64": qr_base64,
                "elapsed_time": elapsed,
                "success": True
            }
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ Ошибка создания платежа: {e}", flush=True)
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
                print("✅ MultiTransfer браузер закрыт", flush=True)
            except:
                pass
            self.driver = None
        self.is_ready = False


# Глобальный экземпляр
multitransfer_manager = MultiTransferManager()
