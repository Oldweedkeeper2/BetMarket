from contextlib import suppress

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from data.config import PAGE_WIDTH
from data.methods.products import ProductSQL
from data.models import Product
from keyboards.inline.products import paginator, Pagination, ProductData, get_product_keyboard, \
    ProductPagination
from utils.misc.clear_chat import clear_chat

router = Router()


async def update_pagination_message(call: CallbackQuery, page: int, product_list):
    """Updates the message for pagination."""
    await call.answer()
    with suppress(TelegramBadRequest):
        await call.message.edit_text(
                text=f"<b>Выберите товар: Можно поставить сюда продающий текст или условия какие-нибудь</b>",
                reply_markup=paginator(product_list, page)
        )


@router.callback_query(Pagination.filter(F.action.in_(["prev", "next"])))
async def handle(call: CallbackQuery, callback_data: Pagination):
    product_list = await ProductSQL.get_all()
    
    page_num = callback_data.page
    page = max(page_num - 1, 0) if callback_data.action == "prev" else page_num + 1
    has_more = len(product_list) > page * PAGE_WIDTH
    
    if callback_data.action == "next" and not has_more:
        page = page_num
    
    await update_pagination_message(call, page, product_list)


@router.callback_query(F.data == 'get_products')
async def handle(call: CallbackQuery, state: FSMContext):
    product_list = await ProductSQL.get_all()
    print(product_list)
    msg = await call.message.answer(
            text='<b>Выберите товар: Можно поставить сюда продающий текст или условия какие-нибудь</b>',
            reply_markup=paginator(product_list=product_list)
    )
    data = await state.get_data()
    await clear_chat(data=data)
    data['items_to_del'].append(msg)
    await state.update_data(data)


def get_product_text(product: Product) -> str:  # вынести в файл с utils
    return (f"<b>Название:</b> {product.name}\n"
            f"<b>Описание:</b> {product.description or 'Нет описания'}\n"
            f"<b>Стоимость:</b> {product.price or 0} $\n"
            f"<b>Оставшееся количество:</b> {product.amount}\n")


def get_cart_product_text(product: Product, amount: int) -> str:  # вынести в файл с utils
    return (f"<b>Название:</b> {product.name}\n"
            f"<b>Описание:</b> {product.description or 'Нет описания'}\n"
            f"<b>Стоимость:</b> {product.price or 0} $\n"
            f"<b>Оставшееся количество:</b> {product.amount}\n"
            f"<b>Выбранное количество:</b> {amount}\n")


@router.callback_query(ProductData.filter(F.id))
async def handle(call: CallbackQuery, state: FSMContext, callback_data: ProductData):
    product_id = callback_data.id
    product = await ProductSQL.get_by_id(product_id)
    product_text = get_product_text(product)
    data = await state.get_data()
    has_in_cart: dict = data['cart'].get(product_id, None)
    if not has_in_cart:
        amount = 0
        data['cart'].setdefault(product_id, amount)
    else:
        amount = data['cart'][product_id]
    keyboard = get_product_keyboard(amount, product.amount)
    with suppress(TelegramBadRequest):
        await call.message.edit_text(
                text=product_text,
                reply_markup=keyboard
        )
    data['current_product'] = product
    await state.update_data(data)


async def update_amount_pagination_message(call: CallbackQuery, amount: int, total_products: int):
    """Updates the message for pagination."""
    await call.answer()
    with suppress(TelegramBadRequest):
        await call.message.edit_reply_markup(
                inline_message_id=call.inline_message_id,
                reply_markup=get_product_keyboard(amount=amount, total_products=total_products)
        )


@router.callback_query(ProductPagination.filter(F.action.in_(["inc_product", "dec_product"])))
async def handle(call: CallbackQuery, state: FSMContext, callback_data: ProductPagination):
    data = await state.get_data()
    amount = callback_data.amount
    new_amount = max(amount - 1, 0) if callback_data.action == "dec_product" else amount + 1
    new_amount = min(new_amount, data['current_product'].amount)
    print(new_amount)
    product = data['current_product']
    
    if callback_data.action == "inc_product" and amount >= product.amount:
        new_amount = amount
    
    await update_amount_pagination_message(call, new_amount, product.amount)
    
    data['cart'][product.id] = new_amount
    await state.update_data(data)


@router.callback_query(F.data == 'empty')
async def handle(call: CallbackQuery):
    await call.answer()
