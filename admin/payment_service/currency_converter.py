#!/usr/bin/env python3
"""
Модуль для автоматической конвертации валюты через API multitransfer.ru
Используется для конвертации RUB -> UZS перед созданием платежа
"""

import httpx
import uuid
from typing import Dict, Optional
from decimal import Decimal


class CurrencyConverter:
    """Конвертер валют через API multitransfer.ru"""
    
    def __init__(self):
        self.base_url = "https://api.multitransfer.ru"
        self.timeout = 10.0
        
    def convert_rub_to_uzs(self, amount_rub: float) -> Optional[Dict]:
        """
        Конвертирует рубли в узбекские сумы через API multitransfer.ru
        
        Args:
            amount_rub: Сумма в рублях
            
        Returns:
            Dict с результатом конвертации:
            {
                'amount_rub': 5000.0,
                'amount_uzs': 758950.0,
                'exchange_rate': 151.79,
                'commission': {...},
                'success': True
            }
            или None при ошибке
        """
        try:
            # Генерируем уникальные ID для запроса
            request_id = str(uuid.uuid4())
            session_id = str(uuid.uuid4())
            
            headers = {
                "accept": "application/json, text/plain, */*",
                "accept-language": "ru,en;q=0.9",
                "client-id": "multitransfer-web-id",
                "content-type": "application/json",
                "fhprequestid": request_id,
                "fhpsessionid": session_id,
                "x-request-id": request_id,
                "origin": "https://multitransfer.ru",
                "referer": "https://multitransfer.ru/"
            }
            
            payload = {
                "countryCode": "UZB",
                "range": "ALL_PLUS_LIMITS",
                "money": {
                    "acceptedMoney": {
                        "amount": amount_rub,
                        "currencyCode": "RUB"
                    },
                    "withdrawMoney": {
                        "currencyCode": "UZS"
                    }
                }
            }
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/anonymous/multi/multitransfer-fee-calc/v3/commissions",
                    json=payload,
                    headers=headers
                )
                
                response.raise_for_status()
                data = response.json()
                
                # API возвращает массив fees с разными способами доставки
                # Берем первый вариант (to_card) и первую комиссию
                if "fees" in data and len(data["fees"]) > 0:
                    first_fee = data["fees"][0]
                    if "commissions" in first_fee and len(first_fee["commissions"]) > 0:
                        first_commission = first_fee["commissions"][0]
                        money_data = first_commission.get("money", {})
                        
                        amount_uzs_str = money_data.get("withdrawMoney", {}).get("amount", "0")
                        amount_uzs = float(amount_uzs_str)
                        
                        # Рассчитываем курс
                        exchange_rate = amount_uzs / amount_rub if amount_rub > 0 else 0
                        
                        return {
                            'amount_rub': amount_rub,
                            'amount_uzs': amount_uzs,
                            'exchange_rate': round(exchange_rate, 2),
                            'commission': first_commission.get('money', {}).get('acceptedTotalFee', {}),
                            'success': True,
                            'raw_response': data,
                            'payment_system': first_commission.get('nameCyrillic', 'Unknown')
                        }
                
                return None
                    
        except Exception as e:
            print(f"❌ Ошибка конвертации валюты: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def convert_rub_to_uzs_async(self, amount_rub: float) -> Optional[Dict]:
        """
        Асинхронная версия конвертации RUB -> UZS
        
        Args:
            amount_rub: Сумма в рублях
            
        Returns:
            Dict с результатом конвертации или None при ошибке
        """
        try:
            request_id = str(uuid.uuid4())
            session_id = str(uuid.uuid4())
            
            headers = {
                "accept": "application/json, text/plain, */*",
                "accept-language": "ru,en;q=0.9",
                "client-id": "multitransfer-web-id",
                "content-type": "application/json",
                "fhprequestid": request_id,
                "fhpsessionid": session_id,
                "x-request-id": request_id,
                "origin": "https://multitransfer.ru",
                "referer": "https://multitransfer.ru/"
            }
            
            payload = {
                "countryCode": "UZB",
                "range": "ALL_PLUS_LIMITS",
                "money": {
                    "acceptedMoney": {
                        "amount": amount_rub,
                        "currencyCode": "RUB"
                    },
                    "withdrawMoney": {
                        "currencyCode": "UZS"
                    }
                }
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/anonymous/multi/multitransfer-fee-calc/v3/commissions",
                    json=payload,
                    headers=headers
                )
                
                response.raise_for_status()
                data = response.json()
                
                # API возвращает массив fees с разными способами доставки
                # Берем первый вариант (to_card) и первую комиссию
                if "fees" in data and len(data["fees"]) > 0:
                    first_fee = data["fees"][0]
                    if "commissions" in first_fee and len(first_fee["commissions"]) > 0:
                        first_commission = first_fee["commissions"][0]
                        money_data = first_commission.get("money", {})
                        
                        amount_uzs_str = money_data.get("withdrawMoney", {}).get("amount", "0")
                        amount_uzs = float(amount_uzs_str)
                        
                        exchange_rate = amount_uzs / amount_rub if amount_rub > 0 else 0
                        
                        return {
                            'amount_rub': amount_rub,
                            'amount_uzs': amount_uzs,
                            'exchange_rate': round(exchange_rate, 2),
                            'commission': first_commission.get('money', {}).get('acceptedTotalFee', {}),
                            'success': True,
                            'raw_response': data,
                            'payment_system': first_commission.get('nameCyrillic', 'Unknown')
                        }
                else:
                    return None
                    
        except Exception as e:
            print(f"Ошибка конвертации валюты: {e}")
            return None


# Пример использования
if __name__ == "__main__":
    converter = CurrencyConverter()
    
    # Тест: конвертируем 5000 RUB в UZS
    result = converter.convert_rub_to_uzs(5000.0)
    
    if result:
        print(f"✅ Конвертация успешна:")
        print(f"   {result['amount_rub']} RUB = {result['amount_uzs']} UZS")
        print(f"   Курс: {result['exchange_rate']}")
        print(f"   Комиссия: {result['commission']}")
    else:
        print("❌ Ошибка конвертации")
