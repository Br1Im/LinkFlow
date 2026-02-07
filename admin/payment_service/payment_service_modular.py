#!/usr/bin/env python3
"""
Сервис для создания платежных ссылок с постоянным браузером
МОДУЛЬНАЯ ВЕРСИЯ: Использует отдельные файлы для каждого этапа (steps/)

Браузер открывается один раз и остается активным между запросами
PRODUCTION VERSION - headless mode, detailed logging
Данные отправителей берутся из БД
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
    fallback_data = {
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
    
    if not DB_AVAILABLE:
        return fallback_data
    
    sender_data = db.get_random_sender_data()
    
    if not sender_data:
        # Используем fallback вместо исключения
        return fallback_data
    
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
        
        self.playwright = await async_playwright().start()
        
        # Настройки размера окна
        if compact_window and not headless:
            viewport_size = {'width': 800, 'height': 900}
            window_size = '--window-size=800,900'
            window_position = '--window-position=50,50'
        else:
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
        
        # Реалистичный User-Agent
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        
        self.context = await self.browser.new_context(
            viewport=viewport_size,
            user_agent=user_agent,
            locale='ru-RU',
            timezone_id='Europe/Moscow',
            permissions=['geolocation'],
            geolocation={'latitude': 55.7558, 'longitude': 37.6173},
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
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.chrome = { runtime: {} };
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['ru-RU', 'ru', 'en-US', 'en'] });
        """)
        
        self.page = await self.context.new_page()
        
        # Автозакрыватель модалок
        await self.page.evaluate("""
            () => {
                const closeErrorModal = () => {
                    const buttons = document.querySelectorAll('button[buttontext="Понятно"]');
                    buttons.forEach(btn => {
                        if (btn.textContent.includes('Понятно')) btn.click();
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
        Создает платежную ссылку (МОДУЛЬНАЯ ВЕРСИЯ)
        
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
        
        # Очищаем логи
        current_payment_logs.clear()
        log(f"Начало создания платежа: {amount}₽, карта {card_number}, владелец {owner_name}", "INFO")
        
        # Получаем данные отправителя
        if custom_sender:
            SENDER_DATA = {
                "first_name": custom_sender.get('first_name', ''),
                "last_name": custom_sender.get('last_name', ''),
                "middle_name": custom_sender.get('middle_name', ''),
                "birth_date": custom_sender.get('birth_date', ''),
                "phone": custom_sender.get('phone', ''),
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
            # Перезагрузка страницы
            log("Перезагружаю страницу...", "DEBUG")
            await self.page.goto("https://multitransfer.ru/transfer/uzbekistan", wait_until='load', timeout=60000)
            await self.page.wait_for_selector('input[placeholder="0 RUB"]', state='visible', timeout=10000)
            
            # ЭТАП 1: Ввод суммы (используем модуль)
            step1_result = await process_step1(self.page, amount, log)
            
            if not step1_result['success']:
                return {
                    'success': False,
                    'qr_link': None,
                    'time': time.time() - start_time,
                    'step1_time': step1_result['time'],
                    'step2_time': 0,
                    'error': step1_result['error'],
                    'logs': current_payment_logs.copy()
                }
            
            step1_time = step1_result['time']
            
            # ЭТАП 2: Заполнение формы (используем модуль)
            step2_result = await process_step2(self.page, card_number, owner_name, SENDER_DATA, log)
            
            if not step2_result['success']:
                return {
                    'success': False,
                    'qr_link': None,
                    'time': time.time() - start_time,
                    'step1_time': step1_time,
                    'step2_time': step2_result['time'],
                    'error': step2_result['error'],
                    'logs': current_payment_logs.copy()
                }
            
            step2_time = step2_result['time']
            
            # Ждем QR ссылку
            log("Жду QR-ссылку...", "DEBUG")
            for i in range(60):
                if qr_link:
                    log(f"QR-ссылка получена на итерации {i+1}", "SUCCESS")
                    break
                await self.page.wait_for_timeout(500)
            
            elapsed = time.time() - start_time
            success = qr_link is not None and qr_link != ""
            
            # Если QR не получен - делаем скриншот
            if not success:
                log("QR-ссылка не получена, сохраняю скриншот", "WARNING")
                timestamp = int(time.time())
                screenshot_path = f"screenshots/no_qr_{timestamp}.png"
                try:
                    os.makedirs("screenshots", exist_ok=True)
                    await self.page.screenshot(path=screenshot_path, full_page=True)
                    log(f"Скриншот сохранен: {screenshot_path}", "WARNING")
                except Exception as e:
                    log(f"Не удалось сохранить скриншот: {e}", "WARNING")
            
            return {
                'success': success,
                'qr_link': qr_link,
                'time': elapsed,
                'step1_time': step1_time,
                'step2_time': step2_time,
                'error': None if success else 'QR-ссылка не получена',
                'logs': current_payment_logs.copy()
            }
            
        except Exception as e:
            log(f"ИСКЛЮЧЕНИЕ: {e}", "ERROR")
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
        await service.start(headless=True)
        
        results = []
        for i in range(2):
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
            
            if i < 1:
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
