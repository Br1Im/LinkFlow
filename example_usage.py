#!/usr/bin/env python3
"""
Пример использования API БЕЗ браузера
Для серверного использования
"""

from multitransfer_api import MultitransferAPI

def main():
    print("🚀 ПРИМЕР ИСПОЛЬЗОВАНИЯ API")
    print("="*50)
    
    # Токен получаешь через решение капчи (любым способом)
    # Например через anticaptcha.com, capmonster.cloud и т.д.
    token = input("Введи токен (fhptokenid): ").strip()
    
    if not token:
        print("❌ Токен не введен")
        print()
        print("💡 КАК ПОЛУЧИТЬ ТОКЕН:")
        print("1. Открой https://multitransfer.ru/transfer/uzbekistan")
        print("2. Заполни форму и реши капчу")
        print("3. F12 → Network → найди запрос к api.multitransfer.ru")
        print("4. Скопируй fhptokenid из заголовков")
        print()
        print("💡 ДЛЯ АВТОМАТИЗАЦИИ:")
        print("- Используй anticaptcha.com")
        print("- Или capmonster.cloud")
        print("- Или любой другой сервис решения капчи")
        return
    
    # Создаем API клиент
    api = MultitransferAPI(token)
    
    # Создаем QR-платеж
    print("\n🎯 Создаю QR-платеж...")
    qr_link = api.create_qr_payment(
        card_number="9860080323894719",
        recipient_name="Nodir Asadullayev",
        amount=110
    )
    
    if qr_link:
        print(f"✅ УСПЕХ! QR-ссылка: {qr_link}")
        
        with open('result.txt', 'w') as f:
            f.write(f"QR Link: {qr_link}\n")
        
        print("💾 Результат сохранен в result.txt")
    else:
        print("❌ Не удалось создать QR-ссылку")
        print("💡 Возможно токен устарел - получи новый")

if __name__ == "__main__":
    main()