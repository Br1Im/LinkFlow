#!/usr/bin/env python3
"""
Скрипт для обновления системы восстановления браузера
"""

import subprocess
import time

def update_admin_panel():
    """Обновляет admin_panel.py с улучшенным восстановлением браузера"""
    
    # Читаем текущий файл
    with open('/app/bot/admin_panel.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Заменяем функцию восстановления браузера при таймауте
    old_recovery = '''            # Проверяем статус браузера
            try:
                from payment_service_ultra import is_browser_ready, get_pool_status
                browser_status = get_pool_status()
                logger.error(f"🔍 Статус браузера: {browser_status}")
            except Exception as e:
                logger.error(f"❌ Ошибка проверки браузера: {e}")
            
            return jsonify({
                "success": False,
                "error": "Request timeout",
                "message": "Payment processing took too long (120s). System may be overloaded or browser needs restart.",
                "queuePosition": payment_queue.qsize(),
                "recommendation": "Try again in a few minutes or contact administrator"
            }), 408'''
    
    new_recovery = '''            # Проверяем статус браузера и принудительно перезапускаем при таймауте
            try:
                from payment_service_ultra import is_browser_ready, get_pool_status, initialize_warmed_browser
                browser_status = get_pool_status()
                logger.error(f"🔍 Статус браузера: {browser_status}")
                
                # КРИТИЧНО: При таймауте принудительно убиваем все процессы Chrome и перезапускаем браузер
                logger.error("🔄 ПРИНУДИТЕЛЬНОЕ УБИЙСТВО CHROME ПРОЦЕССОВ...")
                try:
                    import subprocess
                    # Убиваем все процессы Chrome/Chromium
                    subprocess.run(['pkill', '-9', '-f', 'chrome'], capture_output=True, timeout=10)
                    subprocess.run(['pkill', '-9', '-f', 'chromium'], capture_output=True, timeout=10)
                    subprocess.run(['pkill', '-9', '-f', 'chromedriver'], capture_output=True, timeout=10)
                    logger.error("✅ Chrome процессы убиты")
                    
                    # Ждем немного для полной очистки
                    import time
                    time.sleep(3)
                    
                    # Очищаем временные файлы Chrome
                    subprocess.run(['rm', '-rf', '/tmp/.com.google.Chrome.*'], capture_output=True, timeout=5)
                    subprocess.run(['rm', '-rf', '/tmp/chrome_*'], capture_output=True, timeout=5)
                    logger.error("✅ Временные файлы Chrome очищены")
                    
                except Exception as kill_error:
                    logger.error(f"⚠️ Ошибка убийства процессов: {kill_error}")
                
                logger.error("🔄 ПРИНУДИТЕЛЬНЫЙ ПЕРЕЗАПУСК БРАУЗЕРА после таймаута...")
                recovery_success = initialize_warmed_browser()
                if recovery_success:
                    logger.error("✅ Браузер принудительно перезапущен после таймаута")
                else:
                    logger.error("❌ Не удалось перезапустить браузер после таймаута")
                    
            except Exception as e:
                logger.error(f"❌ Ошибка восстановления браузера после таймаута: {e}")
            
            return jsonify({
                "success": False,
                "error": "Request timeout",
                "message": "Payment processing took too long (120s). Browser has been restarted automatically.",
                "queuePosition": payment_queue.qsize(),
                "recommendation": "Browser restarted - try again in 30 seconds"
            }), 408'''
    
    # Заменяем в файле
    if old_recovery in content:
        content = content.replace(old_recovery, new_recovery)
        print("✅ Обновлена функция восстановления браузера при таймауте")
    else:
        print("⚠️ Старая функция восстановления не найдена")
    
    # Добавляем новый API endpoint для перезапуска браузера
    api_endpoint = '''
@app.route('/api/browser/restart', methods=['POST'])
def restart_browser():
    """API для принудительного перезапуска браузера"""
    try:
        logger.info("🔄 Получен запрос на принудительный перезапуск браузера")
        
        # Принудительно убиваем все процессы Chrome
        try:
            import subprocess
            subprocess.run(['pkill', '-9', '-f', 'chrome'], capture_output=True, timeout=10)
            subprocess.run(['pkill', '-9', '-f', 'chromium'], capture_output=True, timeout=10)
            subprocess.run(['pkill', '-9', '-f', 'chromedriver'], capture_output=True, timeout=10)
            
            # Очищаем временные файлы
            subprocess.run(['rm', '-rf', '/tmp/.com.google.Chrome.*'], capture_output=True, timeout=5)
            subprocess.run(['rm', '-rf', '/tmp/chrome_*'], capture_output=True, timeout=5)
            
            import time
            time.sleep(3)
            logger.info("✅ Chrome процессы убиты и файлы очищены")
        except Exception as kill_error:
            logger.error(f"⚠️ Ошибка убийства процессов: {kill_error}")
        
        # Перезапускаем браузер
        from payment_service_ultra import initialize_warmed_browser
        success = initialize_warmed_browser()
        
        if success:
            logger.info("✅ Браузер успешно перезапущен")
            return jsonify({
                "success": True,
                "message": "Browser restarted successfully"
            })
        else:
            logger.error("❌ Не удалось перезапустить браузер")
            return jsonify({
                "success": False,
                "error": "Failed to restart browser"
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Ошибка перезапуска браузера: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

'''
    
    # Добавляем новый endpoint перед функцией start_admin_panel
    if '@app.route(\'/api/browser/restart\'' not in content:
        # Ищем место для вставки (перед def start_admin_panel)
        insert_pos = content.find('def start_admin_panel(')
        if insert_pos != -1:
            content = content[:insert_pos] + api_endpoint + '\n' + content[insert_pos:]
            print("✅ Добавлен API endpoint для перезапуска браузера")
        else:
            print("⚠️ Не найдено место для вставки API endpoint")
    else:
        print("ℹ️ API endpoint для перезапуска уже существует")
    
    # Сохраняем обновленный файл
    with open('/app/bot/admin_panel.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Файл admin_panel.py обновлен")

if __name__ == '__main__':
    print("🔧 Обновление системы восстановления браузера...")
    update_admin_panel()
    print("✅ Обновление завершено")