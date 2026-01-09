from database import Database

def update_real_account():
    db = Database()
    
    # Очищаем старые аккаунты
    db.data["accounts"] = []
    
    # Добавляем РЕАЛЬНЫЙ аккаунт elecsnet
    phone = "+79880260334"
    password = "xowxut-wemhej-3zAsno"
    
    account_index = db.add_account(phone, password)
    print(f'✅ РЕАЛЬНЫЙ аккаунт добавлен с индексом: {account_index}')
    print(f'📱 Телефон: {phone}')
    print('🔐 Пароль: [СКРЫТ]')
    
    # Также обновляем реквизиты на новые
    db.data["requisites"] = []
    db.add_requisite("9860100126186921", "AVAZBEK ISAQOV")
    print('💳 Реквизиты обновлены на AVAZBEK ISAQOV')
    
    accounts = db.get_accounts()
    print('📋 Текущие аккаунты:')
    for i, acc in enumerate(accounts):
        print(f'  {i}: {acc["phone"]} - {acc["status"]}')
    
    requisites = db.get_requisites()
    print('💳 Текущие реквизиты:')
    for i, req in enumerate(requisites):
        print(f'  {i}: {req["card_number"]} - {req["owner_name"]}')

if __name__ == '__main__':
    update_real_account()