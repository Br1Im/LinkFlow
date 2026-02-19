from typing import List, Dict, Optional
from typing import Sequence, Mapping, Any

from aiogram import types
import config  # берём ссылки/настройки из config.py


def main_menu() -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="💼 Профиль", callback_data="profile"),
                types.InlineKeyboardButton(text="💎 Подписка", callback_data="subscription"),
            ],
            [
                types.InlineKeyboardButton(text="📩 Поддержка", callback_data="support"),
                types.InlineKeyboardButton(text="📣 О канале", callback_data="about_channel"),
            ],
        ]
    )


def tariff_menu(tariffs: dict) -> types.InlineKeyboardMarkup:
    """Кнопки тарифов: показываем только цену в RUB."""
    rows: list[list[types.InlineKeyboardButton]] = []
    for name, t in tariffs.items():
        price_rub = t.get("price", 0)
        rows.append(
            [
                types.InlineKeyboardButton(
                    text=f"{name} — {price_rub} RUB",
                    callback_data=f"tariff_{name}",
                )
            ]
        )
    rows.append(
        [types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    )
    return types.InlineKeyboardMarkup(inline_keyboard=rows)


def payment_methods(
    tariff: str,
    methods: Sequence[Mapping[str, Any]],
    with_back: bool = True,
) -> types.InlineKeyboardMarkup:
    """Строим список способов оплаты по данным из БД.

    methods — список словарей:
      {"code": "yookassa", "title": "🇷🇺 YooKassa (RUB)", "enabled": True, ...}
    Предполагаем, что сюда уже передали только enabled-методы.
    """
    rows: list[list[types.InlineKeyboardButton]] = []

    for m in methods:
        code = str(m.get("code") or "").strip()
        title = str(m.get("title") or "").strip() or code
        if not code:
            continue
        rows.append(
            [
                types.InlineKeyboardButton(
                    text=title,
                    callback_data=f"pay_{code}_{tariff}",
                )
            ]
        )

    if with_back:
        rows.append(
            [
                types.InlineKeyboardButton(
                    text="⬅️ Назад к тарифам",
                    callback_data="subscription",
                )
            ]
        )

    return types.InlineKeyboardMarkup(inline_keyboard=rows)



def payment_methods(tariff: str, methods_from_db: List[Dict]) -> types.InlineKeyboardMarkup:
    rows = []

    for m in methods_from_db:
        code = m["code"]          # например "im"
        title = m["title"]        # "IntellectMoney (карта / СБП)"
        rows.append([
            types.InlineKeyboardButton(
                text=title,
                callback_data=f"pay_{code}_{tariff}",
            )
        ])

    rows.append([types.InlineKeyboardButton(
        text="⬅️ Назад к тарифам", callback_data="subscription"
    )])

    return types.InlineKeyboardMarkup(inline_keyboard=rows)



def admin_menu() -> types.ReplyKeyboardMarkup:
    """Клавиатура админ-панели с пунктом '💳 Способы оплаты'."""
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text="📊 Статистика"),
                types.KeyboardButton(text="👥 Пользователи"),
            ],
            [
                types.KeyboardButton(text="📈 Управление тарифами"),
                types.KeyboardButton(text="📢 Рассылка"),
            ],
            [
                types.KeyboardButton(text="💳 Способы оплаты"),
                types.KeyboardButton(text="🔧 Настройки автоудаления"),
            ],
            [
                types.KeyboardButton(text="📺 Сменить канал"),
                types.KeyboardButton(text="🖼 Сменить фото приветствия"),
            ],
            [
                types.KeyboardButton(text="✍️ Изменить текст 'О канале'"),
                types.KeyboardButton(text="🔙 Назад"),
            ],
        ],
        resize_keyboard=True,
    )
