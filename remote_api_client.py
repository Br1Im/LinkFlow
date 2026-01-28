#!/usr/bin/env python3
"""
Клиент для удаленного API на 85.192.56.74:5001
"""

import requests
import time

class RemotePaymentAPI:
    def __init__(self, api_url="http://85.192.56.74:5001", api_token="-3uVLlbWyy90eapOGkv70C2ZltaYTxq-HtDbq-DtlLo"):
        self.api_url = api_url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_token}"
        }
    
    def create_payment(self, card_number: str, owner_name: str, amount: float, order_id: str = None):
        """Создать платеж через удаленный API"""
        
        if not order_id:
            order_id = f"order_{int(time.time())}"
        
        payload = {
            "amount": amount,
            "orderId": order_id,
            "cardNumber": card_number,
            "ownerName": owner_name
        }
        
        print(f"🚀 Отправляю запрос на {self.api_url}/api/payment")
        print(f"📦 Данные: {payload}")
        print()
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.api_url}/api/payment",
                json=payload,
                headers=self.headers,
                timeout=120
            )
            
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                print("="*70)
                print("✅ УСПЕХ!")
                print("="*70)
                print(f"⏱️  Время: {elapsed:.1f}s")
                print(f"🆔 Payment ID: {data.get('payment_id')}")
                print(f"📦 Order ID: {data.get('order_id')}")
                print(f"🔗 Payment Link: {data.get('payment_link')}")
                print(f"📊 Status: {data.get('status')}")
                
                if data.get('elapsed_time'):
                    print(f"⏱️  Server Time: {data.get('elapsed_time'):.1f}s")
                
                print("="*70)
                
                return data
            else:
                print(f"❌ Ошибка: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"❌ Timeout после {time.time() - start_time:.1f}s")
            return None
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None
    
    def get_payment_status(self, payment_id: int):
        """Получить статус платежа"""
        try:
            response = requests.get(
                f"{self.api_url}/api/payment/{payment_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None
    
    def get_payment_by_order(self, order_id: str):
        """Получить платеж по order_id"""
        try:
            response = requests.get(
                f"{self.api_url}/api/payment/order/{order_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None


if __name__ == "__main__":
    # Тест API
    api = RemotePaymentAPI()
    
    result = api.create_payment(
        card_number="9860080323894719",
        owner_name="Nodir Asadullayev",
        amount=110,
        order_id="test_" + str(int(time.time()))
    )
    
    if result:
        print()
        print("🎉 Платеж создан успешно!")
