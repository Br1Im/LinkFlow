#!/usr/bin/env python3
"""
ЧИСТЫЙ API для multitransfer.ru
Только основные методы без лишнего кода
"""

import requests
import uuid
from typing import Optional

class MultitransferAPI:
    def __init__(self, fhp_token: str):
        self.session = requests.Session()
        self.api_base = "https://api.multitransfer.ru"
        self.fhp_token = fhp_token
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:147.0) Gecko/20100101 Firefox/147.0",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Client-Id": "multitransfer-web-id"
        }
    
    def _get_headers(self, with_token: bool = True) -> dict:
        headers = self.headers.copy()
        headers.update({
            "X-Request-Id": str(uuid.uuid4()),
            "FhpSessionId": str(uuid.uuid4()),
            "FhpRequestId": str(uuid.uuid4())
        })
        
        if with_token and self.fhp_token:
            headers["fhptokenid"] = self.fhp_token
        
        return headers
    
    def get_commissions(self, amount: float) -> Optional[str]:
        """Получает commission_id для создания платежа"""
        url = f"{self.api_base}/anonymous/multi/multitransfer-fee-calc/v3/commissions"
        
        payload = {
            "countryCode": "UZB",
            "range": "ALL_PLUS_LIMITS",
            "money": {
                "acceptedMoney": {"amount": amount, "currencyCode": "RUB"},
                "withdrawMoney": {"currencyCode": "UZS"}
            }
        }
        
        response = self.session.post(url, json=payload, headers=self._get_headers(with_token=False))
        
        if response.status_code == 200:
            data = response.json()
            fees = data.get("fees", [])
            if fees and fees[0].get("commissions"):
                return fees[0]["commissions"][0]["commissionId"]
        
        return None
    
    def create_payment(self, commission_id: str, card_number: str, recipient_name: str) -> Optional[str]:
        """Создает платеж и возвращает transaction_id"""
        url = f"{self.api_base}/anonymous/multi/multitransfer-transfer-create/v3/anonymous/transfers/create"
        
        name_parts = recipient_name.split()
        first_name = name_parts[0] if name_parts else "Nodir"
        last_name = name_parts[1] if len(name_parts) > 1 else "Asadullayev"
        
        payload = {
            "beneficiary": {"lastName": last_name, "firstName": first_name},
            "transfer": {
                "beneficiaryAccountNumber": card_number,
                "commissionId": commission_id,
                "paymentInstrument": {"type": "ANONYMOUS_CARD"}
            },
            "sender": {
                "lastName": "Непокрытый", "firstName": "Дмитрий",
                "phoneNumber": "79880260334", "birthDate": "2000-07-03T12:00:00",
                "addresses": {
                    "birthPlaceAddress": {"full": "Камыш", "countryCode": "RUS"},
                    "registrationAddress": {"full": "Камыш", "countryCode": "RUS"}
                },
                "documents": [{
                    "type": "21", "number": "657875", "series": "1820",
                    "issueDate": "2020-07-22T12:00:00", "countryCode": "RUS"
                }]
            }
        }
        
        response = self.session.post(url, json=payload, headers=self._get_headers(with_token=True))
        
        if response.status_code == 200:
            return response.json()["transferId"]
        
        return None
    
    def get_qr_link(self, transaction_id: str) -> Optional[str]:
        """Получает QR-ссылку по transaction_id"""
        url = f"{self.api_base}/anonymous/multi/multitransfer-qr-processing/v3/anonymous/confirm"
        
        payload = {"transactionId": transaction_id, "recordType": "transfer"}
        
        response = self.session.post(url, json=payload, headers=self._get_headers(with_token=False))
        
        if response.status_code == 200:
            return response.json()["externalData"]["payload"]
        
        return None
    
    def create_qr_payment(self, card_number: str, recipient_name: str, amount: float) -> Optional[str]:
        """Полный процесс: создает платеж и возвращает QR-ссылку"""
        # 1. Получаем комиссии
        commission_id = self.get_commissions(amount)
        if not commission_id:
            return None
        
        # 2. Создаем платеж
        transaction_id = self.create_payment(commission_id, card_number, recipient_name)
        if not transaction_id:
            return None
        
        # 3. Получаем QR-ссылку
        return self.get_qr_link(transaction_id)