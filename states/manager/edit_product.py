from aiogram.filters.state import StatesGroup, State


class ProductEditState(StatesGroup):
    edit_name = State()
    edit_description = State()
    edit_price = State()
    edit_quantity = State()
