import os

from data.config import ROOT_FOLDER


def generate_dynamic_zip_path(root_folder=ROOT_FOLDER):
    """Генерирует динамический путь к папке BetMarket/zip."""
    def find_relative_path_to_root(current_path):
        """Находит относительный путь к корневой папке."""
        depth = 0
        if os.path.basename(current_path) == ROOT_FOLDER:
            return ''
        while current_path != os.path.dirname(current_path):
            if os.path.basename(current_path) == root_folder:
                return '../' * depth  # Формирование относительного пути
            current_path = os.path.dirname(current_path)
            depth += 1
        return None
    
    # Путь к текущей рабочей директории
    current_path = os.getcwd()
    
    # Находим относительный путь к BetMarket
    relative_path = find_relative_path_to_root(current_path)
    
    if relative_path is not None:
        # Формирование путей к подпапкам внутри BetMarket/zip
        root_zip_path = os.path.join(relative_path, 'zip')
        accounts_path = os.path.join(root_zip_path, 'accounts')
        r_zipped_file_path = os.path.join(root_zip_path, 'zipped_files_received')
        unzipped_file_path = os.path.join(root_zip_path, 'zip_files_extracted')
        s_zipped_file_path = os.path.join(root_zip_path, 'zipped_files_sent')
        
        return {
            "ROOT_ZIP_PATH": root_zip_path,
            "ACCOUNTS_PATH": accounts_path,
            "R_ZIPPED_FILE_PATH": r_zipped_file_path,
            "UNZIPPED_FILE_PATH": unzipped_file_path,
            "S_ZIPPED_FILE_PATH": s_zipped_file_path
        }
    else:
        return "Папка BetMarket не найдена."


def get_relative_path(RELATIVE_ROOT_ZIP_PATH):
    R_ZIPPED_FILE_PATH = f'{RELATIVE_ROOT_ZIP_PATH}zip/zipped_files_received'
    UNZIPPED_FILE_PATH = f'{RELATIVE_ROOT_ZIP_PATH}zip/zip_files_extracted'
    S_ZIPPED_FILE_PATH = f'{RELATIVE_ROOT_ZIP_PATH}zip/zipped_files_sent'

    return {
        "R_ZIPPED_FILE_PATH": R_ZIPPED_FILE_PATH,
        "UNZIPPED_FILE_PATH": UNZIPPED_FILE_PATH,
        "S_ZIPPED_FILE_PATH": S_ZIPPED_FILE_PATH
    }
