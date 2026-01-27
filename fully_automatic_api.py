#!/usr/bin/env python3
"""
ПОЛНОСТЬЮ АВТОМАТИЧЕСКИЙ API для multitransfer.ru
Автоматически получает токены и создает QR-ссылки
"""

import time
from multitransfer_api import MultitransferAPI
from auto_token_generator import AutoTokenGenerator

class FullyAutomaticAPI:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.current_token = None
        self.api = None
        self.token_generator = AutoTokenGenerator(headless=headless)
    
    def _get_fresh_token(self) -> bool:
        """Получение свежего токена"""
        print("🔄 Получаю свежий токен...")
        
        token = self.token_generator.get_fresh_token()
        
        if token:
            self.current_token = token
            self.api = MultitransferAPI(token)
            print(f"✅ Токен обновлен: {token[:20]}...")
            return True
        else:
            print("❌ Не удалось получить токен")
            return False
    
    def _is_token_valid(self) -> bool:
        """Проверка валидности токена"""
        if not self.api or not self.current_token:
            return False
        
        # Пробуем простой запрос
        try:
            commission_id = self.api.get_commissions(110)
            return commission_id is not None
        except:
            return False
    
    def create_qr_payment(self, card_number: str, recipient_name: str, amount: float, max_retries: int = 3) -> str:
        """
        Создание QR-платежа с автоматическим обновлением токена
        """
        print(f"🎯 Создаю QR-платеж: {amount} RUB → {card_number}")
        
        for attempt in range(max_retries):
            print(f"🔄 Попытка {attempt + 1}/{max_retries}")
            
            # Проверяем токен или получаем новый
            if not self._is_token_valid():
                print("🔑 Токен недействителен, получаю новый...")
                if not self._get_fresh_token():
                    print(f"❌ Попытка {attempt + 1} неудачна")
                    continue
            
            # Пробуем создать платеж
            try:
                qr_link = self.api.create_qr_payment(card_number, recipient_name, amount)
                
                if qr_link:
                    print(f"✅ QR-ссылка создана: {qr_link}")
                    return qr_link
                else:
                    print("❌ Не удалось создать QR-ссылку")
                    # Возможно токен устарел, пробуем еще раз
                    self.current_token = None
                    
            except Exception as e:
                print(f"❌ Ошибка создания платежа: {e}")
                self.current_token = None
            
            if attempt < max_retries - 1:
                print("⏳ Жду перед следующей попыткой...")
                time.sleep(5)
        
        print("💥 Все попытки исчерпаны")
        return None
    
    def create_multiple_payments(self, payments: list) -> list:
        """
        Создание нескольких платежей
        payments = [{"card": "123", "name": "Name", "amount": 110}, ...]
        """
        results = []
        
        print(f"🚀 Создаю {len(payments)} платежей...")
        
        for i, payment in enumerate(payments, 1):
            print(f"\n📦 Платеж {i}/{len(payments)}")
            
            qr_link = self.create_qr_payment(
                payment["card"],
                payment["name"], 
                payment["amount"]
            )
            
            results.append({
                "payment": payment,
                "qr_link": qr_link,
                "success": qr_link is not None
            })
            
            # Небольшая пауза между платежами
            if i < len(payments):
                time.sleep(2)
        
        success_count = sum(1 for r in results if r["success"])
        print(f"\n🎉 Готово! Успешно: {success_count}/{len(payments)}")
        
        return results

def main():
    """Пример использования полностью автоматического API"""
    
    # Создаем автоматический API
    auto_api = FullyAutomaticAPI(headless=True)
    
    # Один платеж
    print("=== ТЕСТ: Один платеж ===")
    qr_link = auto_api.create_qr_payment(
        card_number="9860080323894719",
        recipient_name="Nodir Asadullayev",
        amount=110
    )
    
    if qr_link:
        print(f"✅ Успех: {qr_link}")
        with open('auto_qr_link.txt', 'w') as f:
            f.write(qr_link)
    
    # Несколько платежей
    print("\n=== ТЕСТ: Несколько платежей ===")
    payments = [
        {"card": "9860080323894719", "name": "Nodir Asadullayev", "amount": 110},
        {"card": "9860080323894719", "name": "Test User", "amount": 200},
        {"card": "9860080323894719", "name": "Another User", "amount": 150}
    ]
    
    results = auto_api.create_multiple_payments(payments)
    
    # Сохраняем результаты
    with open('auto_results.txt', 'w') as f:
        for result in results:
            f.write(f"{result['payment']} -> {result['qr_link']}\n")
    
    print("💾 Результаты сохранены в auto_results.txt")

if __name__ == "__main__":
    main()