#!/usr/bin/env python3
"""
Проверка текущего состояния BridgeAPI_Bot на хосте
"""

import subprocess
import sys
from pathlib import Path
import json

def run_command(command, cwd=None):
    """Выполнить команду и вернуть результат"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True, 
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_bot_process():
    """Проверить процесс бота"""
    print("🔍 Проверка процесса бота...")
    
    success, stdout, stderr = run_command("pgrep -f 'python.*run.py'")
    
    if success and stdout.strip():
        pids = stdout.strip().split('\n')
        print(f"✅ Найдено процессов: {len(pids)}")
        for pid in pids:
            # Получаем детали процесса
            success2, stdout2, stderr2 = run_command(f"ps -p {pid} -o pid,ppid,cmd --no-headers")
            if success2:
                print(f"   PID {pid}: {stdout2.strip()}")
        return True
    else:
        print("❌ Процесс бота не найден")
        return False

def check_bot_files():
    """Проверить файлы бота"""
    print("\n📁 Проверка файлов бота...")
    
    bot_path = Path("bots/BridgeAPI_Bot")
    
    if not bot_path.exists():
        print("❌ Директория бота не найдена")
        return False
    
    # Основные файлы
    required_files = [
        "run.py",
        "handlers.py", 
        "config.py",
        "db.py",
        "keyboards.py",
        "sbp_payment.py",
        ".env",
        "requirements.txt"
    ]
    
    # Новые файлы
    new_files = [
        "ai_service.py",
        "ai_handlers.py",
        "admin_handlers.py"
    ]
    
    print("📋 Основные файлы:")
    for file_name in required_files:
        file_path = bot_path / file_name
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"   ✅ {file_name} ({size} байт)")
        else:
            print(f"   ❌ {file_name} - отсутствует")
    
    print("\n📋 Новые файлы (AI и админка):")
    new_files_count = 0
    for file_name in new_files:
        file_path = bot_path / file_name
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"   ✅ {file_name} ({size} байт)")
            new_files_count += 1
        else:
            print(f"   ❌ {file_name} - отсутствует")
    
    print(f"\n📊 Новых файлов найдено: {new_files_count}/{len(new_files)}")
    return new_files_count > 0

def check_config():
    """Проверить конфигурацию"""
    print("\n⚙️ Проверка конфигурации...")
    
    bot_path = Path("bots/BridgeAPI_Bot")
    env_file = bot_path / ".env"
    
    if not env_file.exists():
        print("❌ .env файл не найден")
        return False
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем ключевые параметры
        checks = [
            ("API_TOKEN", "Telegram Bot Token"),
            ("SBP_SHOP_ID", "SBP Shop ID"),
            ("SBP_SECRET_KEY", "SBP Secret Key"),
            ("PROXYAPI_KEY", "ProxyAPI Key (новый)"),
            ("ADMIN_IDS", "Admin IDs (новый)")
        ]
        
        for param, description in checks:
            if param in content:
                # Извлекаем значение
                lines = content.split('\n')
                for line in lines:
                    if line.startswith(f"{param}="):
                        value = line.split('=', 1)[1]
                        if value and value != "your_value_here":
                            print(f"   ✅ {param}: {description}")
                        else:
                            print(f"   ⚠️ {param}: не настроен")
                        break
            else:
                print(f"   ❌ {param}: отсутствует")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка чтения .env: {e}")
        return False

def check_database():
    """Проверить базу данных"""
    print("\n🗄️ Проверка базы данных...")
    
    bot_path = Path("bots/BridgeAPI_Bot")
    db_file = bot_path / "bridgeapi_bot.db"
    
    if db_file.exists():
        size = db_file.stat().st_size
        print(f"✅ База данных найдена ({size} байт)")
        
        # Попытка подключения к БД
        try:
            import sqlite3
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Проверяем таблицы
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            print(f"📋 Таблиц в БД: {len(tables)}")
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                print(f"   • {table[0]}: {count} записей")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"⚠️ Ошибка подключения к БД: {e}")
            return False
    else:
        print("❌ База данных не найдена")
        return False

def check_logs():
    """Проверить логи"""
    print("\n📋 Проверка логов...")
    
    bot_path = Path("bots/BridgeAPI_Bot")
    log_file = bot_path / "bot.log"
    
    if log_file.exists():
        size = log_file.stat().st_size
        print(f"✅ Лог файл найден ({size} байт)")
        
        # Показываем последние строки
        success, stdout, stderr = run_command(f"tail -10 {log_file}")
        if success:
            print("📄 Последние 10 строк лога:")
            for i, line in enumerate(stdout.strip().split('\n'), 1):
                print(f"   {i:2d}. {line}")
        
        return True
    else:
        print("⚠️ Лог файл не найден")
        return False

def check_dependencies():
    """Проверить зависимости"""
    print("\n📦 Проверка зависимостей...")
    
    bot_path = Path("bots/BridgeAPI_Bot")
    
    # Проверяем основные пакеты
    packages = [
        "aiogram",
        "aiosqlite", 
        "requests",
        "aiohttp"  # Новая зависимость
    ]
    
    for package in packages:
        success, stdout, stderr = run_command(f"python -c 'import {package}; print({package}.__version__)'", cwd=bot_path)
        if success:
            version = stdout.strip()
            print(f"   ✅ {package}: {version}")
        else:
            print(f"   ❌ {package}: не установлен")

def main():
    print("🔍 ПРОВЕРКА СОСТОЯНИЯ BRIDGEAPI_BOT")
    print("=" * 50)
    
    checks = [
        ("Процесс бота", check_bot_process),
        ("Файлы бота", check_bot_files),
        ("Конфигурация", check_config),
        ("База данных", check_database),
        ("Логи", check_logs),
        ("Зависимости", check_dependencies)
    ]
    
    results = []
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"💥 Ошибка в {check_name}: {e}")
            results.append((check_name, False))
    
    print("\n" + "=" * 50)
    print("📊 ИТОГИ ПРОВЕРКИ")
    print("=" * 50)
    
    success_count = sum(1 for _, result in results if result)
    
    for check_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
    
    print(f"\n📈 Успешно: {success_count}/{len(results)}")
    
    if success_count == len(results):
        print("\n🎉 ВСЕ ПРОВЕРКИ ПРОШЛИ!")
        print("✅ Бот готов к работе")
    elif success_count >= len(results) * 0.7:
        print("\n⚠️ ЧАСТИЧНАЯ ГОТОВНОСТЬ")
        print("🔧 Требуются небольшие исправления")
    else:
        print("\n❌ ТРЕБУЕТСЯ ОБНОВЛЕНИЕ")
        print("🔧 Запустите update_bridgeapi_bot.py")
    
    # Рекомендации
    print("\n💡 РЕКОМЕНДАЦИИ:")
    
    if not any(result for name, result in results if "Новые файлы" in name):
        print("• Обновите бота для получения AI-функций и админки")
    
    if not any(result for name, result in results if "Процесс" in name):
        print("• Запустите бота: cd bots/BridgeAPI_Bot && python run.py")
    
    print("• Проверьте настройки в .env файле")
    print("• Убедитесь что все зависимости установлены")

if __name__ == "__main__":
    main()