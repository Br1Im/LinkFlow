# common.py
from datetime import datetime, timedelta, timezone
import config
from db import run_db_query, init_db
from tariffs import TARIFFS


# --------------------------------------------------------
# Текст "О канале"
# --------------------------------------------------------
async def get_channel_text():
    row = await run_db_query(
        "SELECT value FROM settings WHERE key='channel_text'",
        fetchone=True
    )
    return row[0] if row else config.CHANNEL_TEXT


# --------------------------------------------------------
# Безопасное создание инвайт-ссылки
# --------------------------------------------------------
async def generate_invite_link(bot, user_id, tariff):
    """
    - expire_date минимум +5 минут
    - максимум +365 дней
    - корректный unix timestamp
    """

    # секунды из тарифа
    seconds = TARIFFS[tariff]["seconds"]

    now = datetime.now(timezone.utc)
    end_dt = now + timedelta(seconds=seconds)

    # Telegram ограничения
    min_dt = now + timedelta(minutes=5)
    max_dt = now + timedelta(days=365)

    if end_dt < min_dt:
        end_dt = min_dt
    if end_dt > max_dt:
        end_dt = max_dt

    expire_ts = int(end_dt.timestamp())

    invite = await bot.create_chat_invite_link(
        chat_id=config.CHANNEL_ID,
        expire_date=expire_ts,
        member_limit=1,
        name=f"Invite for {user_id}",
    )

    await run_db_query(
        "UPDATE users SET invite_link=? WHERE user_id=?",
        (invite.invite_link, user_id)
    )

    return invite.invite_link


# --------------------------------------------------------
# ensure_db — вызывается при старте бота
# --------------------------------------------------------
async def ensure_db():
    await init_db()


# --------------------------------------------------------
# Приветственное фото
# --------------------------------------------------------
async def get_welcome_photo():
    """
    Возвращает file_id / URL / None.
    Приоритет: БД -> config.CHANNEL_PHOTO -> None
    """
    try:
        row = await run_db_query(
            "SELECT value FROM settings WHERE key='CHANNEL_PHOTO'",
            fetchone=True
        )
        if row and row[0]:
            return row[0]
    except Exception:
        pass

    if config.CHANNEL_PHOTO:
        return config.CHANNEL_PHOTO

    return None
