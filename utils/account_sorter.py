import asyncio
import logging
import mimetypes
import os
import random
import shutil

from data.methods.accounts import AccountSQL
from data.methods.files import FileSQL
from data.methods.products import ProductSQL
from data.models import Account, File
from utils.generate_dynamic_path import generate_dynamic_zip_path
from utils.zip_reader import unzip_command_handler, zip_command_handler


def get_mime_type(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type if mime_type else "unknown"


# # ОБНОВЛЕНИЕ! НУЖНО ПРОВЕРИТЬ
class ProductFileProcessor:
    def __init__(self, product_id, root_zip_path):
        self.product_id = product_id
        self.root_zip_path = root_zip_path
    
    async def process_text_file(self, file_path, is_add):
        with open(file_path, 'r') as file:
            accounts = file.read().split(';')
        
        for account_name in accounts:
            if account_name:
                account_data = {'account_name': account_name, 'product_id': self.product_id}
                file_data = {'file_name': account_name, 'file_path': file_path, 'file_type': 'text', 'account_id': -1}
                await AccountSQL.add_account(account_data)
                await FileSQL.add_file(file_data)
        
        if accounts:
            await ProductSQL.update_product_amount(product_id=self.product_id, amount=len(accounts), is_add=is_add)
        
        self._move_file(file_path)
    
    async def process_unzipped_files(self, product_folder, is_add):
        count_accounts = 0
        for account_folder in os.listdir(product_folder):
            
            account_path = os.path.join(product_folder, account_folder)
            if os.path.isdir(account_path):
                count_accounts += 1
                account_data = {'account_name': account_folder, 'product_id': self.product_id}
                account_id = await AccountSQL.add_account(account_data)
                
                # Список файлов для архивации
                files_to_zip = [os.path.join(account_path, file) for file in os.listdir(account_path) if
                                os.path.isfile(os.path.join(account_path, file))]
                # Путь к архиву
                zip_destination = os.path.join(self.root_zip_path, f"{account_folder}.zip")
                
                # Вызов функции архивации
                await zip_command_handler(files_to_zip, zip_destination)
                
                # Добавляем данные об архиве в БД
                archive_data = {'file_name': f"{account_folder}.zip", 'file_path': zip_destination,
                                'file_type': 'application/zip',
                                'account_id': account_id}
                
                delete_product_folder(account_folder=account_folder,
                                      root_zip_path=self.root_zip_path)
                await FileSQL.add_file(archive_data)
        
        if count_accounts > 0:
            await ProductSQL.update_product_amount(product_id=self.product_id, amount=count_accounts, is_add=is_add)
    
    def _move_file(self, file_path):
        destination_file_path = os.path.join(self.root_zip_path, os.path.basename(file_path))
        shutil.move(file_path, destination_file_path)


def delete_product_folder(account_folder, root_zip_path):
    try:
        product_folder_path = os.path.join(root_zip_path, str(account_folder))
        if os.path.exists(product_folder_path):
            shutil.rmtree(product_folder_path, ignore_errors=True)
            return True
    except Exception as e:
        logging.warning(e)
        return False


def delete_product_files(product_id, root_zip_path, extension='.zip'):
    try:
        product_folder_path = os.path.join(root_zip_path, str(product_id) + extension)
        if os.path.exists(product_folder_path):
            shutil.rmtree(product_folder_path, ignore_errors=True)
            return True
    except Exception as e:
        logging.warning(e)
        return False


def create_product_folder(product_id, root_zip_path):
    product_folder_path = os.path.join(root_zip_path, str(product_id))
    if not os.path.exists(product_folder_path):
        os.mkdir(product_folder_path)
    return product_folder_path


async def handle_product_file(product_id, file_path, relative_path, is_zip=False, is_add=False):
    processor = ProductFileProcessor(product_id,
                                     create_product_folder(product_id, relative_path['ACCOUNTS_PATH']))
    
    if is_zip:
        await unzip_command_handler(path_to_zip_file=file_path, path_to_extract=processor.root_zip_path)
        # delete_product_files(product_id, relative_path['ACCOUNTS_PATH'])
        await processor.process_unzipped_files(processor.root_zip_path, is_add=is_add)
    else:
        await processor.process_text_file(file_path, is_add=is_add)


#
#
# key = product_id, value = amount
test_cart_data = {
    1: 4,
    2: 5,
    3: 1
}


# У нас есть корзина, которая содержит идентификаторы продуктов и их количество. Мы должны взять один product_id
# проверить в наличии (чтобы его не забрали, пока пользователь выбирал) уменьшить количество товаров.
# Если нет, то выдать сообщение о том, что продукта такого-то не хватает в наличии. Иначе - берём рандомные
# аккаунты этого продукта, смотрим их файлы, если у всех аккаунтов один и тот же файл, то это txt файл, мы открываем
# его, выбираем первые amount аккаунтов, перемещаем их в папку ZIPPED_FILES_SENT в подпапку {номер заказа},
# в новый файл txt, иначе - папка такого формата zip\accounts\{product_id}\{account_id}, где лежит архив с аккаунтом
# одним. Дальше мы берём amount таких папок с аккаунтами и перемещаем их в папку ZIPPED_FILES_SENT в подпапку
# {номер заказа}. После прохода по всей корзине - заходим в подпапку {номер заказа}, собираем их в архив.


async def handle_buy_product(cart_data: dict, order_id: int, relative_path: dict):
    zipped_files_sent_path = os.path.join(relative_path['S_ZIPPED_FILE_PATH'], str(order_id))
    accounts_path = relative_path['ACCOUNTS_PATH']
    print(accounts_path)
    # Создание подпапки для заказа, если она еще не существует
    if not os.path.exists(zipped_files_sent_path):
        os.makedirs(zipped_files_sent_path)
    
    for product_id, amount in cart_data.items():
        # Получение информации о продукте
        product = await ProductSQL.get_by_id(id=product_id)
        
        # Проверка наличия продукта и его количества
        if not product or int(product.amount) < int(amount):
            print(f"Недостаточно товара с ID {product_id} в наличии.")
            continue
        
        # Выбор случайных аккаунтов
        selected_accounts = random.sample(product.accounts, amount)
        
        # Проверка, одинаковый ли файл у всех аккаунтов
        first_account_file: File = selected_accounts[0].files[0]
        first_account_file_file_path = first_account_file.file_path
        print(first_account_file_file_path)
        # print(os.path.join(accounts_path[:3], first_account_file_file_path))
        if all(account.files[0].file_path == first_account_file_file_path for account in selected_accounts):
            # Обработка текстового файла
            with open(os.path.join(accounts_path[:3], first_account_file_file_path), 'r') as file:
                account_names = file.read().split(';')
            
            # Запись первых 'amount' аккаунтов в новый txt файл
            with open(f'{zipped_files_sent_path}/accounts_{product_id}.txt', 'w') as file:
                file.write(';'.join(account_names[:amount]))
        else:
            # Обработка ZIP файлов
            for account in selected_accounts:
                account_file = f'zip/accounts/{product_id}/{account.id}.zip'
                # Перемещение ZIP файла в папку заказа
                shutil.move(account_file, f'{zipped_files_sent_path}/{os.path.basename(account_file)}')
        
        # Обновление количества товара
        await ProductSQL.update_product_amount(product_id=product_id, amount=-amount, is_add=False)

# TODO: СОЗДАТЬ КОММИТ ДЛЯ НАЧАЛА!!!!
#  1. Создать функции, которые будут принимать amount и product_id, смотреть из бд путь к этому файлу,
#                       а потом выдавать его, после чего файлы с акками удаляем из бд и папок, так меньше мороки,
#                       хотя функции для складирования тоже есть. Необходимо будет учитывать связные файлы
#                       и относительный путь, благо все вспомогательные функции уже есть.
#  2. Добавить правильное заполнение товара для менеджера
#  3. Добавить кнопку "Очистить корзину"
#  4. Добавить кнопку "Оплатить" и процесс оплаты с баланса личного кабинета. Товары мы не резервируем, так как
#                       иначе можно просто сломать бота, оставив все акки в резервации.
#  5. Нужно учитывать, что бота будут бить и пытаться ломать, нужно делать на совесть и тестировать
#


# # Пример использования
# cart_data = {19: 1}
# order_id = 123
# relative_path = generate_dynamic_zip_path()
# print(relative_path)
# asyncio.run(handle_buy_product(cart_data, order_id, relative_path))
# #
#
#
#
# async def handle_buy_product(cart_data: dict, order_id: int):
#     zipped_files_sent_path = f'ZIPPED_FILES_SENT/{order_id}'
#
#     # Создание подпапки для заказа, если она еще не существует
#     if not os.path.exists(zipped_files_sent_path):
#         os.makedirs(zipped_files_sent_path)
#
#     for product_id, amount in cart_data.items():
#         # Получение информации о продукте
#         product = await ProductSQL.get_by_id(id=product_id)
#
#         # Проверка наличия продукта и его количества
#         if not product or int(product.amount) < int(amount):
#             print(f"Недостаточно товара с ID {product_id} в наличии.")
#             continue
#
#         # Выбор случайных аккаунтов
#         selected_accounts = random.sample(product.accounts, amount)
#
#         # Проверка, одинаковый ли файл у всех аккаунтов
#         first_account_file = selected_accounts[0].files[0]
#         if all(account.files[0] == first_account_file for account in selected_accounts):
#             # Обработка текстового файла
#             with open(first_account_file, 'r') as file:
#                 account_names = file.read().split(';')
#
#             # Запись первых 'amount' аккаунтов в новый txt файл
#             with open(f'{zipped_files_sent_path}/accounts_{product_id}.txt', 'w') as file:
#                 file.write(';'.join(account_names[:amount]))
#         else:
#             # Обработка ZIP файлов
#             for account in selected_accounts:
#                 account_file = f'zip/accounts/{product_id}/{account.id}.zip'
#                 # Перемещение ZIP файла в папку заказа
#                 shutil.move(account_file, f'{zipped_files_sent_path}/{os.path.basename(account_file)}')
#
#         # Обновление количества товара
#         await ProductSQL.update_product_amount(product_id=product_id, amount=-amount, is_add=False)
#
#     # Дополнительная логика по сборке всех файлов в архив может быть добавлена здесь
#     # ...
