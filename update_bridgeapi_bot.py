#!/usr/bin/env python3
"""
Скрипт обновления BridgeAPI_Bot на хосте со всеми новыми функциями
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def run_command(command, cwd=None):
    """Выполнить команду и вернуть результат"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True, 
            timeout=60
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"
    except Exception as e:
        return False, "", str(e)

def backup_current_bot():
    """Создать бэкап текущего бота"""
    print("📦 Создание бэкапа текущего бота...")
    
    bot_path = Path("bots/BridgeAPI_Bot")
    backup_path = Path("bots/BridgeAPI_Bot_backup")
    
    if bot_path.exists():
        if backup_path.exists():
            shutil.rmtree(backup_path)
        shutil.copytree(bot_path, backup_path)
        print(f"✅ Бэкап создан: {backup_path}")
        return True
    else:
        print("⚠️ Текущий бот не найден, пропускаем бэкап")
        return False

def stop_current_bot():
    """Остановить текущий процесс бота"""
    print("🛑 Остановка текущего бота...")
    
    # Попытка найти и остановить процесс
    success, stdout, stderr = run_command("pkill -f 'python.*run.py'")
    
    if success:
        print("✅ Бот остановлен")
    else:
        print("⚠️ Процесс бота не найден или уже остановлен")
    
    return True

def update_bot_files():
    """Обновить файлы бота"""
    print("📁 Обновление файлов бота...")
    
    bot_path = Path("bots/BridgeAPI_Bot")
    
    # Список новых файлов для копирования
    new_files = [
        "ai_service.py",
        "ai_handlers.py", 
        "admin_handlers.py",
        "handlers.py",
        "config.py",
        "keyboards.py",
        "run.py",
        "db.py",
        "requirements.txt"
    ]
    
    updated_files = []
    
    for file_name in new_files:
        src_file = bot_path / file_name
        if src_file.exists():
            print(f"✅ Обновлен: {file_name}")
            updated_files.append(file_name)
        else:
            print(f"⚠️ Не найден: {file_name}")
    
    print(f"📊 Обновлено файлов: {len(updated_files)}")
    return len(updated_files) > 0

def install_dependencies():
    """Установить зависимости"""
    print("📦 Установка зависимостей...")
    
    bot_path = Path("bots/BridgeAPI_Bot")
    requirements_file = bot_path / "requirements.txt"
    
    if requirements_file.exists():
        success, stdout, stderr = run_command(
            "pip install -r requirements.txt", 
            cwd=bot_path
        )
        
        if success:
            print("✅ Зависимости установлены")
            return True
        else:
            print(f"❌ Ошибка установки зависимостей: {stderr}")
            return False
    else:
        print("⚠️ requirements.txt не найден")
        return False

def update_env_file():
    """Обновить .env файл с новыми параметрами"""
    print("⚙️ Обновление конфигурации...")
    
    bot_path = Path("bots/BridgeAPI_Bot")
    env_file = bot_path / ".env"
    
    # Новые параметры для добавления
    new_params = [
        "# ProxyAPI.ru Configuration for AI Services",
        "PROXYAPI_KEY=sk-YEMVoEtElex2mgBoEYe4K79pOBoONUtr",
        "",
        "# Admin IDs (замените на ваш реальный ID)",
        "ADMIN_IDS=123456789"
    ]
    
    if env_file.exists():
        # Читаем существующий файл
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем, есть ли уже новые параметры
        if "PROXYAPI_KEY" not in content:
            # Добавляем новые параметры
            with open(env_file, 'a', encoding='utf-8') as f:
                f.write("\n\n")
                f.write("\n".join(new_params))
            
            print("✅ Конфигурация обновлена")
            print("⚠️ ВАЖНО: Замените ADMIN_IDS на ваш реальный Telegram ID!")
        else:
            print("✅ Конфигурация уже актуальна")
        
        return True
    else:
        print("❌ .env файл не найден")
        return False

def start_bot():
    """Запустить обновленный бот"""
    print("🚀 Запуск обновленного бота...")
    
    bot_path = Path("bots/BridgeAPI_Bot")
    
    # Запускаем бота в фоне
    success, stdout, stderr = run_command(
        "nohup python run.py > bot.log 2>&1 &", 
        cwd=bot_path
    )
    
    if success:
        print("✅ Бот запущен в фоновом режиме")
        print("📋 Логи: bots/BridgeAPI_Bot/bot.log")
        return True
    else:
        print(f"❌ Ошибка запуска: {stderr}")
        return False

def check_bot_status():
    """Проверить статус бота"""
    print("🔍 Проверка статуса бота...")
    
    # Проверяем процесс
    success, stdout, stderr = run_command("pgrep -f 'python.*run.py'")
    
    if success and stdout.strip():
        pid = stdout.strip()
        print(f"✅ Бот работает (PID: {pid})")
        
        # Проверяем логи
        bot_path = Path("bots/BridgeAPI_Bot")
        log_file = bot_path / "bot.log"
        
        if log_file.exists():
            print("📋 Последние строки лога:")
            success, stdout, stderr = run_command(f"tail -5 {log_file}")
            if success:
                print(stdout)
        
        return True
    else:
        print("❌ Бот не запущен")
        return False

def main():
    print("🤖 ОБНОВЛЕНИЕ BRIDGEAPI_BOT НА ХОСТЕ")
    print("=" * 50)
    
    steps = [
        ("Создание бэкапа", backup_current_bot),
        ("Остановка бота", stop_current_bot),
        ("Обновление файлов", update_bot_files),
        ("Установка зависимостей", install_dependencies),
        ("Обновление конфигурации", update_env_file),
        ("Запуск бота", start_bot),
        ("Проверка статуса", check_bot_status)
    ]
    
    success_count = 0
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        try:
            if step_func():
                success_count += 1
                print(f"✅ {step_name} - успешно")
            else:
                print(f"❌ {step_name} - ошибка")
        except Exception as e:
            print(f"💥 {step_name} - исключение: {e}")
    
    print("\n" + "=" * 50)
    print("📊 ИТОГИ ОБНОВЛЕНИЯ")
    print("=" * 50)
    
    if success_count == len(steps):
        print("🎉 ОБНОВЛЕНИЕ ЗАВЕРШЕНО УСПЕШНО!")
        print()
        print("✅ Все новые функции активированы:")
        print("• 💳 Платежная система СБП")
        print("• 🤖 10 AI-инструментов")
        print("• 👑 Админ-панель (/admin)")
        print("• 🎬 Генерация видео")
        print("• 📊 Статистика и аналитика")
        print()
        print("🔧 Что нужно сделать:")
        print("1. Замените ADMIN_IDS в .env на ваш Telegram ID")
        print("2. Протестируйте бота: отправьте /start")
        print("3. Проверьте админку: отправьте /admin")
        print("4. Протестируйте AI-функции")
        
    else:
        print(f"⚠️ ОБНОВЛЕНИЕ ЧАСТИЧНО ЗАВЕРШЕНО ({success_count}/{len(steps)})")
        print()
        print("🔧 Рекомендации:")
        print("• Проверьте логи ошибок выше")
        print("• Убедитесь что все файлы на месте")
        print("• Проверьте права доступа")
        print("• Попробуйте запустить бота вручную")
    
    print(f"\n📁 Бэкап сохранен в: bots/BridgeAPI_Bot_backup")
    print(f"📋 Логи бота: bots/BridgeAPI_Bot/bot.log")

if __name__ == "__main__":
    main()