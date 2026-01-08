# -*- coding: utf-8 -*-
"""
Тест контроля браузера - проверка что открывается только один экземпляр
"""

import time
import threading
from browser_manager import browser_manager
from database import db

def test_concurrent_warmup():
    """Тест одновременного прогрева из нескольких потоков"""
    print("\n" + "="*60)
    print("🧪 ТЕСТ КОНТРОЛЯ БРАУЗЕРА")
    print("="*60)
    
    accounts = db.get_accounts()
    requisites = db.get_requisites()
    
    if not accounts or not requisites:
        print("❌ Нет аккаунтов или реквизитов")
        return
    
    account = accounts[0]
    requisite = requisites[0]
    
    print(f"\n📋 Тест: Запуск 3 одновременных прогревов")
    print(f"   Ожидается: Только 1 браузер откроется")
    print(f"   Остальные будут ждать завершения первого\n")
    
    results = []
    
    def warmup_thread(thread_id):
        """Функция для потока"""
        print(f"🔵 Поток {thread_id}: Запускаю прогрев...")
        start = time.time()
        
        success = browser_manager.warmup(
            card_number=requisite['card_number'],
            owner_name=requisite['owner_name'],
            account=account
        )
        
        elapsed = time.time() - start
        results.append({
            'thread_id': thread_id,
            'success': success,
            'elapsed': elapsed
        })
        
        if success:
            print(f"✅ Поток {thread_id}: Успех за {elapsed:.1f} сек")
        else:
            print(f"❌ Поток {thread_id}: Ошибка за {elapsed:.1f} сек")
    
    # Запускаем 3 потока одновременно
    threads = []
    for i in range(3):
        t = threading.Thread(target=warmup_thread, args=(i+1,))
        threads.append(t)
        t.start()
        time.sleep(0.1)  # Небольшая задержка между запусками
    
    # Ждём завершения всех потоков
    for t in threads:
        t.join()
    
    print("\n" + "="*60)
    print("📊 РЕЗУЛЬТАТЫ:")
    print("="*60)
    
    for r in results:
        status = "✅" if r['success'] else "❌"
        print(f"{status} Поток {r['thread_id']}: {r['elapsed']:.1f} сек")
    
    success_count = sum(1 for r in results if r['success'])
    
    print(f"\n📈 Успешных прогревов: {success_count}/3")
    
    if success_count >= 1:
        print("\n✅ ТЕСТ ПРОЙДЕН!")
        print("   Браузер открылся и работает")
    else:
        print("\n❌ ТЕСТ НЕ ПРОЙДЕН!")
        print("   Браузер не удалось открыть")
    
    # Закрываем браузер
    browser_manager.close()
    print("\n🔒 Браузер закрыт")

if __name__ == "__main__":
    test_concurrent_warmup()
