"""Bot dispatcher setup."""
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.core.settings import Settings
from app.handlers import greetings, karma, moderation, start_help
from app.bot.middlewares import ChatFilterMiddleware

logger = logging.getLogger(__name__)


def setup_dispatcher(bot: Bot, settings: Settings) -> Dispatcher:
    """Setup and configure dispatcher."""
    dp = Dispatcher()

    # Register middlewares
    dp.message.middleware(ChatFilterMiddleware(settings))
    dp.callback_query.middleware(ChatFilterMiddleware(settings))

    # Register routers (order matters - commands first, then general handlers)
    dp.include_router(start_help.router)
    dp.include_router(moderation.get_moderation_router(bot, settings))  # Commands first
    dp.include_router(greetings.get_greeting_router(settings))
    dp.include_router(karma.get_karma_router(settings))  # General message handler last

    logger.info("Dispatcher configured")
    return dp


def create_bot(settings: Settings) -> Bot:
    """Create bot instance."""
    return Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

