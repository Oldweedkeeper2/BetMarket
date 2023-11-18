from aiogram.filters.state import StatesGroup, State


class ManagerState(StatesGroup):
    username_add = State()
    username_del = State()


class UserState(StatesGroup):
    username = State()
    amount = State()
