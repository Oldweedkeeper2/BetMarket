from contextlib import suppress

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from data.methods.users import UserSQL
from filters.admin_filter import AdminFilter
from filters.manager_filter import ManagerFilter
from keyboards.inline.start import get_role_start_keyboard
from utils.misc.clear_chat import clear_chat

router = Router()


def get_user_data(message: Message):  # Вынести вспомогательные функции в utils
    user = {
        'id': message.from_user.id,
        'username': message.from_user.username,
        'surname': message.from_user.last_name,
    }
    return user


async def main_menu(message: Message, state: FSMContext, role: str):
    data = await state.get_data()
    await state.clear()
    
    if role == 'Пользователь':
        await UserSQL.add(get_user_data(message))
    
    keyboard = get_role_start_keyboard(role=role)
    with suppress(TelegramBadRequest):
        msg = await message.answer(f'Ваш статус: {role}', reply_markup=keyboard)
    
    await message.delete()
    
    await clear_chat(data=data, chat_id=int(message.from_user.id))
    data.setdefault('items_to_del', [])
    data.setdefault('cart', {})
    data['items_to_del'].append(msg)
    await state.update_data(data)


@router.message(CommandStart(), AdminFilter())
async def handle(message: Message, state: FSMContext):
    await main_menu(message, state, 'Админ')


@router.message(CommandStart(), ManagerFilter())
async def handle(message: Message, state: FSMContext):
    await main_menu(message, state, 'Менеджер')


@router.message(CommandStart())
async def handle(message: Message, state: FSMContext):
    await main_menu(message, state, 'Пользователь')


# Код ниже можно переделать с использованием мидлваря,
# нужно посмотреть насколько это уместно
@router.callback_query(F.data == 'start', AdminFilter())
async def handle(call: CallbackQuery, state: FSMContext):
    await main_menu(call.message, state, 'Админ')


@router.callback_query(F.data == 'start', ManagerFilter())
async def handle(call: CallbackQuery, state: FSMContext):
    await main_menu(call.message, state, 'Менеджер')


@router.callback_query(F.data == 'start')
async def handle(call: CallbackQuery, state: FSMContext):
    await main_menu(call.message, state, 'Пользователь')
