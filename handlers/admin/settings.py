from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from keyboards.inline.admin.settings import get_settings_management_menu_keyboard
from utils.misc.clear_chat import clear_chat

router = Router()


@router.callback_query(F.data == 'settings_management_menu')
async def handle(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    keyboard = get_settings_management_menu_keyboard()
    msg = await call.message.answer(text='<b>Это меню для управления пользователями и менеджерами</b>\n\n',
                                    reply_markup=keyboard)
    await clear_chat(data=data)
    data['items_to_del'].append(msg)
    await state.update_data(data)
