#!/usr/bin/env python3
"""
Скрипт для развертывания исправлений админских привилегий в BridgeAPI_Bot
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Выполнить команду и показать результат"""
    print(f"\n🔄 {description}")
    print(f"Команда: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"✅ Успешно: {description}")
            if result.stdout.strip():
                print(f"Вывод: {result.stdout.strip()}")
        else:
            print(f"❌ Ошибка: {description}")
            print(f"Код ошибки: {result.returncode}")
            if result.stderr.strip():
                print(f"Ошибка: {result.stderr.strip()}")
            if result.stdout.strip():
                print(f"Вывод: {result.stdout.strip()}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"⏰ Таймаут: {description}")
        return False
    except Exception as e:
        print(f"💥 Исключение: {e}")
        return False

def main():
    """Основная функция развертывания"""
    
    print("🚀 Развертывание исправлений админских привилегий BridgeAPI_Bot")
    print("=" * 60)
    
    # Файлы для копирования
    files_to_copy = [
        "bots/BridgeAPI_Bot/ai_handlers.py",
        "bots/BridgeAPI_Bot/handlers.py",
        "bots/BridgeAPI_Bot/keyboards.py"
    ]
    
    server = "85.192.56.74"
    remote_path = "/root/BridgeAPI_Bot/"
    
    success_count = 0
    total_operations = len(files_to_copy) + 2  # +2 для перезапуска и проверки
    
    # Копируем файлы
    for file_path in files_to_copy:
        if os.path.exists(file_path):
            filename = os.path.basename(file_path)
            command = f'scp "{file_path}" root@{server}:{remote_path}{filename}'
            
            if run_command(command, f"Копирование {filename}"):
                success_count += 1
        else:
            print(f"❌ Файл не найден: {file_path}")
    
    # Перезапускаем бота
    restart_command = f'ssh root@{server} "cd {remote_path} && pkill -f run.py && nohup python3 run.py > bot.log 2>&1 &"'
    if run_command(restart_command, "Перезапуск бота"):
        success_count += 1
    
    # Проверяем статус
    import time
    time.sleep(3)
    
    check_command = f'ssh root@{server} "cd {remote_path} && ps aux | grep run.py | grep -v grep"'
    if run_command(check_command, "Проверка статуса бота"):
        success_count += 1
    
    # Итоги
    print("\n" + "=" * 60)
    print(f"📊 Результат развертывания: {success_count}/{total_operations} операций успешно")
    
    if success_count == total_operations:
        print("✅ Все исправления успешно развернуты!")
        print("👑 Админские привилегии для ID 7036953540 активированы")
        print("🎨 Все AI-функции теперь бесплатны для админа")
    else:
        print("⚠️ Некоторые операции завершились с ошибками")
    
    print(f"\n🤖 Бот доступен: @Very_iimportant_Bot")
    print(f"🔧 Логи: ssh root@{server} 'cd {remote_path} && tail -f bot.log'")

if __name__ == "__main__":
    main()