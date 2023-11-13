from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_back_keyboard():
    return InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Главная", callback_data="start")]])


def get_status_setting_keyboard(user):
    buttons = [
        [
            InlineKeyboardButton(text="Выдать права менеджера", callback_data="accept_add_new_manager")
        ],
        [
            InlineKeyboardButton(text="Главная", callback_data="start")
        ]
    
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
