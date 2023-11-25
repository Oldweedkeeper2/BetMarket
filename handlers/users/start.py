from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from data.config import ADMIN_USERNAME
from data.methods.users import UserSQL
from data.models import User
from filters.admin_filter import AdminFilter
from filters.manager_filter import ManagerFilter
from filters.user_filter import BannedUserFilter
from keyboards.inline.start import get_role_start_keyboard
from utils.misc.clear_chat import clear_chat
import logging

router = Router()


def get_user_data(message: Message):  # Вынести вспомогательные функции в utils
    user = {
        'id': message.from_user.id,
        'username': message.from_user.username,
        'surname': message.from_user.last_name,
    }
    return user


def get_main_menu_text(user: User):
    return f'<b>Ваш статус:</b> {user.role}\n\n' \
           f'<b>💰 Баланс:</b> {user.balance} $\n\n'


async def main_menu(message: Message, state: FSMContext, role: str):
    data = await state.get_data()
    await state.clear()
    if role == 'Пользователь':
        await UserSQL.add(get_user_data(message))
    
    user = await UserSQL.get_by_id(id=int(message.chat.id))
    main_menu_text = get_main_menu_text(user)
    keyboard = get_role_start_keyboard(role=role)
    msg = None
    
    try:
        msg = await message.answer(text=main_menu_text, reply_markup=keyboard)
    except TelegramBadRequest as e:
        logging.warning(e)
    await clear_chat(data=data)
    data.setdefault('cart', {})
    data['items_to_del'].append(msg) if msg else None
    data['product'] = {}
    await state.update_data(data)


@router.message(CommandStart(), AdminFilter())
async def handle(message: Message, state: FSMContext):
    await message.delete()
    await main_menu(message, state, 'Админ')


@router.message(CommandStart(), ManagerFilter())
async def handle(message: Message, state: FSMContext):
    await message.delete()
    await main_menu(message, state, 'Менеджер')


@router.message(CommandStart(), BannedUserFilter())
async def handle(message: Message, state: FSMContext):
    await message.delete()
    await main_menu(message, state, 'Пользователь')


@router.message(CommandStart(), ~BannedUserFilter())
async def handle(message: Message, state: FSMContext):
    await message.delete()
    await message.answer(text=f'<b>Приношу свои извинения, но вы были забанены в этом боте!</b>\n'
                              f'<i>В случае, если вы несогласны с баном, то можете обратится к администратору бота!\n\n'
                              f'@{ADMIN_USERNAME}</i>', show_alert=True)


# Код ниже можно переделать с использованием мидлваря,
# нужно посмотреть насколько это уместно
@router.callback_query(F.data == 'start', AdminFilter())
async def handle(call: CallbackQuery, state: FSMContext):
    await main_menu(call.message, state, 'Админ')


@router.callback_query(F.data == 'start', ManagerFilter())
async def handle(call: CallbackQuery, state: FSMContext):
    await main_menu(call.message, state, 'Менеджер')


@router.callback_query(F.data == 'start', BannedUserFilter())
async def handle(call: CallbackQuery, state: FSMContext):
    await main_menu(call.message, state, 'Пользователь')


@router.callback_query(F.data == 'start', ~BannedUserFilter())
async def handle(call: CallbackQuery, state: FSMContext):
    await call.answer(text=f'<b>Приношу свои извинения, но вы были забанены в этом боте!\n\n</b>'
                           f'<i>В случае, если вы несогласны с баном, то можете обратится к администратору бота!\n'
                           f'@{ADMIN_USERNAME}</i>', show_alert=True)

# ВОРОВАТЬ ТУТ: https://t.me/fulltimekeeperdoc_bot
# TODO: ✔️Поправить добавление менеджера и добавить удаление менеджера
#  ✔️Добавление\убавление баланса пользователю
#  ✔️Бан пользователя
#  ✔️Изменение и добавление! товара (только админу), а добавление аккаунтов к товару (админ + менеджер)
#  ❌Посмотреть баги удаления сообщений
#  ❌Кодировка названий zip файлов
#  ✔️Баг с нулевой корзиной (если товара 0, то должен выдать ошибку, но вроде бы это и не баг, так как не пройдёт заказ)
#  ✔️Удалять полученные архивы после распаковки
#  ✔️Техподдержку можно сделать на кнопке ссылке (оставить пункт Помощь, но добавить кнопку с ссылкой на менеджера)
#  ❌Добавить историю пополнений для пользователя
#   ...
#  На будущее:
#       ❌доп процент на баланс с пополнения (пример:10% от 100, 15% от 200)
#       ❌оптовая покупка
#       ❌рассылка
#       ❌Разделение аккаунтов на базы (новореги, старореги)
#       💠️Купить x5-x10 и т.д. или ввести своё количество
#       ❌История заказов
#       ❌История заказов для админа. + Ввести номер заказа. Показывает основную информацию о заказе,
#                                           а также есть кнопка отправить файлы заказа
#       ❌Добавить статистику в гугл доки. Рассмотреть возможность хранить акки на гугл доках. Админ получит кнопку
#                                           Запросить статистику, либо она будет обновляться каждые 5 минут
#       ✔️Удаление заказов, если прошло больше месяца, также добавить обработку этого, если запрашивается статистика
#       ❌Реферальная система
