from contextlib import suppress

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from data.config import PAGE_WIDTH
from data.methods.products import ProductSQL
from keyboards.inline.products import paginator, Pagination

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
    product_list = await ProductSQL.get_all_product()
    
    page_num = callback_data.page
    page = max(page_num - 1, 0) if callback_data.action == "prev" else page_num + 1
    has_more = len(product_list) > page * PAGE_WIDTH
    
    if callback_data.action == "next" and not has_more:
        page = page_num
    
    await update_pagination_message(call, page, product_list)


@router.callback_query(F.data == 'get_products')
async def handle(call: CallbackQuery, state: FSMContext):
    product_list = await ProductSQL.get_all_product()
    await call.message.answer(
            text='<b>Выберите товар: Можно поставить сюда продающий текст или условия какие-нибудь</b>',
            reply_markup=paginator(product_list=product_list)
    )


@router.callback_query(F.data == 'empty')
async def handle(call: CallbackQuery):
    await call.answer()
