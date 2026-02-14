#!/usr/bin/env python3
"""
Интеграция с H2H API для получения реквизитов
Документация: https://docs.example.com/api
"""

import requests
import time
from typing import Dict, Optional


class H2HAPI:
    """Клиент для работы с H2H API"""
    
    def __init__(self, base_url: str, access_token: str):
        """
        Инициализация клиента
        
        Args:
            base_url: Базовый URL API (например, "https://api.example.com")
            access_token: Токен доступа из админки
        """
        self.base_url = base_url.rstrip('/')
        self.access_token = access_token
        self.headers = {
            'Accept': 'application/json',
            'Access-Token': access_token
        }
    
    def get_currencies(self) -> Dict:
        """
        Получить список доступных валют
        
        Returns:
            Dict: Список валют
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/currencies",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_payment_gateways(self) -> Dict:
        """
        Получить список доступных платежных методов
        
        Returns:
            Dict: Список платежных методов
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/payment-gateways",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_order(
        self,
        external_id: str,
        amount: int,
        merchant_id: str,
        currency: Optional[str] = None,
        pay_gateway: Optional[str] = None,
        payment_detail_type: Optional[str] = None,
        client_id: Optional[str] = None,
        callback_url: Optional[str] = None,
        payer_bank: Optional[str] = None,
        max_wait_ms: int = 30000
    ) -> Dict:
        """
        Создать заказ через H2H API
        
        Args:
            external_id: Уникальный ID заказа на вашей стороне
            amount: Сумма заказа (целое число)
            merchant_id: UUID мерчанта
            currency: Код валюты (rub, kzt и т.д.)
            pay_gateway: Код платежного метода (используется pay_gateway, не payment_gateway!)
            payment_detail_type: Тип реквизита (card, phone, account_number, qr_code)
            client_id: ID клиента (для контрагентов)
            callback_url: URL для callback уведомлений
            payer_bank: Банк плательщика (для deeplinks)
            max_wait_ms: Максимальное время ожидания в миллисекундах
            
        Returns:
            Dict: Данные заказа с реквизитами
        """
        payload = {
            "external_id": external_id,
            "amount": amount,
            "merchant_id": merchant_id
        }
        
        if currency:
            payload["currency"] = currency
        if pay_gateway:
            payload["pay_gateway"] = pay_gateway  # Правильное имя параметра!
        if payment_detail_type:
            payload["payment_detail_type"] = payment_detail_type
        if client_id:
            payload["client_id"] = client_id
        if callback_url:
            payload["callback_url"] = callback_url
        if payer_bank:
            payload["payer_bank"] = payer_bank
        
        headers = self.headers.copy()
        headers['X-Max-Wait-Ms'] = str(max_wait_ms)
        
        try:
            response = requests.post(
                f"{self.base_url}/api/h2h/order",
                json=payload,
                headers=headers,
                timeout=(max_wait_ms / 1000) + 5
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            # Возвращаем детальную информацию об ошибке
            try:
                error_data = e.response.json()
            except:
                error_data = {"message": e.response.text}
            
            return {
                "success": False,
                "error": str(e),
                "status_code": e.response.status_code,
                "details": error_data
            }
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Request timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_order(self, order_id: str) -> Dict:
        """
        Получить информацию о заказе
        
        Args:
            order_id: UUID заказа
            
        Returns:
            Dict: Данные заказа
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/h2h/order/{order_id}",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_order_by_external_id(self, merchant_id: str, external_id: str) -> Dict:
        """
        Получить информацию о заказе по external_id
        
        Args:
            merchant_id: UUID мерчанта
            external_id: Внешний ID заказа
            
        Returns:
            Dict: Данные заказа
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/h2h/order/{merchant_id}/{external_id}",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def cancel_order(self, order_id: str) -> Dict:
        """
        Отменить заказ
        
        Args:
            order_id: UUID заказа
            
        Returns:
            Dict: Результат отмены
        """
        try:
            response = requests.patch(
                f"{self.base_url}/api/h2h/order/{order_id}/cancel",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_deeplinks(self, order_id: str) -> Dict:
        """
        Получить deeplinks для заказа
        
        Args:
            order_id: UUID заказа
            
        Returns:
            Dict: Deeplinks для iOS и Android
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/h2h/order/{order_id}/deeplinks",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Глобальная функция для быстрого получения реквизитов
def get_h2h_requisite(
    amount: int,
    base_url: str,
    access_token: str,
    merchant_id: str,
    currency: str = "rub",
    payment_detail_type: str = "card"
) -> Optional[Dict]:
    """
    Быстрое получение реквизитов от H2H API
    
    Args:
        amount: Сумма платежа
        base_url: Базовый URL API
        access_token: Токен доступа
        merchant_id: UUID мерчанта
        currency: Валюта (по умолчанию rub)
        payment_detail_type: Тип реквизита (по умолчанию card)
        
    Returns:
        Dict с реквизитами или None если недоступны
        {
            'card_number': '1000200030004000',
            'card_owner': 'Пол Атрейдес',
            'order_id': 'uuid',
            'amount': 1000
        }
    """
    api = H2HAPI(base_url=base_url, access_token=access_token)
    
    try:
        external_id = f"REQ_{int(time.time() * 1000)}"
        
        result = api.create_order(
            external_id=external_id,
            amount=amount,
            merchant_id=merchant_id,
            currency=currency,
            payment_detail_type=payment_detail_type
        )
        
        if result.get("success") and "data" in result:
            data = result["data"]
            payment_detail = data.get("payment_detail", {})
            
            if payment_detail:
                return {
                    'card_number': payment_detail.get('detail', ''),
                    'card_owner': payment_detail.get('initials', ''),
                    'order_id': data.get('order_id'),
                    'amount': data.get('amount'),
                    'payment_gateway': data.get('payment_gateway'),
                    'expires_at': data.get('expires_at')
                }
        
        return None
        
    except Exception as e:
        print(f"H2H API error: {e}")
        return None


# Пример использования
if __name__ == "__main__":
    import json
    
    # Конфигурация (замените на реальные значения)
    BASE_URL = "https://api.example.com"
    ACCESS_TOKEN = "your_access_token_here"
    MERCHANT_ID = "your_merchant_uuid_here"
    
    # Создаем клиент
    api = H2HAPI(
        base_url=BASE_URL,
        access_token=ACCESS_TOKEN
    )
    
    # Получаем доступные валюты
    print("=== Доступные валюты ===")
    currencies = api.get_currencies()
    print(json.dumps(currencies, indent=2, ensure_ascii=False))
    
    # Получаем платежные методы
    print("\n=== Платежные методы ===")
    gateways = api.get_payment_gateways()
    print(json.dumps(gateways, indent=2, ensure_ascii=False))
    
    # Создаем заказ
    print("\n=== Создание заказа ===")
    order = api.create_order(
        external_id=f"TEST_{int(time.time())}",
        amount=1000,
        merchant_id=MERCHANT_ID,
        currency="rub",
        payment_detail_type="card"
    )
    print(json.dumps(order, indent=2, ensure_ascii=False))
    
    if order.get("success"):
        order_id = order["data"]["order_id"]
        
        # Получаем информацию о заказе
        print(f"\n=== Информация о заказе {order_id} ===")
        order_info = api.get_order(order_id)
        print(json.dumps(order_info, indent=2, ensure_ascii=False))
