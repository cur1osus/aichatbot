from aiogram import Router

from . import new_chat, start, end_chat

router = Router()

router.include_routers(
    end_chat.router,
    new_chat.router,
    start.router,
)
