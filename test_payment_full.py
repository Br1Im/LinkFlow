#!/usr/bin/env python3
"""
Полноценный тест генерации платежей
Тестирует весь процесс создания платежа от начала до конца
"""
import requests
import json
import time
import sys
from datetime import datetime

# Конфигурация
API_URL = "http://localhost:5001"
API_TOKEN = "-3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo"

# Цвета для вывода
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Печать заголовка"""
    print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text:^60}{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*60}{Colors.RESET}\n")

def print_success(text):
    """Печать успеха"""
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text):
    """Печать ошибки"""
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_info(text):
    """Печать информации"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")

def print_warning(text):
    """Печать предупреждения"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def check_api_health():
    """Проверка доступности API"""
    print_info("Проверка доступности API...")
    
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"API доступен: {data.get('service', 'Unknown')}")
            print_info(f"Режим работы: {data.get('mode', 'unknown')}")
            
            if data.get('mode') == 'playwright':
                browser_ready = data.get('browser_ready', False)
                if browser_ready:
                    print_success("Браузер готов к работе")
                else:
                    print_warning("Браузер еще не готов (прогревается)")
            
            return True, data.get('mode', 'unknown')
        else:
            print_error(f"API вернул код {response.status_code}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print_error("Не удается подключиться к API")
        print_info("Убедитесь, что сервер запущен:")
        print_info("  - Локально: python start_admin.py")
        print_info("  - Docker: docker-compose up")
        return False, None
    except Exception as e:
        print_error(f"Ошибка при проверке API: {e}")
        return False, None

def create_test_payment(amount, order_id):
    """Создание тестового платежа"""
    print_info(f"Создание платежа: {amount}₽, заказ {order_id}")
    
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'amount': amount,
        'orderId': order_id
    }
    
    print_info(f"Отправка запроса на {API_URL}/api/payment...")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{API_URL}/api/payment",
            json=payload,
            headers=headers,
            timeout=180  # 3 минуты таймаут
        )
        
        elapsed_time = time.time() - start_time
        
        print_info(f"Получен ответ за {elapsed_time:.2f} секунд")
        print_info(f"HTTP статус: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print_success("Платеж создан успешно!")
            
            print(f"\n{Colors.BOLD}Детали платежа:{Colors.RESET}")
            print(f"  Order ID: {data.get('order_id')}")
            print(f"  Сумма: {data.get('amount')}₽")
            print(f"  Статус: {data.get('status')}")
            print(f"  QR-ссылка: {data.get('qr_link', 'N/A')}")
            print(f"  Время генерации: {data.get('payment_time', 'N/A')}с")
            
            if data.get('step1_time'):
                print(f"  Шаг 1 (заполнение): {data.get('step1_time')}с")
            if data.get('step2_time'):
                print(f"  Шаг 2 (генерация): {data.get('step2_time')}с")
            if data.get('total_time'):
                print(f"  Полное время: {data.get('total_time')}с")
            
            return True, data
            
        elif response.status_code == 409:
            data = response.json()
            print_warning("Платеж уже генерируется")
            print_info(f"Текущий заказ: {data.get('current_order')}")
            print_info(f"Прошло времени: {data.get('elapsed_time')}с")
            return False, data
            
        else:
            data = response.json() if response.text else {}
            print_error(f"Ошибка создания платежа: {data.get('error', 'Unknown error')}")
            
            if data.get('payment_time'):
                print_info(f"Время до ошибки: {data.get('payment_time')}с")
            
            return False, data
            
    except requests.exceptions.Timeout:
        print_error("Таймаут запроса (>180 секунд)")
        print_warning("Возможно, браузер завис или процесс слишком долгий")
        return False, None
        
    except requests.exceptions.ConnectionError:
        print_error("Потеряно соединение с API")
        return False, None
        
    except Exception as e:
        print_error(f"Неожиданная ошибка: {e}")
        return False, None

def run_full_test():
    """Запуск полного теста"""
    print_header("ПОЛНЫЙ ТЕСТ ГЕНЕРАЦИИ ПЛАТЕЖЕЙ")
    
    # Шаг 1: Проверка API
    print_header("Шаг 1: Проверка API")
    api_ok, mode = check_api_health()
    
    if not api_ok:
        print_error("API недоступен. Тест прерван.")
        return False
    
    # Информация о режиме
    if mode == 'proxy':
        print_warning("API работает в Proxy режиме")
        print_info("Для реальной генерации установите Playwright:")
        print_info("  pip install -r requirements_playwright.txt")
        print_info("  playwright install chromium")
        print()
        
        choice = input("Продолжить тест в Proxy режиме? (y/n): ")
        if choice.lower() != 'y':
            print_info("Тест отменен")
            return False
    
    # Шаг 2: Создание тестового платежа
    print_header("Шаг 2: Создание тестового платежа")
    
    # Генерируем уникальный ID заказа
    timestamp = int(time.time())
    order_id = f"TEST-{timestamp}"
    amount = 1000  # 1000 рублей
    
    print_info(f"Параметры теста:")
    print(f"  Сумма: {amount}₽")
    print(f"  Order ID: {order_id}")
    print()
    
    if mode == 'playwright':
        print_warning("Генерация через Playwright может занять 30-60 секунд")
        print_info("Ожидайте...")
    
    print()
    
    success, result = create_test_payment(amount, order_id)
    
    # Шаг 3: Результаты
    print_header("Шаг 3: Результаты теста")
    
    if success:
        print_success("✅ ТЕСТ ПРОЙДЕН УСПЕШНО!")
        print()
        print(f"{Colors.BOLD}Итоговая статистика:{Colors.RESET}")
        print(f"  Режим: {mode}")
        print(f"  Платеж создан: Да")
        print(f"  QR-ссылка получена: {'Да' if result.get('qr_link') else 'Нет'}")
        
        if result.get('total_time'):
            total_time = result.get('total_time')
            print(f"  Общее время: {total_time:.2f}с")
            
            if total_time < 5:
                print_success("  Скорость: Отлично!")
            elif total_time < 30:
                print_info("  Скорость: Хорошо")
            elif total_time < 60:
                print_warning("  Скорость: Приемлемо")
            else:
                print_warning("  Скорость: Медленно")
        
        return True
    else:
        print_error("❌ ТЕСТ НЕ ПРОЙДЕН")
        print()
        print(f"{Colors.BOLD}Причина:{Colors.RESET}")
        if result:
            print(f"  {result.get('error', 'Unknown error')}")
        else:
            print("  Нет ответа от сервера")
        
        return False

def run_stress_test(count=3):
    """Стресс-тест: несколько платежей подряд"""
    print_header(f"СТРЕСС-ТЕСТ: {count} ПЛАТЕЖЕЙ ПОДРЯД")
    
    results = []
    
    for i in range(count):
        print_header(f"Платеж {i+1}/{count}")
        
        timestamp = int(time.time() * 1000)
        order_id = f"STRESS-{timestamp}-{i+1}"
        amount = 1000 + (i * 100)
        
        success, result = create_test_payment(amount, order_id)
        results.append({
            'success': success,
            'order_id': order_id,
            'amount': amount,
            'time': result.get('total_time') if result else None
        })
        
        if i < count - 1:
            print_info("Ожидание 5 секунд перед следующим платежом...")
            time.sleep(5)
    
    # Итоги стресс-теста
    print_header("ИТОГИ СТРЕСС-ТЕСТА")
    
    successful = sum(1 for r in results if r['success'])
    failed = count - successful
    
    print(f"Всего платежей: {count}")
    print_success(f"Успешных: {successful}")
    if failed > 0:
        print_error(f"Неудачных: {failed}")
    
    avg_time = sum(r['time'] for r in results if r['time']) / len([r for r in results if r['time']]) if any(r['time'] for r in results) else 0
    
    if avg_time > 0:
        print_info(f"Среднее время: {avg_time:.2f}с")
    
    return successful == count

def main():
    """Главная функция"""
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║         ТЕСТИРОВАНИЕ ГЕНЕРАЦИИ ПЛАТЕЖЕЙ LINKFLOW          ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    
    print("\nВыберите тип теста:")
    print("  1. Полный тест (один платеж)")
    print("  2. Стресс-тест (3 платежа подряд)")
    print("  3. Только проверка API")
    print()
    
    choice = input("Ваш выбор (1-3): ").strip()
    
    if choice == '1':
        success = run_full_test()
    elif choice == '2':
        success = run_stress_test(3)
    elif choice == '3':
        api_ok, mode = check_api_health()
        success = api_ok
    else:
        print_error("Неверный выбор")
        return
    
    print()
    print_header("ТЕСТ ЗАВЕРШЕН")
    
    if success:
        print_success("Все тесты пройдены успешно! 🎉")
        sys.exit(0)
    else:
        print_error("Некоторые тесты не пройдены")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Тест прерван пользователем{Colors.RESET}")
        sys.exit(130)
