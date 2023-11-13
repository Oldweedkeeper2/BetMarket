from aiogram.filters.state import StatesGroup, State


class StatusSetting(StatesGroup):
    username = State()
