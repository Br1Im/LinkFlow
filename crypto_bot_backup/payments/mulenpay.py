# payments/mulenpay.py
import uuid
from datetime import datetime, timezone

from aiogram import types
from aiogram.fsm.context import FSMContext

import config
from tariffs import TARIFFS
from db import run_db_query
from services import async_log
from .base import register_payment

# Импортируем MulenPayClient из локального файла
from .mulenpay_client import MulenPayClient

# TODO: Заменить на реальные ключи для crypto-bot
MULENPAY_SECRET_KEY = '09a9972a4245b55339f9233cbd4b2edfe2a81a3f2cde4fcf9d67298298ad00ee'
MULENPAY_PRIVATE_KEY2 = 'aFZRjeQm4YQcZpN1kfqVJJsWGGkQrMPdH5U3elaQ3455b840'
MULENPAY_SHOP_ID = '322'

mp = MulenPayClient(secret_key=MULENPAY_SECRET_KEY)


@register_payment("mp")
async def start_payment(callback, state, storage, bot, tariff, user_id, helpers):
    """Создаёт платёж MulenPay и отправляет ссылку пользователю"""
    await async_log("INFO", f"[MulenPay] Создание платежа для user={user_id}, tariff={tariff}")
    
    # Получаем сумму из storage (для кастомных тарифов) или из TARIFFS
    if tariff == "custom":
        user_data = storage.get(user_id, {})
        amount = user_data.get("amount", 3000)
        tariff_info = user_data.get("tariff_info", {})
        description = tariff_info.get("description", "Курс по криптовалютам")
    else:
        amount = TARIFFS[tariff]["price"]
        description = f"Курс по криптовалютам - {tariff}"
    
    order_id = f"{user_id}_{tariff}_{uuid.uuid4().hex[:8]}"
    
    try:
        response = await mp.create_payment(
            private_key2=MULENPAY_PRIVATE_KEY2,
            currency="rub",
            amount=amount,
            uuid=order_id,
            shopId=MULENPAY_SHOP_ID,
            description=description,
        )
        
        payment_id = response["id"]
        payment_url = response["paymentUrl"]
        
        # Сохраняем платёж в БД
        await register_payment(
            user_id=user_id,
            tariff=tariff,
            amount=amount,
            method="mulenpay",
            external_id=str(payment_id),
        )
        
        # Отправляем ссылку на оплату
        kb = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="💳 Оплатить", url=payment_url)],
            [types.InlineKeyboardButton(text="🔄 Проверить оплату", callback_data=f"check_mp:{payment_id}:{amount}")],
            [types.InlineKeyboardButton(text="❌ Отмена", callback_data="back_to_main")]
        ])
        
        await callback.message.delete()
        await callback.message.answer(
            f"💳 Оплата через MulenPay (СБП)\n\n"
            f"💰 Сумма: {amount} руб.\n"
            f"📝 Описание: {description}\n\n"
            f"Нажмите кнопку ниже для оплаты:",
            reply_markup=kb
        )
        
    except Exception as e:
        await async_log("ERROR", f"[MulenPay] Ошибка создания платежа: {e}")
        await callback.message.answer(
            "⚠️ Ошибка при создании платежа. Попробуйте позже или обратитесь в поддержку.",
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_main")]
            ])
        )


async def check_payment_status(callback: types.CallbackQuery, payment_id: str, amount: str, bot) -> None:
    """Проверяет статус платежа MulenPay"""
    try:
        response = await mp.get_payment(
            private_key2=MULENPAY_PRIVATE_KEY2,
            payment_id=payment_id
        )
        
        status = int(response["payment"]["status"])
        
        # Статусы: 3, 5, 6 = успешная оплата
        if status in [3, 5, 6]:
            await callback.message.delete()
            
            user_id = callback.from_user.id
            
            # Находим платёж в БД
            row = await run_db_query(
                "SELECT tariff FROM payments WHERE user_id = ? AND external_id = ?",
                (user_id, str(payment_id)),
                fetchone=True
            )
            
            if row:
                tariff = row[0]
                
                # Обновляем статус платежа
                await run_db_query(
                    "UPDATE payments SET status = 'paid' WHERE external_id = ?",
                    (str(payment_id),)
                )
                
                # Генерируем инвайт-ссылку
                from common import generate_invite_link
                invite_link = await generate_invite_link(bot, tariff)
                
                await callback.message.answer(
                    f"✅ Оплата успешно получена!\n\n"
                    f"💰 Сумма: {amount} руб.\n\n"
                    f"Ваша ссылка для вступления:\n{invite_link}",
                    disable_web_page_preview=True
                )
            else:
                await callback.answer("Платёж не найден", show_alert=True)
        else:
            await callback.answer("Платёж ещё не оплачен. Попробуйте позже.", show_alert=True)
            
    except Exception as e:
        await async_log("ERROR", f"[MulenPay] Ошибка проверки платежа: {e}")
        await callback.answer("Ошибка при проверке платежа", show_alert=True)
