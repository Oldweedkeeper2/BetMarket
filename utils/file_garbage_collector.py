import logging
from pathlib import Path

from data.methods.orders import OrderSQL
from utils.account_sorter import delete_product_folder
from utils.generate_dynamic_path import generate_dynamic_zip_path


async def garbage_collector(relative_path: dict):
    # relative_path = generate_dynamic_zip_path()
    legacy_orders = await OrderSQL.get_legacy_orders()
    logging.debug('Удаление файлов: %s', legacy_orders)
    for order in legacy_orders:
        file_path = Path(relative_path['S_ZIPPED_FILE_PATH']) / str(order.id)
        logging.info('Удаление файла: %s', file_path)
        
        result = delete_product_folder(root_zip_path=relative_path['S_ZIPPED_FILE_PATH'], account_folder=order.id)
        logging.info('result: %s', result)

