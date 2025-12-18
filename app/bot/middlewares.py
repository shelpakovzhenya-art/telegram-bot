"""Bot middlewares."""
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from app.core.settings import Settings

logger = __import__("logging").getLogger(__name__)


class ChatFilterMiddleware(BaseMiddleware):
    """Middleware to filter messages by allowed chat IDs."""

    def __init__(self, settings: Settings) -> None:
        """Initialize middleware with settings."""
        self.settings = settings
        self.allowed_chat_ids = settings.get_allowed_chat_ids()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Filter events by chat ID."""
        # Get chat ID from event
        chat_id = None
        if isinstance(event, (Message, CallbackQuery)):
            if isinstance(event, Message):
                chat = event.chat
            else:
                chat = event.message.chat if event.message else None

            if chat:
                chat_id = chat.id

        # If no chat ID restrictions, allow all
        if self.allowed_chat_ids is None:
            return await handler(event, data)

        # If chat ID is not in allowed list, skip handler
        if chat_id is None or chat_id not in self.allowed_chat_ids:
            logger.debug(f"Event from chat {chat_id} filtered out")
            return None

        return await handler(event, data)

