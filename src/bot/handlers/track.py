from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.parser.utils import extract_nm_id
from src.parser.client import get_product_info
from src.db.models import User, Product, Subscription, PriceHistory
from src.bot.keyboards.inline import interval_keyboard

router = Router()


class AddTrackStates(StatesGroup):
    """Машина состояний (FSM) для пошагового добавления трекера"""
    waiting_for_input = State()  # Ожидание ссылки или артикула
    waiting_for_interval = State()  # Ожидание нажатия кнопки с интервалом


@router.message(F.text == "➕ Добавить трекер")
async def start_tracking(message: Message, state: FSMContext):
    """Запуск сценария добавления трекера"""
    await state.set_state(AddTrackStates.waiting_for_input)
    await message.answer("Отправьте ссылку на товар Wildberries или его артикул (nm_id):")


@router.message(AddTrackStates.waiting_for_input)
async def process_input(message: Message, state: FSMContext):
    """Валидация введенной ссылки и получение информации о товаре через парсер"""
    # Извлекаем чистый nm_id из текста (игнорируя параметры ?size=)
    nm_id = extract_nm_id(message.text)
    if not nm_id:
        await message.answer(
            "⚠️ Не удалось извлечь артикул. Отправьте корректную ссылку WB или чистый номер товара:"
        )
        return

    prod_data = await get_product_info(nm_id)
    if not prod_data:
        await message.answer(
            "⚠️ Не удалось найти товар на WB. Проверьте артикул или повторите попытку позже."
        )
        return

    # Сохраняем данные товара во временное состояние FSM
    await state.update_data(prod_data=prod_data)

    price_fmt = f"<b>{prod_data['price']} руб.</b>" if prod_data.get("price") is not None else "<i>Нет в наличии</i>"

    await message.answer(
        f"📦 <b>Товар найден:</b>\n\n"
        f"<b>Название:</b> {prod_data['title']}\n"
        f"<b>Артикул:</b> <code>{prod_data['nm_id']}</code>\n"
        f"<b>Текущая цена:</b> {price_fmt}\n\n"
        f"Выберите интервал проверки цены:",
        reply_markup=interval_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(AddTrackStates.waiting_for_interval)


@router.callback_query(StateFilter(AddTrackStates.waiting_for_interval),F.data.startswith("interval_"))
async def process_interval(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Сохранение выбранного интервала и записи трекера в БД"""
    await call.answer()

    try:
        interval = int(call.data.split("_")[1])
    except (IndexError, ValueError):
        await call.message.edit_text("❌ Произошла ошибка при выборе интервала.")
        await state.clear()
        return

    data = await state.get_data()
    prod_data = data.get("prod_data")

    if not prod_data:
        await call.message.edit_text("❌ Данные сессии истекли. Начните добавление заново.")
        await state.clear()
        return

    # 1. Находим или создаем пользователя
    res_user = await session.execute(select(User).where(User.tg_id == call.from_user.id))
    user = res_user.scalar_one_or_none()
    if not user:
        user = User(tg_id=call.from_user.id, username=call.from_user.username)
        session.add(user)
        await session.flush()

    # 2. Ищем или создаем товар в БД
    res_prod = await session.execute(select(Product).where(Product.nm_id == prod_data["nm_id"]))
    product = res_prod.scalar_one_or_none()

    if not product:
        product = Product(
            nm_id=prod_data["nm_id"],
            title=prod_data["title"],
            current_price=prod_data.get("price"),
            image_url=prod_data.get("image_url")
        )
        session.add(product)
        await session.flush()

        # Фиксируем начальную цену в истории, если цена определена
        if prod_data.get("price") is not None:
            session.add(PriceHistory(product_id=product.id, price=prod_data["price"]))
    else:
        product.current_price = prod_data.get("price")

    # 3. Проверяем наличие подписки (защита от дубликатов)
    res_sub = await session.execute(
        select(Subscription).where(
            Subscription.user_id == user.id,
            Subscription.product_id == product.id
        )
    )
    sub = res_sub.scalar_one_or_none()

    if sub:
        sub.check_interval = interval
        msg_text = f"🔄 Интервал отслеживания обновлен!\nНовый интервал: <b>{interval} ч.</b>"
    else:
        sub = Subscription(user_id=user.id, product_id=product.id, check_interval=interval)
        session.add(sub)
        msg_text = f"✅ Трекер успешно добавлен!\nИнтервал проверки: <b>{interval} ч.</b>"

    await session.commit()

    await call.message.edit_text(msg_text, parse_mode="HTML")
    await state.clear()