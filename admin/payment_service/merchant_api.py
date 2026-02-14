#!/usr/bin/env python3
"""
Интеграция с Merchant API Liberty.top
Упрощенная версия API для создания платежных ссылок
"""

import requests
import time
from typing import Dict, Optional


class MerchantAPI:
    """Клиент для работы с Merchant API"""
    
    def __init__(self, base_url: str, access_token: str):
        """
        Инициализация клиента
        
        Args:
            base_url: Базовый URL API (например, "https://liberty.top")
            access_token: Токен доступа из админки
        """
        self.base_url = base_url.rstrip('/')
        self.access_token = access_token
        self.headers = {
            'Accept': 'application/json',
            'Access-Token': access_token
        }
    
    def create_order(
        self,
        external_id: str,
        amount: int,
        merchant_id: str,
        currency: Optional[str] = None,
        payment_gateway: Optional[str] = None,
        payment_detail_type: Optional[str] = None,
        client_id: Optional[str] = None,
        callback_url: Optional[str] = None,
        success_url: Optional[str] = None,
        fail_url: Optional[str] = None,
        manually: Optional[str] = None,
        max_wait_ms: int = 30000
    ) -> Dict:
        """
        Создать заказ через Merchant API
        
        Args:
            external_id: Уникальный ID заказа на вашей стороне
            amount: Сумма заказа (целое число)
            merchant_id: UUID мерчанта
            currency: Код валюты (rub, kzt и т.д.)
            payment_gateway: Код платежного метода
            payment_detail_type: Тип реквизита (card, phone, account_number, qr_code)
            client_id: ID клиента (для контрагентов)
            callback_url: URL для callback уведомлений
            success_url: URL для редиректа при успехе
            fail_url: URL для редиректа при неудаче
            manually: "1" для ручного выбора метода клиентом
            max_wait_ms: Максимальное время ожидания в миллисекундах
            
        Returns:
            Dict: Данные заказа с платежной ссылкой
        """
        payload = {
            "external_id": external_id,
            "amount": amount,
            "merchant_id": merchant_id
        }
        
        if currency:
            payload["currency"] = currency
        if payment_gateway:
            payload["payment_gateway"] = payment_gateway
        if payment_detail_type:
            payload["payment_detail_type"] = payment_detail_type
        if client_id:
            payload["client_id"] = client_id
        if callback_url:
            payload["callback_url"] = callback_url
        if success_url:
            payload["success_url"] = success_url
        if fail_url:
            payload["fail_url"] = fail_url
        if manually:
            payload["manually"] = manually
        
        headers = self.headers.copy()
        headers['X-Max-Wait-Ms'] = str(max_wait_ms)
        
        try:
            response = requests.post(
                f"{self.base_url}/api/merchant/order",
                json=payload,
                headers=headers,
                timeout=(max_wait_ms / 1000) + 5
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
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
                f"{self.base_url}/api/merchant/order/{order_id}",
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
                f"{self.base_url}/api/merchant/order/{merchant_id}/{external_id}",
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
                f"{self.base_url}/api/merchant/order/{order_id}/deeplinks",
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


# Глобальная функция для быстрого создания заказа
def create_merchant_order(
    amount: int,
    base_url: str,
    access_token: str,
    merchant_id: str,
    currency: str = "rub",
    payment_detail_type: str = "card"
) -> Optional[Dict]:
    """
    Быстрое создание заказа через Merchant API
    
    Args:
        amount: Сумма платежа
        base_url: Базовый URL API
        access_token: Токен доступа
        merchant_id: UUID мерчанта
        currency: Валюта (по умолчанию rub)
        payment_detail_type: Тип реквизита (по умолчанию card)
        
    Returns:
        Dict с данными заказа и реквизитами или None если ошибка
        {
            'order_id': 'uuid',
            'payment_link': 'https://...',
            'amount': 1000,
            'payment_gateway': 'Milly',
            'card_number': '8600123456789012',
            'card_owner': 'qwerty',
            'expires_at': 1771064884
        }
    """
    api = MerchantAPI(base_url=base_url, access_token=access_token)
    
    try:
        external_id = f"ORDER_{int(time.time() * 1000)}"
        
        result = api.create_order(
            external_id=external_id,
            amount=amount,
            merchant_id=merchant_id,
            currency=currency,
            payment_detail_type=payment_detail_type
        )
        
        if result.get("success") and "data" in result:
            data = result["data"]
            payment_detail = data.get('payment_detail', {})
            
            return {
                'order_id': data.get('order_id'),
                'payment_link': data.get('payment_link'),
                'amount': data.get('amount'),
                'payment_gateway': data.get('payment_gateway_name'),
                'card_number': payment_detail.get('detail', ''),
                'card_owner': payment_detail.get('initials', ''),
                'detail_type': payment_detail.get('detail_type', ''),
                'expires_at': data.get('expires_at'),
                'status': data.get('status'),
                'sub_status': data.get('sub_status')
            }
        
        return None
        
    except Exception as e:
        print(f"Merchant API error: {e}")
        return None


if __name__ == "__main__":
    import json
    
    # Конфигурация
    BASE_URL = "https://liberty.top"
    ACCESS_TOKEN = "dtpf8uupsbhumevz4pz2jebrqzqmv62o"
    MERCHANT_ID = "d5c17c6c-dc40-428a-80e5-2ca01af99f68"
    
    # Создаем клиент
    api = MerchantAPI(
        base_url=BASE_URL,
        access_token=ACCESS_TOKEN
    )
    
    # Создаем заказ
    print("=== Создание заказа ===")
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
