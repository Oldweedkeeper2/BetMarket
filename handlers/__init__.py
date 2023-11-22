from aiogram import Router

from filters import ChatPrivateFilter


def setup_routers() -> Router:
    from .users import start, help, products, cart, balance
    from .admin import settings, setting_managers, setting_users, manage_product, manage_product_edit, \
        manage_product_add
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
    router.include_router(manage_product.router)
    router.include_router(manage_product_edit.router)
    
    # ADMIN & MANAGER
    router.include_router(manage_product_add.router)
    
    return router
