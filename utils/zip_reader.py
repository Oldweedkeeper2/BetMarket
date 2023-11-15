import asyncio
import os
import zipfile
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Any, List


async def async_zip_extractor(zip_path: str, extract_to: str, executor: ThreadPoolExecutor) -> None:
    loop = asyncio.get_running_loop()
    
    async def run_in_thread(fn: Callable, *args: Any) -> Any:
        return await loop.run_in_executor(executor, fn, *args)
    
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        for file in zipf.namelist():
            await run_in_thread(zipf.extract, file, extract_to)


async def unzip_command_handler(path_to_zip_file: str, path_to_extract: str) -> None:
    with ThreadPoolExecutor() as executor:
        await async_zip_extractor(path_to_zip_file, path_to_extract, executor)
        print("Файлы разархивированы в ZIP.")


async def async_zip_archiver(files_to_zip: List[str], zip_path: str, executor: ThreadPoolExecutor) -> None:
    loop = asyncio.get_running_loop()
    
    async def run_in_thread(fn: Callable, *args: Any) -> Any:
        return await loop.run_in_executor(executor, fn, *args)
    
    async def zip_files() -> None:
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file in files_to_zip:
                arcname = os.path.basename(file)
                await run_in_thread(zipf.write, file, arcname)
    
    await zip_files()


async def zip_command_handler(files_to_zip: List[str], zip_destination: str) -> None:
    with ThreadPoolExecutor() as executor:
        await async_zip_archiver(files_to_zip, zip_destination, executor)
        print("Файлы архивированы в ZIP.")

# TODO: При добавлении товара менеджером, ему присваивается product.id, и создаётся папка с именем {product.id}
#  для этого товара. Если товар - архив, то он разархивируется в папку с именем {product.id} с сохранением имён папок
#  под каждый аккаунт отдельно, иначе - в эту папку скачивается текстовый файл.
#
#
# TODO: ВОЗМОЖНО СТОИТ ВЫДЕЛИТЬ ВСЕ МЕТОДЫ ZIP В ОТДЕЛЬНЫЙ КЛАСС
#
#
#
# TODO: https://gist.github.com/lanfon72/0e3641c6cef3a5de75196619658d8f5b
#  1. Доделать личный кабинет, если нужно. Или хотя бы кнопку Пополнить баланс (Глеб должен подключить систему крипты).
#                                   Рассмотреть возможность реферального бонуса
#  2. Доделать методы для распаковки и сборки zip файлов.
#  3. Доделать добавление товаров (взять из ChannelMarket), попробовать использовать dataclasses, вместо fsm,
#                   также сделать фильтры по типу файла. (если возможно - проверять документ на zip архив)
#  4. Запланировать выгрузку статистики в гугл доки. Возможно дать админу кнопку выгрузки статистики.
#                       (это есть в SmokyBro)
#  5. Доделать оплату; деньги снимаются с баланса
#  6. Добавить модель заказов, после отправки файла попробовать забирать file_id документа и добавлять его в бд.
#  7. Добавить возможность удалять товары (список товаров с пагинацей, а также подтверждение удаления,
#                           пока права только у админа)
