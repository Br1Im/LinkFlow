#!/usr/bin/env python3
"""
Диагностика прогрева браузера
"""

import sys
import os
sys.path.append('/root/LinkFlow')

from database import Database
from payment_service import warmup_for_user

def test_warmup():
    print("🧪 Тестируем прогрев браузера...")
    
    # Проверяем базу данных
    db = Database()
    requisites = db.get_requisites()
    accounts = db.get_accounts()
    
    print(f"📋 Реквизиты: {len(requisites)}")
    for i, req in enumerate(requisites):
        print(f"  {i}: {req['card_number']} - {req['owner_name']}")
    
    print(f"👤 Аккаунты: {len(accounts)}")
    for i, acc in enumerate(accounts):
        print(f"  {i}: {acc['phone']} - {acc['status']}")
    
    if not requisites or not accounts:
        print("❌ Нет реквизитов или аккаунтов!")
        return False
    
    # Тестируем прогрев
    print("🔥 Запускаем прогрев...")
    try:
        result = warmup_for_user(1)
        print(f"📊 Результат прогрева: {result}")
        
        if result.get('success'):
            print("✅ Прогрев успешен!")
            return True
        else:
            print(f"❌ Прогрев не удался: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка прогрева: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_warmup()