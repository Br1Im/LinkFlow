import logging, aiohttp, uuid, asyncio
from logging.handlers import RotatingFileHandler
from aiogram.enums import ParseMode
from yookassa import Payment
import config
from tariffs import TARIFFS

# logging
logger = logging.getLogger("bot")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(filename='bot.log', maxBytes=1_048_576, backupCount=2)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

async def async_log(level: str, message: str):
    lvl = getattr(logging, level.upper(), logging.INFO)
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, lambda: logger.log(lvl, message))

# TON rate
async def get_ton_rate():
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(config.COINGECKO_API_URL) as r:
                data = await r.json()
                return float(data['the-open-network']['rub'])
    except Exception as e:
        await async_log("ERROR", f"Ошибка получения курса TON: {e}")
        return 100.0

# Admin notify
async def notify_admins(bot, user_id, tariff, amount, payment_method):
    try:
        user_info = await bot.get_chat(user_id)
        username = f"@{user_info.username}" if user_info.username else "Нет логина"
    except Exception:
        username = "Ошибка получения"
    msg = (
        f"💰 Новый платёж!\n"
        f"Пользователь: {user_id} ({username})\n"
        f"Тариф: {TARIFFS[tariff]['duration']}\n"
        f"Сумма: {amount} {payment_method.upper()}\n"
        f"Способ оплаты: {payment_method}\n"
        f"Дата: "
    )
    import datetime as _dt
    msg += _dt.datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    for admin_id in config.ADMIN_IDS:
        try:
            await bot.send_message(admin_id, msg)
        except Exception as e:
            await async_log("ERROR", f"Не удалось уведомить админа {admin_id}: {e}")

# YooKassa payment
async def create_yookassa_payment(user_id, tariff, email):
    idempotence_key = str(uuid.uuid4())
    loop = asyncio.get_event_loop()
    payment = await loop.run_in_executor(None, lambda: Payment.create({
        "amount": {"value": f"{TARIFFS[tariff]['price']:.2f}", "currency": "RUB"},
        "confirmation": {"type": "redirect", "return_url": "https://yourdomain.com/return"},
        "capture": True,
        "description": f"Подписка {TARIFFS[tariff]['duration']} для {user_id}",
        "metadata": {"user_id": str(user_id), "tariff": tariff},
        "receipt": {
            "customer": {"email": email},
            "items": [{"description": f"Подписка {TARIFFS[tariff]['duration']}", "quantity": "1.00",
                       "amount": {"value": f"{TARIFFS[tariff]['price']:.2f}", "currency": "RUB"}, "vat_code": 2}]
        }
    }, idempotence_key))
    return payment

# TON explorer request
async def fetch_ton_transactions(limit=10):
    headers = {"X-API-Key": config.TON_API_KEY} if config.TON_API_KEY else {}
    async with aiohttp.ClientSession() as s:
        async with s.get(f"{config.TON_API_URL}/getTransactions?address={config.TON_WALLET_ADDRESS}&limit={limit}",
                         headers=headers) as r:
            return await r.json()
