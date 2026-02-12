import io
from typing import Optional, List, Dict, Any
from datetime import datetime
from aiogram import types, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest  # ← добавлено

import config
from keyboards import admin_menu, main_menu
from services import async_log, get_ton_rate
from tariffs import TARIFFS
from db import run_db_query, get_payment_methods, set_payment_method_enabled


# -------------------- FSM --------------------

class GreetingPhotoFSM(StatesGroup):
    waiting_photo = State()


class TariffAddFSM(StatesGroup):
    waiting_key = State()
    waiting_price = State()
    waiting_stars = State()
    waiting_name = State()
    waiting_seconds = State()


class TariffEditFSM(StatesGroup):
    waiting_price = State()
    waiting_stars = State()
    waiting_name = State()
    waiting_seconds = State()


class BroadcastFSM(StatesGroup):
    waiting_content = State()
    confirm = State()


class AboutFSM(StatesGroup):
    waiting_message = State()   # ждём одно сообщение (текст/фото/фото+подпись)
    waiting_text = State()      # редактируем только текст
    waiting_photo = State()     # редактируем только фото
    confirm = State()           # подтверждение сохранения


# -------------------- helpers --------------------

def _is_admin(user_id: int) -> bool:
    return user_id in getattr(config, "ADMIN_IDS", [])


def _fmt_rub(v) -> str:
    try:
        return f"{float(v):.2f}"
    except Exception:
        return str(v or 0)


def _fmt_table_row(name: str, price: int, stars: int, ton: float, duration: str) -> str:
    return f"{name:<12} | {price:>6} RUB | {stars:>5} XTR | {ton:>6.2f} TON | {duration}"


def _tariffs_inline_kb() -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for key in TARIFFS.keys():
        kb.button(text=f"✏️ {key}", callback_data=f"adm_tariff_edit:{key}")
        kb.button(text="🗑", callback_data=f"adm_tariff_del:{key}")
        kb.adjust(2)
    kb.button(text="➕ Добавить тариф", callback_data="adm_tariff_add")
    return kb.as_markup()


def _bc_confirm_kb() -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🚀 Отправить активным", callback_data="bc_send_active")
    kb.button(text="🧪 Отправить всем", callback_data="bc_send_all")
    kb.button(text="❌ Отмена", callback_data="bc_cancel")
    kb.adjust(1, 1, 1)
    return kb.as_markup()


def _about_kb() -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✉️ Сохранить из сообщения", callback_data="about_from_msg")
    kb.button(text="✏️ Изменить текст", callback_data="about_edit_text")
    kb.button(text="🖼 Изменить фото", callback_data="about_edit_photo")
    kb.button(text="🗑 Удалить фото", callback_data="about_del_photo")
    kb.adjust(1, 2, 1)
    return kb.as_markup()


async def _get_about_from_db():
    row_t = await run_db_query("SELECT value FROM settings WHERE key='channel_text'", fetchone=True)
    row_p = await run_db_query("SELECT value FROM settings WHERE key='about_photo'", fetchone=True)
    text = (row_t[0] if row_t else None) or getattr(config, "ABOUT_TEXT", "—")
    photo = (row_p[0] if row_p else None)
    return text, photo


async def _save_about(text: Optional[str] = None, photo: Optional[str] = None):
    if text is not None:
        await run_db_query(
            "INSERT INTO settings (key, value) VALUES ('channel_text', ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (text,)
        )
    if photo is not None:
        if photo == "":
            # пустая строка = удалить фото
            await run_db_query("DELETE FROM settings WHERE key='about_photo'")
        else:
            await run_db_query(
                "INSERT INTO settings (key, value) VALUES ('about_photo', ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (photo,)
            )


async def _preview_photo(bot, chat_id: int, photo: str, caption: Optional[str] = None) -> bool:
    """
    Пробуем отправить фото в чат админа и сразу удаляем.
    True — если Telegram принял file_id/URL.
    """
    try:
        msg = await bot.send_photo(chat_id, photo=photo, caption=caption)
        try:
            await bot.delete_message(chat_id, msg.message_id)
        except Exception:
            pass
        return True
    except Exception as e:
        await async_log("WARNING", f"Preview about_photo failed: {e}")
        return False


# -------------------- handlers --------------------

def setup_admin_handlers(dp: Dispatcher, bot):

    # ---------- ПАНЕЛЬ ----------
    @dp.message(Command("admin"))
    async def admin_panel(message: types.Message):
        if not _is_admin(message.from_user.id):
            return await message.answer("🚫 Доступ запрещен")
        await message.answer(
            f"👨‍💻 Админ-панель\n"
            f"• Тест: {'вкл' if config.TEST_MODE else 'выкл'}\n"
            f"• Автоудаление: {'вкл' if config.AUTO_DELETE_ENABLED else 'выкл'}",
            reply_markup=admin_menu()
        )

    # ---------- СТАТИСТИКА ----------
    @dp.message(F.text == "📊 Статистика")
    async def show_stats(message: types.Message):
        if not _is_admin(message.from_user.id):
            return await message.answer("🚫 Доступ запрещен")

        active_users_row = await run_db_query(
            "SELECT COUNT(*) FROM users WHERE access = 1", fetchone=True
        )
        active_users = (active_users_row[0] if active_users_row else 0) or 0

        total_row = await run_db_query(
            "SELECT SUM(amount), COUNT(*) FROM payments", fetchone=True
        )
        total_revenue = _fmt_rub(total_row[0] if total_row else 0)
        total_payments = (total_row[1] if total_row else 0) or 0

        ton_rate = await get_ton_rate()
        await message.answer(
            "📊 Статистика:\n"
            f"• Активных пользователей: {active_users}\n"
            f"• Всего платежей: {total_payments}\n"
            f"• Общая выручка: {total_revenue} RUB\n"
            f"• Курс TON сейчас: {ton_rate:.2f} RUB",
            reply_markup=admin_menu()
        )

    # ---------- ПОЛЬЗОВАТЕЛИ ----------
    @dp.message(F.text == "👥 Пользователи")
    async def list_users(message: types.Message):
        if not _is_admin(message.from_user.id):
            return await message.answer("🚫 Доступ запрещен")

        users = await run_db_query(
            """
            SELECT u.user_id, u.tariff, u.end_date, u.access, COALESCE(SUM(p.amount), 0)
            FROM users u
            LEFT JOIN payments p ON u.user_id = p.user_id
            GROUP BY u.user_id, u.tariff, u.end_date, u.access
            """
        )
        if not users:
            return await message.answer("Нет пользователей в базе.", reply_markup=admin_menu())

        output = io.StringIO()
        output.write("Список пользователей:\n\n")
        for (user_id, tariff, end_date, access, total_paid) in users:
            try:
                user_info = await bot.get_chat(user_id)
                username = f"@{user_info.username}" if user_info.username else "Нет логина"
            except Exception as e:
                username = "Ошибка получения"
                await async_log("ERROR", f"Не удалось получить данные пользователя {user_id}: {e}")

            status = "Активна" if access else "Неактивна"
            if end_date:
                try:
                    end_dt = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
                    end_date_fmt = end_dt.strftime("%d.%m.%Y %H:%M:%S")
                except Exception:
                    end_date_fmt = str(end_date)
            else:
                end_date_fmt = "Нет"

            output.write(
                f"ID: {user_id}\n"
                f"Логин: {username}\n"
                f"Тариф: {tariff or 'Нет'}\n"
                f"Статус: {status}\n"
                f"Дата окончания: {end_date_fmt}\n"
                f"Всего оплачено: {_fmt_rub(total_paid)} RUB\n"
                f"{'-'*30}\n"
            )

        data = output.getvalue().encode("utf-8")
        file = types.BufferedInputFile(data, filename=f"users_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt")
        await bot.send_document(
            message.chat.id,
            document=file,
            caption="Список всех пользователей",
            reply_markup=admin_menu()
        )

    # ---------- ТАРИФЫ ----------
    @dp.message(F.text == "📈 Управление тарифами")
    async def manage_tariffs(message: types.Message):
        if not _is_admin(message.from_user.id):
            return await message.answer("🚫 Доступ запрещен")

        rate = await get_ton_rate()
        header = "<b>📈 Тарифы</b>\n" \
                 "<pre>Ключ         |    RUB |   XTR |    TON | Длительность\n" \
                 "-------------+--------+-------+--------+--------------\n"
        lines = []
        for key, v in TARIFFS.items():
            ton = v["price"] / (rate or 1.0)
            lines.append(_fmt_table_row(key, v["price"], v["stars"], ton, v["duration"]))
        table = header + ("\n".join(lines) if lines else "(пока нет)") + "</pre>"

        hint = (
            "• Нажмите ✏️, чтобы изменить тариф\n"
            "• Нажмите 🗑, чтобы удалить тариф (будет подтверждение)\n"
            "• Или используйте команды:\n"
            "/add key price stars name seconds\n"
            "/edit key price stars name seconds\n"
            "/del key"
        )
        await message.answer(f"{table}\n{hint}", reply_markup=_tariffs_inline_kb())

    @dp.callback_query(lambda c: c.data == "adm_tariff_add")
    async def adm_tariff_add_start(cq: types.CallbackQuery, state: FSMContext):
        if not _is_admin(cq.from_user.id):
            return await cq.answer("Нет доступа", show_alert=True)
        await cq.message.answer("➕ Введите <b>ключ</b> тарифа (lat/цифры, напр. <code>month</code>):")
        await state.set_state(TariffAddFSM.waiting_key)
        await cq.answer()

    @dp.message(TariffAddFSM.waiting_key)
    async def adm_tariff_add_key(message: types.Message, state: FSMContext):
        key = (message.text or "").strip()
        if not key or " " in key:
            return await message.answer("⚠️ Ключ без пробелов. Попробуйте ещё раз.")
        await state.update_data(key=key)
        await message.answer("Введите <b>цену в RUB</b> (целое число):")
        await state.set_state(TariffAddFSM.waiting_price)

    @dp.message(TariffAddFSM.waiting_price)
    async def adm_tariff_add_price(message: types.Message, state: FSMContext):
        try:
            price = int((message.text or "").strip())
        except Exception:
            return await message.answer("⚠️ Нужно целое число. Введите цену в RUB:")
        await state.update_data(price=price)
        await message.answer("Введите <b>стоимость в XTR</b> (целое число):")
        await state.set_state(TariffAddFSM.waiting_stars)

    @dp.message(TariffAddFSM.waiting_stars)
    async def adm_tariff_add_stars(message: types.Message, state: FSMContext):
        try:
            stars = int((message.text or "").strip())
        except Exception:
            return await message.answer("⚠️ Нужно целое число. Введите XTR:")
        await state.update_data(stars=stars)
        await message.answer("Введите <b>название/длительность</b> (например, <code>1 month</code>):")
        await state.set_state(TariffAddFSM.waiting_name)

    @dp.message(TariffAddFSM.waiting_name)
    async def adm_tariff_add_name(message: types.Message, state: FSMContext):
        name = (message.text or "").strip()
        if not name:
            return await message.answer("⚠️ Пусто. Введите название:")
        await state.update_data(name=name)
        await message.answer("Введите <b>длительность в секундах</b> (например, 2592000 для 30 дней):")
        await state.set_state(TariffAddFSM.waiting_seconds)

    @dp.message(TariffAddFSM.waiting_seconds)
    async def adm_tariff_add_finish(message: types.Message, state: FSMContext):
        try:
            seconds = int((message.text or "").strip())
        except Exception:
            return await message.answer("⚠️ Нужно целое число. Введите секунды:")
        data = await state.get_data()
        key = data["key"]
        TARIFFS[key] = {
            "price": data["price"],
            "stars": data["stars"],
            "duration": data["name"],
            "seconds": seconds,
        }
        await state.clear()
        await message.answer(f"✅ Тариф «{key}» добавлен.", reply_markup=_tariffs_inline_kb())

    @dp.callback_query(lambda c: c.data.startswith("adm_tariff_del:"))
    async def adm_tariff_del_ask(cq: types.CallbackQuery):
        if not _is_admin(cq.from_user.id):
            return await cq.answer("Нет доступа", show_alert=True)
        key = cq.data.split(":", 1)[1]
        if key not in TARIFFS:
            return await cq.answer("Не найден", show_alert=True)

        kb = InlineKeyboardBuilder()
        kb.button(text="✅ Да, удалить", callback_data=f"adm_tariff_del_confirm:{key}")
        kb.button(text="↩️ Отмена", callback_data="adm_tariff_cancel")
        kb.adjust(2)

        await cq.message.answer(f"Удалить тариф «{key}»?", reply_markup=kb.as_markup())
        await cq.answer()

    @dp.callback_query(lambda c: c.data == "adm_tariff_cancel")
    async def adm_tariff_del_cancel(cq: types.CallbackQuery):
        await cq.answer("Отменено")

    @dp.callback_query(lambda c: c.data.startswith("adm_tariff_del_confirm:"))
    async def adm_tariff_del_do(cq: types.CallbackQuery):
        if not _is_admin(cq.from_user.id):
            return await cq.answer("Нет доступа", show_alert=True)
        key = cq.data.split(":", 1)[1]
        if key in TARIFFS:
            del TARIFFS[key]
            await cq.message.answer(f"🗑 Удалён: {key}", reply_markup=_tariffs_inline_kb())
        else:
            await cq.message.answer("⚠️ Тариф не найден.")
        await cq.answer()

    @dp.callback_query(lambda c: c.data.startswith("adm_tariff_edit:"))
    async def adm_tariff_edit_start(cq: types.CallbackQuery, state: FSMContext):
        if not _is_admin(cq.from_user.id):
            return await cq.answer("Нет доступа", show_alert=True)
        key = cq.data.split(":", 1)[1]
        if key not in TARIFFS:
            return await cq.answer("Не найден", show_alert=True)

        await state.update_data(key=key)
        cur = TARIFFS[key]
        await cq.message.answer(
            "✏️ Редактирование «{0}».\n"
            "Текущие значения:\n"
            "• RUB: {1}\n• XTR: {2}\n• Название: {3}\n• Секунды: {4}\n\n"
            "Введите новую <b>цену в RUB</b> (целое число):".format(
                key, cur["price"], cur["stars"], cur["duration"], cur["seconds"]
            )
        )
        await state.set_state(TariffEditFSM.waiting_price)
        await cq.answer()

    @dp.message(TariffEditFSM.waiting_price)
    async def adm_tariff_edit_price(message: types.Message, state: FSMContext):
        try:
            price = int((message.text or "").strip())
        except Exception:
            return await message.answer("⚠️ Нужно целое число. Введите цену в RUB:")
        await state.update_data(price=price)
        await message.answer("Введите новую <b>стоимость в XTR</b> (целое число):")
        await state.set_state(TariffEditFSM.waiting_stars)

    @dp.message(TariffEditFSM.waiting_stars)
    async def adm_tariff_edit_stars(message: types.Message, state: FSMContext):
        try:
            stars = int((message.text or "").strip())
        except Exception:
            return await message.answer("⚠️ Нужно целое число. Введите XTR:")
        await state.update_data(stars=stars)
        await message.answer("Введите новое <b>название/длительность</b>:")
        await state.set_state(TariffEditFSM.waiting_name)

    @dp.message(TariffEditFSM.waiting_name)
    async def adm_tariff_edit_name(message: types.Message, state: FSMContext):
        name = (message.text or "").strip()
        if not name:
            return await message.answer("⚠️ Пусто. Введите название:")
        await state.update_data(name=name)
        await message.answer("Введите новые <b>секунды</b> (целое число):")
        await state.set_state(TariffEditFSM.waiting_seconds)

    @dp.message(TariffEditFSM.waiting_seconds)
    async def adm_tariff_edit_finish(message: types.Message, state: FSMContext):
        try:
            seconds = int((message.text or "").strip())
        except Exception:
            return await message.answer("⚠️ Нужно целое число. Введите секунды:")
        data = await state.get_data()
        key = data["key"]
        if key not in TARIFFS:
            await state.clear()
            return await message.answer("⚠️ Тариф исчез во время редактирования.")
        TARIFFS[key] = {
            "price": data["price"],
            "stars": data["stars"],
            "duration": data["name"],
            "seconds": seconds,
        }
        await state.clear()
        await message.answer(f"✅ Тариф «{key}» обновлён.", reply_markup=_tariffs_inline_kb())


    # ---------- СПОСОБЫ ОПЛАТЫ ----------

    async def _render_payments_panel(chat_id: int, message: Optional[types.Message] = None):
        methods = await get_payment_methods()
        if not methods:
            text = "Способы оплаты не найдены в БД."
            kb = None
        else:
            lines = ["💳 <b>Способы оплаты</b>\n"]
            kb = InlineKeyboardBuilder()
            for m in methods:
                code = m["code"]
                title = m["title"]
                enabled = m["enabled"]
                mark = "✅" if enabled else "🚫"
                lines.append(f"{mark} <code>{code}</code> — {title}")
                kb.button(
                    text=f"{mark} {title}",
                    callback_data=f"adm_pay_toggle:{code}",
                )
            kb.adjust(1)
            text = "\n".join(lines)

        if message is not None:
            await message.answer(text, reply_markup=kb.as_markup() if kb else admin_menu())
        else:
            await bot.send_message(chat_id, text, reply_markup=kb.as_markup() if kb else admin_menu())

    @dp.message(F.text == "💳 Способы оплаты")
    async def admin_payments_menu(message: types.Message):
        if not _is_admin(message.from_user.id):
            return await message.answer("🚫 Доступ запрещен")
        await _render_payments_panel(message.chat.id, message)

    @dp.callback_query(F.data.startswith("adm_pay_toggle:"))
    async def admin_toggle_payment(cq: types.CallbackQuery):
        if not _is_admin(cq.from_user.id):
            return await cq.answer("Нет доступа", show_alert=True)

        code = cq.data.split(":", 1)[1]
        methods = await get_payment_methods()
        target = next((m for m in methods if m["code"] == code), None)
        if not target:
            return await cq.answer("Не найден метод", show_alert=True)

        new_state = not bool(target["enabled"])
        await set_payment_method_enabled(code, new_state)
        await cq.answer("Включен" if new_state else "Выключен")

        # обновим текст и кнопки
        try:
            methods = await get_payment_methods()
            lines = ["💳 <b>Способы оплаты</b>\n"]
            kb = InlineKeyboardBuilder()
            for m in methods:
                c = m["code"]
                title = m["title"]
                enabled = m["enabled"]
                mark = "✅" if enabled else "🚫"
                lines.append(f"{mark} <code>{c}</code> — {title}")
                kb.button(
                    text=f"{mark} {title}",
                    callback_data=f"adm_pay_toggle:{c}",
                )
            kb.adjust(1)
            await cq.message.edit_text(
                "\n".join(lines),
                reply_markup=kb.as_markup(),
            )
        except Exception:
            pass

    # ---------- РАССЫЛКА ----------
    @dp.message(F.text == "📢 Рассылка")
    async def bc_start(message: types.Message, state: FSMContext):
        if not _is_admin(message.from_user.id):
            return await message.answer("🚫 Доступ запрещен")
        await state.clear()
        await message.answer(
            "✉️ Пришлите <b>одно сообщение</b> для рассылки:\n"
            "• просто текст\n• фото\n• фото с подписью\n\n"
            "После этого я покажу превью и предложу отправить.",
            reply_markup=admin_menu()
        )
        await state.set_state(BroadcastFSM.waiting_content)

    @dp.message(BroadcastFSM.waiting_content, F.photo)
    async def bc_got_photo(message: types.Message, state: FSMContext):
        if not _is_admin(message.from_user.id):
            return
        file_id = message.photo[-1].file_id
        caption = (message.caption or "").strip() or None
        await state.update_data(kind="photo", file_id=file_id, caption=caption)
        await bot.send_photo(message.chat.id, photo=file_id, caption=caption, reply_markup=_bc_confirm_kb())
        await state.set_state(BroadcastFSM.confirm)

    @dp.message(BroadcastFSM.waiting_content, F.text)
    async def bc_got_text(message: types.Message, state: FSMContext):
        if not _is_admin(message.from_user.id):
            return
        text = message.text
        await state.update_data(kind="text", text=text)
        await message.answer(text, reply_markup=_bc_confirm_kb())
        await state.set_state(BroadcastFSM.confirm)

    @dp.callback_query(BroadcastFSM.confirm, F.data == "bc_cancel")
    async def bc_cancel(cq: types.CallbackQuery, state: FSMContext):
        await state.clear()
        await cq.message.answer("❌ Рассылка отменена.", reply_markup=admin_menu())
        await cq.answer()

    async def _bc_send(to_all: bool, message_obj: types.Message, state: FSMContext):
        data = await state.get_data()
        kind = data.get("kind")
        if kind not in {"text", "photo"}:
            return await message_obj.answer("⚠️ Не найдено содержимое для рассылки.", reply_markup=admin_menu())

        if to_all:
            users = await run_db_query("SELECT user_id FROM users")
        else:
            users = await run_db_query("SELECT user_id FROM users WHERE access = 1")

        ok = 0
        fail = 0
        for (uid,) in users or []:
            try:
                if kind == "text":
                    await bot.send_message(uid, data["text"])
                else:
                    await bot.send_photo(uid, data["file_id"], caption=data.get("caption"))
                ok += 1
            except Exception as e:
                fail += 1
                await async_log("WARNING", f"Не удалось отправить {uid}: {e}")

        await state.clear()
        aud = "всем" if to_all else "активным"
        await message_obj.answer(f"📢 Рассылка отправлена {aud}.\n✅ Успешно: {ok}\n⚠️ Ошибок: {fail}",
                                 reply_markup=admin_menu())

    @dp.callback_query(BroadcastFSM.confirm, F.data == "bc_send_active")
    async def bc_send_active(cq: types.CallbackQuery, state: FSMContext):
        if not _is_admin(cq.from_user.id):
            return await cq.answer("Нет доступа", show_alert=True)
        await _bc_send(False, cq.message, state)
        await cq.answer()

    @dp.callback_query(BroadcastFSM.confirm, F.data == "bc_send_all")
    async def bc_send_all(cq: types.CallbackQuery, state: FSMContext):
        if not _is_admin(cq.from_user.id):
            return await cq.answer("Нет доступа", show_alert=True)
        await _bc_send(True, cq.message, state)
        await cq.answer()

    # ---------- АВТОУДАЛЕНИЕ ----------
    @dp.message(F.text == "🔧 Настройки автоудаления")
    async def toggle_auto_delete(message: types.Message):
        if not _is_admin(message.from_user.id):
            return await message.answer("🚫 Доступ запрещен")
        config.AUTO_DELETE_ENABLED = not config.AUTO_DELETE_ENABLED
        await message.answer(
            f"🛠 Автоудаление {'вкл' if config.AUTO_DELETE_ENABLED else 'выкл'}",
            reply_markup=admin_menu()
        )

    # ---------- СМЕНА КАНАЛА ----------
    @dp.message(F.text == "📺 Сменить канал")
    async def change_channel_id_start(message: types.Message):
        if not _is_admin(message.from_user.id):
            return await message.answer("🚫 Доступ запрещен")
        await message.answer(
            f"Текущий CHANNEL_ID: {config.CHANNEL_ID}\n"
            f"Отправьте команду:\n"
            f"/channel &lt;id&gt;",
            reply_markup=admin_menu()
        )

    @dp.message(F.text.func(lambda t: isinstance(t, str) and t.startswith("/channel ")))
    async def process_new_channel_id(message: types.Message):
        if not _is_admin(message.from_user.id):
            return
        try:
            config.CHANNEL_ID = int(message.text.split(maxsplit=1)[1])
            await message.answer(f"✅ CHANNEL_ID обновлён: {config.CHANNEL_ID}", reply_markup=admin_menu())
        except Exception:
            await message.answer("⚠️ Введите корректный числовой ID!", reply_markup=admin_menu())

    # ---------- ПРИВЕТСТВЕННОЕ ФОТО ----------
    @dp.message(F.text == "🖼 Сменить фото приветствия")
    async def change_greeting_photo_start(message: types.Message, state: FSMContext):
        if not _is_admin(message.from_user.id):
            return await message.answer("🚫 Доступ запрещен")
        await message.answer(
            "📸 Пришлите фото одним сообщением (как изображение).\n"
            "Либо отправьте команду:\n"
            "/photo &lt;file_id&gt;",
            reply_markup=admin_menu()
        )
        await state.set_state(GreetingPhotoFSM.waiting_photo)

    @dp.message(GreetingPhotoFSM.waiting_photo, F.photo)
    async def on_greeting_photo(message: types.Message, state: FSMContext):
        if not _is_admin(message.from_user.id):
            return
        file_id = message.photo[-1].file_id
        await run_db_query(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            ('CHANNEL_PHOTO', file_id)
        )
        config.CHANNEL_PHOTO = file_id
        await message.answer("✅ Фото приветствия обновлено. Новые пользователи увидят его при /start.",
                             reply_markup=admin_menu())
        await state.clear()

    @dp.message(GreetingPhotoFSM.waiting_photo, F.text.func(lambda t: isinstance(t, str) and t.startswith("/photo")))
    async def on_greeting_photo_by_id(message: types.Message, state: FSMContext):
        if not _is_admin(message.from_user.id):
            return
        parts = (message.text or "").split(maxsplit=1)
        if len(parts) < 2:
            return await message.answer("⚠️ Укажи file_id: /photo &lt;file_id&gt;")
        file_id = parts[1].strip()
        if not file_id:
            return await message.answer("⚠️ Пустой file_id")
        await run_db_query(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            ('CHANNEL_PHOTO', file_id)
        )
        config.CHANNEL_PHOTO = file_id
        await message.answer("✅ Фото приветствия обновлено. Новые пользователи увидят его при /start.",
                             reply_markup=admin_menu())
        await state.clear()

    # ---------- «О КАНАЛЕ» — красивый редактор ----------
    @dp.message(F.text == "✍️ Изменить текст 'О канале'")
    async def about_open(message: types.Message, state: FSMContext):
        if not _is_admin(message.from_user.id):
            return await message.answer("🚫 Доступ запрещен")
        await state.clear()
        text, photo = await _get_about_from_db()
        text = (text or "").strip() or "—"

        # Безопасное превью текущего состояния
        if photo:
            try:
                await bot.send_photo(message.chat.id, photo=photo, caption=text, reply_markup=_about_kb())
            except TelegramBadRequest:
                await async_log("WARNING", f"Invalid about_photo stored: {photo}")
                await message.answer(
                    f"⚠️ Текущее фото для 'О канале' недоступно (битый file_id/URL).\n\n{text}",
                    reply_markup=_about_kb()
                )
        else:
            await message.answer(f"Текущий текст:\n\n{text}", reply_markup=_about_kb())

    # — сохранить из одного сообщения (текст/фото/фото+подпись)
    @dp.callback_query(F.data == "about_from_msg")
    async def about_from_msg_start(cq: types.CallbackQuery, state: FSMContext):
        if not _is_admin(cq.from_user.id):
            return await cq.answer("Нет доступа", show_alert=True)
        await cq.message.answer(
            "Пришлите одно сообщение:\n"
            "• текст — сохраню как описание\n"
            "• фото — сохраню как обложку (без текста)\n"
            "• фото с подписью — сохраню <i>фото и текст</i>",
            reply_markup=admin_menu()
        )
        await state.set_state(AboutFSM.waiting_message)
        await cq.answer()

    @dp.message(AboutFSM.waiting_message, F.photo)
    async def about_from_msg_photo(message: types.Message, state: FSMContext):
        file_id = message.photo[-1].file_id
        caption = (message.caption or "").strip() or None

        ok = await _preview_photo(bot, message.chat.id, photo=file_id, caption=caption)
        if not ok:
            return await message.answer("❌ Не удалось принять фото. Пришлите изображение ещё раз (как фото).")

        await state.update_data(photo=file_id, text=caption)
        # превью
        await bot.send_photo(message.chat.id, photo=file_id, caption=caption, reply_markup=_about_kb())
        await message.answer("Нажмите любую кнопку выше, чтобы продолжить (или снова пришлите другое сообщение).")
        # сохраняем сразу
        await _save_about(text=caption or "", photo=file_id)

    @dp.message(AboutFSM.waiting_message, F.text)
    async def about_from_msg_text(message: types.Message, state: FSMContext):
        text = (message.text or "").strip()
        await state.update_data(text=text, photo=None)
        await message.answer(f"Превью текста:\n\n{text}", reply_markup=_about_kb())
        await message.answer("Нажмите любую кнопку выше, чтобы продолжить (или пришлите другое сообщение).")
        await _save_about(text=text)  # сохраняем сразу

    # — редактировать ТОЛЬКО текст
    @dp.callback_query(F.data == "about_edit_text")
    async def about_edit_text(cq: types.CallbackQuery, state: FSMContext):
        if not _is_admin(cq.from_user.id):
            return await cq.answer("Нет доступа", show_alert=True)
        await cq.message.answer("Отправьте новый текст «О канале» одним сообщением:")
        await state.set_state(AboutFSM.waiting_text)
        await cq.answer()

    @dp.message(AboutFSM.waiting_text, F.text)
    async def about_save_text(message: types.Message, state: FSMContext):
        new_text = (message.text or "").strip()
        if not new_text:
            return await message.answer("⚠️ Текст пустой. Пришлите ещё раз.")
        await _save_about(text=new_text)
        await state.clear()
        await message.answer("✅ Текст «О канале» сохранён!", reply_markup=admin_menu())

    # — редактировать ТОЛЬКО фото
    @dp.callback_query(F.data == "about_edit_photo")
    async def about_edit_photo(cq: types.CallbackQuery, state: FSMContext):
        if not _is_admin(cq.from_user.id):
            return await cq.answer("Нет доступа", show_alert=True)
        await cq.message.answer("Пришлите фото одним сообщением (или ответьте file_id командой /aphoto &lt;id&gt;):")
        await state.set_state(AboutFSM.waiting_photo)
        await cq.answer()

    @dp.message(AboutFSM.waiting_photo, F.photo)
    async def about_save_photo(message: types.Message, state: FSMContext):
        file_id = message.photo[-1].file_id
        ok = await _preview_photo(bot, message.chat.id, photo=file_id)
        if not ok:
            return await message.answer("❌ Не удалось принять фото. Пришлите изображение ещё раз (как фото, не как файл).")
        await _save_about(photo=file_id)
        await state.clear()
        await message.answer("✅ Фото для «О канале» сохранено!", reply_markup=admin_menu())

    @dp.message(AboutFSM.waiting_photo, F.text.func(lambda t: isinstance(t, str) and t.startswith("/aphoto ")))
    async def about_save_photo_id(message: types.Message, state: FSMContext):
        file_id = (message.text.split(maxsplit=1)[1] if " " in message.text else "").strip()
        if not file_id:
            return await message.answer("⚠️ Укажи file_id: /aphoto &lt;id&gt;")
        ok = await _preview_photo(bot, message.chat.id, photo=file_id)
        if not ok:
            return await message.answer("❌ Неверный file_id. Отправь корректный /aphoto &lt;id&gt; или пришли фото сообщением.")
        await _save_about(photo=file_id)
        await state.clear()
        await message.answer("✅ Фото для «О канале» сохранено!", reply_markup=admin_menu())

    # — удалить фото
    @dp.callback_query(F.data == "about_del_photo")
    async def about_del_photo(cq: types.CallbackQuery):
        if not _is_admin(cq.from_user.id):
            return await cq.answer("Нет доступа", show_alert=True)
        await _save_about(photo="")  # пустая строка = удалить
        await cq.message.answer("🗑 Обложка удалена. Останется только текст.", reply_markup=admin_menu())
        await cq.answer()

    # ---------- НАЗАД ----------
    @dp.message(F.text == "🔙 Назад")
    async def back_to_main(message: types.Message):
        await message.answer("Главное меню", reply_markup=main_menu())
