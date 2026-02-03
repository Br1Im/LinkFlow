# -*- coding: utf-8 -*-
"""
Данные отправителя для заполнения формы
Загружаются из Excel файла 100.xlsx
"""
import pandas as pd
import random
import os

def get_random_sender_data():
    """
    Получает случайные данные отправителя из Excel файла
    
    Структура Excel (без заголовков):
    0: Паспорт (полный номер)
    1: Фамилия
    2: Имя
    3: Отчество
    4: Телефон
    5: Адрес регистрации
    6: Дата рождения
    7: Место рождения
    8: Серия паспорта
    9: Номер паспорта
    10: Дата выдачи паспорта
    11: Кем выдан
    12: Пол
    """
    excel_path = os.path.join(os.path.dirname(__file__), '..', '100.xlsx')
    
    # Читаем Excel без заголовков
    df = pd.read_excel(excel_path, header=None)
    
    # Выбираем случайную строку
    row = df.sample(n=1).iloc[0]
    
    # Форматируем даты в DD.MM.YYYY (формат для формы)
    birth_date = row[6]
    if hasattr(birth_date, 'strftime'):
        birth_date = birth_date.strftime('%d.%m.%Y')
    else:
        birth_date = str(birth_date)
    
    issue_date = row[10]
    if hasattr(issue_date, 'strftime'):
        issue_date = issue_date.strftime('%d.%m.%Y')
    else:
        issue_date = str(issue_date)
    
    # Форматируем телефон
    phone = str(row[4])
    if not phone.startswith('+'):
        phone = f'+{phone}'
    
    # Очищаем адреса от двойных запятых и лишних пробелов
    def clean_address(addr):
        addr = str(addr)
        # Убираем двойные запятые
        while ',,' in addr:
            addr = addr.replace(',,', ',')
        # Убираем запятые в начале и конце
        addr = addr.strip(',').strip()
        # Убираем лишние пробелы
        addr = ' '.join(addr.split())
        return addr
    
    birth_place = clean_address(row[7])
    registration_place = clean_address(row[5])
    
    return {
        # Паспортные данные
        "passport_series": str(row[8]),
        "passport_number": str(row[9]),
        "passport_issue_date": issue_date,
        
        # Место рождения
        "birth_country": "Россия",
        "birth_place": birth_place,
        
        # Личные данные
        "first_name": str(row[2]),
        "last_name": str(row[1]),
        "middle_name": str(row[3]),
        "birth_date": birth_date,
        
        # Контакты
        "phone": phone,
        
        # Место регистрации
        "registration_country": "Россия",
        "registration_place": registration_place
    }

# Для обратной совместимости
SENDER_DATA = get_random_sender_data()
