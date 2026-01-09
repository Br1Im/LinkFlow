from database import Database

def check_accounts():
    db = Database()
    accounts = db.get_accounts()
    print(f'Accounts: {len(accounts)}')
    for i, acc in enumerate(accounts):
        print(f'  {i}: {acc["phone"]} - {acc["status"]}')
    
    if len(accounts) == 0:
        print('No accounts found. Adding test account...')
        # ЗАМЕНИТЕ НА РЕАЛЬНЫЕ ДАННЫЕ!
        phone = '+998901234567'  # ВАШ НОМЕР
        password = 'your_password'  # ВАШ ПАРОЛЬ
        
        account_index = db.add_account(phone, password)
        print(f'Account added with index: {account_index}')
        print('WARNING: Replace with real credentials!')

if __name__ == '__main__':
    check_accounts()