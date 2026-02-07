#!/usr/bin/env python3
"""
Сервис для создания платежных ссылок с постоянным браузером
Браузер открывается один раз и остается активным между запросами
PRODUCTION VERSION - headless mode, detailed logging
Данные отправителей берутся из БД

МОДУЛЬНАЯ ВЕРСИЯ: Использует отдельные файлы для каждого этапа
"""

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import asyncio
import time
import sys
import os
from datetime import datetime
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'playwright_version'))

# Импортируем функцию для получения данных из БД
admin_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, admin_path)
try:
    import database as db
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    print("⚠️ База данных недоступна, используется fallback режим")

# Импортируем модульные этапы
from steps import process_step1, process_step2


# Глобальное хранилище логов для текущего платежа
current_payment_logs = []
# Файл для обмена логами между процессами
LOGS_FILE = os.path.join(os.path.dirname(__file__), '..', 'current_payment_logs.json')


def log(message: str, level: str = "INFO"):
    """Логирование с временной меткой и сохранением в файл"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    prefix = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "ERROR": "❌",
        "WARNING": "⚠️",
        "DEBUG": "🔍"
    }.get(level, "📝")
    print(f"[{timestamp}] {prefix} {message}")
    
    # Сохраняем лог в глобальный список
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'level': level.lower(),
        'message': message
    }
    current_payment_logs.append(log_entry)
    
    # Сохраняем в файл для обмена с админ-панелью
    try:
        with open(LOGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(current_payment_logs, f, ensure_ascii=False)
    except:
        pass


def get_sender_data_from_db():
    """Получает случайные данные отправителя из БД"""
    if not DB_AVAILABLE:
        # Fallback: используем тестовые данные
        return {
            "passport_series": "9217",
            "passport_number": "224758",
            "passport_issue_date": "14.07.2017",
            "birth_country": "Россия",
            "birth_place": "ГОР. НАБЕРЕЖНЫЕЧЕЛНЫРЕСПУБЛИКИТАТАРСТАН",
            "first_name": "МАРИЯ",
            "last_name": "ЗАМОРЕНАЯ",
            "middle_name": "ФИДЕЛЕВНА",
            "birth_date": "10.08.1992",
            "phone": "+7 904 673-17-33",
            "registration_country": "Россия",
            "registration_place": "423831, РОССИЯ, Татарстан Респ, Набережные Челныг, Сююмбикепр-кт, 27, 154"
        }
    
    sender_data = db.get_random_sender_data()
    
    if not sender_data:
        raise Exception("Нет активных данных отправителей в БД. Импортируйте данные через import_excel_to_db.py")
    
    # Заменяем Ё на Е во всех текстовых полях
    for key, value in sender_data.items():
        if isinstance(value, str):
            sender_data[key] = value.replace('Ё', 'Е').replace('ё', 'е')
    
    return sender_data


class PaymentService:
    """Сервис для создания платежных ссылок"""
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.is_ready = False
        
    async def start(self, headless: bool = True, compact_window: bool = False):
        """Запускает браузер и подготавливает страницу
        
        Args:
            headless: Запуск в headless режиме (без видимого окна)
            compact_window: Маленькое окно для мониторинга (800x900)
        """
        log(f"Запуск браузера (headless={headless}, compact={compact_window})...", "INFO")
        
        # Удаляем старые скриншоты
        try:
            import glob
            screenshots_dir = "screenshots"
            if os.path.exists(screenshots_dir):
                old_files = glob.glob(os.path.join(screenshots_dir, "*"))
                # НЕ удаляем старые файлы - оставляем для отладки
                # for f in old_files:
                #     try:
                #         os.remove(f)
                #         log(f"Удален старый файл: {f}", "DEBUG")
                #     except:
                #         pass
        except Exception as e:
            log(f"Не удалось очистить старые скриншоты: {e}", "WARNING")
        
        self.playwright = await async_playwright().start()
        
        # Настройки размера окна
        if compact_window and not headless:
            # Маленькое окно для мониторинга
            viewport_size = {'width': 800, 'height': 900}
            window_size = '--window-size=800,900'
            window_position = '--window-position=50,50'  # Позиция в левом верхнем углу
        else:
            # Обычный размер
            viewport_size = {'width': 1920, 'height': 1080}
            window_size = '--window-size=1920,1080'
            window_position = '--window-position=0,0'
        
        launch_args = [
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process',
            '--disable-site-isolation-trials',
            window_size,
            window_position
        ]
        
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            args=launch_args,
            chromium_sandbox=False
        )
        
        # Более реалистичный User-Agent
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        
        self.context = await self.browser.new_context(
            viewport=viewport_size,
            user_agent=user_agent,
            locale='ru-RU',
            timezone_id='Europe/Moscow',
            permissions=['geolocation'],
            geolocation={'latitude': 55.7558, 'longitude': 37.6173},  # Москва
            color_scheme='dark',
            extra_http_headers={
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0'
            }
        )
        
        # Скрываем признаки автоматизации
        await self.context.add_init_script("""
            // Переопределяем webdriver
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Добавляем chrome объект
            window.chrome = {
                runtime: {},
            };
            
            // Переопределяем permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // Добавляем плагины
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            // Добавляем языки
            Object.defineProperty(navigator, 'languages', {
                get: () => ['ru-RU', 'ru', 'en-US', 'en'],
            });
        """)
        
        self.page = await self.context.new_page()
        
        # Автозакрыватель модалок
        await self.page.evaluate("""
            () => {
                const closeErrorModal = () => {
                    const buttons = document.querySelectorAll('button[buttontext="Понятно"]');
                    buttons.forEach(btn => {
                        if (btn.textContent.includes('Понятно')) {
                            btn.click();
                        }
                    });
                };
                setInterval(closeErrorModal, 50);
                const observer = new MutationObserver(() => closeErrorModal());
                observer.observe(document.body, { childList: true, subtree: true });
            }
        """)
        
        # Предзагружаем страницу
        log("Предзагрузка страницы...", "INFO")
        await self.page.goto("https://multitransfer.ru/transfer/uzbekistan", wait_until='load', timeout=90000)
        await self.page.wait_for_selector('input[placeholder="0 RUB"]', state='visible', timeout=30000)
        
        self.is_ready = True
        log("Сервис готов к работе!", "SUCCESS")
        
    async def stop(self):
        """Останавливает браузер"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        self.is_ready = False
        print("🛑 Сервис остановлен")
        
    async def create_payment_link(self, amount: int, card_number: str, owner_name: str, custom_sender: dict = None) -> dict:
        """
        Создает платежную ссылку
        
        Args:
            amount: Сумма платежа
            card_number: Номер карты получателя
            owner_name: Имя владельца карты
            custom_sender: Кастомные данные отправителя (опционально)
        
        Returns:
            dict: {
                'success': bool,
                'qr_link': str or None,
                'time': float,
                'step1_time': float,
                'step2_time': float,
                'error': str or None,
                'logs': list
            }
        """
        global current_payment_logs
        
        if not self.is_ready:
            return {'success': False, 'error': 'Сервис не запущен', 'time': 0, 'logs': []}
        
        # Очищаем логи перед началом нового платежа
        current_payment_logs.clear()
        log(f"Начало создания платежа: {amount}₽, карта {card_number}, владелец {owner_name}", "INFO")
        
        # Получаем данные отправителя: кастомные или из БД
        if custom_sender:
            # Используем кастомные данные
            SENDER_DATA = {
                "first_name": custom_sender.get('first_name', ''),
                "last_name": custom_sender.get('last_name', ''),
                "middle_name": custom_sender.get('middle_name', ''),
                "birth_date": custom_sender.get('birth_date', ''),
                "phone": custom_sender.get('phone', ''),
                # Остальные поля берем из БД (если не указаны)
                "passport_series": custom_sender.get('passport_series', '9217'),
                "passport_number": custom_sender.get('passport_number', '224758'),
                "passport_issue_date": custom_sender.get('passport_issue_date', '14.07.2017'),
                "birth_country": custom_sender.get('birth_country', 'Россия'),
                "birth_place": custom_sender.get('birth_place', 'ГОР. НАБЕРЕЖНЫЕЧЕЛНЫРЕСПУБЛИКИТАТАРСТАН'),
                "registration_country": custom_sender.get('registration_country', 'Россия'),
                "registration_place": custom_sender.get('registration_place', '423831, РОССИЯ, Татарстан Респ, Набережные Челныг, Сююмбикепр-кт, 27, 154')
            }
            log(f"Используются КАСТОМНЫЕ данные: {SENDER_DATA['last_name']} {SENDER_DATA['first_name']} {SENDER_DATA['middle_name']}", "INFO")
        else:
            # Получаем случайные данные отправителя из БД
            SENDER_DATA = get_sender_data_from_db()
            log(f"Используются данные из БД: {SENDER_DATA['last_name']} {SENDER_DATA['first_name']} {SENDER_DATA['middle_name']}", "INFO")
        
        start_time = time.time()
        qr_link = None
        
        # Обработчик для перехвата QR ссылки
        async def handle_response(response):
            nonlocal qr_link
            if '/anonymous/confirm' in response.url:
                try:
                    data = await response.json()
                    if 'externalData' in data and 'payload' in data['externalData']:
                        qr_link = data['externalData']['payload']
                except:
                    pass
        
        self.page.on('response', handle_response)
        
        try:
            # Полная перезагрузка страницы с очисткой состояния
            log("Перезагружаю страницу...", "DEBUG")
            await self.page.goto("https://multitransfer.ru/transfer/uzbekistan", wait_until='load', timeout=60000)
            # Ждем появления поля суммы вместо фиксированной задержки
            await self.page.wait_for_selector('input[placeholder="0 RUB"]', state='visible', timeout=10000)
            
            # ЭТАП 1: Ввод суммы
            log("=" * 50, "INFO")
            log("ЭТАП 1: ВВОД СУММЫ", "INFO")
            log("=" * 50, "INFO")
            
            amount_input = self.page.locator('input[placeholder="0 RUB"]')
            await amount_input.wait_for(state='visible', timeout=5000)
            
            # ВАЖНО: Очищаем старую сумму перед вводом новой
            log("Очищаю старую сумму...", "DEBUG")
            await amount_input.click()
            await amount_input.evaluate("el => el.value = ''")
            
            # Очищаем через Ctrl+A + Delete
            await amount_input.click()
            await self.page.keyboard.press('Control+A')
            await self.page.keyboard.press('Delete')
            
            log(f"Ввожу новую сумму: {amount} RUB", "DEBUG")
            
            commission_ok = False
            for attempt in range(10):
                if attempt > 0:
                    log(f"Попытка #{attempt + 1} ввода суммы", "WARNING")
                
                # Закрываем модалку если есть
                try:
                    modal_closed = await self.page.evaluate("""
                        () => {
                            const buttons = document.querySelectorAll('button[buttontext="Понятно"]');
                            let closed = false;
                            buttons.forEach(btn => {
                                if (btn.textContent.includes('Понятно')) {
                                    btn.click();
                                    closed = true;
                                }
                            });
                            return closed;
                        }
                    """)
                    if modal_closed:
                        log("Модалка закрыта, повторяю ввод", "WARNING")
                        await self.page.wait_for_timeout(500)
                        # Очищаем поле снова после закрытия модалки
                        await amount_input.click()
                        await amount_input.evaluate("el => el.value = ''")
                        await self.page.wait_for_timeout(100)
                except:
                    pass
                
                # Вводим сумму
                await amount_input.evaluate(f"""
                    (element) => {{
                        element.focus();
                        element.click();
                        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                            window.HTMLInputElement.prototype, 
                            'value'
                        ).set;
                        nativeInputValueSetter.call(element, '{amount}');
                        element.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        element.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        element.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', bubbles: true }}));
                        element.dispatchEvent(new KeyboardEvent('keyup', {{ key: 'Enter', bubbles: true }}));
                    }}
                """)
                
                # Проверяем комиссию - ждем пока значение изменится
                try:
                    await self.page.wait_for_function("""
                        () => {
                            const input = document.querySelector('input[placeholder*="UZS"]');
                            return input && input.value && input.value !== '0 UZS' && input.value !== '';
                        }
                    """, timeout=1000)
                    log("Комиссия рассчитана успешно", "SUCCESS")
                    commission_ok = True
                    break
                except:
                    pass
            
            if not commission_ok:
                log("Не удалось рассчитать комиссию за 10 попыток", "ERROR")
                # Делаем скриншот при ошибке
                screenshot_path = f"screenshots/error_commission_{int(time.time())}.png"
                try:
                    await self.page.screenshot(path=screenshot_path)
                    log(f"Скриншот сохранен: {screenshot_path}", "INFO")
                except:
                    pass
                return {'success': False, 'error': 'Не удалось рассчитать комиссию', 'time': time.time() - start_time, 'logs': current_payment_logs.copy()}
            
            # Выбор способа платежа и Uzcard с улучшенной логикой
            log("Выбираю способ перевода и Uzcard...", "DEBUG")
            
            # Клик по "Способ перевода"
            transfer_selectors = [
                'div.css-c8d8yl:has-text("Способ перевода")',
                'div:has-text("Способ перевода")',
            ]
            
            for selector in transfer_selectors:
                try:
                    transfer_block = self.page.locator(selector).first
                    if await transfer_block.is_visible(timeout=200):
                        await transfer_block.click()
                        log("Способ перевода выбран", "DEBUG")
                        break
                except:
                    continue
            
            await self.page.wait_for_timeout(200)
            
            # Выбор Uzcard с retry
            uzcard_selected = False
            for uzcard_attempt in range(5):
                try:
                    bank_selectors = [
                        'text=Uzcard',
                        '[role="button"]:has-text("Uzcard")',
                    ]
                    
                    for selector in bank_selectors:
                        try:
                            bank_option = self.page.locator(selector).first
                            if await bank_option.is_visible(timeout=500):
                                await bank_option.click()
                                log(f"Uzcard выбран (попытка #{uzcard_attempt + 1})", "DEBUG")
                                uzcard_selected = True
                                break
                        except:
                            continue
                    
                    if uzcard_selected:
                        break
                    
                    # Если не нашли, пробуем через JS
                    if uzcard_attempt > 1:
                        await self.page.evaluate("""
                            () => {
                                const uzcardBtn = Array.from(document.querySelectorAll('[role="button"]')).find(
                                    el => el.textContent.includes('Uzcard')
                                );
                                if (uzcardBtn) {
                                    uzcardBtn.click();
                                    return true;
                                }
                                return false;
                            }
                        """)
                        uzcard_selected = True
                        log(f"Uzcard выбран через JS (попытка #{uzcard_attempt + 1})", "DEBUG")
                        break
                    
                    await self.page.wait_for_timeout(200)
                    
                except Exception as e:
                    log(f"Попытка #{uzcard_attempt + 1} выбора Uzcard не удалась: {e}", "WARNING")
                    await self.page.wait_for_timeout(200)
            
            if not uzcard_selected:
                log("Не удалось выбрать Uzcard", "ERROR")
                # Делаем скриншот при ошибке
                screenshot_path = f"screenshots/error_uzcard_{int(time.time())}.png"
                try:
                    await self.page.screenshot(path=screenshot_path)
                    log(f"Скриншот сохранен: {screenshot_path}", "INFO")
                except:
                    pass
                return {'success': False, 'error': 'Не удалось выбрать Uzcard', 'time': time.time() - start_time, 'logs': current_payment_logs.copy()}
            
            await self.page.wait_for_timeout(200)
            
            # Ждем активации кнопки "Продолжить" с retry
            log("Жду активации кнопки Продолжить...", "DEBUG")
            button_active = False
            for btn_attempt in range(25):  # Увеличено с 15 до 25 попыток
                try:
                    is_active = await self.page.evaluate("""
                        () => {
                            const btn = document.getElementById('pay');
                            return btn && !btn.disabled;
                        }
                    """)
                    
                    if is_active:
                        log(f"Кнопка активна (попытка #{btn_attempt + 1})", "SUCCESS")
                        button_active = True
                        break
                    
                    # Если кнопка не активна после 3 попыток, вводим сумму заново
                    if btn_attempt == 3:
                        log("Кнопка не активна, ввожу сумму заново...", "WARNING")
                        await amount_input.click()
                        await self.page.wait_for_timeout(100)
                        await amount_input.evaluate("el => el.value = ''")
                        await self.page.wait_for_timeout(100)
                        
                        await amount_input.evaluate(f"""
                            (element) => {{
                                element.focus();
                                element.click();
                                const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                                    window.HTMLInputElement.prototype, 
                                    'value'
                                ).set;
                                nativeInputValueSetter.call(element, '{amount}');
                                element.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                element.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                element.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', bubbles: true }}));
                                element.dispatchEvent(new KeyboardEvent('keyup', {{ key: 'Enter', bubbles: true }}));
                            }}
                        """)
                        
                        await self.page.wait_for_timeout(500)
                        
                        # Ждем пересчета комиссии
                        try:
                            await self.page.wait_for_function("""
                                () => {
                                    const input = document.querySelector('input[placeholder*="UZS"]');
                                    return input && input.value && input.value !== '0 UZS' && input.value !== '';
                                }
                            """, timeout=1000)
                            log("Комиссия пересчитана", "SUCCESS")
                        except:
                            log("Не удалось пересчитать комиссию", "WARNING")
                        
                        # Повторно выбираем Uzcard
                        await self.page.evaluate("""
                            () => {
                                const uzcardBtn = Array.from(document.querySelectorAll('[role="button"]')).find(
                                    el => el.textContent.includes('Uzcard')
                                );
                                if (uzcardBtn) uzcardBtn.click();
                            }
                        """)
                        await self.page.wait_for_timeout(300)
                    
                    # Если кнопка не активна после 7 попыток, пробуем кликнуть по способу перевода снова
                    if btn_attempt == 7:
                        log("Повторный клик по 'Способ перевода'...", "WARNING")
                        try:
                            transfer_block = self.page.locator('div:has-text("Способ перевода")').first
                            if await transfer_block.is_visible(timeout=500):
                                await transfer_block.click()
                                await self.page.wait_for_timeout(200)
                        except:
                            pass
                        
                        # И снова Uzcard
                        await self.page.evaluate("""
                            () => {
                                const uzcardBtn = Array.from(document.querySelectorAll('[role="button"]')).find(
                                    el => el.textContent.includes('Uzcard')
                                );
                                if (uzcardBtn) uzcardBtn.click();
                            }
                        """)
                        await self.page.wait_for_timeout(300)
                    
                    # Дополнительная попытка на 14-й итерации (как на 7-й)
                    if btn_attempt == 14:
                        log("Повторный клик по 'Способ перевода' (попытка #14)...", "WARNING")
                        try:
                            transfer_block = self.page.locator('div:has-text("Способ перевода")').first
                            if await transfer_block.is_visible(timeout=500):
                                await transfer_block.click()
                                await self.page.wait_for_timeout(200)
                        except:
                            pass
                        
                        # И снова Uzcard
                        await self.page.evaluate("""
                            () => {
                                const uzcardBtn = Array.from(document.querySelectorAll('[role="button"]')).find(
                                    el => el.textContent.includes('Uzcard')
                                );
                                if (uzcardBtn) uzcardBtn.click();
                            }
                        """)
                        await self.page.wait_for_timeout(300)
                    
                    # Если кнопка не активна, пробуем кликнуть Uzcard еще раз
                    if btn_attempt > 4 and btn_attempt % 2 == 0:
                        await self.page.evaluate("""
                            () => {
                                const uzcardBtn = Array.from(document.querySelectorAll('[role="button"]')).find(
                                    el => el.textContent.includes('Uzcard')
                                );
                                if (uzcardBtn) uzcardBtn.click();
                            }
                        """)
                        log(f"Повторный клик по Uzcard (попытка #{btn_attempt + 1})", "WARNING")
                    
                    await self.page.wait_for_timeout(300)
                    
                except Exception as e:
                    log(f"Ошибка проверки кнопки: {e}", "WARNING")
                    await self.page.wait_for_timeout(300)
            
            if not button_active:
                log("Кнопка Продолжить не активировалась", "ERROR")
                # Делаем скриншот при ошибке
                screenshot_path = f"screenshots/error_button_{int(time.time())}.png"
                try:
                    os.makedirs("screenshots", exist_ok=True)
                    await self.page.screenshot(path=screenshot_path, full_page=True)
                    log(f"Скриншот сохранен: {screenshot_path}", "INFO")
                except Exception as e:
                    log(f"Не удалось сохранить скриншот: {e}", "WARNING")
                return {'success': False, 'error': 'Кнопка Продолжить не активировалась', 'time': time.time() - start_time, 'logs': current_payment_logs.copy()}
            
            # Клик по кнопке
            await self.page.locator('#pay').evaluate('el => el.click()')
            log("Кнопка Продолжить нажата", "SUCCESS")
            
            await self.page.wait_for_url('**/sender-details**', timeout=10000)
            log("Переход на страницу заполнения данных", "SUCCESS")
            
            step1_time = time.time() - start_time
            step2_start = time.time()
            
            # ЭТАП 2: Заполнение полей
            await self.page.wait_for_selector('input', state='visible', timeout=10000)
            # Ждем пока страница полностью загрузится - проверяем наличие всех ключевых полей
            await self.page.wait_for_function("""
                () => {
                    const cardInput = document.querySelector('input[name="transfer_beneficiaryAccountNumber"]');
                    const firstNameInput = document.querySelector('input[name="beneficiary_firstName"]');
                    const lastNameInput = document.querySelector('input[name="beneficiary_lastName"]');
                    return cardInput && firstNameInput && lastNameInput;
                }
            """, timeout=5000)
            
            # Закрываем модалки перед заполнением
            log("Проверяю модалки...", "DEBUG")
            for _ in range(1):  # было 2, теперь 1 раз
                modal_closed = await self.page.evaluate("""
                    () => {
                        const buttons = document.querySelectorAll('button[buttontext="Понятно"]');
                        let closed = false;
                        buttons.forEach(btn => {
                            if (btn.textContent.includes('Понятно')) {
                                btn.click();
                                closed = true;
                            }
                        });
                        return closed;
                    }
                """)
                if modal_closed:
                    log("Модалка закрыта", "WARNING")
                    await self.page.wait_for_timeout(50)  # было 100
                else:
                    break
            
            owner_parts = owner_name.split()
            first_name = owner_parts[0] if len(owner_parts) > 0 else ""
            last_name = owner_parts[1] if len(owner_parts) > 1 else ""
            
            log("=" * 50, "INFO")
            log("ЭТАП 2: ЗАПОЛНЕНИЕ ПОЛЕЙ", "INFO")
            log("=" * 50, "INFO")
            
            print("\n⚡ Заполняю поля отправителя (оптимизированные задержки)...")
            
            # Убираем начальное движение мыши - не критично
            # Последовательное заполнение с ОПТИМИЗИРОВАННЫМИ задержками (300-600мс вместо 500-1200мс)
            await fill_field_simple(self.page, "sender_documents_series", SENDER_DATA["passport_series"], "Серия паспорта")
            await self.page.wait_for_timeout(random.randint(300, 500))
            
            await fill_field_simple(self.page, "sender_documents_number", SENDER_DATA["passport_number"], "Номер паспорта")
            await self.page.wait_for_timeout(random.randint(300, 500))
            
            await fill_field_simple(self.page, "issueDate", SENDER_DATA["passport_issue_date"], "Дата выдачи")
            await self.page.wait_for_timeout(random.randint(400, 600))
            
            await fill_field_simple(self.page, "sender_middleName", SENDER_DATA["middle_name"], "Отчество")
            await self.page.wait_for_timeout(random.randint(300, 500))
            
            await fill_field_simple(self.page, "sender_firstName", SENDER_DATA["first_name"], "Имя отправителя")
            await self.page.wait_for_timeout(random.randint(300, 500))
            
            await fill_field_simple(self.page, "sender_lastName", SENDER_DATA["last_name"], "Фамилия отправителя")
            await self.page.wait_for_timeout(random.randint(300, 500))
            
            await fill_field_simple(self.page, "birthDate", SENDER_DATA["birth_date"], "Дата рождения")
            await self.page.wait_for_timeout(random.randint(400, 600))
            
            await fill_field_simple(self.page, "phoneNumber", SENDER_DATA["phone"], "Телефон")
            await self.page.wait_for_timeout(random.randint(300, 500))
            
            await fill_field_simple(self.page, "birthPlaceAddress_full", SENDER_DATA["birth_place"], "Место рождения")
            await self.page.wait_for_timeout(random.randint(400, 600))
            
            await fill_field_simple(self.page, "registrationAddress_full", SENDER_DATA["registration_place"], "Место регистрации")
            await self.page.wait_for_timeout(random.randint(400, 600))
            
            print("\n🌍 Заполняю страны...")
            # Страны
            birth_country_ok = await select_country_async(self.page, "birthPlaceAddress_countryCode", SENDER_DATA["birth_country"], "Страна рождения")
            reg_country_ok = await select_country_async(self.page, "registrationAddress_countryCode", SENDER_DATA["registration_country"], "Страна регистрации")
            
            if not birth_country_ok:
                print(f"   ❌ Страна рождения: не выбрана")
            if not reg_country_ok:
                print(f"   ❌ Страна регистрации: не выбрана")
            
            # Галочка
            try:
                checkbox = self.page.locator('input[type="checkbox"]').first
                if not await checkbox.is_checked():
                    await checkbox.click(force=True)
            except:
                pass
            
            # Пауза перед заполнением получателя (уменьшена с 700 до 400)
            log("Жду обработки полей отправителя...", "DEBUG")
            await self.page.wait_for_timeout(400)
            
            print("\n💳 Заполняю реквизиты получателя (в конце)...")
            # КРИТИЧЕСКИ ВАЖНО: Заполняем поля получателя В САМОМ КОНЦЕ
            card_ok = await fill_beneficiary_card(self.page, card_number)
            if not card_ok:
                log("КРИТИЧЕСКАЯ ОШИБКА: Номер карты не заполнен!", "ERROR")
                screenshot_path = f"screenshots/error_card_{int(time.time())}.png"
                try:
                    await self.page.screenshot(path=screenshot_path)
                    log(f"Скриншот сохранен: {screenshot_path}", "INFO")
                except:
                    pass
                return {
                    'success': False,
                    'qr_link': None,
                    'time': time.time() - start_time,
                    'step1_time': step1_time,
                    'step2_time': 0,
                    'error': 'Не удалось заполнить номер карты',
                    'logs': current_payment_logs.copy()
                }
            
            await self.page.wait_for_timeout(300)
            
            fname_ok, lname_ok = await fill_beneficiary_name(self.page, first_name, last_name)
            if not fname_ok or not lname_ok:
                log(f"КРИТИЧЕСКАЯ ОШИБКА: Имя/Фамилия не заполнены (fname={fname_ok}, lname={lname_ok})", "ERROR")
                screenshot_path = f"screenshots/error_name_{int(time.time())}.png"
                try:
                    await self.page.screenshot(path=screenshot_path)
                    log(f"Скриншот сохранен: {screenshot_path}", "INFO")
                except:
                    pass
                return {
                    'success': False,
                    'qr_link': None,
                    'time': time.time() - start_time,
                    'step1_time': step1_time,
                    'step2_time': 0,
                    'error': 'Не удалось заполнить имя/фамилию получателя',
                    'logs': current_payment_logs.copy()
                }
            
            log("Реквизиты получателя заполнены успешно!", "SUCCESS")
            
            # КРИТИЧНО: Быстро прокликиваем все инпуты чтобы React пересчитал валидацию
            log("Прокликиваю все поля для пересчета валидации...", "DEBUG")
            try:
                all_inputs = await self.page.locator('input[type="text"], input[type="tel"]').all()
                for inp in all_inputs:
                    try:
                        # Проверяем что поле видимо
                        if await inp.is_visible():
                            await inp.click(timeout=100)
                            await self.page.wait_for_timeout(30)
                    except:
                        pass
                
                # Клик мимо всех полей
                await self.page.evaluate("document.body.click()")
                await self.page.wait_for_timeout(200)
                log("Все поля прокликаны", "SUCCESS")
            except Exception as e:
                log(f"Ошибка при прокликивании полей: {e}", "WARNING")
            
            # Двойная проверка ошибок с паузами
            log("Двойная проверка валидации полей...", "DEBUG")
            for check_num in range(2):
                await self.page.wait_for_timeout(800)
                
                error_count = await self.page.evaluate("""
                    () => {
                        const inputs = document.querySelectorAll('input[type="text"], input[type="tel"]');
                        let count = 0;
                        
                        inputs.forEach(input => {
                            if (input.offsetParent === null) return;
                            const parent = input.closest('div.MuiFormControl-root');
                            if (parent) {
                                const isInvalid = input.getAttribute('aria-invalid') === 'true';
                                const errorText = parent.querySelector('p.Mui-error');
                                const hasErrorText = errorText && errorText.textContent.trim().length > 0;
                                
                                if (isInvalid || hasErrorText) {
                                    count++;
                                }
                            }
                        });
                        
                        return count;
                    }
                """)
                
                log(f"Проверка #{check_num + 1}: найдено {error_count} полей с ошибками", "DEBUG")
                
                if error_count == 0:
                    log("✅ Все поля валидны!", "SUCCESS")
                    break
            
            # ПРОВЕРКА И ПЕРЕЗАПОЛНЕНИЕ полей с ошибками (несколько раундов)
            for round_num in range(3):  # До 3 раундов перезаполнения
                log(f"Раунд {round_num + 1}: Проверяю поля с ошибками...", "DEBUG")
                
                # Находим все поля с ошибками
                error_fields = await self.page.evaluate("""
                    () => {
                        const errors = [];
                        const inputs = document.querySelectorAll('input[type="text"], input[type="tel"]');
                        
                        inputs.forEach(input => {
                            // Пропускаем скрытые поля
                            if (input.offsetParent === null) return;
                            
                            const parent = input.closest('div.MuiFormControl-root');
                            if (parent) {
                                // Проверяем aria-invalid
                                const isInvalid = input.getAttribute('aria-invalid') === 'true';
                                
                                // Проверяем класс Mui-error на input
                                const hasErrorClass = input.classList.contains('Mui-error');
                                
                                // Проверяем текст ошибки
                                const errorText = parent.querySelector('p.Mui-error');
                                const hasErrorText = errorText && errorText.textContent.trim().length > 0;
                                
                                // Проверяем красную иконку
                                const errorIcon = parent.querySelector('svg path[fill="#E93544"]');
                                
                                if (isInvalid || hasErrorClass || hasErrorText || errorIcon) {
                                    errors.push({
                                        name: input.name,
                                        placeholder: input.placeholder,
                                        currentValue: input.value,
                                        errorText: errorText ? errorText.textContent : '',
                                        isInvalid: isInvalid,
                                        hasErrorClass: hasErrorClass
                                    });
                                }
                            }
                        });
                        
                        return errors;
                    }
                """)
                
                if len(error_fields) == 0:
                    log("✅ Все поля заполнены корректно!", "SUCCESS")
                    break
                
                log(f"⚠️ Найдено {len(error_fields)} полей с ошибками:", "WARNING")
                for field in error_fields:
                    log(f"  - {field['name']}: {field.get('errorText', 'красная обводка')}", "WARNING")
                
                # Перезаполняем поля с ошибками через клик + Tab
                for field in error_fields:
                    field_name = field['name']
                    
                    # Определяем значение для перезаполнения
                    value_map = {
                        'transfer_beneficiaryAccountNumber': card_number,
                        'beneficiary_firstName': first_name,
                        'beneficiary_lastName': last_name,
                        'sender_documents_series': SENDER_DATA["passport_series"],
                        'sender_documents_number': SENDER_DATA["passport_number"],
                        'issueDate': SENDER_DATA["passport_issue_date"],
                        'sender_middleName': SENDER_DATA["middle_name"],
                        'sender_firstName': SENDER_DATA["first_name"],
                        'sender_lastName': SENDER_DATA["last_name"],
                        'birthDate': SENDER_DATA["birth_date"],
                        'phoneNumber': SENDER_DATA["phone"],
                        'birthPlaceAddress_full': SENDER_DATA["birth_place"],
                        'registrationAddress_full': SENDER_DATA["registration_place"]
                    }
                    
                    if field_name in value_map:
                        value = value_map[field_name]
                        log(f"🔄 Перезаполняю {field_name} = {value}", "DEBUG")
                        
                        try:
                            input_elem = await self.page.query_selector(f'input[name="{field_name}"]')
                            if input_elem:
                                escaped_value = value.replace('\\', '\\\\').replace("'", "\\'").replace('"', '\\"')
                                
                                await input_elem.evaluate(f"""
                                    (element) => {{
                                        element.focus();
                                        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                                            window.HTMLInputElement.prototype,
                                            'value'
                                        ).set;
                                        nativeInputValueSetter.call(element, '{escaped_value}');
                                        element.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                        element.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                        element.blur();
                                    }}
                                """)
                                
                                await self.page.wait_for_timeout(200)
                                
                        except Exception as e:
                            log(f"❌ Ошибка при перезаполнении {field_name}: {e}", "ERROR")
                
                # Ждем после перезаполнения
                await self.page.wait_for_timeout(1000)
            
            # Ждем чтобы React обработал все изменения
            log("Жду обработки всех полей...", "DEBUG")
            await self.page.wait_for_timeout(700)
            
            # Проверяем что ВСЕ поля заполнены перед нажатием кнопки
            log("Проверяю заполненность ВСЕХ полей...", "DEBUG")
            fields_filled = await self.page.evaluate("""
                () => {
                    const getFieldValue = (name) => {
                        const input = document.querySelector(`input[name="${name}"]`);
                        return input ? input.value : '';
                    };
                    
                    return {
                        card: getFieldValue('transfer_beneficiaryAccountNumber'),
                        firstName: getFieldValue('beneficiary_firstName'),
                        lastName: getFieldValue('beneficiary_lastName'),
                        senderFirstName: getFieldValue('sender_firstName'),
                        senderLastName: getFieldValue('sender_lastName'),
                        senderMiddleName: getFieldValue('sender_middleName'),
                        birthDate: getFieldValue('birthDate'),
                        phone: getFieldValue('phoneNumber'),
                        passportSeries: getFieldValue('sender_documents_series'),
                        passportNumber: getFieldValue('sender_documents_number'),
                        issueDate: getFieldValue('issueDate')
                    };
                }
            """)
            log(f"Получатель: карта={fields_filled['card']}, имя={fields_filled['firstName']}, фамилия={fields_filled['lastName']}", "DEBUG")
            log(f"Отправитель: {fields_filled['senderLastName']} {fields_filled['senderFirstName']} {fields_filled['senderMiddleName']}", "DEBUG")
            log(f"Дата рождения: {fields_filled['birthDate']}, телефон: {fields_filled['phone']}", "DEBUG")
            log(f"Паспорт: {fields_filled['passportSeries']} {fields_filled['passportNumber']}, выдан: {fields_filled['issueDate']}", "DEBUG")
            
            # Проверяем что критичные поля заполнены
            if not fields_filled['card'] or not fields_filled['firstName'] or not fields_filled['lastName']:
                log("КРИТИЧЕСКАЯ ОШИБКА: Поля получателя пустые!", "ERROR")
                screenshot_path = f"screenshots/error_empty_fields_{int(time.time())}.png"
                try:
                    await self.page.screenshot(path=screenshot_path, full_page=True)
                    log(f"Скриншот сохранен: {screenshot_path}", "INFO")
                except:
                    pass
                return {
                    'success': False,
                    'qr_link': None,
                    'time': time.time() - start_time,
                    'step1_time': step1_time,
                    'step2_time': 0,
                    'error': 'Поля получателя пустые перед отправкой',
                    'logs': current_payment_logs.copy()
                }
            
            # Кнопка "Продолжить" - отправляем форму и ждем навигации
            log("Отправляю форму (этап 2)...", "DEBUG")
            
            # Сохраняем текущий URL перед отправкой
            url_before = self.page.url
            log(f"URL перед отправкой: {url_before}", "DEBUG")
            
            # Проверяем что кнопка активна
            button_clicked = False
            for attempt in range(25):
                try:
                    is_enabled = await self.page.evaluate("""
                        () => {
                            const btn = document.getElementById('pay');
                            return btn && !btn.disabled;
                        }
                    """)
                    
                    if is_enabled:
                        log(f"Кнопка активна (попытка #{attempt + 1})", "DEBUG")
                        
                        # Кликаем и ждем навигации или сетевой активности
                        try:
                            # Ждем либо навигации, либо сетевого запроса
                            async with self.page.expect_event("response", timeout=5000) as response_info:
                                await self.page.locator('#pay').click(force=True)
                            
                            response = await response_info.value
                            log(f"Получен ответ: {response.url}", "DEBUG")
                            button_clicked = True
                            await self.page.wait_for_timeout(2000)
                            break
                        except:
                            # Если не дождались ответа - пробуем просто кликнуть
                            try:
                                await self.page.locator('#pay').evaluate('el => el.click()')
                                log("Кнопка Продолжить нажата (JS клик)", "SUCCESS")
                                button_clicked = True
                                await self.page.wait_for_timeout(2000)
                                break
                            except:
                                pass
                        
                        # Дополнительная попытка на 7 и 14 итерации
                        if attempt in [7, 14]:
                            try:
                                await self.page.locator('#pay').evaluate("""
                                    el => {
                                        el.dispatchEvent(new MouseEvent('click', {
                                            view: window,
                                            bubbles: true,
                                            cancelable: true
                                        }));
                                    }
                                """)
                                log(f"Кнопка Продолжить нажата (dispatchEvent, попытка {attempt + 1})", "SUCCESS")
                                button_clicked = True
                                await self.page.wait_for_timeout(2000)
                                break
                            except:
                                pass
                    else:
                        log(f"Кнопка не активна (попытка #{attempt + 1}), жду...", "WARNING")
                        
                except Exception as e:
                    log(f"Ошибка при проверке кнопки: {e}", "WARNING")
                
                await self.page.wait_for_timeout(500)
            
            if not button_clicked:
                log("⚠️ Не удалось нажать кнопку Продолжить!", "WARNING")
            
            # Проверяем изменился ли URL после клика
            url_after = self.page.url
            log(f"URL после клика: {url_after}", "DEBUG")
            
            if url_before == url_after and 'sender-details' in url_after:
                log("⚠️ URL не изменился после клика, пробую другие способы...", "WARNING")
                
                # Пробуем через requestSubmit
                try:
                    await self.page.evaluate("""
                        () => {
                            const form = document.querySelector('form');
                            if (form && form.requestSubmit) {
                                form.requestSubmit();
                            }
                        }
                    """)
                    log("Попытка отправки через form.requestSubmit()", "DEBUG")
                    await self.page.wait_for_timeout(2000)
                    
                    url_after_submit = self.page.url
                    if url_after_submit != url_before:
                        log(f"✅ URL изменился после requestSubmit: {url_after_submit}", "SUCCESS")
                except Exception as e:
                    log(f"Ошибка requestSubmit: {e}", "DEBUG")
                
                # Если все еще не изменился - пробуем Enter
                if self.page.url == url_before:
                    try:
                        await self.page.keyboard.press('Enter')
                        log("Попытка отправки через Enter", "DEBUG")
                        await self.page.wait_for_timeout(2000)
                        url_after_enter = self.page.url
                        if url_after_enter != url_before:
                            log(f"✅ URL изменился после Enter: {url_after_enter}", "SUCCESS")
                    except Exception as e:
                        log(f"Ошибка Enter: {e}", "DEBUG")
            
            # Проверяем есть ли ошибки валидации на странице
            try:
                validation_errors = await self.page.evaluate("""
                    () => {
                        const errors = [];
                        // Проверяем красные поля
                        const invalidFields = document.querySelectorAll('input.is-invalid, input[aria-invalid="true"]');
                        invalidFields.forEach(field => {
                            errors.push({
                                name: field.name || field.id,
                                value: field.value
                            });
                        });
                        // Проверяем сообщения об ошибках
                        const errorMessages = document.querySelectorAll('.invalid-feedback, .error-message');
                        errorMessages.forEach(msg => {
                            if (msg.offsetParent !== null) {  // видимый элемент
                                errors.push({ message: msg.textContent.trim() });
                            }
                        });
                        return errors;
                    }
                """)
                
                if validation_errors and len(validation_errors) > 0:
                    log(f"⚠️ Найдены ошибки валидации: {validation_errors}", "WARNING")
                    # Пробуем исправить - кликаем по всем полям еще раз
                    await self.page.evaluate("""
                        () => {
                            const inputs = document.querySelectorAll('input');
                            inputs.forEach(input => {
                                input.focus();
                                input.blur();
                            });
                        }
                    """)
                    await self.page.wait_for_timeout(1000)
            except Exception as e:
                log(f"Ошибка при проверке валидации: {e}", "DEBUG")
            
            # Капча
            log("Проверяю наличие капчи...", "DEBUG")
            try:
                captcha_iframe_selector = 'iframe[src*="smartcaptcha.yandexcloud.net/checkbox"]'
                await self.page.wait_for_selector(captcha_iframe_selector, state='visible', timeout=3000)
                
                log("Капча обнаружена, решаю...", "DEBUG")
                await self.page.wait_for_timeout(500)
                
                # Движение мыши к капче
                try:
                    iframe_element = self.page.locator(captcha_iframe_selector)
                    bbox = await iframe_element.bounding_box()
                    if bbox:
                        center_x = bbox['x'] + bbox['width'] / 2
                        center_y = bbox['y'] + bbox['height'] / 2
                        await self.page.mouse.move(center_x - 50, center_y - 50)
                        await self.page.wait_for_timeout(200)
                        await self.page.mouse.move(center_x, center_y)
                        await self.page.wait_for_timeout(300)
                except:
                    pass
                
                captcha_frame = self.page.frame_locator(captcha_iframe_selector)
                checkbox_button = captcha_frame.locator('#js-button')
                
                await checkbox_button.wait_for(state='visible', timeout=3000)
                
                # Пробуем разные способы клика с несколькими попытками
                captcha_clicked = False
                
                for attempt in range(5):
                    if captcha_clicked:
                        break
                    
                    # Способ 1: Обычный клик
                    try:
                        await checkbox_button.click(timeout=2000)
                        log(f"Капча решена (клик, попытка {attempt + 1})", "SUCCESS")
                        captcha_clicked = True
                        break
                    except:
                        pass
                    
                    # Способ 2: Force клик
                    if not captcha_clicked:
                        try:
                            await checkbox_button.click(force=True, timeout=2000)
                            log(f"Капча решена (force клик, попытка {attempt + 1})", "SUCCESS")
                            captcha_clicked = True
                            break
                        except:
                            pass
                    
                    # Способ 3: JS клик
                    if not captcha_clicked:
                        try:
                            await checkbox_button.evaluate('el => el.click()')
                            log(f"Капча решена (JS клик, попытка {attempt + 1})", "SUCCESS")
                            captcha_clicked = True
                            break
                        except:
                            pass
                    
                    # Способ 4: dispatchEvent
                    if not captcha_clicked:
                        try:
                            await checkbox_button.evaluate("""
                                el => {
                                    el.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
                                    el.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
                                    el.dispatchEvent(new MouseEvent('click', { bubbles: true }));
                                }
                            """)
                            log(f"Капча решена (dispatchEvent, попытка {attempt + 1})", "SUCCESS")
                            captcha_clicked = True
                            break
                        except:
                            pass
                    
                    # Пауза между попытками
                    await self.page.wait_for_timeout(300)
                
                if not captcha_clicked:
                    log("⚠️ Не удалось кликнуть капчу после 5 попыток", "WARNING")
                
                await self.page.wait_for_timeout(800)  # Ждем появления модалки после капчи
                    
            except Exception as e:
                log(f"Капча не обнаружена или ошибка: {e}", "DEBUG")
            
            # Модалка "Проверка данных" - появляется сразу после капчи
            log("Проверяю модалку проверки данных...", "DEBUG")
            try:
                # Ищем модалку с заголовком "Проверка данных"
                modal_info = await self.page.evaluate("""
                    () => {
                        const headers = document.querySelectorAll('h4');
                        for (const h of headers) {
                            if (h.textContent.includes('Проверка данных')) {
                                // Ищем текст под заголовком
                                const parent = h.closest('div');
                                const paragraphs = parent ? parent.querySelectorAll('p') : [];
                                let text = '';
                                paragraphs.forEach(p => {
                                    text += p.textContent + ' ';
                                });
                                return {
                                    found: true,
                                    text: text.trim()
                                };
                            }
                        }
                        return { found: false, text: '' };
                    }
                """)
                
                if modal_info['found']:
                    log(f"📋 Модалка 'Проверка данных': {modal_info['text']}", "INFO")
                    
                    # Проверяем текст модалки
                    if 'Ошибка' in modal_info['text'] or 'ошибка' in modal_info['text']:
                        log("⚠️ ОШИБКА: Реквизиты получателя устарели!", "WARNING")
                        
                        # Закрываем модалку
                        buttons = await self.page.locator('button[buttontext="Продолжить"]').all()
                        if len(buttons) > 0:
                            await buttons[-1].click()
                            log("Модалка закрыта", "SUCCESS")
                            await self.page.wait_for_timeout(300)
                        
                        step2_time = time.time() - step2_start
                        log(f"⏱️ Этап 2 занял: {step2_time:.2f}s", "INFO")
                        
                        return {
                            'success': False,
                            'qr_link': None,
                            'time': time.time() - start_time,
                            'step1_time': step1_time,
                            'step2_time': step2_time,
                            'error': 'Реквизиты получателя больше не актуальны (модалка с ошибкой)',
                            'logs': current_payment_logs.copy()
                        }
                    else:
                        # Это просто подтверждение данных - нажимаем "Продолжить"
                        log("✅ Модалка подтверждения данных - ищу кнопку 'Продолжить'", "SUCCESS")
                        
                        # Ждем появления кнопки и нажимаем
                        try:
                            # Ждем кнопку с текстом "Продолжить"
                            button = self.page.locator('button:has-text("Продолжить")').last
                            await button.wait_for(state='visible', timeout=3000)
                            
                            # Пробуем разные способы клика
                            clicked = False
                            
                            # Способ 1: Обычный клик
                            try:
                                await button.click(timeout=2000)
                                log("Кнопка нажата (обычный клик)", "DEBUG")
                                clicked = True
                            except:
                                pass
                            
                            # Способ 2: Force клик
                            if not clicked:
                                try:
                                    await button.click(force=True, timeout=2000)
                                    log("Кнопка нажата (force клик)", "DEBUG")
                                    clicked = True
                                except:
                                    pass
                            
                            # Способ 3: Клик через evaluate
                            if not clicked:
                                try:
                                    await button.evaluate('el => el.click()')
                                    log("Кнопка нажата (JS клик)", "DEBUG")
                                    clicked = True
                                except:
                                    pass
                            
                            # Способ 4: Клик по координатам
                            if not clicked:
                                try:
                                    box = await button.bounding_box()
                                    if box:
                                        x = box['x'] + box['width'] / 2
                                        y = box['y'] + box['height'] / 2
                                        await self.page.mouse.click(x, y)
                                        log("Кнопка нажата (mouse клик)", "DEBUG")
                                        clicked = True
                                except:
                                    pass
                            
                            # Способ 5: Через dispatchEvent
                            if not clicked:
                                try:
                                    await button.evaluate("""
                                        el => {
                                            el.dispatchEvent(new MouseEvent('click', {
                                                view: window,
                                                bubbles: true,
                                                cancelable: true
                                            }));
                                        }
                                    """)
                                    log("Кнопка нажата (dispatchEvent)", "DEBUG")
                                    clicked = True
                                except:
                                    pass
                            
                            if clicked:
                                log("✅ Модалка закрыта, проверяю что на странице...", "SUCCESS")
                                
                                # Ждем чтобы модалка точно закрылась
                                await self.page.wait_for_timeout(2000)
                                
                                # СКРИНШОТ 1: Сразу после закрытия модалки
                                timestamp = int(time.time())
                                screenshot1_path = f"screenshots/after_modal_close_{timestamp}.png"
                                await self.page.screenshot(path=screenshot1_path, full_page=True)
                                log(f"📸 Скриншот после закрытия модалки: {screenshot1_path}", "INFO")
                                
                                # ПРОВЕРЯЕМ ВСЁ, ЧТО ЕСТЬ НА СТРАНИЦЕ
                                page_state = await self.page.evaluate("""
                                    () => {
                                        const state = {
                                            url: window.location.href,
                                            modals: [],
                                            captchas: [],
                                            buttons: [],
                                            errors: []
                                        };
                                        
                                        // Ищем все модалки
                                        const modalTexts = document.querySelectorAll('h4, h3, h2');
                                        modalTexts.forEach(h => {
                                            if (h.offsetParent !== null) {
                                                state.modals.push(h.textContent.trim());
                                            }
                                        });
                                        
                                        // Ищем капчи
                                        const captchaIframes = document.querySelectorAll('iframe[src*="captcha"]');
                                        state.captchas.push(`Найдено капч: ${captchaIframes.length}`);
                                        
                                        // Ищем кнопки
                                        const buttons = document.querySelectorAll('button');
                                        buttons.forEach(btn => {
                                            if (btn.offsetParent !== null && btn.textContent.trim()) {
                                                state.buttons.push({
                                                    text: btn.textContent.trim(),
                                                    disabled: btn.disabled,
                                                    id: btn.id
                                                });
                                            }
                                        });
                                        
                                        // Ищем ошибки
                                        const errorElements = document.querySelectorAll('.error, .invalid-feedback, [class*="error"]');
                                        errorElements.forEach(err => {
                                            if (err.offsetParent !== null && err.textContent.trim()) {
                                                state.errors.push(err.textContent.trim());
                                            }
                                        });
                                        
                                        return state;
                                    }
                                """)
                                
                                log(f"📊 Состояние страницы после закрытия модалки:", "INFO")
                                log(f"   URL: {page_state['url']}", "INFO")
                                log(f"   Модалки: {page_state['modals']}", "INFO")
                                log(f"   Капчи: {page_state['captchas']}", "INFO")
                                log(f"   Кнопки: {page_state['buttons'][:5]}", "INFO")  # Первые 5
                                log(f"   Ошибки: {page_state['errors']}", "INFO")
                                
                                # Проверяем есть ли ещё капча
                                if any('captcha' in str(c).lower() for c in page_state['captchas']) or len(page_state['captchas']) > 0:
                                    log("⚠️ ОБНАРУЖЕНА ЕЩЁ ОДНА КАПЧА после модалки!", "WARNING")
                                    
                                    # СКРИНШОТ 2: Перед решением второй капчи
                                    screenshot2_path = f"screenshots/before_second_captcha_{timestamp}.png"
                                    await self.page.screenshot(path=screenshot2_path, full_page=True)
                                    log(f"📸 Скриншот перед второй капчей: {screenshot2_path}", "INFO")
                                    
                                    # Пробуем решить
                                    try:
                                        captcha_iframe_selector = 'iframe[src*="smartcaptcha.yandexcloud.net/checkbox"]'
                                        await self.page.wait_for_selector(captcha_iframe_selector, state='visible', timeout=2000)
                                        log("Решаю вторую капчу...", "DEBUG")
                                        
                                        captcha_frame = self.page.frame_locator(captcha_iframe_selector)
                                        checkbox_button = captcha_frame.locator('#js-button')
                                        await checkbox_button.click(timeout=2000)
                                        log("✅ Вторая капча решена", "SUCCESS")
                                        await self.page.wait_for_timeout(2000)
                                        
                                        # СКРИНШОТ 3: После решения второй капчи
                                        screenshot3_path = f"screenshots/after_second_captcha_{timestamp}.png"
                                        await self.page.screenshot(path=screenshot3_path, full_page=True)
                                        log(f"📸 Скриншот после второй капчи: {screenshot3_path}", "INFO")
                                    except Exception as e:
                                        log(f"Не удалось решить вторую капчу: {e}", "DEBUG")
                                
                                # Теперь пробуем кликнуть основную кнопку
                                try:
                                    is_enabled = await self.page.evaluate("""
                                        () => {
                                            const btn = document.getElementById('pay');
                                            return btn && !btn.disabled;
                                        }
                                    """)
                                    
                                    if is_enabled:
                                        log("Основная кнопка Продолжить активна, кликаю...", "DEBUG")
                                        
                                        # СКРИНШОТ 4: Перед кликом основной кнопки
                                        screenshot4_path = f"screenshots/before_main_button_{timestamp}.png"
                                        await self.page.screenshot(path=screenshot4_path, full_page=True)
                                        log(f"📸 Скриншот перед кликом основной кнопки: {screenshot4_path}", "INFO")
                                        
                                        await self.page.locator('#pay').click(force=True)
                                        log("✅ Основная кнопка нажата", "SUCCESS")
                                        
                                        # Ждем навигации
                                        try:
                                            await self.page.wait_for_url(lambda url: 'sender-details' not in url, timeout=5000)
                                            log(f"✅ Навигация выполнена: {self.page.url}", "SUCCESS")
                                            
                                            # СКРИНШОТ 5: После успешной навигации
                                            screenshot5_path = f"screenshots/after_navigation_{timestamp}.png"
                                            await self.page.screenshot(path=screenshot5_path, full_page=True)
                                            log(f"📸 Скриншот после навигации: {screenshot5_path}", "INFO")
                                        except:
                                            log("⚠️ Навигация не произошла", "WARNING")
                                            
                                            # СКРИНШОТ 6: Если навигация не произошла
                                            screenshot6_path = f"screenshots/no_navigation_{timestamp}.png"
                                            await self.page.screenshot(path=screenshot6_path, full_page=True)
                                            log(f"📸 Скриншот - навигация не произошла: {screenshot6_path}", "INFO")
                                    else:
                                        log("⚠️ Основная кнопка не активна", "WARNING")
                                        
                                        # СКРИНШОТ 7: Кнопка не активна
                                        screenshot7_path = f"screenshots/button_disabled_{timestamp}.png"
                                        await self.page.screenshot(path=screenshot7_path, full_page=True)
                                        log(f"📸 Скриншот - кнопка не активна: {screenshot7_path}", "INFO")
                                except Exception as e:
                                    log(f"Ошибка при клике: {e}", "WARNING")
                                
                                # КРИТИЧНО: Проверяем модалку с ошибкой
                                log("Проверяю модалку с ошибкой после подтверждения...", "DEBUG")
                                try:
                                    error_check = await self.page.evaluate("""
                                        () => {
                                            const buttons = document.querySelectorAll('button[buttontext="Понятно"]');
                                            let hasError = false;
                                            let errorText = '';
                                            
                                            buttons.forEach(btn => {
                                                if (btn.textContent.includes('Понятно')) {
                                                    hasError = true;
                                                    const parent = btn.closest('div');
                                                    if (parent) {
                                                        errorText = parent.innerText || parent.textContent;
                                                    }
                                                }
                                            });
                                            
                                            return { hasError, errorText };
                                        }
                                    """)
                                    
                                    if error_check['hasError']:
                                        error_text = error_check['errorText']
                                        log(f"❌ ОШИБКА РЕКВИЗИТОВ: {error_text}", "ERROR")
                                        
                                        # Закрываем модалку
                                        await self.page.evaluate("""
                                            () => {
                                                const buttons = document.querySelectorAll('button[buttontext="Понятно"]');
                                                buttons.forEach(btn => {
                                                    if (btn.textContent.includes('Понятно')) {
                                                        btn.click();
                                                    }
                                                });
                                            }
                                        """)
                                        
                                        step2_time = time.time() - step2_start
                                        log(f"⏱️ Этап 2 занял: {step2_time:.2f}s", "INFO")
                                        
                                        return {
                                            'success': False,
                                            'qr_link': None,
                                            'time': time.time() - start_time,
                                            'step1_time': step1_time,
                                            'step2_time': step2_time,
                                            'error': 'Реквизиты получателя больше не актуальны (модалка с ошибкой после подтверждения)',
                                            'logs': current_payment_logs.copy()
                                        }
                                except Exception as e:
                                    log(f"Ошибка при проверке модалки с ошибкой: {e}", "DEBUG")
                                
                                await self.page.wait_for_timeout(500)
                            else:
                                log("⚠️ Не удалось нажать кнопку!", "WARNING")
                                
                        except Exception as e:
                            log(f"⚠️ Ошибка при нажатии кнопки: {e}", "WARNING")
                else:
                    log("Модалка проверки данных не обнаружена", "DEBUG")
                    
            except Exception as e:
                log(f"Ошибка при проверке модалки: {e}", "DEBUG")
            
            # Ждем QR ссылку (увеличено до 30 секунд)
            log("Жду QR-ссылку...", "DEBUG")
            for i in range(60):  # 60 * 500ms = 30 секунд
                if qr_link:
                    log(f"QR-ссылка получена на итерации {i+1}", "SUCCESS")
                    break
                
                # Проверяем URL каждые 2 секунды
                if i % 4 == 0:
                    current_url = self.page.url
                    log(f"Текущий URL (итерация {i}): {current_url}", "DEBUG")
                    
                    # Если URL изменился - значит форма отправилась
                    if 'sender-details' not in current_url:
                        log(f"URL изменился! Новый URL: {current_url}", "SUCCESS")
                
                # Проверяем модалки с ошибками каждые 2 секунды
                if i % 4 == 0:
                    try:
                        error_modal_info = await self.page.evaluate("""
                            () => {
                                const buttons = document.querySelectorAll('button[buttontext="Понятно"]');
                                let hasError = false;
                                let errorText = '';
                                
                                buttons.forEach(btn => {
                                    if (btn.textContent.includes('Понятно')) {
                                        hasError = true;
                                        // Ищем текст ошибки в родительском элементе
                                        const parent = btn.closest('div');
                                        if (parent) {
                                            const allText = parent.innerText || parent.textContent;
                                            errorText = allText;
                                        }
                                        btn.click();
                                    }
                                });
                                
                                return { hasError, errorText };
                            }
                        """)
                        
                        if error_modal_info['hasError']:
                            error_text = error_modal_info['errorText'][:200]
                            log(f"⚠️ МОДАЛКА С ОШИБКОЙ: {error_text}", "WARNING")
                            
                            # Если это критическая ошибка - возвращаем
                            if 'некорректна' in error_text or 'неверн' in error_text.lower():
                                step2_time = time.time() - step2_start
                                return {
                                    'success': False,
                                    'qr_link': None,
                                    'time': time.time() - start_time,
                                    'step1_time': step1_time,
                                    'step2_time': step2_time,
                                    'error': f'Ошибка валидации: {error_text}',
                                    'logs': current_payment_logs.copy()
                                }
                    except:
                        pass
                
                await self.page.wait_for_timeout(500)
            
            step2_time = time.time() - step2_start
            elapsed = time.time() - start_time
            
            # Успех только если есть QR-ссылка
            success = qr_link is not None and qr_link != ""
            
            # Если QR не получен - делаем скриншот и сохраняем HTML
            if not success:
                log("QR-ссылка не получена, сохраняю отладочную информацию", "WARNING")
                timestamp = int(time.time())
                screenshot_full_path = f"screenshots/no_qr_full_{timestamp}.png"
                html_path = f"screenshots/page_{timestamp}.html"
                
                try:
                    os.makedirs("screenshots", exist_ok=True)
                    
                    # ВАЖНО: Прокручиваем к самому верху перед full_page скриншотом
                    await self.page.evaluate("window.scrollTo({ top: 0, behavior: 'instant' })")
                    await self.page.wait_for_timeout(500)
                    
                    # Делаем скриншот всей страницы (теперь начиная с верха)
                    await self.page.screenshot(path=screenshot_full_path, full_page=True)
                    log(f"Скриншот полной страницы сохранен: {screenshot_full_path}", "WARNING")
                    
                    # Сохраняем HTML страницы
                    html_content = await self.page.content()
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    log(f"HTML сохранен: {html_path}", "WARNING")
                    
                    # Проверяем текущий URL
                    current_url = self.page.url
                    log(f"Текущий URL: {current_url}", "DEBUG")
                except Exception as e:
                    log(f"Не удалось сохранить скриншот/HTML: {e}", "WARNING")
            
            return {
                'success': success,
                'qr_link': qr_link,
                'time': elapsed,
                'step1_time': step1_time,
                'step2_time': step2_time,
                'error': None if success else 'QR-ссылка не получена',
                'logs': current_payment_logs.copy()  # Добавляем логи в результат
            }
            
        except Exception as e:
            log(f"ИСКЛЮЧЕНИЕ: {e}", "ERROR")
            # Делаем скриншот при исключении
            screenshot_path = f"screenshots/error_exception_{int(time.time())}.png"
            try:
                await self.page.screenshot(path=screenshot_path)
                log(f"Скриншот сохранен: {screenshot_path}", "INFO")
            except:
                pass
            return {
                'success': False,
                'qr_link': None,
                'time': time.time() - start_time,
                'step1_time': 0,
                'step2_time': 0,
                'error': str(e),
                'logs': current_payment_logs.copy()
            }
        finally:
            self.page.remove_listener('response', handle_response)


async def main():
    """Пример использования сервиса"""
    service = PaymentService()
    
    try:
        # Запускаем сервис в headless режиме (True для production, False для отладки)
        await service.start(headless=True)
        
        # Создаем несколько платежей подряд
        results = []
        for i in range(2):  # Уменьшаем с 3 до 2
            log("=" * 70, "INFO")
            log(f"ПЛАТЕЖ #{i+1}", "INFO")
            log("=" * 70, "INFO")
            
            result = await service.create_payment_link(
                amount=110,
                card_number="9860080323894719",
                owner_name="Nodir Asadullayev"
            )
            
            results.append(result)
            
            if result['success']:
                log(f"Успех!", "SUCCESS")
                log(f"Этап 1: {result['step1_time']:.2f}s", "INFO")
                log(f"Этап 2: {result['step2_time']:.2f}s", "INFO")
                log(f"Общее время: {result['time']:.2f}s", "INFO")
                if result['qr_link']:
                    log(f"QR: {result['qr_link'][:80]}...", "SUCCESS")
            else:
                log(f"Ошибка: {result['error']}", "ERROR")
            
            if i < 2:
                await asyncio.sleep(1)
        
        # Статистика
        log("=" * 70, "INFO")
        log("СТАТИСТИКА", "INFO")
        log("=" * 70, "INFO")
        successful = [r for r in results if r['success']]
        if successful:
            avg_time = sum(r['time'] for r in successful) / len(successful)
            avg_step1 = sum(r['step1_time'] for r in successful) / len(successful)
            avg_step2 = sum(r['step2_time'] for r in successful) / len(successful)
            log(f"Успешных: {len(successful)}/{len(results)}", "SUCCESS")
            log(f"Среднее время: {avg_time:.2f}s", "INFO")
            log(f"Средний этап 1: {avg_step1:.2f}s", "INFO")
            log(f"Средний этап 2: {avg_step2:.2f}s", "INFO")
        else:
            log("Все тесты провалились!", "ERROR")
        
    finally:
        await service.stop()


if __name__ == "__main__":
    asyncio.run(main())
