from typing import Any

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from keyboards.inline.start import get_start_keyboard
from utils.misc.clear_chat import clear_chat

router = Router()


@router.callback_query(F.data == "help")
async def handle(call: CallbackQuery, state: FSMContext) -> Any:
    msg = await call.message.answer(
            text="<b>ТЕКСТ ДЛЯ ПОМОЩИ ЗАБЛУБИВШИМСЯ ИЛИ ДЕБИЛАМ\n\n</b>"
                 f"<b>Лучше всего поставить также контакты менеджера @Oldweedkeeper</b>",
            reply_markup=get_start_keyboard()
    )
    data = await state.get_data()
    await clear_chat(data=data, chat_id=int(call.from_user.id))
    data['items_to_del'].append(msg)
    await state.update_data(data)
