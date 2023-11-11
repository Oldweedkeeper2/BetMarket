from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_role_start_keyboard(role: str) -> InlineKeyboardMarkup:
    buttons = []
    if role == "Admin":
        buttons.append([
            InlineKeyboardButton(text="Добавить товар", callback_data="add_new_product")]
        )
        buttons.append([
            InlineKeyboardButton(text="Добавить менеджера", callback_data="add_new_manager")]
        )
    if role == "Manager":
        buttons.append([InlineKeyboardButton(text="Добавить товар", callback_data="add_new_product")])
    
    buttons.append([
        InlineKeyboardButton(text="Товары", callback_data="get_products")
    ])
    buttons.append([
        InlineKeyboardButton(text="Помощь", callback_data="help")
    ])
    
    keyboard_markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard_markup
