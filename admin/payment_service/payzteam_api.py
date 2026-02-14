#!/usr/bin/env python3
"""
Интеграция с PayzTeam Exchange API (P2P)
Документация: https://payzteam.com/api-for-developers

API для P2P оплат:
- POST /exchange/create_deal_v2/{id} - создать оплату и получить реквизиты
- POST /exchange/get - получение статуса оплаты
- POST /exchange/cancel - отмена оплаты

Структура запроса create_deal_v2:
{
  "client": "test@test.ru",
  "amount": "11055.5",
  "fiat_currency": "rub",
  "uuid": "12124234",
  "language": "ru",
  "payment_method": "c2c",
  "bank": "sber",
  "is_intrabank_transfer": false,
  "token": "string",
  "ip": "172.16.58.3",
  "sign": "sha1(client+uuid+amount+fiat_currency+payment_method+SecretKey)"
}

Структура ответа:
{
  "id": 100,
  "status": 0,
  "success": true,
  "paymentInfo": {...}
}

Статусы:
0 - новая оплата
2 - время оплаты вышло
3 - ожидает обработки
4 - оплата успешно прошла
5 - отправка callback партнеру
"""

import requests
import hashlib
import json
import time
from typing import Dict, Optional


class PayzTeamAPI:
    """Клиент для работы с PayzTeam Exchange API (P2P)"""
    
    def __init__(self, merchant_id: str, api_key: str, secret_key: str):
        """
        Инициализация клиента
        
        Args:
            merchant_id: ID мерчанта (например, "747")
            api_key: API ключ (указывается в заголовке X-Api-Key)
            secret_key: Секретный ключ для подписи запросов
        """
        self.merchant_id = merchant_id
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = "https://payzteam.com"
        
    def _generate_signature(self, client: str, uuid: str, amount: str, 
                           fiat_currency: str, payment_method: str) -> str:
        """
        Генерация подписи для запроса create_deal_v2
        
        Формула: sha1(client+uuid+amount+fiat_currency+payment_method+SecretKey)
        
        Args:
            client: Email клиента
            uuid: Уникальный ID платежа
            amount: Сумма
            fiat_currency: Валюта
            payment_method: Метод оплаты
            
        Returns:
            str: SHA1 подпись
        """
        # Формируем строку для подписи
        sign_string = f"{client}{uuid}{amount}{fiat_currency}{payment_method}{self.secret_key}"
        
        # Генерируем SHA1 хеш
        signature = hashlib.sha1(sign_string.encode('utf-8')).hexdigest()
        
        return signature
    
    def create_deal(
        self,
        amount: float,
        uuid: str,
        client_email: str = "client@example.com",
        fiat_currency: str = "rub",
        payment_method: str = "abh_c2c",
        bank: Optional[str] = None,
        is_intrabank_transfer: bool = False,
        client_ip: str = "127.0.0.1",
        language: str = "ru",
        token: Optional[str] = None
    ) -> Dict:
        """
        Создание P2P оплаты через /exchange/create_deal_v2/{id}
        
        Args:
            amount: Сумма платежа
            uuid: Уникальный номер платежа в вашей системе
            client_email: Email клиента
            fiat_currency: Код валюты (rub, azn, kzt, try)
            payment_method: Метод оплаты (c2c, sbp, qrcode, transgran_c2c, transgran_sbp, abh_c2c, abh_sbp, mob_com, nspk)
            bank: Банк для перевода (sber, tinkoff, vtb, alfa) - опционально
            is_intrabank_transfer: Флаг внутрибанковского перевода
            client_ip: IP клиента
            language: Язык (ru, en)
            token: Токен капчи (опционально)
            
        Returns:
            Dict: Ответ от API
            {
                "id": 100,
                "status": 0,
                "success": true,
                "paymentInfo": {...}
            }
        """
        # Генерируем подпись
        signature = self._generate_signature(
            client=client_email,
            uuid=uuid,
            amount=str(amount),
            fiat_currency=fiat_currency,
            payment_method=payment_method
        )
        
        # Формируем тело запроса
        payload = {
            "client": client_email,
            "amount": str(amount),
            "fiat_currency": fiat_currency,
            "uuid": uuid,
            "language": language,
            "payment_method": payment_method,
            "is_intrabank_transfer": is_intrabank_transfer,
            "ip": client_ip,
            "sign": signature
        }
        
        # Добавляем bank только если указан
        if bank:
            payload["bank"] = bank
        
        if token:
            payload["token"] = token
        
        # Заголовки с API ключом в X-Api-Key
        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key
        }
        
        try:
            # Отправляем запрос
            response = requests.post(
                f"{self.base_url}/exchange/create_deal_v2/{self.merchant_id}",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            return result
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Request failed: {str(e)}"
            }
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Invalid JSON response"
            }
    
    def get_payment_status(self, deal_id: int) -> Dict:
        """
        Получение статуса платежа через /exchange/get
        
        Args:
            deal_id: ID заявки на оплату
            
        Returns:
            Dict: Статус платежа
        """
        payload = {
            "id": deal_id
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/exchange/get",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Request failed: {str(e)}"
            }
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Invalid JSON response"
            }
    
    def cancel_payment(self, deal_id: int) -> Dict:
        """
        Отмена оплаты через /exchange/cancel
        
        Args:
            deal_id: ID заявки на оплату
            
        Returns:
            Dict: Результат отмены
        """
        payload = {
            "id": str(deal_id)
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Api-Key": self.api_key
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/exchange/cancel",
                data=payload,
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Request failed: {str(e)}"
            }
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Invalid JSON response"
            }


# Пример использования
if __name__ == "__main__":
    # Конфигурация (замените на реальные значения)
    MERCHANT_ID = "747"
    API_KEY = "your_api_key_here"  # API ключ (указывается в X-Api-Key)
    SECRET_KEY = "your_secret_key_here"  # Секретный ключ для подписи
    
    # Создаем клиент
    api = PayzTeamAPI(
        merchant_id=MERCHANT_ID,
        api_key=API_KEY,
        secret_key=SECRET_KEY
    )
    
    # Создаем P2P платеж
    import time
    uuid = f"TEST_{int(time.time())}"
    
    result = api.create_deal(
        amount=1000.00,
        uuid=uuid,
        client_email="test@example.com",
        payment_method="abh_c2c",
        bank=None
    )
    
    print("Результат создания платежа:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Если платеж создан успешно
    if result.get("success"):
        deal_id = result.get("id")
        print(f"\nID платежа: {deal_id}")
        print(f"Статус: {result.get('status')}")
        
        if "paymentInfo" in result:
            print("\nИнформация для оплаты:")
            print(json.dumps(result["paymentInfo"], indent=2, ensure_ascii=False))
        
        # Проверяем статус
        print("\n--- Проверка статуса ---")
        status = api.get_payment_status(deal_id)
        print(json.dumps(status, indent=2, ensure_ascii=False))
        
        # Отменяем платеж (для теста)
        print("\n--- Отмена платежа ---")
        cancel_result = api.cancel_payment(deal_id)
        print(json.dumps(cancel_result, indent=2, ensure_ascii=False))


# Глобальная функция для быстрого получения реквизитов
def get_payzteam_requisite(amount: float) -> Optional[Dict]:
    """
    Быстрое получение реквизитов (поддерживает Auto, H2H и PayzTeam)
    
    Args:
        amount: Сумма платежа
        
    Returns:
        Dict с реквизитами или None если недоступны
        {
            'card_number': '5614682414447872',
            'card_owner': 'Ziedullo Goziev',
            'bank': 'Trast Bank' (опционально),
            'source': 'h2h' или 'payzteam'
        }
    """
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(__file__))
        
        # Импортируем конфигурацию
        from requisite_config import get_requisite_service, get_h2h_config, get_payzteam_config
        
        service = get_requisite_service()
        
        if service == 'auto':
            # АВТОМАТИЧЕСКИЙ РЕЖИМ: сначала H2H, потом PayzTeam
            print("🔄 Режим AUTO: пробуем H2H API...")
            
            # Пробуем H2H API
            from h2h_api import get_h2h_requisite
            config = get_h2h_config()
            
            h2h_result = get_h2h_requisite(
                amount=int(amount),
                base_url=config['base_url'],
                access_token=config['access_token'],
                merchant_id=config['merchant_id'],
                currency=config.get('currency', 'rub'),
                payment_detail_type=config.get('payment_detail_type', 'card')
            )
            
            if h2h_result:
                print("✅ H2H API вернул реквизиты")
                h2h_result['source'] = 'h2h'
                return h2h_result
            
            # Если H2H не вернул - пробуем PayzTeam
            print("⚠️ H2H API не вернул реквизиты, пробуем PayzTeam API...")
            
            config = get_payzteam_config()
            api = PayzTeamAPI(
                merchant_id=config['merchant_id'],
                api_key=config['api_key'],
                secret_key=config['secret_key']
            )
            
            uuid = f"REQ_{int(time.time() * 1000)}"
            
            result = api.create_deal(
                amount=amount,
                uuid=uuid,
                client_email="requisite@linkflow.com",
                payment_method=config.get('payment_method', 'abh_c2c')
            )
            
            if result.get("success") and "paymentInfo" in result:
                credentials = result["paymentInfo"].get("paymentCredentials", "")
                parts = credentials.split("|")
                
                if len(parts) >= 2:
                    print("✅ PayzTeam API вернул реквизиты")
                    return {
                        'card_number': parts[0],
                        'card_owner': parts[1],
                        'bank': parts[2] if len(parts) > 2 else 'Unknown',
                        'deal_id': result.get('id'),
                        'source': 'payzteam'
                    }
            
            print("❌ Оба API не вернули реквизиты")
            return None
        
        elif service == 'h2h':
            # ТОЛЬКО H2H API
            from h2h_api import get_h2h_requisite
            
            config = get_h2h_config()
            
            result = get_h2h_requisite(
                amount=int(amount),
                base_url=config['base_url'],
                access_token=config['access_token'],
                merchant_id=config['merchant_id'],
                currency=config.get('currency', 'rub'),
                payment_detail_type=config.get('payment_detail_type', 'card')
            )
            
            if result:
                result['source'] = 'h2h'
            
            return result
        
        elif service == 'payzteam':
            # ТОЛЬКО PAYZTEAM API
            config = get_payzteam_config()
            
            api = PayzTeamAPI(
                merchant_id=config['merchant_id'],
                api_key=config['api_key'],
                secret_key=config['secret_key']
            )
            
            uuid = f"REQ_{int(time.time() * 1000)}"
            
            result = api.create_deal(
                amount=amount,
                uuid=uuid,
                client_email="requisite@linkflow.com",
                payment_method=config.get('payment_method', 'abh_c2c')
            )
            
            if result.get("success") and "paymentInfo" in result:
                credentials = result["paymentInfo"].get("paymentCredentials", "")
                parts = credentials.split("|")
                
                if len(parts) >= 2:
                    return {
                        'card_number': parts[0],
                        'card_owner': parts[1],
                        'bank': parts[2] if len(parts) > 2 else 'Unknown',
                        'deal_id': result.get('id'),
                        'source': 'payzteam'
                    }
            
            return None
        
        else:
            print(f"Unknown requisite service: {service}")
            return None
            
    except Exception as e:
        print(f"Requisite API error: {e}")
        import traceback
        traceback.print_exc()
        return None
