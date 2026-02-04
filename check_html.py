import re

with open('screenshots/page_1770195409.html', 'r', encoding='utf-8') as f:
    html = f.read()
    
# Ищем поля с name и их значения
fields = re.findall(r'<input[^>]*name="([^"]+)"[^>]*value="([^"]*)"[^>]*>', html)
print('Найденные поля:')
for name, value in fields:
    if 'transfer_' in name or 'beneficiary_' in name or 'sender_' in name or 'Date' in name or 'phone' in name or 'Address' in name:
        print(f'{name}: {value}')
