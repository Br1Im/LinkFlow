import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import config
from handlers_public import setup_public_handlers
from handlers_admin import setup_admin_handlers
from tasks import start_background_tasks
from services import async_log


async def main():
    # Сессия HTTP (таймаут в секундах)
    session = AiohttpSession(timeout=10)

    # Токен: проверь, что именно API_TOKEN есть в config
    bot = Bot(
        token=getattr(config, "API_TOKEN", None),
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher()

    # Регистрируем хендлеры
    setup_public_handlers(dp, bot)
    setup_admin_handlers(dp, bot)

    # Сбрасываем вебхук и дропаем «висящие» апдейты (аналог skip_updates)
    await bot.delete_webhook(drop_pending_updates=True)

    await async_log("INFO", "Бот запускается…")

    # Фоновые задачи (проверки платежей/напоминания и т.п.)
    await start_background_tasks(bot)

    # Старт поллинга
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
