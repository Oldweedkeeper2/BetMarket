from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.models import User
from keyboards.inline.admin.settings import ManageSetting


class ManagerSetting(CallbackData, prefix="manage_setting_Manager"):
    id: int
    sub_action: str


def get_with_managers_keyboard(managers_list: list):
    builder = InlineKeyboardBuilder()
    
    for manager in managers_list:  # type: User
        builder.row(InlineKeyboardButton(text=str(manager.username),
                                         callback_data=ManagerSetting(id=manager.id,
                                                                      sub_action="edit").pack()))
    builder.row(InlineKeyboardButton(text='Назад',
                                     callback_data=ManageSetting(role="Manager",
                                                                               action="choice_action").pack()))
    return builder.as_markup()


def get_manager_setting_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
            InlineKeyboardButton(text="Добавить менеджера",
                                 callback_data=ManagerSetting(id=0, sub_action="add").pack()),
            InlineKeyboardButton(text="Удалить менеджера", callback_data=ManagerSetting(id=0, sub_action="view").pack())
    )
    builder.row(InlineKeyboardButton(text="Назад", callback_data="settings_management_menu"))
    
    return builder.as_markup()


def get_manager_edit_keyboard(id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Изменить роль на пользователя",  # TODO: можно переделать для выбора роли
                                     callback_data=ManagerSetting(id=id, sub_action="del").pack()))
    builder.row(InlineKeyboardButton(text="Назад", callback_data="settings_management_menu"))
    
    return builder.as_markup()


def get_accept_manager_keyboard(id):
    buttons = [
        [
            InlineKeyboardButton(text="Выдать права менеджера",
                                 callback_data=ManagerSetting(id=id, sub_action="accept").pack())
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data=ManagerSetting(id=0, sub_action="add").pack())
        ],
        [
            InlineKeyboardButton(text="Главная", callback_data="start")
        ]
    
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_back_in_choice_keyboard():
    return InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Назад",
                                                   callback_data=ManageSetting(role="Manager",
                                                                               action="choice_action").pack())]])
