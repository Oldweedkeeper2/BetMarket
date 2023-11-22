from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class ManageProductEdit(CallbackData, prefix="manage_product_edit"):
    action: str
    

def get_back_keyboard():
    return InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="manage_product")]])


def get_add_product_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Добавить", callback_data=ManageProductEdit(action="add").pack()))  # Поменять на CallbackData
    builder.row(InlineKeyboardButton(text="Отклонить", callback_data=ManageProductEdit(action="cancel").pack()))
    return builder.as_markup()
