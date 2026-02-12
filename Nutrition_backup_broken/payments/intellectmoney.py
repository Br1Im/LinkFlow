# payments/intellectmoney.py
import uuid
from typing import Union, Tuple, List, Dict, Optional, Any
import hashlib
import aiohttp
from datetime import datetime, timezone

from aiogram import types
from aiogram.fsm.context import FSMContext

import config
from tariffs import TARIFFS
from db import run_db_query
from services import async_log
from .base import register_payment


IM_API_URL = "https://api.intellectmoney.ru/merchant/createInvoice"
IM_MERCHANT_URL = "https://merchant.intellectmoney.ru/ru/"


def _fmt_amount(price_rub: Union[int, float]) -> str:
    # IntellectMoney ждёт строку с 2 знаками после запятой
    return f"{float(price_rub):.2f}"


def _build_sign_and_hash(
    eshop_id: str,
    order_id: str,
    amount: str,
    currency: str,
    email: str,
    preference: str,
) -> Tuple[str, str]:
    """
    Формулы взяты из документации Merchant 2.0 API:
    sign  = SHA256( eshopId::orderId::...::preference::signSecretKey )
    hash  =  MD5(  eshopId::orderId::...::preference::eshopSecretKey )
    Всё, что нам не нужно, заполняем пустыми строками, но разделители "::" сохраняем.
    """
    service_name = ""
    user_name = ""
    success_url = config.IM_SUCCESS_URL or ""
    fail_url = config.IM_FAIL_URL or ""
    back_url = config.IM_BACK_URL or ""
    result_url = config.IM_RESULT_URL or ""
    expire_date = ""
    hold_mode = ""
    # order: eshopId::orderId::serviceName::recipientAmount::recipientCurrency::
    #        userName::email::successUrl::failUrl::backUrl::resultUrl::expireDate::holdMode::preference::KEY
    base = "::".join(
        [
            eshop_id,
            order_id,
            service_name,
            amount,
            currency,
            user_name,
            email,
            success_url,
            fail_url,
            back_url,
            result_url,
            expire_date,
            hold_mode,
            preference,
        ]
    )

    sign_str = f"{base}::{config.IM_SIGN_SECRET_KEY}"
    hash_str = f"{base}::{config.IM_ESHOP_SECRET_KEY}"

    sign = hashlib.sha256(sign_str.encode("utf-8")).hexdigest()
    hash_ = hashlib.md5(hash_str.encode("utf-8")).hexdigest()
    return sign, hash_


async def _create_invoice(user_id: int, tariff: str, email: Optional[str] = None) -> dict:
    """
    Выставляем счёт по Merchant 2.0 API и возвращаем JSON.
    preference='BankCard,Sbp' – на платёжной странице будут карта + СБП.
    """
    eshop_id = str(config.IM_ESHOP_ID)
    if not (eshop_id and config.IM_BEARER_TOKEN and config.IM_SIGN_SECRET_KEY and config.IM_ESHOP_SECRET_KEY):
        raise RuntimeError("IntellectMoney не сконфигурирован (eshopId / токены пустые)")

    amount = _fmt_amount(TARIFFS[tariff]["price"])
    currency = "TST"  # для тестового стенда; в бою укажешь RUB, если у тебя боевой магазин
    email = (email or "").strip()
    order_id = f"{user_id}_{tariff}_{uuid.uuid4().hex[:8]}"

    preference = "BankCard,Sbp"

    sign, hash_ = _build_sign_and_hash(
        eshop_id=eshop_id,
        order_id=order_id,
        amount=amount,
        currency=currency,
        email=email,
        preference=preference,
    )

    headers = {
        "Authorization": f"Bearer {config.IM_BEARER_TOKEN}",
        "Sign": sign,
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }

    data = {
        "eshopId": eshop_id,
        "orderId": order_id,
        "recipientAmount": amount,
        "recipientCurrency": currency,
        "email": email,
        "hash": hash_,
        "serviceName": f"Подписка {TARIFFS[tariff]['duration']}",
        "successUrl": config.IM_SUCCESS_URL,
        "failUrl": config.IM_FAIL_URL,
        "backUrl": config.IM_BACK_URL,
        "resultUrl": config.IM_RESULT_URL,
        "preference": preference,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(IM_API_URL, data=data, headers=headers) as resp:
            text = await resp.text()
            try:
                js = await resp.json()
            except Exception:
                raise RuntimeError(f"Ошибочный ответ IntellectMoney: {resp.status} {text}")

    await async_log("INFO", f"IntellectMoney createInvoice response: {js}")

    # по доке: OperationState.Code == 0 и Result.State.Code == 0 => успех
    if js.get("OperationState", {}).get("Code") != 0 or js.get("Result", {}).get("State", {}).get("Code") != 0:
        raise RuntimeError(f"CreateInvoice вернул ошибку: {js}")

    return js


def _build_payment_url(invoice_id: str) -> str:
    eshop_id = str(config.IM_ESHOP_ID)

    base = f"{eshop_id}::{invoice_id}::{config.IM_ESHOP_SECRET_KEY}"
    h = hashlib.md5(base.encode("utf-8")).hexdigest()

    return f"{IM_MERCHANT_URL}?eshopId={eshop_id}&invoiceId={invoice_id}&hash={h}"


@register_payment("im")   # ← ВАЖНО: регистрируем код способа оплаты
async def start_intellectmoney_payment(
    callback: types.CallbackQuery,
    state: FSMContext,
    storage: Dict[int, dict],
    bot,
    tariff: str,
    user_id: int,
    helpers: dict,
):
    """
    Старт обработчика для кнопки pay_im_<tariff>.
    1) создаём счёт через API;
    2) строим ссылку на платёжную страницу;
    3) показываем пользователю кнопку «Оплатить».
    """
    email = ""  # пока пустой, для теста можно так.

    try:
        inv = await _create_invoice(user_id=user_id, tariff=tariff, email=email)
    except Exception as e:
        await async_log("ERROR", f"IntellectMoney createInvoice error: {e}")
        await callback.message.answer(
            f"⚠️ Не удалось создать счёт в IntellectMoney.\n"
            f"Сообщите в поддержку: {config.SUPPORT_CONTACT}",
        )
        return await callback.answer("Ошибка IntellectMoney", show_alert=True)

    invoice_id = str(inv["Result"]["InvoiceId"])
    pay_url = _build_payment_url(invoice_id)

    await run_db_query(
        "INSERT INTO payments (user_id, amount, tariff, date, ton_comment) VALUES (?, ?, ?, ?, ?)",
        (
            user_id,
            TARIFFS[tariff]["price"],
            tariff,
            datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            f"IM:{invoice_id}",
        ),
    )

    caption = (
        f"💳 <b>Оплата через IntellectMoney</b>\n"
        f"Тариф: {TARIFFS[tariff]['duration']}\n"
        f"Сумма: {_fmt_amount(TARIFFS[tariff]['price'])} RUB\n\n"
        "Нажмите кнопку ниже, откроется страница IntellectMoney,\n"
        "где можно выбрать оплату <b>картой</b> или <b>СБП</b>."
    )

    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="💳 Оплатить (IntellectMoney)", url=pay_url)],
            [types.InlineKeyboardButton(text="⬅️ Назад к тарифам", callback_data="subscription")],
        ]
    )

    photo = await helpers["welcome_photo"]()
    if photo:
        await helpers["edit_to_photo_screen"](callback.message, photo, caption, kb)
    else:
        await helpers["edit_to_text_screen"](callback.message, caption, kb)

    storage[user_id] = {
        **storage.get(user_id, {}),
        "panel_chat_id": callback.message.chat.id,
        "panel_message_id": callback.message.message_id,
    }

    await callback.answer()