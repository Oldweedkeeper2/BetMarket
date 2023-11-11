from typing import Any

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.methods import SendMessage
from aiogram.types import Message

from data.methods.users import UserSQL
from filters.admin_filter import AdminFilter
from filters.manager_filter import ManagerFilter
from keyboards.inline.start import get_role_start_keyboard

router = Router()


@router.message(CommandStart(), AdminFilter())
async def handle(message: Message, state: FSMContext):
    await message.delete()
    await state.clear()
    keyboard = get_role_start_keyboard(role='Admin')
    await message.answer('Ваш статус: Админ', reply_markup=keyboard)


@router.message(CommandStart(), ManagerFilter())
async def handle(message: Message, state: FSMContext):
    await message.delete()
    await state.clear()
    keyboard = get_role_start_keyboard(role='Manager')
    await message.answer('Ваш статус: Менеджер', reply_markup=keyboard)


def get_user_data(message: Message):  # Вынести вспомогательные функции в utils
    user = {
        'id': message.from_user.id,
        'username': message.from_user.username,
        'surname': message.from_user.last_name,
    }
    return user


@router.message(CommandStart())
async def handle(message: Message, state: FSMContext):
    await message.delete()
    await state.clear()
    keyboard = get_role_start_keyboard(role='User')
    await UserSQL.add(get_user_data(message))
    await message.answer('Ваш статус: Пользователь', reply_markup=keyboard)
