"""
MulenPay minimal async client (ONE FILE)
- Create payment: POST /v2/payments
- Get payment:    GET  /v2/payments/{id}

Requirements:
  pip install httpx pydantic

Notes:
- sign = sha1(currency + amount + shopId + secret_key)
- amount MUST be a string exactly as sent (e.g. "1000.50")
- Auth header: by default uses Authorization: <api_key> (no Bearer).
  If your account requires Bearer, set AUTH_SCHEME = "Bearer".
  If your account requires X-Api-Key, set AUTH_HEADER_NAME = "X-Api-Key" and AUTH_SCHEME = "".
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel, Field


# =========================
# Config
# =========================

BASE_URL = "https://mulenpay.ru/api/v2"

AUTH_HEADER_NAME = ""  # or "X-Api-Key"
AUTH_SCHEME = ""                   # "" (raw key) or "Bearer"


# =========================
# Errors
# =========================

class MulenPayError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None, payload: Any = None):
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


# =========================
# Schemas
# =========================

class CreatePayment(BaseModel):
    currency: str
    amount: str = Field(..., description='String amount, e.g. "1000.50"')
    uuid: str
    shopId: int
    description: str
    website_url: Optional[str] = None
    subscribe: Any = None
    holdTime: Any = None
    language: str = "ru"
    items: List[Dict[str, Any]] = Field(default_factory=list)


# =========================
# Sign
# =========================

def calculate_sign(secret_key: str, *, currency: str, amount: str, shopId: int) -> str:
    if not isinstance(amount, str):
        raise TypeError("amount must be a string (e.g. '1000.50') to avoid signature mismatch")
    raw = f"{currency}{amount}{shopId}{secret_key}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


# =========================
# Client
# =========================

@dataclass
class MulenPayClient:
    api_key: str
    secret_key: str
    base_url: str = BASE_URL
    timeout: float = 20.0

    auth_header_name: str = AUTH_HEADER_NAME
    auth_scheme: str = AUTH_SCHEME

    def __post_init__(self) -> None:
        self.api_key = (self.api_key or "").strip()
        self.secret_key = (self.secret_key or "").strip()
        if not self.api_key:
            raise ValueError("api_key is empty")
        if not self.secret_key:
            raise ValueError("secret_key is empty")

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        headers[self.auth_header_name] = f"{self.auth_scheme} {self.api_key}".strip()

        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout, headers=headers)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def create_payment(self, data: CreatePayment) -> Dict[str, Any]:
        payload = data.model_dump()
        payload["sign"] = calculate_sign(
            self.secret_key,
            currency=payload["currency"],
            amount=payload["amount"],
            shopId=payload["shopId"],
        )

        resp = await self._client.post("/payments", json=payload)
        _raise_for_api(resp)
        return resp.json()

    async def get_payment(self, payment_id: int) -> Dict[str, Any]:
        resp = await self._client.get(f"/payments/{payment_id}")
        _raise_for_api(resp)
        return resp.json()