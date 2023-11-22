from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.config import TECH_SUPPORT_USERNAME


def get_help_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Техподдержка", url=f'https://t.me/{TECH_SUPPORT_USERNAME}'),
                InlineKeyboardButton(text="О нас", url=f'https://telegra.ph/O-nas-11-05'))  # TODO: изменить ссылку
    builder.row(InlineKeyboardButton(text="Главная", callback_data="start"))
    return builder.as_markup()
