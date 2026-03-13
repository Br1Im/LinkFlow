#!/usr/bin/env python3
"""
Скрипт для проверки статуса BridgeAPI бота на удаленном хосте через SSH
"""

import subprocess
import sys
import os

def run_ssh_command(host, command, user="root"):
    """Выполняет команду на удаленном хосте через SSH"""
    try:
        ssh_command = f"ssh {user}@{host} '{command}'"
        print(f"🔗 Выполняю: {ssh_command}")
        
        result = subprocess.run(
            ssh_command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": "Timeout: команда выполнялась более 30 секунд",
            "returncode": -1
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "returncode": -1
        }

def check_remote_bot_status(host):
    """Проверяет статус бота на удаленном хосте"""
    
    print(f"🚀 ПРОВЕРКА СТАТУСА BRIDGEAPI БОТА НА ХОСТЕ {host}")
    print("=" * 60)
    
    # 1. Проверка подключения
    print("\n1️⃣ Проверка SSH подключения...")
    result = run_ssh_command(host, "echo 'SSH connection OK'")
    
    if not result["success"]:
        print(f"❌ Ошибка подключения: {result['stderr']}")
        print("\n💡 Возможные причины:")
        print("   • SSH ключ не настроен")
        print("   • Хост недоступен")
        print("   • Неверные учетные данные")
        print(f"\n🔧 Попробуйте подключиться вручную:")
        print(f"   ssh root@{host}")
        return False
    
    print(f"✅ SSH подключение успешно: {result['stdout']}")
    
    # 2. Проверка процессов Python
    print("\n2️⃣ Проверка процессов Python...")
    result = run_ssh_command(host, "ps aux | grep python | grep -v grep")
    
    if result["success"] and result["stdout"]:
        print("✅ Найдены процессы Python:")
        for line in result["stdout"].split('\n'):
            if 'python' in line.lower():
                print(f"   📋 {line}")
    else:
        print("❌ Процессы Python не найдены")
    
    # 3. Проверка процессов бота
    print("\n3️⃣ Проверка процессов бота...")
    bot_processes = [
        "ps aux | grep 'run.py' | grep -v grep",
        "ps aux | grep 'BridgeAPI' | grep -v grep",
        "ps aux | grep 'bot' | grep python | grep -v grep"
    ]
    
    bot_found = False
    for cmd in bot_processes:
        result = run_ssh_command(host, cmd)
        if result["success"] and result["stdout"]:
            print(f"✅ Найден процесс бота:")
            for line in result["stdout"].split('\n'):
                print(f"   🤖 {line}")
            bot_found = True
            break
    
    if not bot_found:
        print("❌ Процессы бота не найдены")
    
    # 4. Проверка директории проекта
    print("\n4️⃣ Проверка директории проекта...")
    project_paths = [
        "/root/LinkFlow",
        "/home/LinkFlow", 
        "/opt/LinkFlow",
        "~/LinkFlow"
    ]
    
    project_found = False
    for path in project_paths:
        result = run_ssh_command(host, f"ls -la {path} 2>/dev/null")
        if result["success"] and result["stdout"]:
            print(f"✅ Найдена директория проекта: {path}")
            print("📁 Содержимое:")
            for line in result["stdout"].split('\n')[:10]:  # Первые 10 строк
                print(f"   {line}")
            project_found = True
            project_path = path
            break
    
    if not project_found:
        print("❌ Директория проекта не найдена")
        print("🔍 Поиск по всей системе...")
        result = run_ssh_command(host, "find / -name 'LinkFlow' -type d 2>/dev/null | head -5")
        if result["success"] and result["stdout"]:
            print("📍 Найдены возможные пути:")
            for line in result["stdout"].split('\n'):
                print(f"   📂 {line}")
        return False
    
    # 5. Проверка файлов бота
    print("\n5️⃣ Проверка файлов BridgeAPI бота...")
    bot_path = f"{project_path}/bots/BridgeAPI_Bot"
    result = run_ssh_command(host, f"ls -la {bot_path}")
    
    if result["success"]:
        print(f"✅ Директория бота найдена: {bot_path}")
        print("📋 Файлы бота:")
        for line in result["stdout"].split('\n'):
            if any(file in line for file in ['run.py', 'handlers.py', 'config.py', '.env']):
                print(f"   📄 {line}")
    else:
        print(f"❌ Директория бота не найдена: {bot_path}")
    
    # 6. Проверка логов
    print("\n6️⃣ Проверка логов...")
    log_files = [
        f"{bot_path}/bot.log",
        f"{bot_path}/bot_error.log",
        "/var/log/bridgeapi_bot.log"
    ]
    
    for log_file in log_files:
        result = run_ssh_command(host, f"tail -10 {log_file} 2>/dev/null")
        if result["success"] and result["stdout"]:
            print(f"✅ Найден лог: {log_file}")
            print("📋 Последние 10 строк:")
            for line in result["stdout"].split('\n'):
                print(f"   {line}")
            break
    else:
        print("❌ Логи не найдены")
    
    # 7. Проверка портов
    print("\n7️⃣ Проверка открытых портов...")
    result = run_ssh_command(host, "netstat -tlnp | grep python")
    
    if result["success"] and result["stdout"]:
        print("✅ Python процессы слушают порты:")
        for line in result["stdout"].split('\n'):
            print(f"   🔌 {line}")
    else:
        print("❌ Python процессы не слушают порты")
    
    # 8. Системная информация
    print("\n8️⃣ Системная информация...")
    
    # Проверка системы
    result = run_ssh_command(host, "uname -a")
    if result["success"]:
        print(f"🖥️ Система: {result['stdout']}")
    
    # Проверка Python
    result = run_ssh_command(host, "python3 --version")
    if result["success"]:
        print(f"🐍 Python: {result['stdout']}")
    
    # Проверка нагрузки
    result = run_ssh_command(host, "uptime")
    if result["success"]:
        print(f"⚡ Нагрузка: {result['stdout']}")
    
    # Проверка памяти
    result = run_ssh_command(host, "free -h")
    if result["success"]:
        print(f"💾 Память:")
        for line in result['stdout'].split('\n'):
            print(f"   {line}")
    
    print("\n" + "=" * 60)
    print("✅ Проверка завершена!")
    
    return True

def main():
    """Главная функция"""
    host = "85.192.56.74"
    
    print("🔍 УДАЛЕННАЯ ПРОВЕРКА СТАТУСА BRIDGEAPI БОТА")
    print(f"🌐 Хост: {host}")
    print("👤 Пользователь: root")
    print()
    
    success = check_remote_bot_status(host)
    
    if success:
        print("\n💡 КОМАНДЫ ДЛЯ РУЧНОГО УПРАВЛЕНИЯ:")
        print(f"   ssh root@{host}")
        print("   cd /root/LinkFlow/bots/BridgeAPI_Bot")
        print("   python3 run.py")
        print("   # или")
        print("   nohup python3 run.py > bot.log 2>&1 &")
        print("   # для остановки:")
        print("   pkill -f 'python.*run.py'")
    
    return 0 if success else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n⏹️ Проверка прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        sys.exit(1)