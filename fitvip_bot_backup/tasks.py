from typing import Union
import asyncio
import os
from datetime import datetime, timedelta
try:
    from zoneinfo import ZoneInfo
except:
    ZoneInfo = None  # <-- таймзоны

from yookassa import Payment
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile

import config
from db import run_db_query, init_db
from tariffs import TARIFFS
from keyboards import main_menu
from services import fetch_ton_transactions, async_log
from common import generate_invite_link

# ===== TZ setup ===============================================================
UTC = ZoneInfo("UTC")
MSK = ZoneInfo("Europe/Moscow")

# ===== helpers (картинка из приветствия) =====================================

try:
    from common import get_welcome_photo as get_welcome_photo_from_db
except Exception:
    get_welcome_photo_from_db = None


def _as_input_file_or_str(value: str) -> Union[str, FSInputFile]:
    if not value:
        return None
    try:
        if os.path.isfile(value):
            return FSInputFile(value)
    except Exception:
        pass
    return value


async def _welcome_photo() -> Union[str, FSInputFile]:
    ph = None
    if callable(get_welcome_photo_from_db):
        try:
            ph = await get_welcome_photo_from_db()
        except Exception:
            ph = None
    if ph is None:
        ph = getattr(config, "CHANNEL_PHOTO", None)
    return _as_input_file_or_str(ph)


async def _send_on_welcome_bg(bot, user_id: int, caption_html: str):
    photo = await _welcome_photo()
    try:
        if photo:
            await bot.send_photo(
                chat_id=user_id,
                photo=photo,
                caption=caption_html,
                parse_mode=ParseMode.HTML,
                reply_markup=main_menu(),
            )
        else:
            await bot.send_message(
                chat_id=user_id,
                text=caption_html,
                parse_mode=ParseMode.HTML,
                reply_markup=main_menu(),
                disable_web_page_preview=True,
            )
    except Exception as e:
        await async_log("WARNING", f"send_on_welcome_bg fallback to text: {e}")
        try:
            await bot.send_message(
                chat_id=user_id,
                text=caption_html,
                parse_mode=ParseMode.HTML,
                reply_markup=main_menu(),
                disable_web_page_preview=True,
            )
        except Exception:
            pass


def _fmt_dt(dt_str: str) -> str:
    """
    Дата/время в БД храним в UTC как 'YYYY-mm-dd HH:MM:SS'.
    Пользователю показываем в МСК.
    """
    if not dt_str:
        return "—"
    try:
        dt_utc = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)
        dt_msk = dt_utc.astimezone(MSK)
        return dt_msk.strftime("%d.%m.%Y %H:%M:%S")
    except Exception:
        return dt_str


# ===== основной функционал ====================================================

async def check_payments_and_subscriptions(bot):
    """
    1) Подтверждаем YooKassa и выдаём доступ (уведомление на приветственной картинке).
    2) Снимаем доступ у истёкших подписок (уведомление тоже на картинке).
    Всё время пишем/читаем в БД в UTC, пользователю показываем в MSK.
    """
    while True:
        try:
            # --- YooKassa pending ---
            pending = await run_db_query("""
                SELECT user_id, tariff, yookassa_payment_id
                FROM payments
                WHERE yookassa_payment_id NOT IN (
                    SELECT payment_id FROM users WHERE access = 1 AND payment_id IS NOT NULL
                )
                  AND yookassa_payment_id IS NOT NULL
            """)
            for user_id, tariff, payment_id in pending:
                payment = await asyncio.get_event_loop().run_in_executor(None, Payment.find_one, payment_id)
                if getattr(payment, "status", None) == "succeeded":
                    end_date = datetime.now(UTC) + timedelta(seconds=TARIFFS[tariff]['seconds'])  # UTC
                    invite_link = await generate_invite_link(bot, user_id, tariff)
                    if invite_link:
                        await run_db_query(
                            "INSERT OR REPLACE INTO users (user_id, tariff, end_date, access, invite_link, payment_id, reminded) "
                            "VALUES (?, ?, ?, ?, ?, ?, 0)",
                            (user_id, tariff, end_date.strftime('%Y-%m-%d %H:%M:%S'), True, invite_link, payment_id)
                        )
                        await run_db_query("DELETE FROM payments WHERE yookassa_payment_id = ?", (payment_id,))
                        caption = (
                            "✅ <b>Оплата успешна!</b>\n"
                            f"🔗 <b>Ссылка:</b> {invite_link}"
                        )
                        await _send_on_welcome_bg(bot, user_id, caption)

            # --- Авто-отключение истёкших подписок ---
            if getattr(config, "AUTO_DELETE_ENABLED", False):
                now = datetime.now(UTC)  # UTC
                expired = await run_db_query("SELECT user_id, tariff, end_date FROM users WHERE access = 1")
                for user_id, tariff, end_str in expired:
                    end_date = datetime.strptime(end_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=UTC)
                    if end_date < now:
                        await run_db_query("UPDATE users SET access = 0, reminded = 0 WHERE user_id = ?", (user_id,))
                        try:
                            await bot.ban_chat_member(chat_id=config.CHANNEL_ID, user_id=user_id)
                            await bot.unban_chat_member(chat_id=config.CHANNEL_ID, user_id=user_id)
                        except Exception as e:
                            await async_log("ERROR", f"Не удалось снять доступ у {user_id}: {e}")

                        # уведомление пользователю — ТЕПЕРЬ на приветственной картинке
                        duration = TARIFFS.get(tariff, {}).get("duration", tariff or "—")
                        caption = (
                            f"⚠️ Ваша подписка на «{duration}» истекла.\n"
                            f"Продлите подписку, чтобы вернуть доступ."
                        )
                        await _send_on_welcome_bg(bot, user_id, caption)

            await asyncio.sleep(config.CHECK_INTERVAL)
        except Exception as e:
            await async_log("CRITICAL", f"Ошибка в check_payments_and_subscriptions: {e}")
            await asyncio.sleep(5)


async def check_ton_payments(bot):
    """Подтверждаем TON-платежи, уведомления — на приветственной картинке."""
    while True:
        try:
            pending = await run_db_query(
                "SELECT user_id, tariff, ton_comment, amount FROM payments "
                "WHERE ton_comment IS NOT NULL AND (yookassa_payment_id IS NULL OR yookassa_payment_id='')"
            )
            data = await fetch_ton_transactions()
            for user_id, tariff, ton_comment, expected_amount in pending:
                for tx in data.get('transactions', []):
                    in_msg = tx.get('in_msg') or {}
                    if in_msg.get('message') == ton_comment:
                        amount = int(in_msg.get('value', 0)) / 10 ** 9
                        if amount >= float(expected_amount) * 0.95:
                            end_date = datetime.now(UTC) + timedelta(seconds=TARIFFS[tariff]['seconds'])  # UTC
                            invite_link = await generate_invite_link(bot, user_id, tariff)
                            await run_db_query(
                                "INSERT OR REPLACE INTO users (user_id, tariff, end_date, access, invite_link, payment_id, reminded) "
                                "VALUES (?, ?, ?, ?, ?, ?, 0)",
                                (user_id, tariff, end_date.strftime('%Y-%m-%d %H:%M:%S'), True, invite_link, ton_comment)
                            )
                            await run_db_query("UPDATE payments SET ton_comment = NULL WHERE ton_comment = ?", (ton_comment,))

                            caption = (
                                "✅ <b>Оплата через Toncoin успешна!</b>\n"
                                f"🔗 <b>Ссылка:</b> {invite_link}"
                            )
                            await _send_on_welcome_bg(bot, user_id, caption)
                            break

            await asyncio.sleep(config.CHECK_INTERVAL)
        except Exception as e:
            await async_log("ERROR", f"Ошибка проверки TON-транзакций: {e}")
            await asyncio.sleep(5)


async def check_subscription_reminders(bot):
    """Напоминания о скором окончании — на приветственной картинке (время по МСК)."""
    while True:
        try:
            now = datetime.now(UTC)  # UTC
            reminder_threshold = now + timedelta(days=config.REMINDER_DAYS)
            users = await run_db_query(
                "SELECT user_id, tariff, end_date FROM users WHERE access = 1 AND (reminded IS NULL OR reminded = 0)"
            )
            for user_id, tariff, end_date_str in users:
                end_date_utc = datetime.strptime(end_date_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=UTC)
                if now < end_date_utc <= reminder_threshold:
                    duration = TARIFFS.get(tariff, {}).get("duration", tariff or "—")
                    caption = (
                        "⏰ <b>Напоминание</b>\n"
                        f"Ваша подписка на «{duration}» истекает <b>{_fmt_dt(end_date_str)}</b>.\n\n"
                        "Продлите подписку, чтобы сохранить доступ!"
                    )
                    await _send_on_welcome_bg(bot, user_id, caption)
                    await run_db_query("UPDATE users SET reminded = 1 WHERE user_id = ?", (user_id,))
        except Exception as e:
            await async_log("ERROR", f"Ошибка в check_subscription_reminders: {e}")

        await asyncio.sleep(config.CHECK_INTERVAL * 2)


async def start_background_tasks(bot):
    await init_db()
    asyncio.create_task(check_payments_and_subscriptions(bot))
    asyncio.create_task(check_ton_payments(bot))
    asyncio.create_task(check_subscription_reminders(bot))
