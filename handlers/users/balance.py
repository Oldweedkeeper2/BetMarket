from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

router = Router()


@router.callback_query(F.data == 'top_up_balance')
async def handle(call: CallbackQuery, state: FSMContext):
    await call.answer(text='Этот функционал находится в разработке до тех пор, пока Глеб не договориться с фирмой\n')
    # data = await state.get_data()
    # cart: dict = data['cart']
    #
    # await clear_chat(data=data)
    # data['items_to_del'] = []
    # await state.update_data(data)
