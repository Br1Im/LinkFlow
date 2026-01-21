# -*- coding: utf-8 -*-
"""
Менеджер платежей для multitransfer.ru
"""

from .multitransfer_payment import MultitransferPayment


class PaymentManager:
    """Главный класс для управления платежами через multitransfer.ru"""
    
    def __init__(self):
        self.multitransfer = None
    
    def initialize(self):
        """
        Инициализация multitransfer.ru (авторизация не требуется)
        """
        print("\n" + "="*60)
        print("🔧 ИНИЦИАЛИЗАЦИЯ: multitransfer.ru")
        print("="*60)
        
        self.multitransfer = MultitransferPayment()
        success = self.multitransfer.login()
        
        if success:
            print("✅ multitransfer.ru готов к работе")
        
        return success
    
    def create_payment(self, card_number, owner_name, amount):
        """
        Создать платеж через multitransfer.ru
        
        Args:
            card_number: Номер карты получателя (Узбекистан)
            owner_name: Имя владельца карты
            amount: Сумма в рублях
            
        Returns:
            dict: Результат с payment_link и qr_base64
        """
        if self.multitransfer:
            return self.multitransfer.create_payment(card_number, owner_name, amount)
        else:
            return {
                "error": "Сервис не инициализирован. Используйте initialize()",
                "success": False
            }
    
    def close(self):
        """Закрыть браузер"""
        if self.multitransfer:
            self.multitransfer.close()


# Пример использования
if __name__ == "__main__":
    manager = PaymentManager()
    
    print("\n" + "="*60)
    print("💳 MULTITRANSFER.RU - МЕНЕДЖЕР ПЛАТЕЖЕЙ")
    print("="*60)
    
    # Инициализация
    if manager.initialize():
        # Данные для платежа
        print("\n📝 Введите данные для платежа:")
        card = input("Номер карты получателя (Узбекистан): ").strip()
        name = input("Имя владельца карты: ").strip()
        amount = int(input("Сумма (руб): ").strip())
        
        # Создаем платеж
        result = manager.create_payment(card, name, amount)
        
        if result.get("success"):
            print("\n" + "="*60)
            print("✅ ПЛАТЕЖ СОЗДАН!")
            print("="*60)
            print(f"🔗 Ссылка: {result['payment_link']}")
            print(f"⏱️  Время: {result['elapsed_time']:.1f} сек")
        else:
            print(f"\n❌ Ошибка: {result.get('error')}")
    else:
        print("❌ Не удалось инициализировать сервис")
    
    # Закрываем браузер
    input("\nНажмите Enter для завершения...")
    manager.close()
