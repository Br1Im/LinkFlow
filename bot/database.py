import json
import os
from typing import Set, Dict, Optional
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(__file__), "bot_database.json")

class Database:
    def __init__(self):
        self.data = self._load()

    def _load(self) -> dict:
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self._default_data()
        return self._default_data()

    def _default_data(self) -> dict:
        return {
            "super_admin": None,
            "admins": [],
            "accounts": [],
            "requisites": [],
            "payments": [],
            "orders": [],  # Новое поле для webhook заказов
            "statistics": {
                "total_payments": 0,
                "total_amount": 0,
                "by_requisite": {},
                "by_admin": {}
            }
        }

    def _save(self):
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def set_super_admin(self, user_id: int):
        self.data["super_admin"] = user_id
        self._save()

    def get_super_admin(self) -> Optional[int]:
        return self.data.get("super_admin")

    def is_super_admin(self, user_id: int) -> bool:
        return self.data.get("super_admin") == user_id

    def add_admin(self, user_id: int) -> bool:
        if user_id not in self.data["admins"]:
            self.data["admins"].append(user_id)
            self._save()
            return True
        return False

    def remove_admin(self, user_id: int) -> bool:
        if user_id in self.data["admins"]:
            self.data["admins"].remove(user_id)
            self._save()
            return True
        return False

    def is_admin(self, user_id: int) -> bool:
        return user_id in self.data["admins"] or self.is_super_admin(user_id)

    def get_admins(self) -> list:
        return self.data["admins"]

    def add_account(self, phone: str, password: str) -> int:
        account = {
            "phone": phone,
            "password": password,
            "status": "not_checked",
            "last_check": None,
            "profile_path": f"profile_{phone.replace('+', '').replace(' ', '')}"
        }
        self.data["accounts"].append(account)
        self._save()
        return len(self.data["accounts"]) - 1

    def update_account_status(self, index: int, status: str, error_msg: str = None):

        if 0 <= index < len(self.data["accounts"]):
            self.data["accounts"][index]["status"] = status
            self.data["accounts"][index]["last_check"] = datetime.now().isoformat()
            if error_msg:
                self.data["accounts"][index]["error"] = error_msg
            self._save()
            return True
        return False

    def remove_account(self, index: int) -> bool:
        if 0 <= index < len(self.data["accounts"]):
            self.data["accounts"].pop(index)
            self._save()
            return True
        return False

    def get_accounts(self) -> list:
        return self.data["accounts"]

    def get_account(self, index: int) -> Optional[dict]:
        if 0 <= index < len(self.data["accounts"]):
            return self.data["accounts"][index]
        return None

    def add_requisite(self, card_number: str, owner_name: str) -> int:
        requisite = {"card_number": card_number, "owner_name": owner_name}
        self.data["requisites"].append(requisite)
        self._save()
        return len(self.data["requisites"]) - 1

    def remove_requisite(self, index: int) -> bool:
        if 0 <= index < len(self.data["requisites"]):
            self.data["requisites"].pop(index)
            self._save()
            return True
        return False

    def get_requisites(self) -> list:
        return self.data["requisites"]

    def get_requisite(self, index: int) -> Optional[dict]:
        if 0 <= index < len(self.data["requisites"]):
            return self.data["requisites"][index]
        return None

    def add_payment(self, admin_id: int, card_number: str, owner_name: str, amount: float, payment_link: str):

        payment = {
            "id": len(self.data["payments"]) + 1,
            "admin_id": admin_id,
            "card_number": card_number,
            "owner_name": owner_name,
            "amount": amount,
            "payment_link": payment_link,
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S")
        }

        self.data["payments"].append(payment)


        stats = self.data["statistics"]
        stats["total_payments"] += 1
        stats["total_amount"] += amount


        requisite_key = f"{card_number}_{owner_name}"
        if requisite_key not in stats["by_requisite"]:
            stats["by_requisite"][requisite_key] = {
                "card_number": card_number,
                "owner_name": owner_name,
                "count": 0,
                "total_amount": 0
            }
        stats["by_requisite"][requisite_key]["count"] += 1
        stats["by_requisite"][requisite_key]["total_amount"] += amount


        admin_key = str(admin_id)
        if admin_key not in stats["by_admin"]:
            stats["by_admin"][admin_key] = {
                "count": 0,
                "total_amount": 0
            }
        stats["by_admin"][admin_key]["count"] += 1
        stats["by_admin"][admin_key]["total_amount"] += amount

        self._save()
        return payment["id"]

    def get_payments(self, limit: int = None) -> list:

        payments = self.data.get("payments", [])
        if limit:
            return payments[-limit:]
        return payments

    def get_statistics(self) -> dict:

        return self.data.get("statistics", {
            "total_payments": 0,
            "total_amount": 0,
            "by_requisite": {},
            "by_admin": {}
        })

    def get_admin_statistics(self, admin_id: int) -> dict:

        stats = self.get_statistics()
        admin_key = str(admin_id)

        return stats["by_admin"].get(admin_key, {
            "count": 0,
            "total_amount": 0
        })

    # Методы для работы с заказами через webhook
    def save_order(self, order_data: dict):
        """Сохранение заказа от webhook"""
        if "orders" not in self.data:
            self.data["orders"] = []
        
        self.data["orders"].append(order_data)
        self._save()

    def get_order_by_id(self, order_id: str) -> Optional[dict]:
        """Получение заказа по ID"""
        if "orders" not in self.data:
            return None
        
        for order in self.data["orders"]:
            if order.get("order_id") == order_id:
                return order
        return None

    def update_order_status(self, order_id: str, status: str) -> bool:
        """Обновление статуса заказа"""
        if "orders" not in self.data:
            return False
        
        for order in self.data["orders"]:
            if order.get("order_id") == order_id:
                order["status"] = status
                order["updated_at"] = datetime.now().isoformat()
                self._save()
                return True
        return False

    def get_orders(self, limit: int = None) -> list:
        """Получение списка заказов"""
        orders = self.data.get("orders", [])
        if limit:
            return orders[-limit:]
        return orders

db = Database()
