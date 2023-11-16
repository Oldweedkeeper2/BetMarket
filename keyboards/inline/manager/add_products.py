from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_back_keyboard():
    return InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Главная", callback_data="start")]])


def get_add_product_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Добавить", callback_data="product_action:add"))
    builder.row(InlineKeyboardButton(text="Отклонить", callback_data="product_action:cancel"))
    return builder.as_markup()
