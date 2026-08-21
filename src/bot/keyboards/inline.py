from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Главная клавиатура с кнопками"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Добавить трекер")],
            [KeyboardButton(text="📋 Мои трекеры")]
        ],
        resize_keyboard=True
    )

def interval_keyboard() -> InlineKeyboardMarkup:
    """клавиатура для выбора интервала отслеживания"""
    builder = InlineKeyboardBuilder()
    builder.button(text="3 часа", callback_data="interval_3")
    builder.button(text="6 часов", callback_data="interval_6")
    builder.button(text="8 часов", callback_data="interval_8")
    builder.adjust(3)
    return builder.as_markup()

def delete_tracker_keyboard(sub_id: int) -> InlineKeyboardMarkup:
    """кнопка удаления конкретного трекера"""
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Удалить", callback_data=f"del_sub_{sub_id}")
    return builder.as_markup()