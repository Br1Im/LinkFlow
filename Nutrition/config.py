# config.py
import os

# Подтягиваем .env, если пакет установлен (иначе просто берём переменные окружения)
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass


# ---------------- helpers ----------------
def _get_bool(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int = 0) -> int:
    try:
        return int(os.getenv(name, "").strip())
    except Exception:
        return default


from typing import Optional, List, Dict

def _get_list_int(name: str, default: Optional[List[int]] = None) -> List[int]:
    raw = os.getenv(name, "")
    if not raw:
        return default or []
    out: List[int] = []
    for item in raw.replace(";", ",").split(","):
        item = item.strip()
        if not item:
            continue
        try:
            out.append(int(item))
        except Exception:
            pass
    return out


# -------------- Основные настройки --------------
API_TOKEN = os.getenv("API_TOKEN", "")

CHANNEL_ID = _get_int("CHANNEL_ID", 0)           # пример: -1002576167422
ADMIN_IDS = _get_list_int("ADMIN_IDS", [])       # "123,456"

TEST_MODE = _get_bool("TEST_MODE", False)
AUTO_DELETE_ENABLED = _get_bool("AUTO_DELETE_ENABLED", True)

CHECK_INTERVAL = _get_int("CHECK_INTERVAL", 30)  # сек для фоновых проверок
REMINDER_DAYS = _get_int("REMINDER_DAYS", 1)


# -------------- Тексты и ссылки --------------
CHANNEL_LINK = os.getenv("CHANNEL_LINK", "https://t.me/your_channel")

WELCOME_TEXT = os.getenv("WELCOME_TEXT") or (
    "🌐Здравствуйте! Рады видеть Вас в боте платных подписок.\n\n"
    "Мы предоставляем доступ к эксклюзивному контенту🔹\n\n"
    "Подробности Вы можете узнать по кнопке «О канале».\n"
    "Для оплаты нажмите кнопку «Подписка».\n\n"
    "После оплаты Вам будет предоставлена ссылка для вступления🤝\n\n"
    "ПОЛИТИКА КОНФИДЕНЦИАЛЬНОСТИ ПО РАБОТЕ С ПЕРСОНАЛЬНЫМИ ДАННЫМИ ПОЛЬЗОВАТЕЛЕЙ\n"
    "https://telegra.ph/POLITIKA-KONFIDENCIALNOSTI-PO-RABOTE-S-PERSONALNYMI-DANNYMI-POLZOVATELEJ-03-30"
)

CHANNEL_TEXT = os.getenv(
    "CHANNEL_TEXT") or ("📺 О нашем канале:\n"
    "Мы предоставляем эксклюзивный контент для подписчиков:\n"
    "🔹 Свежие новости из мира криптовалют\n"
    "🔹 Аналитика и прогнозы от экспертов\n"
    "🔹 Сигналы на сделки (BTC, ETH, альткоины)\n"
    "🔹 Обзоры перспективных проектов (ICO, NFT, DeFi)\n"
    "🔹 Обучение и гайды для новичков и профи\n\n"
    f"Присоединяйтесь: {CHANNEL_LINK}"
)

SUPPORT_CONTACT = os.getenv("SUPPORT_CONTACT", "@username")
SUPPORT_TG_LINK = os.getenv("SUPPORT_TG_LINK", "")   # открыть Telegram по ссылке
SUPPORT_LINK = os.getenv("SUPPORT_LINK", "")         # прямая ссылка в чат/бот поддержки
FAQ_URL = os.getenv("FAQ_URL", "")
CHANNEL_PHOTO = os.getenv("CHANNEL_PHOTO", "")       # file_id или URL приветственного фото
SUPPORT_PHOTO = os.getenv("SUPPORT_PHOTO", "")       # обложка экрана "Поддержка" (необязательно)
ABOUT_TEXT = os.getenv("ABOUT_TEXT", "")             # дефолт "О канале" (если нет в БД)


# -------------- YooKassa --------------
SHOP_ID = os.getenv("SHOP_ID", "")
SECRET_KEY = os.getenv("SECRET_KEY", "")

# Прокидываем в SDK (если установлен yookassa)
try:
    from yookassa import Configuration  # type: ignore

    if SHOP_ID and SECRET_KEY:
        Configuration.account_id = SHOP_ID
        Configuration.secret_key = SECRET_KEY
except Exception:
    pass


# -------------- TON / курсы --------------
TON_WALLET_ADDRESS = os.getenv("TON_WALLET_ADDRESS", "")
TON_API_URL = os.getenv("TON_API_URL", "https://toncenter.com/api/v2")
TON_API_KEY = os.getenv("TON_API_KEY", "")
COINGECKO_API_URL = os.getenv(
    "COINGECKO_API_URL",
    "https://api.coingecko.com/api/v3/simple/price?ids=the-open-network&vs_currencies=rub",
)


# -------------- Stars --------------
STARS_PROVIDER_TOKEN = os.getenv("STARS_PROVIDER_TOKEN", "")


# -------------- Оферта --------------
OFFER_URL = (
    os.getenv("OFFER_URL")
    or os.getenv("OFFERTA_URL")
    or os.getenv("OFERTA_URL")
)


# -------------- IntellectMoney (ImShop) --------------
IM_ESHOP_ID = os.getenv("IM_ESHOP_ID", "")
IM_BEARER_TOKEN = os.getenv("IM_BEARER_TOKEN", "")
IM_SIGN_SECRET_KEY = os.getenv("IM_SIGN_SECRET_KEY", "")
IM_ESHOP_SECRET_KEY = os.getenv("IM_ESHOP_SECRET_KEY", "")

IM_SUCCESS_URL = os.getenv("IM_SUCCESS_URL", "https://t.me/your_bot")
IM_FAIL_URL = os.getenv("IM_FAIL_URL", IM_SUCCESS_URL)
IM_BACK_URL = os.getenv("IM_BACK_URL", IM_SUCCESS_URL)
IM_RESULT_URL = os.getenv("IM_RESULT_URL", "")


# -------------- Tribute --------------
def _parse_tribute_links(raw: str) -> Dict[int, str]:
    """
    Ждём формат в .env:

      TRIBUTE_SUB_LINKS=100=https://t.me/tribute/app?startapp=...,\
250=https://t.me/tribute/app?startapp=...

    Разделитель между парами — запятая,
    внутри пары: СУММА=ССЫЛКА.
    """
    result: Dict[int, str] = {}
    if not raw:
        return result
    for part in raw.split(","):
        part = part.strip()
        if not part or "=" not in part:
            continue
        k, v = part.split("=", 1)
        try:
            amount = int(k.strip())
        except Exception:
            continue
        url = v.strip()
        if url:
            result[amount] = url
    return result


TRIBUTE_API_KEY = os.getenv("TRIBUTE_API_KEY", "")
TRIBUTE_SUB_LINKS: Dict[int, str] = _parse_tribute_links(
    os.getenv("TRIBUTE_SUB_LINKS", "")
)
