from pprint import pprint
from typing import Optional

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.markdown import hbold, hpre, hitalic

from data.methods.products import ProductSQL
from data.models import Product
from filters.admin_filter import AdminFilter
from handlers.admin.manage_product_add import get_full_product_text, write_product_data
from keyboards.inline.admin.manage_product import ManageProduct, \
    get_with_products_keyboard, ManageProductEdit, get_product_action_keyboard, get_product_text_edit_keyboard, \
    get_back_on_view_keyboard, get_manage_product_edit_keyboard
from states.manager.add_product import ProductState
from states.manager.edit_product import ProductEditState
from utils.account_sorter import delete_product_folder
from utils.generate_dynamic_path import generate_dynamic_zip_path
from utils.misc.clear_chat import clear_chat

router = Router()

PRODUCT = 'product_edit'
EDIT_ID = 'id'
EDIT_NAME = 'name'
EDIT_PRICE = 'price'
EDIT_DESCRIPTION = 'description'
EDIT_AMOUNT = 'amount'
EDIT_UPLOADER = 'uploader_id'
CURRENCY_SYMBOL = '$'


@router.callback_query(ManageProduct.filter(F.action == 'edit'))
async def handle(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    product_list = await ProductSQL.get_all()
    keyboard = get_with_products_keyboard(product_list=product_list)
    msg = await call.message.answer(text='Выберите продукт:',
                                    reply_markup=keyboard)
    await clear_chat(data=data)
    data['items_to_del'].append(msg)
    await state.update_data(data)
    await state.set_state(ProductState.name)


@router.callback_query(ManageProductEdit.filter(F.sub_action == 'view'))
async def handle(call: CallbackQuery, state: FSMContext, callback_data: ManageProductEdit):
    data = await state.get_data()
    product = await ProductSQL.get_by_id(id=callback_data.id)
    keyboard = get_product_action_keyboard(callback_data.id)
    text = get_full_product_text(product=product)
    msg = await call.message.answer(text=text,
                                    reply_markup=keyboard)
    await dump_product_model_in_data(state=state, product=product)
    await clear_chat(data=data)
    data['items_to_del'].append(msg)
    await state.update_data(data)
    await state.set_state(ProductState.name)


async def get_product_text_edit(state: FSMContext, end_text: Optional[str] = None,
                                start_text: Optional[str] = None) -> str:
    """Получить текстовое представление информации о продукте."""
    data = await state.get_data()
    product_data = data.get(PRODUCT, {})
    id = product_data.get(EDIT_ID, 'Нет')
    name = product_data.get(EDIT_NAME, 'Нет')
    price = product_data.get(EDIT_PRICE, 'Нет')
    description = product_data.get(EDIT_DESCRIPTION, 'Нет')
    amount = product_data.get(EDIT_AMOUNT, 'Нет')
    uploader_id = product_data.get(EDIT_UPLOADER, 'Нет')
    
    text = (f'ID товара:            {id}\n'
            f'Название:             {name}\n'
            f'Описание:             {description}\n'
            f'Цена:                 {price} {CURRENCY_SYMBOL}\n'
            f'Количество:           {amount}\n'
            f'ID того, кто добавил: {uploader_id}\n')
    if start_text:
        text = f'❗ {hbold(start_text)}\n\n{hpre(text)}'
    if end_text:
        text += '\n\n' + hitalic(end_text)
    return text


async def dump_product_model_in_data(state: FSMContext, product: Product):
    data = await state.get_data()
    data.setdefault(PRODUCT, {})
    id = product.id
    name = product.name
    price = product.price
    description = product.description
    amount = product.amount
    uploader_id = product.uploader_id
    product_data = list(zip((EDIT_ID, EDIT_NAME, EDIT_PRICE, EDIT_DESCRIPTION, EDIT_AMOUNT, EDIT_UPLOADER),
                            (id, name, price, description, amount, uploader_id)))
    for item_name, item in product_data:
        data[PRODUCT][item_name] = item
    pprint(data)
    await state.update_data(data)


@router.callback_query(ManageProductEdit.filter(F.sub_action == 'edit'))
async def handle(call: CallbackQuery, state: FSMContext, callback_data: ManageProductEdit):
    if await AdminFilter().__call__(call):
        role = 'Admin'
        keyboard = get_product_text_edit_keyboard(id=callback_data.id)
        text = await get_product_text_edit(state=state,
                                           start_text='Выберите поле, которое хотите изменить:')
        msg = await call.message.answer(text=text, reply_markup=keyboard)
    else:
        role = 'Manager'
        keyboard = get_manage_product_edit_keyboard(id=callback_data.id)
        text = await get_product_text_edit(state=state,
                                           end_text='<b>Отправьте текстовый документ или zip-aрхив</b>\n\n'
                                                    '<i>Проверьте соответствие формату заполнения:\n'
                                                    '\t ❕ Для текстовых - строки с разеделителем (указать разделитель!)\n'
                                                    '\t ❕ Для zip-архивов - zip-архив с расширением .zip и каждый аккаунт в своей папке</i>')
        msg = await call.message.answer(text=text, reply_markup=keyboard)
    data = await state.get_data()
    
    await clear_chat(data=data)
    data['items_to_del'].append(msg)
    await state.update_data(data)


@router.callback_query(ManageProductEdit.filter(F.sub_action == 'del'))
async def handle(call: CallbackQuery, state: FSMContext, callback_data: ManageProductEdit):
    await call.answer(text='Раздел "Удаление аккаунтов" находится в разработке', show_alert=True)
    result = await ProductSQL.delete(id=callback_data.id)
    print(result)
    relative_path = generate_dynamic_zip_path()
    result = delete_product_folder(root_zip_path=relative_path['ACCOUNTS'], account_folder=str(callback_data.id))
    print(result)


@router.callback_query(ManageProductEdit.filter(F.sub_action == 'edit_name'))
async def handle(call: CallbackQuery, state: FSMContext):
    msg = await call.message.answer("Введите новое название товара:")
    data = await state.get_data()
    data['items_to_del'].append(msg)
    await state.update_data(data=data)
    await state.set_state(ProductEditState.edit_name)


@router.callback_query(ManageProductEdit.filter(F.sub_action == 'edit_price'))
async def handle(call: CallbackQuery, state: FSMContext):
    msg = await call.message.answer("Введите новую цену товара:")
    data = await state.get_data()
    data['items_to_del'].append(msg)
    await state.update_data(data=data)
    await state.set_state(ProductEditState.edit_price)


@router.callback_query(ManageProductEdit.filter(F.sub_action == 'edit_description'))
async def handle(call: CallbackQuery, state: FSMContext):
    msg = await call.message.answer("Введите новое описание товара:")
    data = await state.get_data()
    data['items_to_del'].append(msg)
    await state.update_data(data=data)
    await state.set_state(ProductEditState.edit_description)


@router.message(ProductEditState.edit_name)
async def handle(message: Message, state: FSMContext):
    await message.delete()
    await update_and_prompt(message, state, message.text, EDIT_NAME)


@router.message(ProductEditState.edit_description)
async def handle(message: Message, state: FSMContext):
    await message.delete()
    await update_and_prompt(message, state, message.text, EDIT_DESCRIPTION)


@router.message(ProductEditState.edit_price)
async def handle(message: Message, state: FSMContext):
    await message.delete()
    await update_and_prompt(message, state, message.text, EDIT_PRICE)


async def update_and_prompt(message: Message, state: FSMContext, item: str, item_name: str):
    await write_product_data(state=state,
                             item=item,
                             item_name=item_name,
                             product_name=PRODUCT)
    data = await state.get_data()
    product_id = data[PRODUCT][EDIT_ID]
    keyboard = get_product_text_edit_keyboard(product_id)
    pprint(data)
    text = await get_product_text_edit(state=state,
                                       start_text='Подтвердите добавление товара!',
                                       end_text=f'Чтобы отменить изменения '
                                                f'нажмите "Назад" или отправьте команду /start')
    msg = await message.answer(text=text, reply_markup=keyboard)
    await clear_chat(data=data)
    data['items_to_del'].append(msg)
    await state.update_data(data=data)


@router.callback_query(ManageProductEdit.filter(F.sub_action == 'confirm'))
async def handle(call: CallbackQuery, state: FSMContext, callback_data: ManageProductEdit):
    data = await state.get_data()
    result = await ProductSQL.update(data[PRODUCT]),
    if result:
        msg = await call.message.answer(text='Товар успешно обновлен',
                                        reply_markup=get_back_on_view_keyboard(callback_data.id))
    else:
        msg = await call.message.answer(text='Товар не был обновлен. Обратитесь в техническую поддержку',
                                        reply_markup=get_back_on_view_keyboard(callback_data.id))
    await clear_chat(data=data)
    data['items_to_del'].append(msg)
    await state.update_data(data)
