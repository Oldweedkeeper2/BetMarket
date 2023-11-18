import logging
from contextlib import suppress

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from data.config import USER_PAGE_WIDTH
from data.methods.users import UserSQL
from handlers.admin.setting_managers import get_user_text
from keyboards.inline.admin.setting_users import UserSetting, \
    get_user_balance_changer_keyboard, get_user_setting_keyboard, UsersPagination, paginator, UserBalanceChanger
from keyboards.inline.admin.settings import get_back_keyboard, ManageSetting
from keyboards.inline.products import Pagination
from states.admin.settings import ManagerState, UserState
from utils.misc.clear_chat import clear_chat

router = Router()


def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


async def update_pagination_message(call: CallbackQuery, page: int, product_list):
    """Updates the message for pagination."""
    await call.answer()
    with suppress(TelegramBadRequest):
        await call.message.edit_text(
                text=f"<b>Выберите пользователя</b>",
                reply_markup=paginator(product_list, page)
        )


@router.callback_query(ManageSetting.filter(F.role == 'User' and F.action == 'view'))
async def handle(call: CallbackQuery, state: FSMContext, callback_data: UserSetting):
    data = await state.get_data()
    users_list = await UserSQL.get_all()
    msg = await call.message.answer(text='<b>Выберите пользователя</b>\n\n',
                                    reply_markup=paginator(users_list=users_list))
    await clear_chat(data=data)
    data['items_to_del'].append(msg)
    await state.update_data(data)


@router.callback_query(UsersPagination.filter(F.action.in_(["prev", "next"])))
async def handle(call: CallbackQuery, callback_data: Pagination):
    product_list = await UserSQL.get_all()
    
    page_num = callback_data.page
    page = max(page_num - 1, 0) if callback_data.action == "prev" else page_num + 1
    has_more = len(product_list) > page * USER_PAGE_WIDTH
    
    if callback_data.action == "next" and not has_more:
        page = page_num
    
    await update_pagination_message(call, page, product_list)


@router.callback_query(UserSetting.filter(F.sub_action == 'edit'))
async def handle(call: CallbackQuery, state: FSMContext, callback_data: UserSetting):
    data = await state.get_data()
    manager_id = callback_data.id
    manager = await UserSQL.get_by_id(id=manager_id)
    keyboard = get_user_setting_keyboard(id=manager_id)
    text = get_user_text(user=manager)
    msg = await call.message.answer(text=text,
                                    reply_markup=keyboard)
    await clear_chat(data=data)
    data['items_to_del'].append(msg)
    await state.update_data(data)


@router.callback_query(UserSetting.filter(F.sub_action == 'balance'))
async def handle(call: CallbackQuery, state: FSMContext, callback_data: UserSetting):
    data = await state.get_data()
    user = await UserSQL.get_by_id(id=callback_data.id)
    if not user:
        msg = await call.message.answer(text='<b>Пользователь не найден! Попробуйте ещё раз</b>\n\n')
        await clear_chat(data=data)
        data['items_to_del'].append(msg)
        await state.update_data(data)
        return
    keyboard = get_user_balance_changer_keyboard(id=callback_data.id)
    text = get_user_text(user=user)
    msg = await call.message.answer(text=text,
                                    reply_markup=keyboard)
    await clear_chat(data=data)
    data['items_to_del'].append(msg)
    
    await state.update_data(data)


async def handle_balance_change(call: CallbackQuery, state: FSMContext, callback_data: UserSetting, action: str):
    data = await state.get_data()
    
    if await state.get_state() == UserState.amount:
        try:
            await call.bot.delete_message(call.from_user.id, data['amount_msg'].message_id)
        except Exception as e:
            logging.debug(e)
        await state.clear()
    
    data['current_user'] = callback_data.id
    data['current_action'] = action
    
    action_text = 'добавить' if action == 'add' else 'отнять'
    msg = await call.bot.send_message(chat_id=call.from_user.id,
                                      text=f'Введите сумму, которую вы хотите {action_text}')
    data['amount_msg'] = msg
    await state.update_data(data)
    await state.set_state(UserState.amount)


# Пример использования новой функции
@router.callback_query(UserBalanceChanger.filter(F.sub_action == 'add'))
async def handle_add(call: CallbackQuery, state: FSMContext, callback_data: UserSetting):
    await handle_balance_change(call, state, callback_data, 'add')


@router.callback_query(UserBalanceChanger.filter(F.sub_action == 'deduct'))
async def handle_deduct(call: CallbackQuery, state: FSMContext, callback_data: UserSetting):
    await handle_balance_change(call, state, callback_data, 'deduct')


@router.message(UserState.amount)
async def handle(message: Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    if not is_float(message.text):
        await state.set_state(UserState.amount)
        return
    amount = float(message.text) if data['current_action'] == 'add' else -float(message.text)
    result = await UserSQL.update_balance(id=data['current_user'], amount=amount)
    user = await UserSQL.get_by_id(id=data['current_user'])
    if not result or not user:
        msg = await message.answer(text='<b>Пользователь не найден! Попробуйте ещё раз</b>\n\n'
                                        '<i>Проверьте правильность написания @username. Возможно пользователь был удалён</i>',
                                   reply_markup=get_back_keyboard())
        await clear_chat(data=data)
        data['items_to_del'].append(msg)
        await state.update_data(data)
        await state.set_state(UserState.amount)
        return
    else:
        keyboard = get_back_keyboard()
        user_text = get_user_text(user)
        msg = await message.answer(text=user_text,
                                   reply_markup=keyboard)
    await clear_chat(data=data)
    data['items_to_del'].append(msg)
    data['user_id'] = user.id
    await state.update_data(data)
    await state.set_state(ManagerState.username_add)


async def handle_user_ban_unban(call: CallbackQuery, state: FSMContext, callback_data: UserSetting, ban: bool):
    data = await state.get_data()
    await UserSQL.update_banned(id=callback_data.id, banned=ban)
    user = await UserSQL.get_by_id(id=callback_data.id)
    if not user:
        msg = await call.message.answer(text='<b>Пользователь не найден! Попробуйте ещё раз</b>\n\n')
        await clear_chat(data=data)
        data['items_to_del'].append(msg)
        await state.update_data(data)
        return
    
    keyboard = get_back_keyboard()
    text = get_user_text(user=user)
    msg = await call.message.answer(text=text, reply_markup=keyboard)
    await clear_chat(data=data)
    data['items_to_del'].append(msg)
    await state.update_data(data)


@router.callback_query(UserSetting.filter(F.sub_action == 'ban'))
async def handle_ban(call: CallbackQuery, state: FSMContext, callback_data: UserSetting):
    await handle_user_ban_unban(call, state, callback_data, True)


@router.callback_query(UserSetting.filter(F.sub_action == 'unban'))
async def handle_unban(call: CallbackQuery, state: FSMContext, callback_data: UserSetting):
    await handle_user_ban_unban(call, state, callback_data, False)
