#!/usr/bin/env python3
import sys
sys.path.insert(0, 'admin')
import database as db

beneficiaries = db.get_all_beneficiaries()
print(f'Всего реквизитов: {len(beneficiaries)}')

if beneficiaries:
    print('\nПервые 5:')
    for b in beneficiaries[:5]:
        print(f'{b["id"]}: {b["card_owner"]} - {b["card_number"]} (active={b["is_active"]}, verified={b["is_verified"]})')
else:
    print('Реквизиты отсутствуют!')
    print('\nДобавляю тестовые реквизиты...')
    
    # Добавляем рабочие реквизиты
    test_beneficiaries = [
        ("9860080323894719", "Nodir Asadullayev"),
        ("9860606753188378", "ASIYA ESEMURATOVA")
    ]
    
    for card, owner in test_beneficiaries:
        ben_id = db.add_beneficiary(card, owner)
        # Помечаем как проверенные
        db.update_beneficiary_verification(ben_id, True, f"TEST-{ben_id}")
        print(f'✅ Добавлен: {owner} ({card})')
    
    print('\nГотово!')
