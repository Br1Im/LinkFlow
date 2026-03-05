import os
import uuid
from datetime import datetime, timedelta, timezone  # + timezone

try:
    from zoneinfo import ZoneInfo  # может не быть tzdata в системе
except Exception:
    ZoneInfo = None  # fallback далее

from aiogram import types, Dispatcher
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile

import config
from tariffs import TARIFFS
from keyboards import main_menu, tariff_menu, payment_methods
from payments import get_start_handler
from payments import yookassa as pay_yookassa
from services import get_ton_rate, create_yookassa_payment, notify_admins, async_log
from db import run_db_query, get_payment_methods
from common import get_channel_text, generate_invite_link, ensure_db

try:
    from common import get_welcome_photo as get_welcome_photo_from_db
except Exception:
    get_welcome_photo_from_db = None


# ---- Timezones (безопасные) ----
def _safe_msk():
    # пытаемся взять системную зону; если tzdata не установлена — жёсткий UTC+3
    if ZoneInfo is not None:
        try:
            return ZoneInfo("Europe/Moscow")
        except Exception:
            pass
    return timezone(timedelta(hours=3))

UTC = timezone.utc
MSK = _safe_msk()


# ---------------- FSM ----------------
class SupportUserFSM(StatesGroup):
    waiting_message = State()


class PaymentFSM(StatesGroup):
    waiting_amount = State()


class SupportAdminFSM(StatesGroup):
    waiting_reply = State()


def setup_public_handlers(dp: Dispatcher, bot):
    storage: dict[int, dict] = {}
    admin_reply_target: dict[int, int] = {}  # admin_id -> user_id

    # ===================== helpers =====================

    def _back_to_tariffs_kb() -> types.InlineKeyboardMarkup:
        return types.InlineKeyboardMarkup(
            inline_keyboard=[[types.InlineKeyboardButton(text="⬅️ Назад к тарифам",
                                                         callback_data="subscription")]]
        )

    def _as_input_file_or_str(value: str | None) -> str | FSInputFile | None:
        if not value:
            return None
        try:
            if os.path.isfile(value):
                return FSInputFile(value)
        except Exception:
            pass
        return value

    def _first_existing_img(path_wo_ext: str) -> FSInputFile | None:
        for ext in (".png", ".jpg", ".jpeg", ".webp"):
            p = path_wo_ext + ext
            if os.path.isfile(p):
                return FSInputFile(p)
        return None

    def _get_yookassa_img() -> str | FSInputFile | None:
        val = getattr(config, "YOOKASSA_IMG", "") or ""
        if val:
            return _as_input_file_or_str(val)
        return _first_existing_img(os.path.join("img", "yookassa"))

    def _get_stars_img() -> str | FSInputFile | None:
        val = getattr(config, "STARS_IMG", "") or ""
        if val:
            return _as_input_file_or_str(val)
        return _first_existing_img(os.path.join("img", "stars"))

    async def _welcome_photo() -> str | FSInputFile | None:
        ph = None
        if callable(get_welcome_photo_from_db):
            try:
                ph = await get_welcome_photo_from_db()
            except Exception:
                ph = None
        if ph is None:
            ph = getattr(config, "CHANNEL_PHOTO", None)
        return _as_input_file_or_str(ph)

    async def _get_about_content():
        text = await get_channel_text()
        row_p = await run_db_query("SELECT value FROM settings WHERE key='about_photo'", fetchone=True)
        photo = _as_input_file_or_str(row_p[0] if row_p else None)
        return text, photo

    async def _get_support_photo() -> str | FSInputFile | None:
        """Приоритет: settings.support_photo -> config.SUPPORT_PHOTO -> welcome_photo"""
        row_p = await run_db_query("SELECT value FROM settings WHERE key='support_photo'", fetchone=True)
        photo = _as_input_file_or_str(row_p[0] if row_p else None)
        if not photo:
            photo = _as_input_file_or_str(getattr(config, "SUPPORT_PHOTO", None))
        if not photo:
            photo = await _welcome_photo()
        return photo

    def _support_main_caption() -> str:
        return "💬 <b>Помощь</b>"

    def _support_write_caption_wait() -> str:
        return "Оставьте своё сообщение, и мы обязательно вам ответим! 💬✨"

    def _support_write_caption_done() -> str:
        return "✅ Администраторы уже получили ваше сообщение и вскоре свяжутся с вами"
    

    def _offer_url() -> str | None:
    # подхватываем любое из названий переменной в config
        return (
            getattr(config, "OFFER_URL", None)
            or getattr(config, "OFFERTA_URL", None)
            or getattr(config, "OFERTA_URL", None)
        )

    def _support_kb() -> types.InlineKeyboardMarkup:
        rows: list[list[types.InlineKeyboardButton]] = []
        rows.append([types.InlineKeyboardButton(text="💬 Написать в поддержку",
                                                callback_data="support_write")])
        if getattr(config, "FAQ_URL", None):
            rows.append([types.InlineKeyboardButton(text="📄 Часто задаваемые вопросы",
                                                    url=config.FAQ_URL)])
        if getattr(config, "SUPPORT_TG_LINK", None):
            rows.append([types.InlineKeyboardButton(text="📲 Открыть в Telegram",
                                                    url=config.SUPPORT_TG_LINK)])
            

        offer = _offer_url()
        if offer:
        # широкая кнопка с полным текстом
            rows.append([types.InlineKeyboardButton(
                text="📑 Договор-оферта",
                url=offer
           )])


        rows.append([types.InlineKeyboardButton(text="↩️ Вернуться", callback_data="back_to_main")])
        return types.InlineKeyboardMarkup(inline_keyboard=rows)

    def _support_back_only_kb() -> types.InlineKeyboardMarkup:
        # во время набора показываем только кнопку возврата в экран помощи
        return types.InlineKeyboardMarkup(
            inline_keyboard=[[types.InlineKeyboardButton(text="↩️ Вернуться", callback_data="support")]]
        )

    def _reply_to_support_kb() -> types.InlineKeyboardMarkup:
        return types.InlineKeyboardMarkup(
            inline_keyboard=[[types.InlineKeyboardButton(text="💬 Ответить поддержке",
                                                         callback_data="support_write")]]
        )

    def _reply_to_user_kb(user_id: int) -> types.InlineKeyboardMarkup:
        return types.InlineKeyboardMarkup(
            inline_keyboard=[[types.InlineKeyboardButton(text="↩️ Ответить пользователю",
                                                         callback_data=f"support_reply:{user_id}")]]
        )

    async def _edit_to_photo_screen(callback_msg: types.Message, photo: str | FSInputFile,
                                    caption: str, kb: types.InlineKeyboardMarkup):
        """
        Возвращаем классическую схему без удаления сообщения:
        1) edit_message_media – основной путь
        2) если нельзя – edit_message_caption
        3) если совсем нельзя – отправляем новую фотку (как и было у вас)
        """
        media = types.InputMediaPhoto(media=photo, caption=caption, parse_mode=ParseMode.HTML)
        try:
            await bot.edit_message_media(
                chat_id=callback_msg.chat.id,
                message_id=callback_msg.message_id,
                media=media,
                reply_markup=kb,
            )
        except TelegramBadRequest:
            try:
                await bot.edit_message_caption(
                    chat_id=callback_msg.chat.id,
                    message_id=callback_msg.message_id,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                    reply_markup=kb,
                )
            except Exception:
                # не удаляем – но если совсем нельзя отредактировать, шлём новую карточку
                try:
                    await bot.send_photo(callback_msg.chat.id, photo=photo, caption=caption,
                                         parse_mode=ParseMode.HTML, reply_markup=kb)
                except Exception:
                    # как последний шанс – текстом
                    await bot.send_message(callback_msg.chat.id, caption, parse_mode=ParseMode.HTML,
                                           reply_markup=kb)

    async def _edit_to_text_screen(callback_msg: types.Message, text: str,
                                   kb: types.InlineKeyboardMarkup | None = None):
        try:
            await bot.edit_message_text(
                chat_id=callback_msg.chat.id,
                message_id=callback_msg.message_id,
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=kb,
                disable_web_page_preview=True,
            )
        except TelegramBadRequest:
            try:
                await callback_msg.delete()
            except Exception:
                pass
            await bot.send_message(callback_msg.chat.id, text, parse_mode=ParseMode.HTML,
                                   reply_markup=kb, disable_web_page_preview=True)

    # ---- форматируем дату из БД (UTC) в MSK ----
    def _fmt_dt(s: str | None) -> str | None:
        if not s:
            return None
        try:
            dt_utc = datetime.strptime(s, "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)
            dt_msk = dt_utc.astimezone(MSK)
            return dt_msk.strftime("%d.%m.%Y %H:%M:%S")
        except Exception:
            return s

    async def _clear_email_prompt(chat_id: int, user_id: int):
        """Удалить подсказку 'Введите email…' и сбросить ожидание email, если висит."""
        data = storage.get(user_id, {})
        msg_id = data.pop("email_prompt_msg_id", None)
        data["await_email"] = False
        storage[user_id] = data
        if msg_id:
            try:
                await bot.delete_message(chat_id, msg_id)
            except Exception:
                pass

    async def _exit_support_if_needed(state: FSMContext):
        """Если юзер был в режиме набора сообщения поддержке — снять состояние."""
        cur = await state.get_state()
        if cur == SupportUserFSM.waiting_message.state:
            await state.clear()

    # ===================== /start =====================

    @dp.message(Command("start"))
    async def send_welcome(message: types.Message, state: FSMContext):
        await _exit_support_if_needed(state)
        await _clear_email_prompt(message.chat.id, message.from_user.id)
        await async_log("INFO", f"/start от {message.from_user.id}")
        photo = await _welcome_photo()

        if photo:
            try:
                await bot.send_photo(
                    chat_id=message.chat.id,
                    photo=photo,
                    caption=config.WELCOME_TEXT,
                    reply_markup=main_menu(),
                )
                return
            except Exception as e:
                await async_log("WARNING", f"Приветственное фото не отправлено: {e}")

        await message.answer(config.WELCOME_TEXT, reply_markup=main_menu())

    # ===================== Меню / Канал =====================

    @dp.callback_query(lambda c: c.data == "subscription")
    async def process_subscription(callback: types.CallbackQuery, state: FSMContext):
        await _exit_support_if_needed(state)
        await _clear_email_prompt(callback.message.chat.id, callback.from_user.id)
        await async_log("INFO", f"{callback.from_user.id} нажал 'Подписка'")
        
        # Показываем информацию о стоимости
        pricing_text = (
            "💰 Стоимость курса\n\n"
            "🔹 Базовая стоимость курса: 2000 рублей\n"
            "🔹 Дополнительно: 100 рублей/сутки персональное ведение\n"
            "🔹 Количество максимальных дней: 20\n\n"
            "💡 Итого: от 2000 до 4000 рублей\n"
            "(2000 + 100×количество дней персонального ведения)\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "📋 <b>Дополнительные услуги:</b>\n\n"
            "📝 Генератор постов для Telegram - <b>5₽</b>\n"
            "   Готовый пост с эмодзи и хештегами\n\n"
            "💡 Придумай название для канала/бренда - <b>10₽</b>\n"
            "   10 креативных вариантов\n\n"
            "🎯 Персональный промпт под запрос - <b>15₽</b>\n"
            "   Детальный промпт для ChatGPT/Claude"
        )
        
        kb = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="💳 Ввести сумму", callback_data="enter_amount")],
            [types.InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_main")]
        ])
        
        photo = await _welcome_photo()
        if photo:
            await _edit_to_photo_screen(callback.message, photo, pricing_text, kb)
        else:
            await _edit_to_text_screen(callback.message, pricing_text, kb)
        await callback.answer()

    @dp.callback_query(lambda c: c.data == "about_channel")
    async def process_about_channel(callback: types.CallbackQuery, state: FSMContext):
        await _exit_support_if_needed(state)
        await _clear_email_prompt(callback.message.chat.id, callback.from_user.id)
        await async_log("INFO", f"{callback.from_user.id} нажал 'Пользовательское соглашение'")
        
        agreement_text = (
            "📄 Пользовательское соглашение\n\n"
            "1. Термины и определения\n"
            "1.1. Оферта – настоящее Пользовательское соглашение.\n"
            "1.2. Сервис – Telegram-бот @ai_vip_robot, принадлежащий Исполнителю и предназначенный для продажи Товара.\n"
            "1.3. Пользователь – любое физическое лицо, акцептовавшее (принявшее) настоящую Оферту.\n"
            "1.4. Товар – Курс.\n"
            "1.5. Акцепт Оферты – совершение Пользователем оплаты Товара через Сервис.\n\n"
            "2. Предмет Оферты\n"
            "2.1. Исполнитель обязуется предоставить Пользователю Товар в количестве, выбранном и оплаченном Пользователем.\n"
            "2.2. Сервис @ai_vip_robot является независимой площадкой и не является аффилированным лицом Telegram FZ-LLC.\n\n"
            "3. Порядок оплаты\n"
            "3.1. Стоимость определяется в интерфейсе Сервиса перед оплатой.\n"
            "3.2. Минимальная сумма: 3100 рублей.\n"
            "3.3. Оплата: 100% предоплата через MulenPay (СБП).\n"
            "3.4. Зачисление: автоматически в течение 1-5 минут.\n\n"
            "4. Возврат\n"
            "4.1. Возврат невозможен после предоставления ссылки на вступление.\n"
            "4.2. Возврат 100% при техническом сбое.\n\n"
            "5. Ответственность\n"
            "5.1. Исполнитель не несет ответственности за действия платформы Telegram.\n\n"
            "6. Поддержка\n"
            "6.1. Контакт: @managerr_info\n\n"
            "Полная версия: https://telegra.ph/User-Agreement-AI-VIP-Bot"
        )
        
        await _edit_to_text_screen(callback.message, agreement_text, main_menu())
        await callback.answer()

    # ===================== Кастомный payment flow =====================

    @dp.callback_query(lambda c: c.data == "enter_amount")
    async def enter_amount(callback: types.CallbackQuery, state: FSMContext):
        await _clear_email_prompt(callback.message.chat.id, callback.from_user.id)
        await state.set_state(PaymentFSM.waiting_amount)
        
        amount_text = (
            "💰 Введите сумму для оплаты курса\n\n"
            "🔹 Базовая стоимость: 2000 рублей\n"
            "🔹 + 100 рублей за каждый день персонального ведения (макс. 20 дней)\n\n"
            "💡 Примеры:\n"
            "• 2000 руб. — только курс\n"
            "• 2500 руб. — курс + 5 дней ведения\n"
            "• 4000 руб. — курс + 20 дней ведения\n\n"
            "Введите итоговую сумму числом:"
        )
        
        kb = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_payment")]
        ])
        
        photo = await _welcome_photo()
        if photo:
            await _edit_to_photo_screen(callback.message, photo, amount_text, kb)
        else:
            await _edit_to_text_screen(callback.message, amount_text, kb)
        await callback.answer()

    @dp.callback_query(lambda c: c.data == "cancel_payment")
    async def cancel_payment(callback: types.CallbackQuery, state: FSMContext):
        await state.clear()
        await _clear_email_prompt(callback.message.chat.id, callback.from_user.id)
        photo = await _welcome_photo()
        if photo:
            await _edit_to_photo_screen(callback.message, photo, config.WELCOME_TEXT, main_menu())
        else:
            await _edit_to_text_screen(callback.message, config.WELCOME_TEXT, main_menu())
        await callback.answer()

    @dp.message(PaymentFSM.waiting_amount)
    async def process_amount_input(message: types.Message, state: FSMContext):
        from tariffs import calculate_tariff
        
        try:
            amount = int(message.text.strip())
        except ValueError:
            await message.answer("⚠️ Пожалуйста, введите число (например: 3000)")
            return
        
        tariff_info, error = calculate_tariff(amount)
        
        if error:
            await message.answer(f"⚠️ {error}\n\nПопробуйте ещё раз:")
            return
        
        # Сохраняем сумму и тариф
        user_id = message.from_user.id
        storage[user_id] = {
            "tariff": "custom",
            "amount": amount,
            "tariff_info": tariff_info
        }
        
        await state.clear()
        
        # Показываем способы оплаты
        methods = await get_payment_methods(enabled_only=True)
        if not methods:
            await message.answer(
                "⚠️ Сейчас ни один способ оплаты не включён. Напишите в поддержку: " + config.SUPPORT_CONTACT,
                reply_markup=main_menu(),
            )
            return
        
        description = tariff_info['description']
        payment_text = f"✅ Выбрано: {description}\n💰 Сумма: {amount} руб.\n\nВыберите способ оплаты:"
        
        kb = payment_methods("custom", methods)
        await message.answer(payment_text, reply_markup=kb)

    # ===================== Поддержка (переключение без новых сообщений) =====================

    @dp.callback_query(lambda c: c.data == "support")
    async def process_support(callback: types.CallbackQuery, state: FSMContext):
        # если человек выходил из режима ввода — очищаем состояние
        await _exit_support_if_needed(state)
        await _clear_email_prompt(callback.message.chat.id, callback.from_user.id)
        await async_log("INFO", f"{callback.from_user.id} нажал 'Поддержка'")
        photo = await _get_support_photo()
        caption = _support_main_caption()
        if photo:
            await _edit_to_photo_screen(callback.message, photo, caption, _support_kb())
        else:
            await _edit_to_text_screen(callback.message, caption, _support_kb())
        await callback.answer()

    @dp.callback_query(lambda c: c.data == "support_write")
    async def support_write_start(callback: types.CallbackQuery, state: FSMContext):
        await _clear_email_prompt(callback.message.chat.id, callback.from_user.id)
        # Входим в режим: ставим состояние и сохраняем id текущей карточки
        await state.set_state(SupportUserFSM.waiting_message)
        await state.update_data(panel_chat_id=callback.message.chat.id,
                                panel_message_id=callback.message.message_id)

        photo = await _get_support_photo()
        ask_caption = _support_write_caption_wait()

        if photo:
            await _edit_to_photo_screen(callback.message, photo, ask_caption, _support_back_only_kb())
        else:
            await _edit_to_text_screen(callback.message, ask_caption, _support_back_only_kb())

        await callback.answer()

    @dp.message(SupportUserFSM.waiting_message)
    async def support_receive_from_user(message: types.Message, state: FSMContext):
        # Достанем сохранённую карточку (хотя дальше вернём уже главное меню)
        data = await state.get_data()
        panel_chat_id = data.get("panel_chat_id")
        panel_message_id = data.get("panel_message_id")

        # Пересылаем запрос админам
        u = message.from_user
        uname = f"@{u.username}" if u.username else f"id:{u.id}"
        header = (
            "🆘 <b>Новый запрос в поддержку</b>\n"
            f"От: {uname}\n"
            f"Профиль: <a href=\"tg://user?id={u.id}\">{u.full_name}</a>\n"
            f"UserID: <code>{u.id}</code>"
        )

        for admin_id in (config.ADMIN_IDS or []):
            try:
                await bot.send_message(
                    admin_id, header, parse_mode=ParseMode.HTML,
                    reply_markup=_reply_to_user_kb(u.id)
                )
                try:
                    await bot.copy_message(
                        chat_id=admin_id,
                        from_chat_id=message.chat.id,
                        message_id=message.message_id
                    )
                except Exception:
                    if message.text:
                        await bot.send_message(admin_id, f"Сообщение: {message.text}")
            except Exception as e:
                await async_log("ERROR", f"Не удалось отправить запрос админу {admin_id}: {e}")

        # 1) короткое подтверждение
        try:
            await bot.send_message(
                message.chat.id,
                _support_write_caption_done()
            )
        except Exception:
            pass

        # 2) сразу следом — показать ГЛАВНОЕ МЕНЮ
        try:
            photo = await _welcome_photo()
            if photo:
                await bot.send_photo(
                    chat_id=message.chat.id,
                    photo=photo,
                    caption=config.WELCOME_TEXT,
                    parse_mode=ParseMode.HTML,
                    reply_markup=main_menu(),
                )
            else:
                await bot.send_message(
                    chat_id=message.chat.id,
                    text=config.WELCOME_TEXT,
                    parse_mode=ParseMode.HTML,
                    reply_markup=main_menu(),
                )
        except Exception as e:
            await async_log("WARNING", f"Не удалось вернуть главное меню после поддержки: {e}")

        # Вернуть старую карточку в состояние «Помощь» (без спама)
        try:
            if panel_chat_id and panel_message_id:
                cap = _support_main_caption()
                sp = await _get_support_photo()
                if sp:
                    await bot.edit_message_media(
                        chat_id=panel_chat_id,
                        message_id=panel_message_id,
                        media=types.InputMediaPhoto(media=sp, caption=cap, parse_mode=ParseMode.HTML),
                        reply_markup=_support_kb(),
                    )
                else:
                    await bot.edit_message_text(
                        chat_id=panel_chat_id,
                        message_id=panel_message_id,
                        text=cap,
                        parse_mode=ParseMode.HTML,
                        reply_markup=_support_kb(),
                    )
        except Exception:
            pass

        await state.clear()

    @dp.callback_query(lambda c: c.data.startswith("support_reply:"))
    async def admin_reply_start(callback: types.CallbackQuery, state: FSMContext):
        if callback.from_user.id not in (config.ADMIN_IDS or []):
            await callback.answer("Недоступно", show_alert=True)
            return
        try:
            target_id = int(callback.data.split(":", 1)[1])
        except Exception:
            await callback.answer("Ошибка данных", show_alert=True)
            return
        admin_reply_target[callback.from_user.id] = target_id
        await state.set_state(SupportAdminFSM.waiting_reply)
        await bot.send_message(callback.from_user.id,
                               f"✍️ Введите ответ для пользователя <code>{target_id}</code>.\n"
                               f"Чтобы отменить — отправьте /cancel.",
                               parse_mode=ParseMode.HTML)
        await callback.answer("Введите ответ…")

    @dp.message(Command("cancel"))
    async def admin_or_user_cancel(message: types.Message, state: FSMContext):
        cur = await state.get_state()
        if cur == SupportAdminFSM.waiting_reply.state:
            admin_reply_target.pop(message.from_user.id, None)
            await state.clear()
            await message.answer("❌ Ответ отменён.")
        elif cur == SupportUserFSM.waiting_message.state:
            # Пользователь отменил ввод — удалим /cancel и покажем главное меню
            await state.clear()
            try:
                await message.delete()
            except Exception:
                pass
            photo = await _welcome_photo()
            if photo:
                await bot.send_photo(message.chat.id, photo=photo,
                                     caption=config.WELCOME_TEXT,
                                     parse_mode=ParseMode.HTML,
                                     reply_markup=main_menu())
            else:
                await bot.send_message(message.chat.id, config.WELCOME_TEXT,
                                       parse_mode=ParseMode.HTML, reply_markup=main_menu())

    @dp.message(SupportAdminFSM.waiting_reply)
    async def admin_send_reply(message: types.Message, state: FSMContext):
        admin_id = message.from_user.id
        if admin_id not in (config.ADMIN_IDS or []):
            await state.clear()
            return
        target_id = admin_reply_target.get(admin_id)
        if not target_id:
            await state.clear()
            await message.answer("⚠️ Не выбран получатель. Нажмите кнопку «Ответить пользователю» ещё раз.")
            return
        try:
            await bot.send_message(
                target_id,
                "💬 <b>Ответ от поддержки</b>",
                parse_mode=ParseMode.HTML,
                reply_markup=_reply_to_support_kb(),
            )
            try:
                await bot.copy_message(chat_id=target_id, from_chat_id=message.chat.id,
                                       message_id=message.message_id)
            except Exception:
                if message.text:
                    await bot.send_message(target_id, message.text, reply_markup=_reply_to_support_kb())
        except Exception as e:
            await message.answer(f"⚠️ Не удалось отправить пользователю: {e}")
            await state.clear()
            return
        await message.answer("✅ Ответ отправлен пользователю.")
        await state.clear()

    @dp.callback_query(lambda c: c.data == "back_to_main")
    async def back_to_main(callback: types.CallbackQuery, state: FSMContext):
        await _exit_support_if_needed(state)
        await _clear_email_prompt(callback.message.chat.id, callback.from_user.id)
        photo = await _welcome_photo()
        if photo:
            await _edit_to_photo_screen(callback.message, photo, config.WELCOME_TEXT, main_menu())
        else:
            await _edit_to_text_screen(callback.message, config.WELCOME_TEXT, main_menu())
        await callback.answer()

        # ===================== Выбор тарифа / Оплаты =====================

    @dp.callback_query(lambda c: c.data.startswith("tariff_"))
    async def process_tariff_inline(callback: types.CallbackQuery, state: FSMContext):
        await _exit_support_if_needed(state)
        await _clear_email_prompt(callback.message.chat.id, callback.from_user.id)
        tariff = callback.data.split("_", 1)[1]
        user_id = callback.from_user.id
        await async_log("INFO", f"{user_id} выбрал тариф: {tariff}")

        if tariff not in TARIFFS:
            await callback.message.answer("⚠️ Неверный тариф!", reply_markup=main_menu())
            return await callback.answer()

        storage[user_id] = {"tariff": tariff}

        methods = await get_payment_methods(enabled_only=True)
        if not methods:
            await callback.message.answer(
                "⚠️ Сейчас ни один способ оплаты не включён. Напишите в поддержку: " + config.SUPPORT_CONTACT,
                reply_markup=main_menu(),
            )
            return await callback.answer()

        photo = await _welcome_photo()
        kb = payment_methods(tariff, methods)
        if photo:
            await _edit_to_photo_screen(callback.message, photo, "💳 Выберите способ оплаты:", kb)
        else:
            await _edit_to_text_screen(callback.message, "💳 Выберите способ оплаты:", kb)

        await callback.answer()

    # ---------- Любой способ оплаты (router -> модули payments.*) ----------

    @dp.callback_query(lambda c: c.data.startswith("pay_"))
    async def process_any_payment(callback: types.CallbackQuery, state: FSMContext):
        await _exit_support_if_needed(state)
        await _clear_email_prompt(callback.message.chat.id, callback.from_user.id)

        parts = callback.data.split("_", 2)
        if len(parts) != 3:
            return await callback.answer("Некорректные данные", show_alert=True)

        _, code, tariff = parts
        handler = get_start_handler(code)
        if handler is None:
            return await callback.answer("Способ оплаты временно недоступен", show_alert=True)

        user_id = callback.from_user.id
        helpers = {
            "back_to_tariffs_kb": _back_to_tariffs_kb,
            "welcome_photo": _welcome_photo,
            "edit_to_photo_screen": _edit_to_photo_screen,
            "edit_to_text_screen": _edit_to_text_screen,
            "get_yookassa_img": _get_yookassa_img,
            "get_stars_img": _get_stars_img,
            "exit_support_if_needed": _exit_support_if_needed,
            "clear_email_prompt": _clear_email_prompt,
        }
        await handler(
            callback=callback,
            state=state,
            storage=storage,
            bot=bot,
            tariff=tariff,
            user_id=user_id,
            helpers=helpers,
        )

    @dp.message(lambda m: storage.get(m.from_user.id, {}).get("await_email"))
    async def process_email(message: types.Message):
        # делегируем обработку email в модуль payments.yookassa
        await pay_yookassa.process_email(message, storage, bot)

    # ---------- Профиль ----------

    @dp.callback_query(lambda c: c.data == "profile")
    async def process_profile(callback: types.CallbackQuery, state: FSMContext):
        await _exit_support_if_needed(state)
        await _clear_email_prompt(callback.message.chat.id, callback.from_user.id)

        user_id = callback.from_user.id
        u = callback.from_user

        row = await run_db_query(
            "SELECT tariff, end_date, access, invite_link FROM users WHERE user_id = ?",
            (user_id,),
            fetchone=True,
        )

        row_last = await run_db_query(
            "SELECT MAX(date) FROM payments WHERE user_id = ?",
            (user_id,),
            fetchone=True,
        )
        last_renewal = _fmt_dt(row_last[0] if row_last else None)

        row_first = await run_db_query(
            "SELECT MIN(date) FROM payments WHERE user_id = ?",
            (user_id,),
            fetchone=True,
        )
        registered_at = _fmt_dt(row_first[0] if row_first else None) or "—"

        full_name = u.full_name or "—"
        uid_str = f"<code>{user_id}</code>"

        if row and row[2]:
            end_date_fmt = _fmt_dt(row[1]) or "—"
            tariff_name = TARIFFS.get(row[0], {}).get("duration", row[0] or "—")
            invite = row[3] or "—"
            text = (
                "💎 <b>Ваш профиль</b>\n"
                f"👤 Имя: {full_name}\n"
                f"🆔: {uid_str}\n"
                f"📅 Подписка до: {end_date_fmt} ({tariff_name})\n"
                f"💳 Последнее продление: {last_renewal or 'Отсутствует 😔'}\n"
                f"💠 Дата регистрации: {registered_at}\n"
                f"🔗 Ссылка: {invite}"
            )
        else:
            text = (
                "💎 <b>Ваш профиль</b>\n"
                f"👤 Имя: {full_name}\n"
                f"🆔: {uid_str}\n"
                "📅 Подписка до: Вы не подписаны 😔\n"
                f"💳 Последнее продление: {last_renewal or 'Отсутствует 😔'}\n"
                f"💠 Дата регистрации: {registered_at}"
            )

        # Создаем клавиатуру с кнопкой админки для админов
        is_admin = user_id in (config.ADMIN_IDS or [])
        if is_admin:
            kb = types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="⚙️ Админка", callback_data="admin_panel")],
                    [types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
                ]
            )
        else:
            kb = types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
                ]
            )

        photo = await _welcome_photo()
        if photo:
            await _edit_to_photo_screen(callback.message, photo, text, kb)
        else:
            await _edit_to_text_screen(callback.message, text, kb)
        await callback.answer()

    dp.startup.register(ensure_db)

    # ---------- MulenPay check payment ----------
    @dp.callback_query(lambda c: c.data.startswith("check_mp:"))
    async def check_mulenpay_payment(callback: types.CallbackQuery):
        """Проверка статуса платежа MulenPay"""
        from .payments import mulenpay
        
        parts = callback.data.split(":")
        if len(parts) < 3:
            return await callback.answer("Некорректные данные", show_alert=True)
        
        payment_id = parts[1]
        amount = parts[2]
        
        await mulenpay.check_payment_status(callback, payment_id, amount, bot)
