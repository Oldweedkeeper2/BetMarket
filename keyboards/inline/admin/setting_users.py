from typing import List

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.config import USER_PAGE_WIDTH
from data.models import User
from keyboards.inline.admin.settings import ManageSetting


class UserSetting(CallbackData, prefix="manage_setting_User"):
    id: int
    sub_action: str


class UserBalanceChanger(CallbackData, prefix="manage_setting_User_balance"):
    id: int
    sub_action: str


class UsersPagination(CallbackData, prefix="manage_setting_User_pagination"):
    action: str
    page: int


def get_user_setting_keyboard(id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Бан", callback_data=UserSetting(id=id,
                                                                           sub_action="ban").pack()),
                InlineKeyboardButton(text="Разбан", callback_data=UserSetting(id=id,
                                                                              sub_action="unban").pack()))
    builder.row(InlineKeyboardButton(text="Изменить баланс", callback_data=UserSetting(id=id,
                                                                                       sub_action="balance").pack()))
    builder.row(InlineKeyboardButton(text="Назад", callback_data=ManageSetting(role="User",
                                                                               action="view").pack()))
    
    return builder.as_markup()


def get_user_balance_changer_keyboard(id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Прибавить", callback_data=UserBalanceChanger(id=id,
                                                                                        sub_action="add").pack()),
                InlineKeyboardButton(text="Отнять", callback_data=UserBalanceChanger(id=id,
                                                                                     sub_action="deduct").pack()))
    builder.row(InlineKeyboardButton(text="Назад", callback_data=ManageSetting(role="User",
                                                                               action="view").pack()))
    
    return builder.as_markup()


# USER PAGINATION


def create_pagination_buttons(page: int):
    """Creates pagination buttons."""
    return [
        InlineKeyboardButton(text="←", callback_data=UsersPagination(action="prev", page=page).pack()),
        InlineKeyboardButton(text=str(page + 1), callback_data='empty'),
        InlineKeyboardButton(text="→", callback_data=UsersPagination(action="next", page=page).pack())
    ]


def paginator(users_list: List[User], page: int = 0):
    """Creates a paginated keyboard for product list."""
    builder = InlineKeyboardBuilder()
    start = page * USER_PAGE_WIDTH
    end = start + USER_PAGE_WIDTH
    
    for user in users_list[start:end]:
        builder.row(InlineKeyboardButton(text=str(user.username),
                                         callback_data=UserSetting(id=user.id,
                                                                   sub_action="edit").pack()))
    builder.row(*create_pagination_buttons(page), width=3)
    builder.row(InlineKeyboardButton(text='Назад',
                                     callback_data='settings_management_menu'))
    return builder.as_markup()
