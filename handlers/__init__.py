from aiogram import Router

from filters import ChatPrivateFilter


def setup_routers() -> Router:
    from .users import start, help, products, cart, balance
    from .admin import status_setting
    from .manager import add_product
    from .errors import error_handler
    
    router = Router()
    
    # Устанавливаем локальный фильтр, если нужно
    start.router.message.filter(ChatPrivateFilter(chat_type=["private"]))
    
    router.include_router(start.router)
    router.include_router(products.router)
    router.include_router(status_setting.router)
    router.include_router(add_product.router)
    router.include_router(balance.router)
    router.include_router(cart.router)
    router.include_router(help.router)
    router.include_router(error_handler.router)
    
    return router
