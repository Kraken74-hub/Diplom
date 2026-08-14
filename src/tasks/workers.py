import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from aiogram import Bot

from src.tasks.celery_app import celery
from src.db.session import async_session
from src.db.models import Subscription, PriceHistory
from src.parser.client import get_product_info
from config.settings import settings

async def send_notification(bot: Bot, tg_id: int, text: str):
    """Вспомогательная функция для безопасной отправки сообщений в Telegram"""
    try:
        await bot.send_message(chat_id=tg_id, text=text, parse_mode="Markdown")
    except Exception as e:
        print(f"Ошибка отправки уведомления для {tg_id}: {e}")

async def async_check_prices():
    """
    Основная бизнес-логика фоновой проверки:
    1. Извлекаются все подписки.
    2. Фильтруются те, у которых настал срок проверки (исходя из last_checked и check_interval).
    3. Парсится актуальная цена с WB.
    4. Если цена изменилась — отправляется уведомление юзеру и записывается история.
    """
    bot = Bot(token=settings.BOT_TOKEN)
    try:
        async with async_session() as session:
            now = datetime.utcnow()
            res = await session.execute(
                select(Subscription).options(
                    joinedload(Subscription.product),
                    joinedload(Subscription.user)
                )
            )
            subs = res.scalars().all()

            for sub in subs:
                # Проверяем, настал ли интервал проверки для этой подписки
                if now >= sub.last_checked + timedelta(hours=sub.check_interval):
                    prod_info = await get_product_info(sub.product.nm_id)
                    if prod_info:
                        new_price = prod_info["price"]
                        old_price = sub.product.current_price

                        # Сравниваем старую цену с новой
                        if new_price != old_price:
                            sub.product.current_price = new_price
                            session.add(PriceHistory(product_id=sub.product.id, price=new_price))

                            msg = (
                                f"🔔 **Изменение цены!**\n"
                                f"📦 {sub.product.title}\n\n"
                                f"Было: {old_price} руб.\n"
                                f"Стало: **{new_price} руб.**\n"
                                f"🔗 https://www.wildberries.ru/catalog/{sub.product.nm_id}/detail.aspx"
                            )
                            await send_notification(bot, sub.user.tg_id, msg)

                    sub.last_checked = now
            await session.commit()
    finally:
        await bot.session.close()

@celery.task(name='src.tasks.workers.check_prices')
def check_prices():
    """Синхронный оберточный метод Celery, запускающий асинхронный event loop"""
    asyncio.run(async_check_prices())