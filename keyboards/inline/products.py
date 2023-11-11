import pprint
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


def create_pagination_buttons(page: int):
    """Creates pagination buttons."""
    return [
        InlineKeyboardButton(text="←", callback_data=Pagination(action="prev", page=page).pack()),
        InlineKeyboardButton(text=str(page + 1), callback_data='empty'),
        InlineKeyboardButton(text="→", callback_data=Pagination(action="next", page=page).pack())
    ]


def paginator(product_list: List, page: int = 0):
    """Creates a paginated keyboard for product list."""
    builder = InlineKeyboardBuilder()
    start = page * PAGE_WIDTH
    end = start + PAGE_WIDTH
    
    for product in product_list[start:end]:
        builder.row(InlineKeyboardButton(text=str(product.name),
                                         callback_data=ProductData(id=product.id).pack()))
    
    builder.row(*create_pagination_buttons(page), width=3)
    return builder.as_markup()
