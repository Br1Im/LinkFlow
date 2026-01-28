#!/usr/bin/env python3
"""
Автоматическое заполнение формы через Playwright с замером времени
"""

from playwright.sync_api import sync_playwright
import time
import os

def create_payment(card_number: str, recipient_name: str, amount: float, results_dir: str = "./results"):
    """Создает платеж через браузер"""
    
    start_time = time.time()
    
    print("="*70)
    print(f"🚀 СТАРТ: {time.strftime('%H:%M:%S')}")
    print("="*70)
    print(f"💳 Карта: {card_number}")
    print(f"👤 Получатель: {recipient_name}")
    print(f"💰 Сумма: {amount} RUB")
    print()
    
    with sync_playwright() as p:
        # Запускаем браузер
        browser = p.chromium.launch(
            headless=False,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        page = browser.new_page()
        
        try:
            # 1. Открываем страницу
            step_start = time.time()
            print(f"⏱️  [{time.strftime('%H:%M:%S')}] 1️⃣ Открываю multitransfer.ru...")
            page.goto("https://multitransfer.ru/transfer/uzbekistan")
            page.wait_for_load_state("networkidle")
            time.sleep(1)
            print(f"   ✅ Загружено за {time.time() - step_start:.1f}s")
            print()
            
            # 2. Заполняем сумму
            step_start = time.time()
            print(f"⏱️  [{time.strftime('%H:%M:%S')}] 2️⃣ Ввожу сумму {amount} RUB...")
            amount_input = page.locator('input[type="text"]').first
            amount_input.click()
            amount_input.fill(str(int(amount)))
            time.sleep(0.5)
            print(f"   ✅ Заполнено за {time.time() - step_start:.1f}s")
            print()
            
            # 3. Ждем расчета комиссии
            step_start = time.time()
            print(f"⏱️  [{time.strftime('%H:%M:%S')}] 3️⃣ Жду расчета комиссии...")
            time.sleep(2)  # Даем время на расчет
            print(f"   ✅ Комиссия рассчитана за {time.time() - step_start:.1f}s")
            print()
            
            # 4. Выбираем способ перевода (если нужно)
            step_start = time.time()
            print(f"⏱️  [{time.strftime('%H:%M:%S')}] 4️⃣ Выбираю способ перевода...")
            
            # Ищем кнопку "Способ перевода" по тексту
            transfer_method = page.locator('div:has-text("Способ перевода")').first
            if transfer_method.is_visible():
                transfer_method.click()
                time.sleep(1)
                
                # Выбираем первый доступный способ
                # Можно выбрать конкретный, например "На карту"
                first_option = page.locator('[role="option"]').first
                if first_option.is_visible():
                    first_option.click()
                    time.sleep(0.5)
                
                print(f"   ✅ Способ выбран за {time.time() - step_start:.1f}s")
            else:
                print(f"   ℹ️  Способ перевода уже выбран")
            print()
            
            # 5. Нажимаем "Продолжить"
            step_start = time.time()
            print(f"⏱️  [{time.strftime('%H:%M:%S')}] 5️⃣ Нажимаю 'Продолжить'...")
            continue_button = page.locator('button:has-text("Продолжить")').first
            continue_button.click()
            page.wait_for_load_state("networkidle")
            time.sleep(1)
            print(f"   ✅ Переход за {time.time() - step_start:.1f}s")
            print()
            # 6. Заполняем данные получателя
            step_start = time.time()
            print(f"⏱️  [{time.strftime('%H:%M:%S')}] 6️⃣ Заполняю данные получателя...")
            
            name_parts = recipient_name.split()
            first_name = name_parts[0] if name_parts else "Nodir"
            last_name = name_parts[1] if len(name_parts) > 1 else "Asadullayev"
            
            # Номер карты
            card_input = page.locator('input[placeholder*="карт"]').first
            card_input.click()
            card_input.fill(card_number)
            time.sleep(0.3)
            
            # Имя
            first_name_input = page.locator('input[placeholder*="Имя"]').first
            first_name_input.click()
            first_name_input.fill(first_name)
            time.sleep(0.3)
            
            # Фамилия
            last_name_input = page.locator('input[placeholder*="Фамилия"]').first
            last_name_input.click()
            last_name_input.fill(last_name)
            time.sleep(0.3)
            
            print(f"   ✅ Данные получателя за {time.time() - step_start:.1f}s")
            print()
            
            # 7. Нажимаем "Продолжить"
            step_start = time.time()
            print(f"⏱️  [{time.strftime('%H:%M:%S')}] 7️⃣ Нажимаю 'Продолжить'...")
            continue_button = page.locator('button:has-text("Продолжить")').first
            continue_button.click()
            page.wait_for_load_state("networkidle")
            time.sleep(1)
            print(f"   ✅ Переход за {time.time() - step_start:.1f}s")
            print()
            
            # 8. Заполняем данные отправителя
            step_start = time.time()
            print(f"⏱️  [{time.strftime('%H:%M:%S')}] 8️⃣ Заполняю данные отправителя...")
            
            # Фамилия
            sender_last = page.locator('input[name*="lastName"]').first
            if sender_last.is_visible():
                sender_last.click()
                sender_last.fill("Ivanov")
                time.sleep(0.3)
            
            # Имя
            sender_first = page.locator('input[name*="firstName"]').first
            if sender_first.is_visible():
                sender_first.click()
                sender_first.fill("Dmitry")
                time.sleep(0.3)
            
            # Телефон
            phone_input = page.locator('input[type="tel"]').first
            if phone_input.is_visible():
                phone_input.click()
                phone_input.fill("+79880260334")
                time.sleep(0.3)
            
            # Дата рождения
            birth_input = page.locator('input[type="date"]').first
            if birth_input.is_visible():
                birth_input.click()
                birth_input.fill("2000-07-03")
                time.sleep(0.3)
            
            print(f"   ✅ Данные отправителя за {time.time() - step_start:.1f}s")
            print()
            
            elapsed = time.time() - start_time
            print("="*70)
            print(f"⏸️  ПАУЗА НА КАПЧУ | Прошло: {elapsed:.1f}s")
            print("="*70)
            print("👉 Реши капчу в браузере")
            print("👉 Нажми 'Продолжить'")
            print("👉 Дождись QR-кода")
            print()
            
            captcha_start = time.time()
            input("Нажми Enter когда увидишь QR-код...")
            captcha_time = time.time() - captcha_start
            
            total_time = time.time() - start_time
            
            print()
            print("="*70)
            print(f"⏱️  ИТОГОВОЕ ВРЕМЯ")
            print("="*70)
            print(f"🤖 Автозаполнение: {elapsed:.1f}s")
            print(f"👤 Решение капчи: {captcha_time:.1f}s")
            print(f"⏱️  ВСЕГО: {total_time:.1f}s")
            print("="*70)
            
            # Сохраняем результат
            with open(f'{results_dir}/timing.txt', 'w') as f:
                f.write(f"Auto fill: {elapsed:.1f}s\n")
                f.write(f"Captcha: {captcha_time:.1f}s\n")
                f.write(f"Total: {total_time:.1f}s\n")
            
            print()
            input("Нажми Enter чтобы закрыть браузер...")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            input("Нажми Enter чтобы закрыть браузер...")
        
        finally:
            browser.close()

if __name__ == "__main__":
    # Данные из переменных окружения или дефолтные
    card_number = os.getenv("CARD_NUMBER", "9860080323894719")
    recipient_name = os.getenv("RECIPIENT_NAME", "Nodir Asadullayev")
    amount = float(os.getenv("AMOUNT", "110"))
    
    # Создаем папку для результатов
    results_dir = os.getenv("RESULTS_DIR", "./results")
    os.makedirs(results_dir, exist_ok=True)
    
    create_payment(card_number, recipient_name, amount, results_dir)
