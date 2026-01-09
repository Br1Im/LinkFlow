# -*- coding: utf-8 -*-
"""
Скрипт для обновления реквизитов в базе данных
"""

from database import Database

def setup_new_requisites():
    """Обновление реквизитов на новые данные"""
    db = Database()
    
    print("🔄 Обновление реквизитов...")
    
    # Очищаем старые реквизиты
    db.data["requisites"] = []
    
    # Добавляем новые реквизиты
    db.add_requisite("9860100126186921", "AVAZBEK ISAQOV")
    
    print("✅ Реквизиты обновлены!")
    print("📋 Текущие реквизиты в базе:")
    
    requisites = db.get_requisites()
    for i, req in enumerate(requisites):
        print(f"  {i+1}. {req['card_number']} - {req['owner_name']}")
    
    return True

if __name__ == "__main__":
    setup_new_requisites()