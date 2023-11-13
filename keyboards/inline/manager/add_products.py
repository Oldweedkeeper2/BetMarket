from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_back_keyboard():
    return InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Главная", callback_data="start")]])
