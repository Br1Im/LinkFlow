from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from aiogram import types
from aiogram.fsm.context import FSMContext

import config
from tariffs import TARIFFS
from keyboards import main_menu
from services import get_ton_rate
from db import run_db_query
from .base import register_payment

UTC = timezone.utc


@register_payment("ton")
async def start_payment(
    *,
    callback: types.CallbackQuery,
    state: FSMContext,
    storage: Dict[int, Dict[str, Any]],
    bot,
    tariff: str,
    user_id: int,
    helpers: Dict[str, Any],
):
    """Инструкция по оплате TON (с формированием уникального комментария)."""
    await helpers["exit_support_if_needed"](state)
    await helpers["clear_email_prompt"](callback.message.chat.id, callback.from_user.id)

    ton_rate = await get_ton_rate()
    ton_amount = TARIFFS[tariff]["price"] / ton_rate
    import uuid
    unique_comment = f"payment_{user_id}_{tariff}_{uuid.uuid4().hex[:8]}"

    await run_db_query(
        "INSERT INTO payments (user_id, amount, tariff, date, ton_comment) VALUES (?, ?, ?, ?, ?)",
        (
            user_id,
            ton_amount,
            tariff,
            datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
            unique_comment,
        ),
    )

    storage[user_id] = {
        **storage.get(user_id, {}),
        "panel_chat_id": callback.message.chat.id,
        "panel_message_id": callback.message.message_id,
        "ton_comment": unique_comment,
        "tariff": tariff,
        "ton_amount": ton_amount,
    }

    await callback.message.answer(
        f"💸 Оплатите {ton_amount:.2f} TON на адрес:\n`{config.TON_WALLET_ADDRESS}`\n"
        f"С комментарием: `{unique_comment}`\n"
        "После оплаты бот автоматически проверит транзакцию в течение минуты.\n"
        f"(Курс TON: 1 TON = {ton_rate:.2f} RUB)",
        parse_mode="MARKDOWN",
        reply_markup=main_menu(),
    )
    await callback.answer()
