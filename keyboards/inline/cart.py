from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.models import Product


def cart_product_keyboard(product: Product):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Удалить", callback_data=f"del_product_{product.id}"))
    
    return builder.as_markup()


def cart_last_product_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Перейти к оплате", callback_data="pay"))
    builder.row(InlineKeyboardButton(text="Главная", callback_data="start"))
    return builder.as_markup()


def get_back_keyboard():
    return InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Главная", callback_data="start")]])
