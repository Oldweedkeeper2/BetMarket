from pprint import pprint

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.markdown import hpre

from data.methods.users import UserSQL
from keyboards.inline.admin.settings import ManageSetting, get_back_keyboard
from keyboards.inline.admin.setting_managers import get_manager_setting_keyboard, ManagerSetting, \
    get_with_managers_keyboard, get_manager_edit_keyboard, get_accept_manager_keyboard, \
    get_back_in_choice_keyboard
from states.admin.settings import ManagerState
from utils.misc.clear_chat import clear_chat

router = Router()


def get_user_text(user):
    return hpre(f'Пользователь найден:\n\n'
                f'ID:           {user.id}\n'
                f'UserName:     @{user.username or "нет"}\n'
                f'LastName:     {user.surname or "нет"}\n'
                f'Phone:        {user.phone or "нет"}\n'
                f'Balance:      {user.balance}\n'
                f'Role:         {user.role}\n'
                f'Banned:       {user.banned}\n')


@router.callback_query(ManageSetting.filter(F.role == 'Manager' and F.action == 'choice_action'))
async def handle(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    keyboard = get_manager_setting_keyboard()
    pprint(keyboard)
    
    msg = await call.message.answer(text='<b>Выберите действие</b>\n\n',
                                    reply_markup=keyboard)
    await clear_chat(data=data)
    data['items_to_del'].append(msg)
    await state.update_data(data)


@router.callback_query(ManagerSetting.filter(F.sub_action == 'view'))
async def handle(call: CallbackQuery, state: FSMContext, callback_data: ManagerSetting):
    data = await state.get_data()
    managers_list = await UserSQL.get_all_managers()
    keyboard = get_with_managers_keyboard(managers_list=managers_list)
    msg = await call.message.answer(text='<b>Выберите менеджера</b>\n\n',
                                    reply_markup=keyboard)
    await clear_chat(data=data)
    data['items_to_del'].append(msg)
    await state.update_data(data)
    await state.set_state(ManagerState.username_add)


@router.callback_query(ManagerSetting.filter(F.sub_action == 'edit'))
async def handle(call: CallbackQuery, state: FSMContext, callback_data: ManagerSetting):
    data = await state.get_data()
    manager_id = callback_data.id
    manager = await UserSQL.get_by_id(id=manager_id)
    keyboard = get_manager_edit_keyboard(id=manager_id)
    text = get_user_text(user=manager)
    msg = await call.message.answer(text=text,
                                    reply_markup=keyboard)
    await clear_chat(data=data)
    data['items_to_del'].append(msg)
    await state.update_data(data)


@router.callback_query(ManagerSetting.filter(F.sub_action == 'del'))
async def handle(call: CallbackQuery, state: FSMContext, callback_data: ManagerSetting):
    data = await state.get_data()
    keyboard = get_back_in_choice_keyboard()
    manager_id = callback_data.id
    await UserSQL.update_role(id=manager_id, role='Пользователь')
    msg = await call.message.answer(text='<b>Роль была изменена на менеджера</b>\n\n',
                                    reply_markup=keyboard)
    await clear_chat(data=data)
    data['items_to_del'].append(msg)
    await state.update_data(data)
    await state.set_state(ManagerState.username_add)


@router.callback_query(ManagerSetting.filter(F.sub_action == 'add'))
async def handle(call: CallbackQuery, state: FSMContext, callback_data: ManagerSetting):
    data = await state.get_data()
    keyboard = get_back_in_choice_keyboard()
    msg = await call.message.answer(text='<b>Напишите @username нового менеджера</b>\n\n'
                                         '<i>Этот пользователь должен хотя бы раз активировать бота!</i>',
                                    reply_markup=keyboard)
    await clear_chat(data=data)
    data['items_to_del'].append(msg)
    await state.update_data(data)
    await state.set_state(ManagerState.username_add)


@router.message(ManagerState.username_add)
async def handle(message: Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    if not message.text or not message.text.startswith('@'):
        await state.set_state(ManagerState.username_add)
        return
    username = message.text.split('@')[1]
    user = await UserSQL.get_by_username(username=username)
    if not user:
        msg = await message.answer(text='<b>Пользователь не найден! Попробуйте ещё раз</b>\n\n'
                                        '<i>Проверьте правильность написания @username. Возможно пользователь не активировал бота</i>',
                                   reply_markup=get_back_keyboard())
        await clear_chat(data=data)
        data['items_to_del'].append(msg)
        await state.update_data(data)
        await state.set_state(ManagerState.username_add)
        return
    else:
        keyboard = get_accept_manager_keyboard(id=user.id)
        user_text = get_user_text(user)
        msg = await message.answer(text=user_text,
                                   reply_markup=keyboard)
    await clear_chat(data=data)
    data['items_to_del'].append(msg)
    data['user_id'] = user.id
    await state.update_data(data)
    await state.set_state(ManagerState.username_add)


@router.callback_query(ManagerSetting.filter(F.sub_action == 'accept'))
async def handle(call: CallbackQuery, state: FSMContext, callback_data: ManagerSetting):
    data = await state.get_data()
    user_id = callback_data.id
    user = await UserSQL.update_role(user_id, 'Manager')
    if not user:
        msg = await call.message.answer(text='Пользователь не добавлен в список менеджеров',
                                        reply_markup=get_back_keyboard())
    else:
        msg = await call.message.answer(text='Пользователь добавлен в список менеджеров',
                                        reply_markup=get_back_keyboard())
    await clear_chat(data=data)
    data['items_to_del'].append(msg)
    await state.update_data(data)
    await state.set_state(ManagerState.username_add)
