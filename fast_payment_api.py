# -*- coding: utf-8 -*-
"""
Быстрое создание платежей через прямые API запросы
Скорость: ~1 секунда вместо 3-5 секунд через Selenium
"""

import requests
import json
import time
from typing import Optional, Dict

class FastPaymentAPI:
    """API клиент для быстрого создания платежей"""
    
    BASE_URL = "https://1.elecsnet.ru/NotebookFront"
    
    def __init__(self, session: Optional[requests.Session] = None):
        self.session = session or requests.Session()
        self.headers = {
            "accept": "*/*",
            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "sec-ch-ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-requested-with": "XMLHttpRequest",
            "referer": "https://1.elecsnet.ru/",
            "origin": "https://1.elecsnet.ru"
        }
    
    def format_req_id(self, card_number: str, owner_name: str, amount: float) -> Dict:
        """Шаг 1: Форматирование данных платежа"""
        url = f"{self.BASE_URL}/services/0mhp/formatReqId"
        
        amount_formatted = f"{int(amount):,}".replace(",", " ")
        
        data = {
            "merchantId": "36924",
            "paymentTool": "205",
            "merchantFields[1]": card_number,
            "merchantFields[2]": owner_name,
            "merchantFields[3]": "Непокрытый Дмитрий Евгеньевич",
            "merchantFields[4]": "03.07.2000",
            "merchantFields[5]": "RU",
            "merchantFields[6]": "1820657875",
            "amount": amount_formatted,
            "bill": "",
            "comment": "",
            "clientId": ""
        }
        
        try:
            response = self.session.post(url, headers=self.headers, data=data, timeout=10)
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def log_redirect(self, params_json: str) -> Dict:
        """Шаг 2: Создание платежа"""
        url = f"{self.BASE_URL}/services/0mhp/logredirect"
        
        data = {
            "url": "/SBP/default.aspx",
            "paramsJson": params_json
        }
        
        try:
            response = self.session.post(url, headers=self.headers, data=data, timeout=10)
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_sbp_payment(self, params: Dict) -> Dict:
        """Шаг 3: Получение QR кода и ссылки СБП"""
        url = f"{self.BASE_URL}/SBP/default.aspx"
        
        try:
            response = self.session.get(url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                html = response.text
                
                import re
                qr_match = re.search(r'<img[^>]+id="Image1"[^>]+src="([^"]+)"', html)
                link_match = re.search(r'<a[^>]+id="LinkMobil"[^>]+href="([^"]+)"', html)
                
                if qr_match and link_match:
                    return {
                        "success": True,
                        "qr_base64": qr_match.group(1),
                        "payment_link": link_match.group(1)
                    }
                else:
                    return {"success": False, "error": "QR или ссылка не найдены"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_payment(self, card_number: str, owner_name: str, amount: float) -> Dict:
        """Полный цикл создания платежа"""
        start_time = time.time()
        
        print(f"🚀 Создание платежа через API...", flush=True)
        
        # Шаг 1: formatReqId
        print(f"1️⃣ formatReqId...", flush=True)
        format_result = self.format_req_id(card_number, owner_name, amount)
        
        if not format_result.get("success"):
            return {
                "success": False,
                "error": f"formatReqId: {format_result.get('error')}",
                "elapsed_time": time.time() - start_time
            }
        
        data = format_result["data"]
        reqid = data.get("reqid")
        sign = data.get("sign")
        sign_time = data.get("signTime")
        user_id = data.get("userId", 0)
        ans_id = data.get("ansId", "")
        
        print(f"   ✅ reqid: {reqid[:30]}...", flush=True)
        
        if not reqid or not sign:
            return {
                "success": False,
                "error": "reqid или sign не найдены",
                "elapsed_time": time.time() - start_time
            }
        
        # Формируем paramsJson
        amount_formatted = f"{amount:,.2f}".replace(",", " ")
        
        params_json = {
            "ansId": ans_id,
            "walletId": reqid,
            "amount": amount_formatted,
            "totalSum": amount_formatted,
            "comission": "0,00",
            "payment_id": 205,
            "merchant_id": 36924,
            "form_name": "сайт Элекснет;Каталог (05.2015)",
            "merchant_code": "SRX",
            "back_url": "https://1.elecsnet.ru/NotebookFront/services/0mhp/result",
            "sign": sign,
            "sign_time": sign_time,
            "sender_user_id": user_id,
            "comment": None
        }
        
        # Шаг 2: logredirect
        print(f"2️⃣ logredirect...", flush=True)
        redirect_result = self.log_redirect(json.dumps(params_json, ensure_ascii=False))
        
        if not redirect_result.get("success"):
            return {
                "success": False,
                "error": f"logredirect: {redirect_result.get('error')}",
                "elapsed_time": time.time() - start_time
            }
        
        redirect_data = redirect_result["data"]
        print(f"   ✅ Redirect получен", flush=True)
        
        # Шаг 3: Получаем QR и ссылку
        print(f"3️⃣ Получение QR и ссылки...", flush=True)
        payment_result = self.get_sbp_payment(redirect_data.get("params", {}))
        
        if not payment_result.get("success"):
            return {
                "success": False,
                "error": f"get_sbp_payment: {payment_result.get('error')}",
                "elapsed_time": time.time() - start_time
            }
        
        elapsed = time.time() - start_time
        print(f"✅ Платеж создан за {elapsed:.2f} сек!", flush=True)
        
        return {
            "success": True,
            "payment_link": payment_result["payment_link"],
            "qr_base64": payment_result["qr_base64"],
            "elapsed_time": elapsed
        }


def test_fast_api():
    """Тест быстрого API"""
    print("\n" + "="*60)
    print("🧪 ТЕСТ БЫСТРОГО API")
    print("="*60)
    
    api = FastPaymentAPI()
    
    result = api.create_payment(
        card_number="9860100125857258",
        owner_name="IZZET SAMEKEEV",
        amount=2000
    )
    
    print("\n" + "="*60)
    print("📊 РЕЗУЛЬТАТ:")
    print("="*60)
    
    if result.get("success"):
        print(f"✅ Успех!")
        print(f"⏱ Время: {result['elapsed_time']:.2f} сек")
        print(f"🔗 Ссылка: {result['payment_link']}")
        print(f"📷 QR: {result['qr_base64'][:100]}...")
    else:
        print(f"❌ Ошибка: {result.get('error')}")
        print(f"⏱ Время: {result.get('elapsed_time', 0):.2f} сек")


if __name__ == "__main__":
    test_fast_api()
