import asyncio
import logging
from aiogram import Bot, Dispatcher
from config.settings import settings
from src.db.session import engine
from src.db.base import Base
from src.bot.middlewares.db import DbSessionMiddleware
from src.bot.handlers import routers

logging.basicConfig(level=logging.INFO)


async def init_db():
    """Автоматическое создание таблиц базы данных при первом старте"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def main():
    """Главная функция инициализации и запуска бота"""
    await init_db()

    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    # Подключаем middleware базы данных
    dp.update.middleware(DbSessionMiddleware())

    # Регистрируем роутеры хэндлеров
    for router in routers:
        dp.include_router(router)

    # Пропускаем накопившиеся сообщения и запускаем Long Polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())