#!/usr/bin/env python3
"""
Скрипт для исправления стабильности браузера
Основные проблемы: накопление Chrome процессов, конфликты портов, нестабильность сессий
"""

def update_browser_manager():
    """Обновляет browser_manager.py для большей стабильности"""
    
    with open('/app/bot/browser_manager.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Добавляем более агрессивную очистку процессов в _create_driver
    old_cleanup = '''        # Убиваем все процессы Chrome перед запуском
        try:
            subprocess.run(['pkill', '-f', 'chrome'], capture_output=True, timeout=5)
            subprocess.run(['pkill', '-f', 'chromium'], capture_output=True, timeout=5)
            time.sleep(1)
        except:
            pass'''
    
    new_cleanup = '''        # АГРЕССИВНАЯ очистка всех Chrome процессов перед запуском
        try:
            # Убиваем все процессы Chrome/ChromeDriver принудительно
            subprocess.run(['pkill', '-9', '-f', 'chrome'], capture_output=True, timeout=10)
            subprocess.run(['pkill', '-9', '-f', 'chromium'], capture_output=True, timeout=10)
            subprocess.run(['pkill', '-9', '-f', 'chromedriver'], capture_output=True, timeout=10)
            
            # Очищаем временные файлы и сокеты
            subprocess.run(['rm', '-rf', '/tmp/.com.google.Chrome.*'], capture_output=True, timeout=5)
            subprocess.run(['rm', '-rf', '/tmp/chrome_*'], capture_output=True, timeout=5)
            subprocess.run(['rm', '-rf', '/tmp/.org.chromium.*'], capture_output=True, timeout=5)
            
            # Ждем полной очистки
            time.sleep(2)
            print("🧹 Агрессивная очистка Chrome процессов завершена", flush=True)
        except Exception as e:
            print(f"⚠️ Ошибка очистки процессов: {e}", flush=True)'''
    
    if old_cleanup in content:
        content = content.replace(old_cleanup, new_cleanup)
        print("✅ Обновлена очистка Chrome процессов")
    
    # Добавляем более стабильные опции Chrome
    old_options = '''        # ОТКЛЮЧАЕМ headless - используем виртуальный дисплей Xvfb
        # options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-setuid-sandbox')'''
    
    new_options = '''        # МАКСИМАЛЬНО СТАБИЛЬНЫЕ опции для Docker
        # options.add_argument('--headless=new')  # Отключаем headless - используем Xvfb
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-setuid-sandbox')
        
        # КРИТИЧНО для стабильности в Docker
        options.add_argument('--single-process')  # Один процесс - меньше конфликтов
        options.add_argument('--no-zygote')       # Отключаем zygote процесс
        options.add_argument('--disable-dev-tools')
        options.add_argument('--disable-crash-reporter')
        options.add_argument('--disable-in-process-stack-traces')
        options.add_argument('--disable-logging')
        options.add_argument('--log-level=3')     # Минимум логов
        options.add_argument('--silent')
        
        # Память и производительность
        options.add_argument('--memory-pressure-off')
        options.add_argument('--max_old_space_size=2048')  # Ограничиваем память
        options.add_argument('--aggressive-cache-discard')'''
    
    if old_options in content:
        content = content.replace(old_options, new_options)
        print("✅ Обновлены опции Chrome для стабильности")
    
    # Добавляем принудительное закрытие браузера в finally блоке create_payment
    finally_block = '''        finally:
            # ВСЕГДА закрываем браузер
            if driver:
                try:
                    driver.quit()
                    print(f"[{time.time()-start_time:.1f}s] Браузер закрыт", flush=True)
                except:
                    pass
                
                # Убиваем процессы Chrome для полной очистки
                try:
                    import subprocess
                    subprocess.run(['pkill', '-f', 'chrome'], capture_output=True, timeout=5)
                    subprocess.run(['pkill', '-f', 'chromium'], capture_output=True, timeout=5)
                except:
                    pass'''
    
    new_finally_block = '''        finally:
            # АГРЕССИВНОЕ закрытие браузера и очистка процессов
            if driver:
                try:
                    # Сначала пытаемся закрыть нормально
                    driver.quit()
                    print(f"[{time.time()-start_time:.1f}s] Браузер закрыт", flush=True)
                except Exception as e:
                    print(f"[{time.time()-start_time:.1f}s] Ошибка закрытия браузера: {e}", flush=True)
                
                # ПРИНУДИТЕЛЬНО убиваем все процессы Chrome
                try:
                    import subprocess
                    subprocess.run(['pkill', '-9', '-f', 'chrome'], capture_output=True, timeout=10)
                    subprocess.run(['pkill', '-9', '-f', 'chromium'], capture_output=True, timeout=10)
                    subprocess.run(['pkill', '-9', '-f', 'chromedriver'], capture_output=True, timeout=10)
                    
                    # Очищаем временные файлы
                    subprocess.run(['rm', '-rf', '/tmp/.com.google.Chrome.*'], capture_output=True, timeout=5)
                    subprocess.run(['rm', '-rf', '/tmp/chrome_*'], capture_output=True, timeout=5)
                    
                    print(f"[{time.time()-start_time:.1f}s] Chrome процессы принудительно убиты", flush=True)
                except Exception as cleanup_error:
                    print(f"[{time.time()-start_time:.1f}s] Ошибка очистки: {cleanup_error}", flush=True)'''
    
    if finally_block in content:
        content = content.replace(finally_block, new_finally_block)
        print("✅ Обновлен блок очистки браузера")
    
    # Сохраняем файл
    with open('/app/bot/browser_manager.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ browser_manager.py обновлен для стабильности")

def update_admin_panel_timeout():
    """Обновляет таймауты в admin_panel.py"""
    
    with open('/app/bot/admin_panel.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Обновляем таймаут с 120 до 30 секунд
    content = content.replace('timeout=120', 'timeout=30')
    content = content.replace('(120s)', '(30s)')
    content = content.replace('(120 секунд)', '(30 секунд)')
    
    with open('/app/bot/admin_panel.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Таймауты обновлены до 30 секунд")

if __name__ == '__main__':
    print("🔧 Исправление стабильности браузера...")
    update_browser_manager()
    update_admin_panel_timeout()
    print("✅ Исправления применены")