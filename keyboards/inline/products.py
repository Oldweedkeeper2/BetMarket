from typing import List

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.config import PAGE_WIDTH
from data.models import Product

'''← →'''


class Pagination(CallbackData, prefix="pag"):
    action: str
    page: int


class ProductData(CallbackData, prefix="product"):
    id: int


class ProductPagination(CallbackData, prefix="product_pag"):
    action: str
    amount: int


def create_pagination_buttons(page: int):
    """Creates pagination buttons."""
    return [
        InlineKeyboardButton(text="←", callback_data=Pagination(action="prev", page=page).pack()),
        InlineKeyboardButton(text=str(page + 1), callback_data='empty'),
        InlineKeyboardButton(text="→", callback_data=Pagination(action="next", page=page).pack())
    ]


def paginator(product_list: List[Product], page: int = 0):
    """Creates a paginated keyboard for product list."""
    builder = InlineKeyboardBuilder()
    start = page * PAGE_WIDTH
    end = start + PAGE_WIDTH
    
    for product in product_list[start:end]:
        builder.row(InlineKeyboardButton(text=str(product.name),
                                         callback_data=ProductData(id=product.id).pack()))
    builder.row(*create_pagination_buttons(page), width=3)
    builder.row(InlineKeyboardButton(text='Главная',
                                     callback_data='start'))
    return builder.as_markup()


def get_back_keyboard():
    return InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="get_products")]])


def create_product_pagination_buttons(amount: int):
    """Creates pagination buttons."""
    return [
        InlineKeyboardButton(text="-", callback_data=ProductPagination(action="dec_product", amount=amount).pack()),
        InlineKeyboardButton(text=str(amount), callback_data='empty'),
        InlineKeyboardButton(text="+", callback_data=ProductPagination(action="inc_product", amount=amount).pack())
    ]


def get_product_keyboard(amount: int = 0, total_products: int = 0):
    print(amount, total_products)
    builder = InlineKeyboardBuilder()
    amount5 = amount + 4 if amount + 4 < total_products else total_products
    amount10 = amount + 9 if amount + 9 < total_products else total_products
    builder.row(*create_product_pagination_buttons(amount), width=3)
    builder.row(
            InlineKeyboardButton(text='+ 5',
                                 callback_data=ProductPagination(action="inc_product", amount=amount5).pack()),
            InlineKeyboardButton(text='+ 10',
                                 callback_data=ProductPagination(action="inc_product", amount=amount10).pack()))
    builder.row(InlineKeyboardButton(text="Корзина", callback_data='cart'))
    builder.row(InlineKeyboardButton(text="Назад", callback_data="get_products"))
    # builder.row(InlineKeyboardButton(text="Главная", callback_data="start"))
    return builder.as_markup()
