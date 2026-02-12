# webhook_tribute.py
from __future__ import annotations

import hmac
import hashlib
import logging
import time
from decimal import Decimal
from typing import Any, Dict, Optional, Callable, Awaitable

from fastapi import APIRouter, Request, HTTPException
from aiogram.enums import ParseMode

import config
from db import run_db_query
from tariffs import TARIFFS
from common import generate_invite_link
from services import async_log, notify_admins

from datetime import datetime, timedelta, timezone

router = APIRouter()
log = logging.getLogger(__name__)

UTC = timezone.utc

# ---------------- Идемпотентность (простая, в памяти процесса) ----------------

_SEEN: Dict[str, float] = {}
_DUP_TTL = 60 * 60  # храним id события 1 час


def _mark_and_check_duplicate(key: str) -> bool:
    """True = уже видели это событие недавно (дубликат)."""
    now = time.time()
    # чистим старое
    for k, ts in list(_SEEN.items()):
        if now - ts > _DUP_TTL:
            _SEEN.pop(k, None)
    if key in _SEEN:
        return True
    _SEEN[key] = now
    return False


# ---------------- Подпись TriBute ----------------

def _check_signature(secret: str, body: bytes, got_sig: str) -> bool:
    want = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest((got_sig or "").lower(), want.lower())


# ---------------- Сумма: minor units → RUB ----------------

def _amount_to_rub(value, currency: str = "RUB") -> int:
    """
    Tribute присылает amount в мелких единицах.
    Для RUB это копейки → делим на 100 и берём целые рубли.
    """
    try:
        minor = int(value)
    except Exception:
        try:
            minor = int(Decimal(str(value)))
        except Exception:
            return 0

    curr = (currency or "RUB").upper()
    if curr in {"RUB", "RUR"}:
        return minor // 100

    # если вдруг другая валюта — пока возвращаем как есть
    return minor


def _event_name(data: Dict[str, Any]) -> str:
    return (data.get("event") or data.get("name") or "").strip()


def _event_key(data: Dict[str, Any], body: bytes) -> str:
    """
    Ключ события для идемпотентности.
    Берём id из payload/data, если нет — sha256(body).
    """
    pid = (
        str(data.get("id") or "")
        or str((data.get("payload") or {}).get("id") or "")
    ).strip()
    if not pid:
        pid = hashlib.sha256(body).hexdigest()
    return pid


def _find_tariff_by_price(amount_rub: int) -> Optional[str]:
    """
    По сумме в рублях ищем тариф, у которого price == amount_rub.
    Если несколько — берём первый.
    """
    for key, v in TARIFFS.items():
        try:
            if int(v.get("price", 0)) == int(amount_rub):
                return key
        except Exception:
            continue
    return None


async def _grant_subscription(user_id: int, tariff: str, amount_rub: int, request: Request):
    """
    Выдаём / продлеваем подписку пользователю и шлём простое уведомление.
    """
    bot = request.app.state.bot  # как в твоём примере с Tribute

    seconds = TARIFFS[tariff]["seconds"]
    now = datetime.now(UTC)
    end_date = now + timedelta(seconds=seconds)

    # создаём инвайт в канал
    invite_link = await generate_invite_link(bot, user_id, tariff)

    # users: access=1, новая дата, ссылка, payment_id пометим как TRIBUTE
    await run_db_query(
        """
        INSERT OR REPLACE INTO users (user_id, tariff, end_date, access, invite_link, payment_id, reminded)
        VALUES (?, ?, ?, 1, ?, ?, 0)
        """,
        (
            user_id,
            tariff,
            end_date.strftime("%Y-%m-%d %H:%M:%S"),
            invite_link,
            f"TRIBUTE:{int(time.time())}",
        ),
    )

    # лог в payments
    await run_db_query(
        """
        INSERT INTO payments (user_id, amount, tariff, date, yookassa_payment_id)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            user_id,
            amount_rub,
            tariff,
            now.strftime("%Y-%m-%d %H:%M:%S"),
            f"TRIBUTE:{int(time.time())}",
        ),
    )

    # уведомление юзеру
    caption = (
        "🎉 <b>Оплата через TriBute успешна!</b>\n"
        f"Тариф: {TARIFFS[tariff]['duration']}\n"
        f"🔗 Ссылка: {invite_link}"
    )
    try:
        await bot.send_message(user_id, caption, parse_mode=ParseMode.HTML)
    except Exception as e:
        await async_log("ERROR", f"TriBute: не смог отправить сообщение юзеру {user_id}: {e}")

    # уведомление админам (чтобы всё было в едином стиле)
    try:
        await notify_admins(bot, user_id, tariff, amount_rub, "tribute")
    except Exception as e:
        await async_log("ERROR", f"TriBute: notify_admins failed: {e}")


@router.post("/webhook/tribute")
async def tribute_webhook(request: Request):
    if not config.TRIBUTE_API_KEY:
        raise HTTPException(500, "TRIBUTE_API_KEY not set")

    sig = request.headers.get("trbt-signature", "")
    body = await request.body()

    # 1) подпись
    if not _check_signature(config.TRIBUTE_API_KEY, body, sig):
        log.warning("TriBute: bad signature")
        raise HTTPException(401, "bad signature")

    data = await request.json()
    event = _event_name(data)
    payload = data.get("payload") or {}

    # 2) идемпотентность
    if _mark_and_check_duplicate(_event_key(data, body)):
        log.info("TriBute: duplicate webhook ignored (%s)", event)
        return {"ok": True, "duplicate": True}

    # 3) полезные поля
    user_id = payload.get("telegram_user_id") or data.get("telegram_user_id")
    try:
        user_id = int(user_id)
    except Exception:
        user_id = None

    raw_amount = payload.get("amount") or data.get("amount") or 0
    currency = payload.get("currency") or data.get("currency") or "RUB"
    amount_rub = _amount_to_rub(raw_amount, currency)

    if not user_id:
        log.warning("TriBute: no telegram_user_id in payload: %s", data)
        return {"ok": True}

    log.info(
        "TriBute payment: event=%s raw_amount=%s %s -> %s RUB (user=%s)",
        event,
        raw_amount,
        currency,
        amount_rub,
        user_id,
    )

    # 4) успешные события оплаты
    if event in {"payment.succeeded", "subscription.paid", "new_subscription"}:
        tariff = _find_tariff_by_price(amount_rub)
        if not tariff:
            await async_log(
                "ERROR",
                f"TriBute: не нашёл тариф по сумме {amount_rub} RUB (user={user_id})",
            )
            return {"ok": True, "no_tariff": True}

        await _grant_subscription(user_id, tariff, amount_rub, request)
    else:
        log.info("TriBute: ignored event %s", event)

    return {"ok": True}
