import mimetypes
import os
import shutil

from data.methods.accounts import AccountSQL
from data.methods.files import FileSQL
from data.methods.products import ProductSQL
from utils.zip_reader import unzip_command_handler


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
                
                for file_name in os.listdir(account_path):
                    file_path = os.path.join(account_path, file_name)
                    file_type = get_mime_type(file_path)
                    
                    if os.path.isfile(file_path):
                        file_data = {'file_name': file_name, 'file_path': file_path, 'file_type': file_type,
                                     'account_id': account_id}
                        await FileSQL.add_file(file_data)
        
        if count_accounts > 0:
            await ProductSQL.update_product_amount(product_id=self.product_id, amount=count_accounts, is_add=is_add)
    
    def _move_file(self, file_path):
        destination_file_path = os.path.join(self.root_zip_path, os.path.basename(file_path))
        shutil.move(file_path, destination_file_path)
    
    @staticmethod
    def create_product_folder(product_id, root_zip_path):
        product_folder_path = os.path.join(root_zip_path, str(product_id))
        if not os.path.exists(product_folder_path):
            os.mkdir(product_folder_path)
        return product_folder_path


async def handle_product_file(product_id, file_path, relative_path, is_zip=False, is_add=False):
    processor = ProductFileProcessor(product_id, ProductFileProcessor.create_product_folder(product_id, relative_path[
        'ACCOUNTS_PATH']))
    
    if is_zip:
        await unzip_command_handler(path_to_zip_file=file_path, path_to_extract=processor.root_zip_path)
        await processor.process_unzipped_files(processor.root_zip_path, is_add=is_add)
    else:
        await processor.process_text_file(file_path, is_add=is_add)

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
#
#



