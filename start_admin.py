"""
Локальный запуск админки LinkFlow
Запускает админку на портах 5000 и 5001
"""
import subprocess
import sys
import threading
import time

def run_admin_panel():
    """Запуск админ-панели на порту 5000"""
    subprocess.run([sys.executable, "admin/admin_panel_db.py"])

def run_api_server():
    """Запуск API сервера на порту 5001"""
    # Ждем 2 секунды, чтобы админка запустилась первой
    time.sleep(2)
    subprocess.run([sys.executable, "admin/api_server.py"])

def main():
    print("="*60)
    print("🚀 Запуск LinkFlow Admin Panel")
    print("="*60)
    print("Админка будет доступна на:")
    print("  📊 Admin Panel: http://localhost:5000")
    print("  🔌 API Server:  http://localhost:5001")
    print("="*60)
    print("\nДля остановки нажмите Ctrl+C\n")
    
    try:
        # Запускаем оба сервера в отдельных потоках
        admin_thread = threading.Thread(target=run_admin_panel, daemon=True)
        api_thread = threading.Thread(target=run_api_server, daemon=True)
        
        admin_thread.start()
        api_thread.start()
        
        # Ждем завершения
        admin_thread.join()
        api_thread.join()
        
    except KeyboardInterrupt:
        print("\n\n✅ Серверы остановлены")
    except Exception as e:
        print(f"\n\n❌ Ошибка: {e}")

if __name__ == "__main__":
    main()
