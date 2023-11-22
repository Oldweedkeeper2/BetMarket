from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_role_start_keyboard(role: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    if role == "Админ":
        builder.row(InlineKeyboardButton(text="Управление пользователями", callback_data="settings_management_menu"))
        builder.row(InlineKeyboardButton(text="Управление товаром", callback_data="manage_product"))
    if role == "Менеджер":
        builder.row(InlineKeyboardButton(text="Управление товаром", callback_data="manage_product"))
    
    builder.row(InlineKeyboardButton(text="Пополнить баланс", callback_data="top_up_balance"))
    builder.row(InlineKeyboardButton(text="Товары", callback_data="get_products"))
    builder.row(InlineKeyboardButton(text="Корзина", callback_data="cart"))
    builder.row(InlineKeyboardButton(text="Помощь", callback_data="help"))
    
    return builder.as_markup()


def get_start_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Главная", callback_data="start")]])
