from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.parser.utils import extract_nm_id
from src.parser.client import get_product_info
from src.db.models import User, Product, Subscription, PriceHistory
from src.bot.keyboards.inline import interval_keyboard

router = Router()

class AddTrackStates(StatesGroup):
    """Машина состояний (FSM) для пошагового добавления трекера"""
    waiting_for_input = State()     # Ожидание ссылки или артикула
    waiting_for_interval = State()  # Ожидание нажатия кнопки с интервалом

@router.message(F.text == "➕ Добавить трекер")
async def start_tracking(message: Message, state: FSMContext):
    """Запуск сценария добавления трекера"""
    await message.answer("Отправьте ссылку на товар Wildberries или его артикул (nm_id):")
    await state.set_state(AddTrackStates.waiting_for_input)

@router.message(AddTrackStates.waiting_for_input)
async def process_input(message: Message, state: FSMContext):
    """Валидация введенной ссылки и получение информации о товаре через парсер"""
    nm_id = extract_nm_id(message.text)
    if not nm_id:
        await message.answer("Не удалось извлечь артикул. Введите корректную ссылку или номер:")
        return

    prod_data = await get_product_info(nm_id)
    if not prod_data:
        await message.answer("Не удалось найти товар на WB. Проверьте артикул.")
        return

    # Сохраняем данные товара во временное состояние FSM
    await state.update_data(prod_data=prod_data)
    await message.answer(
        f"Товар: {prod_data['title']}\n"
        f"Текущая цена: {prod_data['price']} руб.\n\n"
        f"Выберите интервал проверки:",
        reply_markup=interval_keyboard()
    )
    await state.set_state(AddTrackStates.waiting_for_interval)

@router.callback_query(AddTrackStates.waiting_for_interval, F.data.startswith("interval_"))
async def process_interval(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Сохранение выбранного интервала и записи трекера в БД"""
    interval = int(call.data.split("_")[1])
    data = await state.get_data()
    prod_data = data["prod_data"]

    # Находим пользователя
    res_user = await session.execute(select(User).where(User.tg_id == call.from_user.id))
    user = res_user.scalar_one_or_none()
    if not user:
        user = User(tg_id=call.from_user.id, username=call.from_user.username)
        session.add(user)
        await session.flush()

    # Ищем или создаем товар в БД
    res_prod = await session.execute(select(Product).where(Product.nm_id == prod_data["nm_id"]))
    product = res_prod.scalar_one_or_none()
    if not product:
        product = Product(
            nm_id=prod_data["nm_id"],
            title=prod_data["title"],
            current_price=prod_data["price"],
            image_url=prod_data.get("image_url")
        )
        session.add(product)
        await session.flush()
        # Фиксируем начальную цену в истории
        session.add(PriceHistory(product_id=product.id, price=prod_data["price"]))
    else:
        product.current_price = prod_data["price"]

    # Создаем подписку
    sub = Subscription(user_id=user.id, product_id=product.id, check_interval=interval)
    session.add(sub)
    await session.commit()

    await call.message.edit_text(f"✅ Трекер добавлен!\nИнтервал: {interval} ч.")
    await state.clear()
    await call.answer()