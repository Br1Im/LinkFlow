#!/usr/bin/env python3
"""
Проверка доступности хоста и альтернативные способы подключения
"""

import subprocess
import socket
import sys
import time

def ping_host(host):
    """Проверка доступности хоста через ping"""
    try:
        # Для Windows используем ping -n, для Linux ping -c
        if sys.platform.startswith('win'):
            cmd = f"ping -n 4 {host}"
        else:
            cmd = f"ping -c 4 {host}"
        
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=15
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": str(e)
        }

def check_port(host, port, timeout=5):
    """Проверка доступности порта"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def traceroute_host(host):
    """Трассировка маршрута до хоста"""
    try:
        if sys.platform.startswith('win'):
            cmd = f"tracert -h 10 {host}"
        else:
            cmd = f"traceroute -m 10 {host}"
        
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": str(e)
        }

def main():
    host = "85.192.56.74"
    
    print(f"🔍 ПРОВЕРКА ДОСТУПНОСТИ ХОСТА {host}")
    print("=" * 50)
    
    # 1. Ping проверка
    print("\n1️⃣ Проверка ping...")
    ping_result = ping_host(host)
    
    if ping_result["success"]:
        print("✅ Хост отвечает на ping")
        print("📊 Результат ping:")
        for line in ping_result["output"].split('\n')[-5:]:
            if line.strip():
                print(f"   {line}")
    else:
        print("❌ Хост не отвечает на ping")
        if ping_result["error"]:
            print(f"   Ошибка: {ping_result['error']}")
    
    # 2. Проверка портов
    print("\n2️⃣ Проверка портов...")
    ports_to_check = [22, 80, 443, 8080, 3000, 5000]
    
    open_ports = []
    for port in ports_to_check:
        print(f"   Проверяю порт {port}...", end=" ")
        if check_port(host, port):
            print("✅ Открыт")
            open_ports.append(port)
        else:
            print("❌ Закрыт")
    
    if open_ports:
        print(f"✅ Открытые порты: {', '.join(map(str, open_ports))}")
    else:
        print("❌ Все проверенные порты закрыты")
    
    # 3. Трассировка
    print("\n3️⃣ Трассировка маршрута...")
    trace_result = traceroute_host(host)
    
    if trace_result["success"]:
        print("✅ Трассировка выполнена:")
        lines = trace_result["output"].split('\n')
        for line in lines[:10]:  # Первые 10 хопов
            if line.strip():
                print(f"   {line}")
    else:
        print("❌ Трассировка не удалась")
        if trace_result["error"]:
            print(f"   Ошибка: {trace_result['error']}")
    
    # 4. DNS проверка
    print("\n4️⃣ DNS проверка...")
    try:
        ip = socket.gethostbyname(host)
        print(f"✅ IP адрес: {ip}")
        
        # Обратный DNS
        try:
            hostname = socket.gethostbyaddr(host)
            print(f"✅ Hostname: {hostname[0]}")
        except:
            print("❌ Обратный DNS не найден")
            
    except Exception as e:
        print(f"❌ DNS ошибка: {e}")
    
    # 5. Альтернативные способы подключения
    print("\n5️⃣ Альтернативные способы подключения...")
    
    print("🔧 Попробуйте следующие команды:")
    print(f"   ssh root@{host}")
    print(f"   ssh -p 2222 root@{host}")  # Альтернативный SSH порт
    print(f"   ssh -o ConnectTimeout=30 root@{host}")
    print(f"   telnet {host} 22")
    
    if 22 not in open_ports:
        print("\n⚠️ SSH порт (22) недоступен. Возможные причины:")
        print("   • SSH сервис не запущен")
        print("   • Firewall блокирует подключения")
        print("   • SSH работает на другом порту")
        print("   • Хост выключен или недоступен")
    
    # 6. Рекомендации
    print("\n6️⃣ Рекомендации...")
    
    if not ping_result["success"]:
        print("❌ Хост недоступен по ping:")
        print("   • Проверьте правильность IP адреса")
        print("   • Убедитесь что хост включен")
        print("   • Проверьте сетевое подключение")
    
    if 22 not in open_ports:
        print("❌ SSH недоступен:")
        print("   • Свяжитесь с администратором сервера")
        print("   • Проверьте настройки firewall")
        print("   • Убедитесь что SSH сервис запущен")
    
    print("\n" + "=" * 50)
    
    if ping_result["success"] and 22 in open_ports:
        print("✅ Хост доступен, SSH порт открыт")
        print("💡 Проблема может быть в аутентификации")
        return 0
    elif ping_result["success"]:
        print("⚠️ Хост доступен, но SSH порт закрыт")
        return 1
    else:
        print("❌ Хост недоступен")
        return 2

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n⏹️ Проверка прервана")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Ошибка: {e}")
        sys.exit(1)