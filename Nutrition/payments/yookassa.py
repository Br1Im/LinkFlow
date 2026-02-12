import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from aiogram import types
from aiogram.fsm.context import FSMContext

import config
from tariffs import TARIFFS
from keyboards import main_menu
from services import create_yookassa_payment, async_log
from db import run_db_query
from common import generate_invite_link
from .base import register_payment

UTC = timezone.utc


@register_payment("yookassa")
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
    """Запуск сценария оплаты через YooKassa (выбор email)."""
    await helpers["exit_support_if_needed"](state)
    await helpers["clear_email_prompt"](callback.message.chat.id, callback.from_user.id)

    # если нет ключей – сразу алерт и выходим
    if not getattr(config, "SHOP_ID", None) or not getattr(config, "SECRET_KEY", None):
        await callback.answer(
            "Способ оплаты YooKassa временно недоступен. Пожалуйста, выберите другой способ.",
            show_alert=True,
        )
        return

    yimg = helpers.get("get_yookassa_img")()
    photo = yimg
    tariff_info = TARIFFS[tariff]
    caption = (
        f"💳 <b>YooKassa (RUB)</b>\n"
        f"Тариф: {tariff_info['duration']}\n\n"
        f"Для чека введите email ниже 👇"
    )
    kb = helpers["back_to_tariffs_kb"]()

    if photo:
        await helpers["edit_to_photo_screen"](callback.message, photo, caption, kb)
    else:
        await helpers["edit_to_text_screen"](callback.message, caption, kb)

    # запоминаем панель, которую потом отредактируем после успешной оплаты
    storage[user_id] = {
        **storage.get(user_id, {}),
        "panel_chat_id": callback.message.chat.id,
        "panel_message_id": callback.message.message_id,
    }

    if config.TEST_MODE and user_id in (config.ADMIN_IDS or []):
        invite_link = await generate_invite_link(bot, user_id, tariff)
        end_date = datetime.now(UTC) + timedelta(seconds=tariff_info["seconds"])  # UTC
        await run_db_query(
            "INSERT OR REPLACE INTO users (user_id, tariff, end_date, access, invite_link, payment_id, reminded) "
            "VALUES (?, ?, ?, ?, ?, ?, 0)",
            (
                user_id,
                tariff,
                end_date.strftime("%Y-%m-%d %H:%M:%S"),
                True,
                invite_link,
                "TEST_" + str(uuid.uuid4()),
            ),
        )
        await run_db_query(
            "INSERT INTO payments (user_id, amount, tariff, date, yookassa_payment_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                user_id,
                tariff_info["price"],
                tariff,
                datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
                "TEST_" + str(uuid.uuid4()),
            ),
        )
        await callback.message.answer(
            f"🧪 [ТЕСТ] Оплата успешна!\nТариф: {tariff_info['duration']}\nСсылка: {invite_link}",
            reply_markup=main_menu(),
        )
        from services import notify_admins

        await notify_admins(bot, user_id, tariff, tariff_info["price"], "yookassa")
        await callback.answer()
        return

    prompt = await callback.message.answer("📧 Введите ваш email для чека:")
    storage[user_id] = {
        **storage.get(user_id, {}),
        "await_email": True,
        "tariff": tariff,
        "email_prompt_msg_id": prompt.message_id,
    }
    await callback.answer()


async def process_email(message: types.Message, storage: Dict[int, Dict[str, Any]], bot):
    """Обработка ввода email для YooKassa."""
    user_id = message.from_user.id
    email = (message.text or "").strip()
    data = storage.get(user_id, {})
    tariff = data.get("tariff")
    prompt_id = data.get("email_prompt_msg_id")

    if not tariff or "@" not in email or "." not in email:
        await message.answer("⚠️ Неверный email. Введите корректный:")
        return

    try:
        payment = await create_yookassa_payment(user_id, tariff, email)

        # аккуратно чистим чат
        try:
            if prompt_id:
                await bot.delete_message(chat_id=message.chat.id, message_id=prompt_id)
            await message.delete()
        except Exception:
            pass

        await run_db_query(
            "INSERT INTO payments (user_id, amount, tariff, date, yookassa_payment_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                user_id,
                TARIFFS[tariff]["price"],
                tariff,
                datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
                payment.id,
            ),
        )
        await message.answer(
            f"💳 Оплатите по ссылке:\n{payment.confirmation.confirmation_url}",
            reply_markup=main_menu(),
        )
    except Exception as e:
        await async_log("ERROR", f"Ошибка платежа YooKassa: {e}")
        await message.answer(
            f"⚠️ Ошибка платежа: {e}\nОбратитесь в {config.SUPPORT_CONTACT}",
            reply_markup=main_menu(),
        )

    storage.setdefault(user_id, {})["await_email"] = False
    storage[user_id].pop("email_prompt_msg_id", None)
