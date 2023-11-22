from typing import List

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.models import Product


class ManageProduct(CallbackData, prefix="manage_product"):
    action: str


class ManageProductEdit(CallbackData, prefix="manage_product_edit"):
    id: int
    sub_action: str


def get_back_keyboard():
    return InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Главная", callback_data="start")]])


def get_with_products_keyboard(product_list: List[Product]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for product in product_list:
        builder.row(
                InlineKeyboardButton(text=product.name,
                                     callback_data=ManageProductEdit(id=product.id, sub_action="view").pack()))
    builder.row(InlineKeyboardButton(text="Назад", callback_data="manage_product"))
    return builder.as_markup()


def get_product_management_keyboard(role: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if role == "Admin":
        builder.row(InlineKeyboardButton(text='Добавить товар',
                                         callback_data=ManageProduct(action="add").pack()))
    builder.row(InlineKeyboardButton(text='Изменить/Удалить товар',
                                     callback_data=ManageProduct(action="edit").pack()))

    builder.row(InlineKeyboardButton(text="Главная",
                                     callback_data="start"))
    return builder.as_markup()


def get_product_action_keyboard(id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Изменить',
                                     callback_data=ManageProductEdit(id=id, sub_action="edit").pack()),
                InlineKeyboardButton(text='Удалить',
                                     callback_data=ManageProductEdit(id=id, sub_action="del").pack()))
    builder.row(InlineKeyboardButton(text="Назад",
                                     callback_data=ManageProduct(action="edit").pack()))
    return builder.as_markup()


def get_product_text_edit_keyboard(id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Название',
                                     callback_data=ManageProductEdit(id=id, sub_action="edit_name").pack()),
                InlineKeyboardButton(text='Описание',
                                     callback_data=ManageProductEdit(id=id, sub_action="edit_description").pack()))
    builder.row(InlineKeyboardButton(text="Цена",
                                     callback_data=ManageProductEdit(id=id, sub_action="edit_price").pack()),
                InlineKeyboardButton(text="Добавить количество",
                                     callback_data=ManageProductEdit(id=id, sub_action="add_quantity").pack()))
    builder.row(InlineKeyboardButton(text="Подтвердить",
                                     callback_data=ManageProductEdit(id=id, sub_action="confirm").pack()))
    builder.row(InlineKeyboardButton(text="Назад",
                                     callback_data=ManageProductEdit(id=id, sub_action="view").pack()))
    return builder.as_markup()


def get_back_on_view_keyboard(id):
    return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Назад", callback_data=ManageProductEdit(id=id, sub_action="view").pack())]])


def get_manage_product_edit_keyboard(id):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Добавить количество",
                                     callback_data=ManageProductEdit(id=id, sub_action="add_quantity").pack()))
    builder.row(InlineKeyboardButton(text="Назад",
                                     callback_data=ManageProductEdit(id=id, sub_action="view").pack()))
    return builder.as_markup()
