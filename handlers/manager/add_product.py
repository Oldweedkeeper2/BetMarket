import os.path

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ContentType as CT, Message

from data.methods.products import ProductSQL
from keyboards.inline.manager.add_products import get_back_keyboard
from states.manager.add_product import FileState
from utils.account_sorter import handle_product_file
from utils.generate_dynamic_path import generate_dynamic_zip_path
from utils.misc.clear_chat import clear_chat
import logging

router = Router()


# router.message.middleware(MediaCatcher()) для нескольких файлов одновременно


@router.callback_query(F.data == 'add_new_product')
async def handle(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    keyboard = get_back_keyboard()
    msg = await call.message.answer(text='<b>Отправьте текстовый документ или zip-aрхив</b>\n\n'
                                         '<i>Проверьте соответствие формату заполнения:\n'
                                         '\t ❕ Для текстовых - строки с разеделителем (указать разделитель!)\n'
                                         '\t ❕ Для zip-архивов - zip-архив с расширением .zip и каждый аккаунт в своей папке</i>',
                                    reply_markup=keyboard)
    await clear_chat(data=data)
    data['items_to_del'].append(msg)
    await state.update_data(data)
    await state.set_state(FileState.upload_file)


def get_test_product_data(message):
    return {
        'name': 'Тестовое имя',
        'description': 'Тестовое описание',
        'price': 100,
        'amount': 100,
        'uploader_id': message.from_user.id,
        'file_id': message.document.file_id
    }


@router.message(FileState.upload_file, F.content_type == CT.DOCUMENT)
async def handle(message: Message, state: FSMContext):
    data = await state.get_data()
    keyboard = get_back_keyboard()
    
    file_id = message.document.file_id
    mime_type = message.document.mime_type
    file_info = await message.bot.get_file(file_id)
    
    product_data = get_test_product_data(message)
    product_id = await ProductSQL.add(product_data=product_data)
    relative_path = generate_dynamic_zip_path()
    
    file_extension = 'zip' if mime_type == 'application/zip' else 'txt'
    local_file_path = os.path.join(relative_path['R_ZIPPED_FILE_PATH'], f'{str(product_id)}.{file_extension}')
    
    try:
        await message.bot.download_file(file_info.file_path, destination=local_file_path)
        is_zip = mime_type == 'application/zip'
        await handle_product_file(product_id=product_id,
                                  file_path=local_file_path,
                                  relative_path=relative_path,
                                  is_zip=is_zip)
    except Exception as e:
        await message.delete()
        await message.answer(text='Не удалось скачать файл. Попробуйте ещё раз', reply_markup=keyboard)
        logging.debug(e)
        await state.set_state(FileState.upload_file)
        return
    
    msg = await message.answer(text='Документ добавлен', reply_markup=keyboard)
    await clear_chat(data=data)
    data['items_to_del'].append(msg)
    await state.update_data(data)
