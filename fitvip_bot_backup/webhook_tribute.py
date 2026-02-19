# webhook_tribute.py
import hmac
import hashlib
import logging
import time
from decimal import Decimal
from typing import Any, Dict

from fastapi import FastAPI, Request, HTTPException

from aiogram import Bot
from aiogram.enums import ParseMode

import config
from tariffs import TARIFFS
from db import run_db_query, init_db
from common import generate_invite_link
from services import async_log

log = logging.getLogger("tribute_webhook")

app = FastAPI(title="TriBute webhook")

# --- aiogram-бот, только для отправки сообщений / инвайтов из вебхука ---
BOT = Bot(token=config.API_TOKEN, parse_mode=ParseMode.HTML)
app.state.bot = BOT  # чтобы при желании брать bot из request.app.state.bot

# --- идемпотентность (защита от повторных событий) ---
_SEEN: Dict[str, float] = {}
_DUP_TTL = 60 * 60  # 1 час


def _mark_and_check_duplicate(key: str) -> bool:
    """True = уже видели это событие недавно (дубликат)."""
    now = time.time()
    # подчистим старые
    for k, ts in list(_SEEN.items()):
        if now - ts > _DUP_TTL:
            _SEEN.pop(k, None)
    if key in _SEEN:
        return True
    _SEEN[key] = now
    return False


# --- подпись TriBute ---
def _check_signature(secret: str, body: bytes, got_sig: str) -> bool:
    expect = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest((got_sig or "").lower(), expect.lower())


# --- конвертация суммы ---
def _amount_to_rub(value: Any, currency: str = "RUB") -> int:
    """
    Tribute шлёт amount в "minor units".
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

    # если другая валюта — тут можно расширить при необходимости
    return minor


def _event_name(data: Dict[str, Any]) -> str:
    return (data.get("event") or data.get("name") or "").strip()


def _event_key(data: Dict[str, Any], body: bytes) -> str:
    """
    Ключ события для идемпотентности:
    сначала пробуем id/payload.id, иначе sha256(body).
    """
    pid = (
        str(data.get("id") or "")
        or str((data.get("payload") or {}).get("id") or "")
    ).strip()
    if not pid:
        pid = hashlib.sha256(body).hexdigest()
    return pid


def _guess_tariff_by_amount(amount_rub: int) -> str]:
    """
    Маппинг "сумма ₽" -> тариф из TARIFFS.
    1) точное совпадение по price
    2) если нет — берём самый дорогой тариф, цена которого <= amount
    3) если всё совсем мимо — берём первый попавшийся тариф.
    """
    if not TARIFFS:
        return None

    # 1) точное совпадение
    for key, cfg in TARIFFS.items():
        try:
            if int(cfg.get("price", 0)) == int(amount_rub):
                return key
        except Exception:
            continue

    # 2) max price <= amount
    best_key = None
    best_price = -1
    for key, cfg in TARIFFS.items():
        try:
            price = int(cfg.get("price", 0))
        except Exception:
            continue
        if price <= amount_rub and price > best_price:
            best_price = price
            best_key = key

    if best_key:
        return best_key

    # 3) fallback — первый тариф
    return next(iter(TARIFFS.keys()))


async def _grant_subscription(bot: Bot, user_id: int, tariff_key: str, amount_rub: int, ext_id: str):
    """
    Выдаём/продлеваем подписку пользователю и пишем в БД платеж.
    """
    cfg = TARIFFS.get(tariff_key)
    if not cfg:
        raise RuntimeError(f"tariff '{tariff_key}' not found")

    seconds = int(cfg["seconds"])
    from datetime import datetime, timezone, timedelta

    now_utc = datetime.now(timezone.utc)

    # смотрим, была ли уже активная подписка
    row = await run_db_query(
        "SELECT end_date, access FROM users WHERE user_id = ?",
        (user_id,),
        fetchone=True,
    )

    if row and row[0]:
        from datetime import datetime as _dt
        try:
            prev_end = _dt.strptime(row[0], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        except Exception:
            prev_end = now_utc
        base = prev_end if row[1] and prev_end > now_utc else now_utc
    else:
        base = now_utc

    new_end = base + timedelta(seconds=seconds)

    # генерируем инвайт
    invite_link = await generate_invite_link(bot, user_id, tariff_key)

    # пишем/обновляем users
    await run_db_query(
        """
        INSERT OR REPLACE INTO users (user_id, tariff, end_date, access, invite_link, payment_id, reminded)
        VALUES (?, ?, ?, 1, ?, ?, 0)
        """,
        (
            user_id,
            tariff_key,
            new_end.strftime("%Y-%m-%d %H:%M:%S"),
            invite_link,
            f"TRIBUTE:{ext_id}",
        ),
    )

    # лог в payments (без использования колонок под YooKassa / TON)
    await run_db_query(
        """
        INSERT INTO payments (user_id, amount, tariff, date, yookassa_payment_id, ton_comment)
        VALUES (?, ?, ?, ?, NULL, NULL)
        """,
        (
            user_id,
            float(amount_rub),
            tariff_key,
            now_utc.strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )

    # сообщение пользователю
    caption = (
        "🎉 <b>Оплата через TriBute успешна!</b>\n"
        f"Тариф: <b>{cfg['duration']}</b>\n"
        f"Сумма: <b>{amount_rub} ₽</b>\n\n"
        f"🔗 Ваша ссылка для входа: {invite_link}"
    )
    await bot.send_message(user_id, caption)

    # можно уведомить админов, если хочешь
    try:
        from services import notify_admins  # чтобы не тянуть циклически сверху
        await notify_admins(bot, user_id, tariff_key, amount_rub, "tribute")
    except Exception as e:
        await async_log("ERROR", f"notify_admins for TriBute failed: {e}")


@app.on_event("startup")
async def _on_startup():
    # инициализируем БД, чтобы таблицы точно были
    await init_db()
    await async_log("INFO", "TriBute webhook started")


@app.post("/webhook/tribute")
async def tribute_webhook(request: Request):
    if not getattr(config, "TRIBUTE_API_KEY", None):
        raise HTTPException(500, "TRIBUTE_API_KEY not set")

    sig = request.headers.get("trbt-signature", "")
    body = await request.body()

    # 1) проверка подписи
    if not _check_signature(config.TRIBUTE_API_KEY, body, sig):
        await async_log("WARNING", "TriBute: bad signature")
        raise HTTPException(401, "bad signature")

    data = await request.json()
    event = _event_name(data)
    payload = data.get("payload") or {}

    # 2) идемпотентность
    if _mark_and_check_duplicate(_event_key(data, body)):
        log.info("TriBute: duplicate webhook ignored (%s)", event)
        return {"ok": True, "duplicate": True}

    # 3) достаём основные поля
    user_id = payload.get("telegram_user_id") or data.get("telegram_user_id")
    try:
        user_id = int(user_id)
    except Exception:
        user_id = None

    raw_amount = payload.get("amount") or data.get("amount") or 0
    currency = payload.get("currency") or data.get("currency") or "RUB"
    amount_rub = _amount_to_rub(raw_amount, currency)

    if not user_id:
        await async_log("WARNING", f"TriBute: no telegram_user_id in payload: {data}")
        return {"ok": True}

    await async_log(
        "INFO",
        f"TriBute payment: event={event} raw_amount={raw_amount} {currency} -> {amount_rub} RUB (user={user_id})",
    )

    # 4) успешные события
    if event in {"payment.succeeded", "subscription.paid", "new_subscription"}:
        tariff_key = _guess_tariff_by_amount(amount_rub)
        if not tariff_key:
            await async_log("ERROR", f"TriBute: no tariff matched amount {amount_rub}")
            return {"ok": False, "error": "no_tariff"}

        ext_id = str(payload.get("id") or data.get("id") or "")
        try:
            await _grant_subscription(BOT, user_id, tariff_key, amount_rub, ext_id)
        except Exception as e:
            await async_log("CRITICAL", f"TriBute: grant subscription failed: {e}")
            raise HTTPException(500, "internal error")

    elif event in {"subscription.canceled", "subscription.cancelled"}:
        # здесь можно при желании что-то делать (прислать уведомление пользователю)
        try:
            await BOT.send_message(
                user_id,
                "🔕 Автопродление через TriBute отключено. "
                "Подписка останется активной до конца оплаченного периода.",
            )
        except Exception as e:
            await async_log("ERROR", f"TriBute: notify user about cancel failed: {e}")
    else:
        log.info("TriBute: ignored event %s", event)

    return {"ok": True}
