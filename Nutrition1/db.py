import sqlite3
import asyncio
from functools import partial

import config
from services import async_log

DB_PATH = "subscriptions.db"


async def run_db_query(query, params=(), fetchone: bool = False):
    """Базовый helper для работы с SQLite в отдельном потоке."""
    loop = asyncio.get_event_loop()
    with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
        cursor = conn.cursor()
        await loop.run_in_executor(None, partial(cursor.execute, query, params))
        result = cursor.fetchone() if fetchone else cursor.fetchall()
        conn.commit()
        return result


async def _ensure_default_settings():
    """Заполняем settings минимальными значениями, если их нет."""
    cur = await run_db_query(
        "SELECT value FROM settings WHERE key='channel_text'",
        fetchone=True,
    )
    if not cur:
        await run_db_query(
            "INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)",
            ("channel_text", config.CHANNEL_TEXT),
        )


async def _ensure_default_payment_methods():
    """Создаём дефолтные способы оплаты, если таблица пустая.

    code       title                            sort_order
    ------------------------------------------------------
    yookassa   🇷🇺 YooKassa (RUB)               10
    stars      ⭐ Telegram Stars                20
    ton        💎 Toncoin (TON)                30
    im         IntellectMoney (карта / СБП)    40
    tribute    TriBute (карта / СБП)           50
    """
    rows = await run_db_query("SELECT code FROM payment_methods")
    existing = {code for (code,) in rows} if rows else set()

    defaults = [
        ("yookassa", "\U0001f1f7\U0001f1fa YooKassa (RUB)", 10),
        ("stars", "⭐ Telegram Stars", 20),
        ("ton", "💎 Toncoin (TON)", 30),
        ("im", "IntellectMoney (карта / СБП)", 40),
        ("tribute", "TriBute (карта / СБП)", 50),
    ]
    for code, title, sort_order in defaults:
        if code in existing:
            continue
        await run_db_query(
            "INSERT INTO payment_methods (code, title, enabled, sort_order) "
            "VALUES (?, ?, 1, ?)",
            (code, title, sort_order),
        )


async def init_db():
    """Создаём все нужные таблицы и дефолтные записи."""
    # Пользователи
    await run_db_query(
        """CREATE TABLE IF NOT EXISTS users (
            user_id     INTEGER PRIMARY KEY,
            tariff      TEXT,
            end_date    TEXT,
            access      INTEGER,
            invite_link TEXT,
            payment_id  TEXT,
            reminded    INTEGER DEFAULT 0
        )"""
    )

    # Платежи
    await run_db_query(
        """CREATE TABLE IF NOT EXISTS payments (
            payment_id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id              INTEGER,
            amount               REAL,
            tariff               TEXT,
            date                 TEXT,
            yookassa_payment_id  TEXT,
            ton_comment          TEXT
        )"""
    )

    # Настройки
    await run_db_query(
        """CREATE TABLE IF NOT EXISTS settings (
            key   TEXT PRIMARY KEY,
            value TEXT
        )"""
    )

    # Способы оплаты
    await run_db_query(
        """CREATE TABLE IF NOT EXISTS payment_methods (
            code       TEXT PRIMARY KEY,
            title      TEXT NOT NULL,
            enabled    INTEGER NOT NULL DEFAULT 1,
            sort_order INTEGER NOT NULL DEFAULT 100
        )"""
    )

    await _ensure_default_settings()
    await _ensure_default_payment_methods()
    await async_log("INFO", "База данных инициализирована")


async def get_setting(key: str):
    row = await run_db_query(
        "SELECT value FROM settings WHERE key = ?",
        (key,),
        fetchone=True,
    )
    return row[0] if row else None


async def set_setting(key: str, value: str):
    await run_db_query(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value),
    )


async def get_payment_methods(enabled_only: bool = False):
    """Возвращает список словарей со способами оплаты.

    [
      {"code": "yookassa", "title": "🇷🇺 YooKassa (RUB)", "enabled": True, "sort_order": 10},
      ...
    ]
    """
    sql = "SELECT code, title, enabled, sort_order FROM payment_methods"
    params = ()
    if enabled_only:
        sql += " WHERE enabled = 1"
    sql += " ORDER BY sort_order, title"

    rows = await run_db_query(sql, params)
    methods = []
    for code, title, enabled, sort_order in rows or []:
        methods.append(
            {
                "code": code,
                "title": title,
                "enabled": bool(enabled),
                "sort_order": sort_order,
            }
        )
    return methods


async def set_payment_method_enabled(code: str, enabled: bool):
    """Включить/выключить способ оплаты."""
    await run_db_query(
        "UPDATE payment_methods SET enabled = ? WHERE code = ?",
        (1 if enabled else 0, code),
    )
