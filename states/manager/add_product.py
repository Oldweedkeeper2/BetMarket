from aiogram.filters.state import StatesGroup, State


class ProductState(StatesGroup):
    name = State()
    description = State()
    price = State()
    upload_file = State()
