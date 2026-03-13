#!/usr/bin/env python3
"""
Скрипт для развертывания Axis Bot и Very Important Bot на удаленном сервере
"""

import subprocess
import os
import sys
from pathlib import Path

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
            timeout=120
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

def deploy_bot(bot_name, bot_path, remote_path, host):
    """Развертывает конкретного бота"""
    
    print(f"\n🤖 РАЗВЕРТЫВАНИЕ {bot_name.upper()}")
    print("=" * 50)
    
    # Проверяем наличие локальных файлов
    required_files = [
        "run.py", "handlers.py", "config.py", "db.py", 
        "keyboards.py", "requirements.txt", ".env"
    ]
    
    print(f"\n1️⃣ Проверка локальных файлов {bot_name}...")
    missing_files = []
    for file in required_files:
        file_path = os.path.join(bot_path, file)
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
    print(f"\n2️⃣ Создание директории на сервере...")
    if not run_command(
        f'ssh root@{host} "mkdir -p {remote_path}"',
        f"Создание директории {remote_path}"
    ):
        return False
    
    # Копируем файлы
    print(f"\n3️⃣ Копирование файлов {bot_name}...")
    
    files_to_copy = [
        "run.py", "handlers.py", "config.py", "db.py", "keyboards.py",
        "requirements.txt", ".env"
    ]
    
    success_count = 0
    for file in files_to_copy:
        local_file = os.path.join(bot_path, file)
        if os.path.exists(local_file):
            if run_command(
                f'scp "{local_file}" root@{host}:{remote_path}/{file}',
                f"Копирование {file}"
            ):
                success_count += 1
        else:
            print(f"   ⚠️ Файл {file} не найден локально, пропускаем")
    
    print(f"\n📊 Скопировано файлов: {success_count}/{len(files_to_copy)}")
    
    # Установка зависимостей
    print(f"\n4️⃣ Установка зависимостей для {bot_name}...")
    run_command(
        f'ssh root@{host} "cd {remote_path} && pip3 install -r requirements.txt"',
        f"Установка Python зависимостей для {bot_name}"
    )
    
    # Проверка файлов на сервере
    print(f"\n5️⃣ Проверка файлов {bot_name} на сервере...")
    run_command(
        f'ssh root@{host} "ls -la {remote_path}"',
        f"Список файлов {bot_name} на сервере"
    )
    
    return True

def start_bot_on_server(bot_name, remote_path, host):
    """Запускает бота на сервере"""
    
    print(f"\n🚀 ЗАПУСК {bot_name.upper()} НА СЕРВЕРЕ")
    print("=" * 40)
    
    # Останавливаем существующий процесс
    print(f"1️⃣ Остановка существующего процесса {bot_name}...")
    run_command(
        f'ssh root@{host} "pkill -f \'{remote_path}/run.py\'"',
        f"Остановка {bot_name}"
    )
    
    # Запускаем бота в фоне
    print(f"2️⃣ Запуск {bot_name} в фоне...")
    run_command(
        f'ssh root@{host} "cd {remote_path} && nohup python3 run.py > bot.log 2>&1 &"',
        f"Запуск {bot_name}"
    )
    
    # Проверяем запуск
    print(f"3️⃣ Проверка запуска {bot_name}...")
    run_command(
        f'ssh root@{host} "sleep 3 && ps aux | grep \'{remote_path}/run.py\' | grep -v grep"',
        f"Проверка процесса {bot_name}"
    )
    
    # Показываем логи
    print(f"4️⃣ Первые строки лога {bot_name}...")
    run_command(
        f'ssh root@{host} "cd {remote_path} && head -20 bot.log"',
        f"Логи {bot_name}"
    )

def main():
    """Главная функция"""
    
    host = "85.192.56.74"
    
    bots_config = [
        {
            "name": "Axis Bot",
            "local_path": "bots/Axis_Bot",
            "remote_path": "/root/LinkFlow/bots/Axis_Bot"
        },
        {
            "name": "Very Important Bot", 
            "local_path": "bots/Very_Important_Bot",
            "remote_path": "/root/LinkFlow/bots/Very_Important_Bot"
        }
    ]
    
    print(f"🚀 РАЗВЕРТЫВАНИЕ БОТОВ НА СЕРВЕРЕ {host}")
    print("=" * 60)
    
    # Проверяем подключение к серверу
    print("\n🔍 Проверка подключения к серверу...")
    if not run_command(
        f'ssh root@{host} "echo \'Подключение успешно\'"',
        "Проверка SSH подключения"
    ):
        print("❌ Не удается подключиться к серверу")
        return False
    
    # Создаем основную директорию
    print("\n📁 Создание основной директории...")
    run_command(
        f'ssh root@{host} "mkdir -p /root/LinkFlow/bots"',
        "Создание /root/LinkFlow/bots"
    )
    
    # Развертываем каждого бота
    deployed_bots = []
    
    for bot_config in bots_config:
        success = deploy_bot(
            bot_config["name"],
            bot_config["local_path"], 
            bot_config["remote_path"],
            host
        )
        
        if success:
            deployed_bots.append(bot_config)
            print(f"✅ {bot_config['name']} развернут успешно")
        else:
            print(f"❌ Ошибка развертывания {bot_config['name']}")
    
    # Запускаем развернутых ботов
    print(f"\n🚀 ЗАПУСК РАЗВЕРНУТЫХ БОТОВ ({len(deployed_bots)})")
    print("=" * 60)
    
    for bot_config in deployed_bots:
        start_bot_on_server(
            bot_config["name"],
            bot_config["remote_path"],
            host
        )
    
    # Итоговая информация
    print("\n" + "=" * 60)
    print("✅ РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО")
    print("=" * 60)
    
    print(f"\n📊 СТАТИСТИКА:")
    print(f"• Всего ботов: {len(bots_config)}")
    print(f"• Развернуто: {len(deployed_bots)}")
    print(f"• Сервер: {host}")
    
    print(f"\n🤖 РАЗВЕРНУТЫЕ БОТЫ:")
    for bot_config in deployed_bots:
        print(f"• {bot_config['name']}: {bot_config['remote_path']}")
    
    print(f"\n💡 КОМАНДЫ ДЛЯ УПРАВЛЕНИЯ:")
    print(f"• Подключение: ssh root@{host}")
    print("• Проверка процессов: ps aux | grep python")
    print("• Остановка всех ботов: pkill -f 'python.*run.py'")
    
    for bot_config in deployed_bots:
        bot_dir = bot_config['remote_path'].split('/')[-1]
        print(f"• Логи {bot_config['name']}: tail -f /root/LinkFlow/bots/{bot_dir}/bot.log")
    
    print(f"\n🔧 СЛЕДУЮЩИЕ ШАГИ:")
    print("1. Проверьте логи ботов на наличие ошибок")
    print("2. Убедитесь что все токены в .env файлах корректны")
    print("3. Протестируйте ботов отправив /start")
    
    return len(deployed_bots) == len(bots_config)

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Развертывание прервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        sys.exit(1)