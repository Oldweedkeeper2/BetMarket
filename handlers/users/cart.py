from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from data.methods.products import ProductSQL
from handlers.users.products import get_product_text
from keyboards.inline.cart import cart_product_keyboard, cart_last_product_keyboard, get_back_keyboard
from utils.misc.clear_chat import clear_chat

router = Router()


@router.callback_query(F.data == 'cart')
async def handle(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cart: dict = data['cart']
    ids_list = []
    
    if not cart:
        await call.answer(text='Ваша корзина пуста\n'
                               'Добавьте товары в корзину',
                          show_alert=True)
        return
    
    for product_id in cart:
        product = await ProductSQL.get_by_id(product_id)
        if not product:
            await call.answer('Такого продукта нет в наличии')
            return
        keyboard = cart_product_keyboard(product=product)
        
        msg = await call.bot.send_message(
                text=get_product_text(product),
                chat_id=call.from_user.id,
                reply_markup=keyboard)
        
        if product_id == list(cart.keys())[-1]:
            keyboard = cart_last_product_keyboard()
            msg = await call.bot.send_message(
                    text='Выберите действие',  # действие
                    chat_id=call.from_user.id,
                    reply_markup=keyboard,
            )
        ids_list.append(msg)
    await clear_chat(data=data)
    data['items_to_del'] = [*ids_list]
    await state.update_data(data)


@router.callback_query(F.data == 'pay')
async def handle(call: CallbackQuery, state: FSMContext):
    # data = await state.get_data()
    await call.answer(text='Этот функционал находится в разработке\n')
    # await clear_chat(data=data)
    # data['items_to_del'] =
    # await state.update_data(data)


@router.callback_query(F.data.startswith('del_product_'))
async def handle(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    product_id = int(call.data.split('_')[-1])
    data['cart'].pop(product_id)
    if not data['cart']:
        await clear_chat(data=data)
        msg = await call.message.answer('Ваша корзина пуста\n'
                                        'Добавьте товары в корзину',
                                        reply_markup=get_back_keyboard())
        data['items_to_del'].append(msg)
    else:
        await call.message.delete()
    await state.update_data(data)
