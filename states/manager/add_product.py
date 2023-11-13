from aiogram.filters.state import StatesGroup, State


class FileState(StatesGroup):
    upload_file = State()
