from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class ManageSetting(CallbackData, prefix="manage_setting"):
    role: str
    action: str


def get_back_keyboard():
    return InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Главная", callback_data="start")]])


def get_settings_management_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    builder.row(InlineKeyboardButton(text="Менеджеры", callback_data=ManageSetting(role="Manager",
                                                                                   action="choice_action").pack()))
    builder.row(InlineKeyboardButton(text="Пользователи", callback_data=ManageSetting(role="User",
                                                                                      action="view").pack()))
    builder.row(InlineKeyboardButton(text="Главная", callback_data="start"))
    return builder.as_markup()
