from aiogram import Router

from filters import ChatPrivateFilter


def setup_routers() -> Router:
    from .users import start, help, products, cart, balance
    from .admin import settings, setting_managers, setting_users
    from .manager import add_product
    from .errors import error_handler
    
    router = Router()
    
    # Устанавливаем локальный фильтр, если нужно
    start.router.message.filter(ChatPrivateFilter(chat_type=["private"]))
    
    # ALL
    router.include_router(start.router)
    router.include_router(products.router)
    router.include_router(balance.router)
    router.include_router(cart.router)
    router.include_router(help.router)
    router.include_router(error_handler.router)
    
    # ADMIN
    router.include_router(settings.router)
    router.include_router(setting_managers.router)
    router.include_router(setting_users.router)
    
    # ADMIN & MANAGER
    router.include_router(add_product.router)
    
    return router
