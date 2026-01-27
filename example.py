#!/usr/bin/env python3
"""
Пример использования API
"""

from multitransfer_api import MultitransferAPI

def main():
    # 1. Получи токен из браузера:
    # - Открой https://multitransfer.ru/transfer/uzbekistan
    # - F12 → Network
    # - Заполни форму и реши капчу
    # - Найди запрос к api.multitransfer.ru
    # - Скопируй fhptokenid из заголовков
    
    token = "ВСТАВЬ_СЮДА_ТОКЕН_ИЗ_БРАУЗЕРА"
    
    # 2. Создай API клиент
    api = MultitransferAPI(token)
    
    # 3. Создай QR-ссылку
    qr_link = api.create_qr_payment(
        card_number="9860080323894719",
        recipient_name="Nodir Asadullayev",
        amount=110  # минимум 110 RUB
    )
    
    if qr_link:
        print(f"✅ QR-ссылка создана: {qr_link}")
        
        # Сохраняем в файл
        with open('qr_link.txt', 'w') as f:
            f.write(qr_link)
        print("💾 Ссылка сохранена в qr_link.txt")
    else:
        print("❌ Ошибка создания QR-ссылки")
        print("💡 Проверь токен - возможно он устарел")

if __name__ == "__main__":
    main()