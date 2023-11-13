from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from data.methods.users import UserSQL
from keyboards.inline.admin.status_setting import get_status_setting_keyboard
from keyboards.inline.cart import get_back_keyboard
from states.admin.status_setting import StatusSetting
from utils.misc.clear_chat import clear_chat

router = Router()


@router.callback_query(F.data == 'add_new_manager')
async def handle(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    keyboard = get_back_keyboard()
    msg = await call.message.answer(text='<b>Напишите @username нового менеджера</b>\n\n'
                                         '<i>Этот пользователь должен хотя бы раз активировать бота!</i>',
                                    reply_markup=keyboard)
    await clear_chat(data=data)
    data['items_to_del'].append(msg)
    await state.update_data(data)
    await state.set_state(StatusSetting.username)


def get_user_text(user):
    return f'Пользователь найден:\n\n' \
           f'<b>ID:</b>\t {user.id}\n' \
           f'<b>UserName:</b>\t @{user.username or "нет"}\n' \
           f'<b>LastName:</b>\t {user.surname or "нет"}\n' \
           f'<b>Phone:</b>\t {user.phone or "нет"}\n' \
           f'<b>Balance:</b>\t {user.balance}\n' \
           f'<b>Role:</b>\t {user.role}\n'


@router.message(StatusSetting.username)
async def handle(message: Message, state: FSMContext):
    data = await state.get_data()
    username = message.text.split('@')[1]
    user = await UserSQL.get_by_username(username=username)
    if not user:
        msg = await message.answer(text='<b>Пользователь не найден! Попробуйте ещё раз</b>\n\n'
                                        '<i>Проверьте правильность написания @username. Возможно пользователь не активировал бота</i>',
                                   reply_markup=get_back_keyboard())
        await state.set_state(StatusSetting.username)
    else:
        keyboard = get_status_setting_keyboard(user)
        user_text = get_user_text(user)
        msg = await message.answer(text=user_text,
                                   reply_markup=keyboard)
    await clear_chat(data=data)
    data['items_to_del'].append(msg)
    data['user_id'] = user.id
    await state.update_data(data)
    await state.set_state(StatusSetting.username)


@router.callback_query(F.data == 'accept_add_new_manager')
async def handle(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = await UserSQL.update_role(data['user_id'], 'Manager')
    if not user:
        msg = await call.message.answer(text='Пользователь не добавлен в список менеджеров',
                                        reply_markup=get_back_keyboard())
    else:
        msg = await call.message.answer(text='Пользователь добавлен в список менеджеров',
                                        reply_markup=get_back_keyboard())
    await clear_chat(data=data)
    data['items_to_del'].append(msg)
    await state.update_data(data)
    await state.set_state(StatusSetting.username)
