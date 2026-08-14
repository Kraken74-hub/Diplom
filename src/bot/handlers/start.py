from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.db.models.user import User
from src.bot.keyboards.inline import main_menu_keyboard

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession):
    """Обработка команды /start: регистрация нового пользователя в БД"""
    result = await session.execute(select(User).where(User.tg_id == message.from_user.id))
    user = result.scalar_one_or_none()

    if not user:
        user = User(tg_id=message.from_user.id, username=message.from_user.username)
        session.add(user)
        await session.commit()

    await message.answer(
        "Привет! Я бот для отслеживания цен на Wildberries.\n"
        "Используйте меню ниже для работы с трекерами.",
        reply_markup=main_menu_keyboard()
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработка команды /help"""
    await message.answer(
        "Бот позволяет отслеживать цены товаров WB.\n"
        "▫️ Нажмите 'Добавить трекер' и отправьте ссылку/артикул товара.\n"
        "▫️ Выберите интервал проверки (3, 6 или 8 часов).\n"
        "▫️ В 'Мои трекеры' можно просмотреть список и удалить отслеживание."
    )