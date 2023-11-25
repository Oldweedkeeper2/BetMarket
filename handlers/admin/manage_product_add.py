import logging
import os.path
from typing import Optional, Union

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ContentType as CT, Message
from aiogram.utils.markdown import hbold, hpre, hcode

from data.methods.products import ProductSQL
from data.models import Product
from keyboards.inline.admin.manage_product import ManageProduct
from keyboards.inline.manager.manage_product_add import get_back_keyboard
from states.manager.add_product import ProductState
from utils.account_sorter import handle_product_file
from utils.generate_dynamic_path import generate_dynamic_zip_path
from utils.misc.clear_chat import clear_chat

router = Router()
PRODUCT = 'product'
NAME = 'name'
PRICE = 'price'
DESCRIPTION = 'description'
MEDIA = 'product_media_group'
CURRENCY_SYMBOL = '$'  # TODO: вынести в конфиг


# router.message.middleware(MediaCatcher()) для нескольких файлов одновременно

async def get_product_text(state: FSMContext, end_text: Optional[str] = None, start_text: Optional[str] = None) -> str:
    """Получить текстовое представление информации о продукте."""
    data = await state.get_data()
    product_data = data.get('product', {})
    name = product_data.get(NAME, '❌')
    price = product_data.get(PRICE, '❌')
    description = product_data.get(DESCRIPTION, '❌')
    
    text = (f'Название:            {name}\n'
            f'Описание:            {description}\n'
            f'Цена:                {price} {CURRENCY_SYMBOL}\n')
    if start_text:
        text = f'❗ {hbold(start_text)}\n\n{hpre(text)}'
    if end_text:
        text += '\n' + end_text
    return text


async def write_product_data(state: FSMContext, item: Union[str, float], item_name: str,
                             product_name: str = PRODUCT) -> None:
    data = await state.get_data()
    data.setdefault(product_name, {})
    data[product_name][item_name] = item
    await state.update_data(data)


def get_full_product_text(product: Product):
    return hcode(f'Название:                  {product.name}\n'
                 f'Описание:                  {product.description}\n'
                 f'Цена:                      {product.price}\n'
                 f'Оставшееся количество:     {product.amount}\n'
                 f'ID того, кто добавил:      {product.uploader_id}\n')


@router.callback_query(ManageProduct.filter(F.action == 'add'))
async def handle(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    keyboard = get_back_keyboard()
    data['product'] = {}
    text = await get_product_text(state=state,
                                  start_text='Заполните поля, чтобы добавить новый товар',
                                  end_text='Введите название товара:')
    msg = await call.message.answer(text=text,
                                    reply_markup=keyboard)
    await clear_chat(data=data)
    data['items_to_del'].append(msg)
    await state.update_data(data)
    await state.set_state(ProductState.name)


@router.callback_query(F.data == 'view_products')
async def handle(call: CallbackQuery, state: FSMContext):
    await call.answer(text='Раздел "Добавление аккаунтов" находится в разработке', show_alert=True)


@router.message(ProductState.name)
async def handle(message: Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    keyboard = get_back_keyboard()
    name = message.text
    await write_product_data(state=state, item=name, item_name=NAME)
    text = await get_product_text(state=state,
                                  start_text='Заполните поля, чтобы добавить новый товар',
                                  end_text='Введите описание:')
    msg = await message.answer(text=text,
                               reply_markup=keyboard)
    await clear_chat(data=data)
    data['items_to_del'].append(msg)
    await state.update_data(data)
    await state.set_state(ProductState.description)


@router.message(ProductState.description)
async def handle(message: Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    keyboard = get_back_keyboard()
    description = message.text
    
    await write_product_data(state=state, item=description, item_name=DESCRIPTION)
    text = await get_product_text(state=state,
                                  start_text='Заполните поля, чтобы добавить новый товар',
                                  end_text='Введите цену:')
    msg = await message.answer(text=text,
                               reply_markup=keyboard)
    await clear_chat(data=data)
    data['items_to_del'].append(msg)
    await state.update_data(data)
    await state.set_state(ProductState.price)


@router.message(ProductState.price)
async def handle(message: Message, state: FSMContext):
    data = await state.get_data()
    keyboard = get_back_keyboard()
    try:
        price = float(message.text)
    except ValueError:
        await message.delete()
        text = await get_product_text(state=state,
                                      start_text='Заполните поля, чтобы добавить новый товар',
                                      end_text='❗ Некорректное значение. Повторите попытку\nЦена должна быть числом')
        msg = await message.answer(text=text,
                                   reply_markup=keyboard)
        await clear_chat(data=data)
        data['items_to_del'].append(msg)
        await state.update_data(data)
        await state.set_state(ProductState.price)
        return
    await write_product_data(state=state, item=price, item_name=PRICE)
    text = await get_product_text(state=state,
                                  end_text='<b>Отправьте текстовый документ или zip-aрхив</b>\n\n'
                                           '<i>Проверьте соответствие формату заполнения:\n'
                                           '\t ❕ Для текстовых - строки с разеделителем (указать разделитель!)\n'
                                           '\t ❕ Для zip-архивов - zip-архив с расширением .zip и каждый аккаунт в своей папке</i>')
    msg = await message.answer(text=text,
                               reply_markup=keyboard)
    await clear_chat(data=data)
    data['items_to_del'].append(msg)
    await state.update_data(data)
    await state.set_state(ProductState.upload_file)


@router.message(ProductState.upload_file, F.content_type == CT.DOCUMENT)
async def handle(message: Message, state: FSMContext):
    data = await state.get_data()
    keyboard = get_back_keyboard()
    
    file_id = message.document.file_id
    mime_type = message.document.mime_type
    file_info = await message.bot.get_file(file_id)
    
    # вынести получение конечного товара в отдельную функцию
    product_data = data['product']
    print(product_data)
    product_data['uploader_id'] = message.from_user.id
    product_data['file_id'] = file_id
    
    product = await ProductSQL.add(product_data=product_data)
    relative_path = generate_dynamic_zip_path()
    
    if product is None:
        logging.error('Не удалось добавить продукт')
        await message.answer(text='Не удалось добавить продукт. Попробуйте ещё раз', reply_markup=keyboard)
        await state.set_state(ProductState.upload_file)
        return
    file_extension = 'zip' if mime_type == 'application/zip' else 'txt'
    local_file_path = os.path.join(relative_path['R_ZIPPED_FILE_PATH'], f'{str(product.id)}.{file_extension}')
    
    try:
        await message.bot.download_file(file_info.file_path, destination=local_file_path)
        is_zip = mime_type == 'application/zip'
        await handle_product_file(product_id=product.id,
                                  file_path=local_file_path,
                                  relative_path=relative_path,
                                  is_zip=is_zip,
                                  is_add=False)
    
    except Exception as e:
        await message.delete()
        await message.answer(text='Не удалось скачать файл. Попробуйте ещё раз', reply_markup=keyboard)
        logging.debug(e)
        await state.set_state(ProductState.upload_file)
        return
    
    updated_product = await ProductSQL.get_by_id(id=product.id)
    text = get_full_product_text(product=updated_product)
    
    msg = await message.answer(text=text, reply_markup=keyboard)
    await clear_chat(data=data)
    data['items_to_del'].append(msg)
    await state.update_data(data)
