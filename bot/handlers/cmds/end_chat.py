from __future__ import annotations

import logging
from typing import TYPE_CHECKING


from aiogram import Router
from aiogram.filters import Command
from bot.states import UserState

from bot.db.models import UserDB

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext
    from aiogram.types import Message
    from sqlalchemy.ext.asyncio import AsyncSession


router = Router()
logger = logging.getLogger(__name__)


@router.message(UserState.enter_question, Command(commands=["end_chat"]))
async def end_chat(
    message: Message,
    user: UserDB,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    await message.answer("До свидания!")
    await state.clear()
