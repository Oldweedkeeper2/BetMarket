import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile

from data.methods.orders import OrderSQL
from data.methods.products import ProductSQL
from data.methods.users import UserSQL
from handlers.users.products import get_cart_product_text
from keyboards.inline.cart import cart_product_keyboard, cart_last_product_keyboard, get_back_keyboard
from utils.account_sorter import ProductBuyProcessor
from utils.generate_dynamic_path import generate_dynamic_zip_path
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
        logging.debug(f'{product_id} {product}')
        if not product:
            # TODO: добавить какой продукт не существует (это может быть только из-за удаления товара)
            await call.answer('Одного из выбранных вами товаров нет в наличии.\n'
                              'Возможно он был удалён. Обратитесь в службу поддержки', )
            return
        keyboard = cart_product_keyboard(product=product)
        
        msg = await call.bot.send_message(
                text=get_cart_product_text(product, cart[product_id]),
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
    data['items_to_del'].extend(ids_list)
    await state.update_data(data)


@router.callback_query(F.data == 'pay')
async def handle(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = int(call.from_user.id)
    user = await UserSQL.get_by_id(id=user_id)
    
    if not user:
        logging.debug('User not found')
        await call.answer('Пользователь не найден. Обратитесь в службу поддержки', show_alert=True)
        return
    
    if user.balance <= 0 or user.balance < sum(data['cart'].values()):
        await call.answer('Недостаточно средств. Пополните баланс', show_alert=True)
        return
    
    msg = await call.bot.send_message(chat_id=user_id,
                                      text='Спасибо за покупку!\n'
                                           'Оплата прошла успешно, бот пришлет вам заказ!',
                                      reply_markup=get_back_keyboard())
    cart_sum = await ProductSQL.get_cart_sum(data['cart'])
    order = await OrderSQL.add(user_id=user_id, cart_sum=cart_sum, cart_items=data['cart'])
    relative_path = generate_dynamic_zip_path()
    zip_file_path = await (ProductBuyProcessor(cart_data=data['cart'],
                                               order_id=order.id,
                                               relative_path=relative_path)
                           .handle_buy_product())
    zip_file = FSInputFile(zip_file_path, filename=f"order_№{order.id}.zip")
    
    try:
        await call.bot.send_document(chat_id=user_id,
                                     document=zip_file)
    except Exception as e:
        logging.error(f'Error: {e}')
        await call.bot.send_message(chat_id=user_id,
                                    text='Не удалось отправить заказ\n'
                                         'Пожалуйста, обратитесь в службу поддержки')
        return
    await UserSQL.update_balance(id=user_id, amount=-1 * cart_sum)
    await clear_chat(data=data)
    data['items_to_del'].append(msg)
    await state.update_data(data)


@router.callback_query(F.data.startswith('del_product_'))
async def handle(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    product_id = int(call.data.split('_')[-1])
    if product_id not in data['cart']:
        await call.answer()
        return
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
