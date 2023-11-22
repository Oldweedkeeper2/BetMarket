from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from filters.admin_filter import AdminFilter
from filters.manager_filter import ManagerFilter
from keyboards.inline.admin.manage_product import get_product_management_keyboard
from states.manager.add_product import ProductState
from utils.misc.clear_chat import clear_chat

router = Router()


@router.callback_query(F.data == 'manage_product')
async def handle(call: CallbackQuery, state: FSMContext):
    if await AdminFilter().__call__(call):
        role = 'Admin'
    else:
        role = 'Manager'
    keyboard = get_product_management_keyboard(role=role)
    data = await state.get_data()
    msg = await call.message.answer(text='<b>Это меню для управления продуктом</b>',
                                    reply_markup=keyboard)
    await clear_chat(data=data)
    data['product'] = {}
    data['items_to_del'].append(msg)
    await state.update_data(data)
