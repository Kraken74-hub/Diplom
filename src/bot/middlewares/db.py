from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from src.db.session import async_session

class DbSessionMiddleware(BaseMiddleware):
    """
    Middleware, который автоматически создает асинхронную сессию БД
    для каждого входящего сообщения/кнопки и передает ее в аргументы хэндлера.
    """
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        async with async_session() as session:
            data["session"] = session
            return await handler(event, data)