import logging
import mimetypes
import os
import random
import shutil
from pathlib import Path
from typing import List, Union

import aiofiles
from aiofiles.os import remove

from data.methods.accounts import AccountSQL
from data.methods.files import FileSQL
from data.methods.products import ProductSQL
from data.models import Account
from utils.zip_reader import unzip_command_handler, zip_command_handler


class FileManager:
    
    @classmethod
    async def read_file(cls, file_path: Union[str, Path]) -> List[str]:
        # TODO: Согласовать разделитель аккаунтов
        async with aiofiles.open(file_path, mode='r') as file:
            content = await file.read()
        return content.split(';')
    
    @classmethod
    async def write_file(cls, file_path: Union[str, Path], content: str) -> None:
        async with aiofiles.open(file_path, mode='w') as file:
            await file.write(content)
    
    @staticmethod
    def create_path(path_str: str) -> Path:
        return Path(path_str)
    
    @staticmethod
    def create_directory(path: Path):
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    async def delete_file_async(file_path: Union[str, Path]) -> None:
        try:
            if type(file_path) is not Path:
                file_path = Path(file_path)
            if file_path.exists():
                await aiofiles.os.remove(file_path)
        except Exception as e:
            logging.debug(f"Ошибка при удалении файла: {e}")
            raise


class ProductFileProcessor(FileManager):
    def __init__(self, product_id: int, root_zip_path: Union[str, Path], is_add: bool = False):
        self.product_id = product_id
        self.root_zip_path = Path(root_zip_path)
        self.id_add = is_add
    
    async def process_text_file(self, product_file_path: Union[str, Path]) -> None:
        accounts = await self.read_file(product_file_path)
        for id, account in enumerate(accounts, start=1):
            if account:
                account_data = {'account_name': str(id), 'product_id': self.product_id}
                account_id = await AccountSQL.add_account(account_data)
                
                simple_account_path = self.root_zip_path / f'{id}.txt'
                await self.write_file(simple_account_path, account)
                
                logging.debug(simple_account_path)
                zip_destination = self.root_zip_path / f'{id}.zip'
                
                logging.debug(zip_destination)
                await zip_command_handler([str(simple_account_path)], str(zip_destination))
                
                logging.debug(get_mime_type(str(zip_destination)))
                await self.add_file_to_db(zip_destination, account_id)
                await self.delete_file_async(simple_account_path)
        if accounts:
            await ProductSQL.update_product_amount(product_id=self.product_id,
                                                   amount=len(accounts),
                                                   is_add=self.id_add)
    
    async def process_unzipped_files(self, product_folder: Union[str, Path]) -> None:
        count_accounts = 0
        product_folder_path = Path(product_folder)
        
        for account_folder in product_folder_path.iterdir():
            if account_folder.is_dir():
                count_accounts += 1
                account_id = await self.add_account(account_folder.name)
                
                files_to_zip = [str(file) for file in account_folder.iterdir() if file.is_file()]
                zip_destination = self.root_zip_path / f"{account_folder.name}.zip"
                
                await zip_command_handler(files_to_zip, str(zip_destination))
                
                await self.add_file_to_db(zip_destination, account_id)
                delete_product_folder(account_folder=account_folder.name, root_zip_path=self.root_zip_path)
        
        if count_accounts > 0:
            await ProductSQL.update_product_amount(product_id=self.product_id,
                                                   amount=count_accounts,
                                                   is_add=self.id_add)
    
    async def add_account(self, account_name: str) -> int | bool:
        account_data = {'account_name': account_name, 'product_id': self.product_id}
        return await AccountSQL.add_account(account_data)
    
    @staticmethod
    async def add_file_to_db(zip_destination: Path, account_id: int) -> int | bool:
        archive_data = {
            'file_name': zip_destination.name,
            'file_path': str(zip_destination),
            'file_type': get_mime_type(str(zip_destination)),
            'account_id': account_id
        }
        return await FileSQL.add_file(archive_data)


def get_mime_type(file_path: Union[str, Path]) -> str:
    mime_type, _ = mimetypes.guess_type(str(file_path))
    return mime_type if mime_type else "unknown"


def delete_product_folder(account_folder: str, root_zip_path: Union[str, Path]) -> bool:
    try:
        product_folder_path = Path(root_zip_path) / str(account_folder)
        if product_folder_path.exists():
            shutil.rmtree(product_folder_path, ignore_errors=True)
            return True
    except Exception as e:
        logging.exception("An error occurred: {e}")
        return False


def create_product_folder(product_id: int, root_zip_path: Union[str, Path]) -> Path:
    product_folder_path = Path(root_zip_path) / str(product_id)
    if not product_folder_path.exists():
        product_folder_path.mkdir(parents=True, exist_ok=True)
    return product_folder_path


async def handle_product_file(product_id: int,
                              file_path: Union[str, Path],
                              relative_path: dict, is_zip: bool = False,
                              is_add: bool = False) -> None:
    processor = ProductFileProcessor(product_id,
                                     create_product_folder(product_id, relative_path['ACCOUNTS_PATH']),
                                     is_add)
    
    if is_zip:
        await unzip_command_handler(path_to_zip_file=file_path, path_to_extract=str(processor.root_zip_path))
        await processor.process_unzipped_files(processor.root_zip_path)
    else:
        logging.debug('processing text file'.upper())
        await processor.process_text_file(file_path)


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
    
    # Создание подпапки для заказа, если она еще не существует
    if not os.path.exists(zipped_files_sent_path):
        os.makedirs(zipped_files_sent_path)
    
    for product_id, amount in cart_data.items():
        # Получение информации о продукте
        product = await ProductSQL.get_by_id(id=product_id)
        # Проверка наличия продукта и его количества
        if not product or int(product.amount) < int(amount):
            logging.warning(f"Недостаточно товара с ID {product_id} в наличии.")
            # TODO: сделать выход программы с ошибкой "недостаточно товара {название товара}"
            continue
        
        # Выбор случайных аккаунтов
        selected_accounts = random.sample(product.accounts, amount)
        # Обработка ZIP файлов
        path_list = []
        for account in selected_accounts:  # type: Account
            
            account_file_path = f'{accounts_path[:3]}{account.files[0].file_path}'
            path_list.append(account_file_path)
        
        await AccountSQL.delete_account(selected_accounts)
        await ProductSQL.update_product_amount(product_id=product_id, amount=-amount, is_add=False)
        zip_order_path = os.path.join(zipped_files_sent_path, f'{order_id}.zip')
        await zip_command_handler(path_list, zip_order_path)
        try:
            for path in path_list:
                os.remove(path)
        except Exception as e:
            logging.debug(f"An error occurred: {e}")
            return e
        return zip_order_path


class ProductBuyProcessor(FileManager):
    """ Класс для обработки покупки продукта """
    
    def __init__(self, cart_data: dict, order_id: int, relative_path: dict):
        self.cart_data = cart_data
        self.order_id = order_id
        self.relative_path = relative_path
        self.zipped_files_sent_path = self.create_path(relative_path['S_ZIPPED_FILE_PATH']).joinpath(
                str(order_id))
        self.accounts_path = relative_path['ACCOUNTS_PATH']
    
    async def handle_buy_product(self) -> str:
        for product_id, amount in self.cart_data.items():
            logging.debug(f'{product_id} {amount}')
            # Получение информации о продукте
            product = await ProductSQL.get_by_id(id=product_id)
            logging.debug(product)
            # Проверка наличия продукта
            if not product or int(product.amount) < int(amount):
                logging.warning(f"Недостаточно товара с ID {product_id} в наличии.")
                return
            
            self.create_directory(self.zipped_files_sent_path)
            # Выбор случайных аккаунтов
            selected_accounts = random.sample(product.accounts, amount)
            logging.debug(selected_accounts[0].files[0].file_path)
            path_list = [f'{account.files[0].file_path}' for account in
                         selected_accounts]
            
            await AccountSQL.delete_account(selected_accounts)
            await ProductSQL.update_product_amount(product_id=product_id, amount=-amount, is_add=False)
            logging.debug(self.zipped_files_sent_path)
            logging.debug(path_list)
            zip_order_path = self.zipped_files_sent_path.joinpath(f'{self.order_id}.zip')
            logging.debug(zip_order_path)
            await zip_command_handler(path_list, str(zip_order_path))
            
            for path in path_list:
                await self.delete_file_async(path)
            
            return str(zip_order_path)

# Пример использования
# key = product_id, value = amount
# cart_data = {3: 2}
# order_id = 14
# relative_path = generate_dynamic_zip_path()
# asyncio.run(ProductBuyProcessor(cart_data, order_id, relative_path).handle_buy_product())
#
#

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

# test_cart_data = {
#     1: 4,
#     2: 5,
#     3: 1
# }
# # Пример использования
# cart_data = {3: 1}
# order_id = 123
# relative_path = generate_dynamic_zip_path()
# print(relative_path)
# asyncio.run(handle_buy_product(cart_data, order_id, relative_path))
