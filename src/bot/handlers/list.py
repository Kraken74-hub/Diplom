from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload

from src.db.models import User, Subscription
from src.bot.keyboards.inline import delete_tracker_keyboard

router = Router()

@router.message(F.text == "📋 Мои трекеры")
async def list_trackers(message: Message, session: AsyncSession):
    """Вывод всех активных отслеживаний текущего пользователя"""
    res_user = await session.execute(select(User).where(User.tg_id == message.from_user.id))
    user = res_user.scalar_one_or_none()

    if not user:
        await message.answer("У вас пока нет отслеживаемых товаров.")
        return

    # Загружаем подписки вместе с привязанными объектами товаров (joinedload)
    res_subs = await session.execute(
        select(Subscription)
        .options(joinedload(Subscription.product))
        .where(Subscription.user_id == user.id)
    )
    subs = res_subs.scalars().all()

    if not subs:
        await message.answer("Ваш список трекеров пуст.")
        return

    for sub in subs:
        p = sub.product
        text = (
            f"📦 **{p.title}**\n"
            f"Артикул: `{p.nm_id}`\n"
            f"Текущая цена: **{p.current_price} руб.**\n"
            f"Интервал: {sub.check_interval} ч."
        )
        await message.answer(text, reply_markup=delete_tracker_keyboard(sub.id), parse_mode="Markdown")

@router.callback_query(F.data.startswith("del_sub_"))
async def delete_tracker_handler(call: CallbackQuery, session: AsyncSession):
    """Удаление подписки по нажатию кнопки"""
    sub_id = int(call.data.split("_")[2])
    await session.execute(delete(Subscription).where(Subscription.id == sub_id))
    await session.commit()
    await call.message.edit_text("❌ Трекер удален.")
    await call.answer()