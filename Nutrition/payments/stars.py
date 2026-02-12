from datetime import datetime, timezone
from typing import Any, Dict, Optional, Callable, Awaitable

from aiogram import types
from aiogram.fsm.context import FSMContext

import config
from tariffs import TARIFFS
from keyboards import main_menu
from services import async_log
from db import run_db_query
from .base import register_payment

UTC = timezone.utc


def _offer_url() -> Optional[str]:
    return (
        getattr(config, "OFFER_URL", None)
        or getattr(config, "OFFERTA_URL", None)
        or getattr(config, "OFERTA_URL", None)
    )


@register_payment("stars")
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
    """Создание инвойса Telegram Stars и показ кнопки 'Оплатить'."""
    await helpers["exit_support_if_needed"](state)
    await helpers["clear_email_prompt"](callback.message.chat.id, callback.from_user.id)

    stars_price = TARIFFS[tariff]["stars"]

    invoice_link = await bot.create_invoice_link(
        title=f"Подписка {TARIFFS[tariff]['duration']}",
        description=f"Доступ на {TARIFFS[tariff]['duration']}",
        payload=f"{user_id}:{tariff}",
        provider_token=(getattr(config, "STARS_PROVIDER_TOKEN", "") or ""),
        currency="XTR",
        prices=[types.LabeledPrice(label="Стоимость", amount=stars_price)],
    )

    offer = _offer_url()
    offer_text = f'<a href="{offer}">данной офертой</a>' if offer else "данной офертой"
    caption = (
        f"⭐ <b>Telegram Stars</b>\n"
        f"Тариф: {TARIFFS[tariff]['duration']}\n"
        f"Сумма: {stars_price} Stars\n"
        "Совершая платеж,\n"
        f"Вы соглашаетесь с {offer_text}"
    )

    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="⭐ Оплатить", url=invoice_link)],
            [types.InlineKeyboardButton(text="⬅️ Назад к тарифам", callback_data="subscription")],
        ]
    )

    simg = helpers.get("get_stars_img")()
    if simg:
        await helpers["edit_to_photo_screen"](callback.message, simg, caption, kb)
    else:
        await helpers["edit_to_text_screen"](callback.message, caption, kb)

    storage[user_id] = {
        **storage.get(user_id, {}),
        "panel_chat_id": callback.message.chat.id,
        "panel_message_id": callback.message.message_id,
    }

    await callback.answer()
