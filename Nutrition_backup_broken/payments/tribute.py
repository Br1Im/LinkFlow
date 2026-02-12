# payments/tribute.py
from __future__ import annotations
from typing import Optional, List, Dict, Any

from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import config
from tariffs import TARIFFS
from services import async_log
from .base import register_payment


@register_payment("tribute")
async def start_tribute_payment(
    callback: types.CallbackQuery,
    state: FSMContext,
    storage: Dict[int, dict],
    bot,
    tariff: str,
    user_id: int,
    helpers: dict,
):
    """
    Старт оплаты через TriBute.
    Ничего не создаём на своей стороне — просто отправляем юзера
    в готовую TriBute-подписку по сумме.
    Подтверждение прилетит вебхуком.
    """
    try:
        price_rub = int(TARIFFS[tariff]["price"])
    except Exception:
        await callback.answer("Тариф настроен некорректно", show_alert=True)
        return

    link = config.TRIBUTE_SUB_LINKS.get(price_rub)
    if not link:
        # для этого тарифа нет ссылки в TRIBUTE_SUB_LINKS
        await async_log(
            "ERROR",
            f"TriBute: нет ссылки для цены {price_rub} RUB (tariff={tariff})",
        )
        await callback.answer(
            "Для этого тарифа пока не настроена оплата через TriBute.",
            show_alert=True,
        )
        return

    caption = (
        "💳 <b>Оплата через TriBute</b>\n"
        f"Тариф: {TARIFFS[tariff]['duration']}\n"
        f"Сумма: {price_rub} ₽\n\n"
        "Нажмите кнопку ниже — откроется приложение TriBute.\n"
        "После оплаты подписка продлится автоматически в течение пары минут."
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💳 Оплатить через TriBute",
                    url=link,
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад к тарифам",
                    callback_data="subscription",
                )
            ],
        ]
    )

    photo = await helpers["welcome_photo"]()
    if photo:
        await helpers["edit_to_photo_screen"](callback.message, photo, caption, kb)
    else:
        await helpers["edit_to_text_screen"](callback.message, caption, kb)

    # сохраним панель, если потом захочешь красиво отрисовывать "оплачено"
    storage[user_id] = {
        **storage.get(user_id, {}),
        "panel_chat_id": callback.message.chat.id,
        "panel_message_id": callback.message.message_id,
    }

    await callback.answer()
