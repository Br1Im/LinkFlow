#!/usr/bin/env python3
"""
Скрипт для развертывания BridgeAPI бота на удаленном сервере
"""

import subprocess
import os
import sys

def run_command(command, description=""):
    """Выполняет команду и возвращает результат"""
    print(f"🔄 {description}")
    print(f"   Команда: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print(f"✅ {description} - успешно")
            if result.stdout.strip():
                print(f"   Вывод: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - ошибка")
            if result.stderr.strip():
                print(f"   Ошибка: {result.stderr.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - таймаут")
        return False
    except Exception as e:
        print(f"💥 {description} - исключение: {e}")
        return False

def deploy_bridgeapi_bot():
    """Развертывает BridgeAPI бота на сервере"""
    
    host = "85.192.56.74"
    remote_path = "/root/LinkFlow/bots/BridgeAPI_Bot"
    local_path = "bots/BridgeAPI_Bot"
    
    print(f"🚀 РАЗВЕРТЫВАНИЕ BRIDGEAPI БОТА НА СЕРВЕРЕ {host}")
    print("=" * 60)
    
    # Проверяем наличие локальных файлов
    required_files = [
        "run.py", "handlers.py", "config.py", "db.py", 
        "keyboards.py", "ai_service.py", "ai_handlers.py",
        "admin_handlers.py", "sbp_payment.py", "requirements.txt"
    ]
    
    print("\n1️⃣ Проверка локальных файлов...")
    missing_files = []
    for file in required_files:
        file_path = os.path.join(local_path, file)
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   ✅ {file} ({size} байт)")
        else:
            print(f"   ❌ {file} - не найден")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Отсутствуют файлы: {', '.join(missing_files)}")
        return False
    
    # Создаем директорию на сервере
    print("\n2️⃣ Создание директории на сервере...")
    if not run_command(
        f'ssh root@{host} "mkdir -p {remote_path}"',
        "Создание директории"
    ):
        return False
    
    # Копируем файлы
    print("\n3️⃣ Копирование файлов...")
    
    files_to_copy = [
        "run.py", "handlers.py", "config.py", "db.py", "keyboards.py",
        "ai_service.py", "ai_handlers.py", "admin_handlers.py", 
        "sbp_payment.py", "requirements.txt", "common.py"
    ]
    
    success_count = 0
    for file in files_to_copy:
        local_file = os.path.join(local_path, file)
        if os.path.exists(local_file):
            if run_command(
                f'scp "{local_file}" root@{host}:{remote_path}/{file}',
                f"Копирование {file}"
            ):
                success_count += 1
        else:
            print(f"   ⚠️ Файл {file} не найден локально, пропускаем")
    
    print(f"\n📊 Скопировано файлов: {success_count}/{len(files_to_copy)}")
    
    # Копируем .env файл (если есть)
    print("\n4️⃣ Копирование конфигурации...")
    env_file = os.path.join(local_path, ".env")
    if os.path.exists(env_file):
        run_command(
            f'scp "{env_file}" root@{host}:{remote_path}/.env',
            "Копирование .env файла"
        )
    else:
        print("   ⚠️ .env файл не найден, нужно будет создать на сервере")
    
    # Установка зависимостей
    print("\n5️⃣ Установка зависимостей...")
    run_command(
        f'ssh root@{host} "cd {remote_path} && pip3 install -r requirements.txt"',
        "Установка Python зависимостей"
    )
    
    # Проверка файлов на сервере
    print("\n6️⃣ Проверка файлов на сервере...")
    run_command(
        f'ssh root@{host} "ls -la {remote_path}"',
        "Список файлов на сервере"
    )
    
    # Проверка конфигурации
    print("\n7️⃣ Проверка конфигурации...")
    run_command(
        f'ssh root@{host} "cd {remote_path} && python3 --version"',
        "Проверка Python"
    )
    
    print("\n" + "=" * 60)
    print("✅ РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО")
    
    print("\n💡 СЛЕДУЮЩИЕ ШАГИ:")
    print(f"1. Подключитесь к серверу: ssh root@{host}")
    print(f"2. Перейдите в директорию: cd {remote_path}")
    print("3. Настройте .env файл с токенами")
    print("4. Запустите бота: python3 run.py")
    print("5. Или в фоне: nohup python3 run.py > bot.log 2>&1 &")
    
    print("\n🔧 КОМАНДЫ ДЛЯ УПРАВЛЕНИЯ:")
    print("• Проверка процессов: ps aux | grep python")
    print("• Остановка бота: pkill -f 'python.*run.py'")
    print("• Просмотр логов: tail -f bot.log")
    
    return True

def main():
    """Главная функция"""
    try:
        success = deploy_bridgeapi_bot()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⏹️ Развертывание прервано пользователем")
        return 1
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())