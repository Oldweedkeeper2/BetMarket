import secrets
import subprocess

from environs import Env

# Список идентификаторов администраторов, которым будут отправляться уведомления при запуске бота
admins = [
    823932122,
]

# Получение текущей версии из системы контроля версий Git
VERSION = subprocess.check_output(["git", "describe", "--always"]).strip().decode()

# Инициализация объекта для работы с переменными окружения
env = Env()
env.read_env()

# Токен бота
BOT_TOKEN: str = env.str("BOT_TOKEN")

ALCHEMY_DATABASE_URL: str = env.str("ALCHEMY_DATABASE_URL")
# Использовать ли вебхук
USE_WEBHOOK: bool = env.bool("USE_WEBHOOK", False)

# Использовать ли SSL
USE_SSL: bool = env.bool("USE_SSL", False)

# Рабочие константы
PAGE_WIDTH = 10
USER_PAGE_WIDTH = 30
ROOT_FOLDER = 'BetMarket'
ROOT_ZIP_PATH = 'zip'

ADMIN_USERNAME = 'Oldweedkeeper'
TECH_SUPPORT_USERNAME = 'Oldweedkeeper'

#
# # Если используется вебхук
if USE_WEBHOOK:
    # Основной адрес вебхука
    MAIN_WEBHOOK_ADDRESS: str = env.str("MAIN_WEBHOOK_ADDRESS")
    
    # Путь к вебхуку
    MAIN_WEBHOOK_PATH: str = env.str("MAIN_WEBHOOK_PATH")
    
    # Секретный токен для вебхука
    MAIN_WEBHOOK_SECRET_TOKEN: str = secrets.token_urlsafe(32)
    
    # Хост для прослушивания вебхука
    MAIN_WEBHOOK_LISTENING_HOST: str = env.str("MAIN_WEBHOOK_LISTENING_HOST")
    
    # Порт для прослушивания вебхука
    MAIN_WEBHOOK_LISTENING_PORT: int = env.int("MAIN_WEBHOOK_LISTENING_PORT")
    
    # Максимальное количество обновлений в очереди
    MAX_UPDATES_IN_QUEUE: int = env.int("MAX_UPDATES_IN_QUEUE", 100)
