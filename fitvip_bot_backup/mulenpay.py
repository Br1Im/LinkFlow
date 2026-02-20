from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, List, Literal, Optional, Union

import httpx


# -----------------------
# Errors
# -----------------------

class MulenPayError(RuntimeError):
    def __init__(self, message: str, status_code: Optional[int] = None, payload: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


def _raise_for_api(resp: httpx.Response) -> None:
    if 200 <= resp.status_code < 300:
        return
    try:
        payload = resp.json()
    except Exception:
        payload = resp.text
    raise MulenPayError(f"HTTP {resp.status_code}: {payload}", status_code=resp.status_code, payload=payload)


# -----------------------
# Helpers
# -----------------------

JsonDict = Dict[str, Any]
Subscribe = Optional[Literal["Day", "Week", "Month"]]

_AMOUNT_RE = re.compile(r"^(0|[1-9]\d*)(\.\d+)?$")  # JSON-number без экспоненты


def _auth_headers(private_key2: str) -> Dict[str, str]:
    k = (private_key2 or "").strip()
    if not k:
        raise ValueError("private_key2 пустой (должен приходить из хендлера)")
    v = k if k.lower().startswith("bearer ") else f"Bearer {k}"
    return {"Authorization": v}


def _ensure_amount_str(amount: Union[str, int, Decimal]) -> str:
    """
    Возвращает amount в виде строки, пригодной:
      1) для sign (точное представление)
      2) для JSON number токена (без кавычек)
    """
    if isinstance(amount, int):
        s = str(amount)
    elif isinstance(amount, Decimal):
        s = format(amount, "f")  # без scientific notation
    elif isinstance(amount, str):
        s = amount.strip()
    else:
        raise TypeError("amount должен быть Union[str, int] | Decimal")

    if not s or not _AMOUNT_RE.match(s):
        raise ValueError(f"amount имеет недопустимый формат для JSON number: {s!r}")
    return s


def calculate_sign(secret_key: str, *, currency: str, amount_str: str, shopId: str) -> str:
    """
    sign = sha1(currency + amount + shopId + secret_key)

    Важно:
    - amount_str — строка ровно в том виде, как она уедет в JSON (например "100.50")
    - shopId — строка
    - secret_key строго ПОСЛЕДНИМ
    """
    sk = (secret_key or "").strip()
    if not sk:
        raise ValueError("secret_key пустой")

    c = (currency or "").strip().lower()
    if not c:
        raise ValueError("currency пустой")

    sid = (shopId or "").strip()
    if not sid:
        raise ValueError("shopId пустой")

    raw = f"{c}{amount_str}{sid}{sk}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def build_default_items(*, order_id: str, amount: Union[str, int, Decimal]) -> List[JsonDict]:
    a = _ensure_amount_str(amount)
    return [
        {
            "description": f"Заказ #{order_id}",
            "quantity": 1,
            "price": a,              # строкой, чтобы сохранить "100.50"
            "vat_code": 0,
            "payment_subject": 1,
            "payment_mode": 1,
        }
    ]


def _validate_items(items: List[JsonDict]) -> None:
    if not isinstance(items, list) or len(items) == 0:
        raise ValueError("items обязателен и должен быть непустым массивом объектов")
    required = {"description", "quantity", "price", "vat_code", "payment_subject", "payment_mode"}
    for i, it in enumerate(items):
        if not isinstance(it, dict) or not it:
            raise ValueError(f"items[{i}] должен быть непустым объектом")
        missing = required - set(it.keys())
        if missing:
            raise ValueError(f"items[{i}] не хватает полей: {sorted(missing)}")

        if isinstance(it["price"], str):
            _ensure_amount_str(it["price"])

        if not isinstance(it["quantity"], int):
            raise ValueError(f"items[{i}].quantity должен быть int")

        for k in ("vat_code", "payment_subject", "payment_mode"):
            if not isinstance(it[k], int):
                raise ValueError(f"items[{i}].{k} должен быть int")


def _json_with_raw_numbers(payload: JsonDict, raw_number_fields: List[str]) -> str:
    """
    Делаем JSON, где указанные поля (верхнего уровня) вставляются как raw number токены (без кавычек),
    сохраняя точное текстовое представление (например 100.50).
    """
    sentinel_prefix = "__RAWNUM__"

    raw_map: Dict[str, str] = {}
    for f in raw_number_fields:
        if f in payload:
            v = payload[f]
            if isinstance(v, str):
                raw_map[f] = _ensure_amount_str(v)
            elif isinstance(v, (int, Decimal)):
                raw_map[f] = _ensure_amount_str(v)
            else:
                raise TypeError(f"Поле {f} должно быть str|int|Decimal, сейчас: {type(v)}")
            payload[f] = f"{sentinel_prefix}{f}"

    if isinstance(payload.get("items"), list):
        for it in payload["items"]:
            if isinstance(it.get("price"), str):
                _ensure_amount_str(it["price"])
                it["price"] = f"{sentinel_prefix}items.price:{it['price']}"

    s = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

    for f, raw in raw_map.items():
        s = s.replace(f"\"{sentinel_prefix}{f}\"", raw)

    def _replace_item_price(match: re.Match) -> str:
        return match.group(1)

    s = re.sub(r"\"__RAWNUM__items\.price:(" + _AMOUNT_RE.pattern[1:-1] + r")\"", _replace_item_price, s)
    return s


# -----------------------
# Client (create + get)
# -----------------------

@dataclass
class MulenPayClient:
    """
    Реальный endpoint:
      POST https://mulenpay.ru/api/v2/payments
      GET  https://mulenpay.ru/api/v2/payments/{id}
    """
    secret_key: str
    timeout: float = 20.0
    # FIX: базовый URL должен включать /api/v2
    base_url: str = "https://mulenpay.ru/api/v2"

    def __post_init__(self) -> None:
        self.secret_key = (self.secret_key or "").strip()
        if not self.secret_key:
            raise ValueError("secret_key пустой")

        self.base_url = (self.base_url or "").rstrip("/")
        if not self.base_url.startswith("http"):
            raise ValueError("base_url должен начинаться с http(s)://")

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            follow_redirects=False,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def create_payment(
        self,
        *,
        private_key2: str,
        currency: str,
        amount: Union[str, int, Decimal],
        uuid: str,
        shopId: str,
        description: str,
        items: Optional[List[JsonDict]] = None,
    ) -> JsonDict:
        c = (currency or "").strip().lower()
        if not c:
            raise ValueError("currency пустой (ожидается lowercase строка)")

        sid = (shopId or "").strip()
        if not sid:
            raise ValueError("shopId пустой")

        desc = (description or "").strip()
        if not desc:
            raise ValueError("description обязателен и не должен быть пустым")

        amount_str = _ensure_amount_str(amount)

        if items is None:
            items = build_default_items(order_id=uuid, amount=amount_str)
        _validate_items(items)

        payload: JsonDict = {
            "currency": c,
            "amount": amount_str,   # сначала строка, потом raw number
            "uuid": uuid,
            "shopId": sid,
            "description": desc,
            "items": items,
        }

        payload["sign"] = calculate_sign(
            self.secret_key,
            currency=c,
            amount_str=amount_str,
            shopId=sid,
        )

        body = _json_with_raw_numbers(payload, raw_number_fields=["amount"])

        # FIX: путь /payments (потому что base_url уже /api/v2)
        resp = await self._client.post(
            "/payments",
            content=body,
            headers=_auth_headers(private_key2),
        )
        _raise_for_api(resp)
        return resp.json()

    async def get_payment(self, *, private_key2: str, payment_id: Union[int, str]) -> JsonDict:
        pid = int(payment_id)
        if pid <= 0:
            raise ValueError("payment_id должен быть положительным")

        # FIX: путь /payments/{id}
        resp = await self._client.get(
            f"/payments/{pid}",
            headers=_auth_headers(private_key2),
        )
        _raise_for_api(resp)
        return resp.json()