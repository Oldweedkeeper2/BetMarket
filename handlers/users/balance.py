from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from data.methods.products import ProductSQL
from handlers.users.products import get_product_text
from keyboards.inline.cart import cart_product_keyboard, cart_last_product_keyboard, get_back_keyboard
from utils.misc.clear_chat import clear_chat

router = Router()


@router.callback_query(F.data == 'add_balance')
async def handle(call: CallbackQuery, state: FSMContext):
    await call.answer(text='Этот функционал находится в разработке до тех пор, пока Глеб не \n')
    # data = await state.get_data()
    # cart: dict = data['cart']
    #
    # await clear_chat(data=data)
    # data['items_to_del'] = []
    # await state.update_data(data)
