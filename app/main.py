"""Main entry point for the bot."""
import asyncio
import logging
import sys

from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession

from app.bot.dispatcher import create_bot, setup_dispatcher
from app.core.settings import Settings
from app.db.base import init_db

# Keep-alive для Replit (чтобы не выключался)
# Запускаем ДО настройки логирования, чтобы сервер успел стартовать
try:
    from keep_alive import keep_alive
    keep_alive()
    import time
    time.sleep(1)  # Даем время серверу запуститься
except ImportError:
    pass  # Если файла нет, просто пропускаем
except Exception as e:
    print(f"Warning: Keep-alive failed to start: {e}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


async def main() -> None:
    """Main function to start the bot."""
    try:
        # Load settings
        settings = Settings()
        logger.info("Settings loaded")

        # Initialize database
        await init_db(settings)
        logger.info("Database initialized")

        # Create bot
        bot = create_bot(settings)
        logger.info("Bot created")

        # Setup dispatcher
        dp = setup_dispatcher(bot, settings)
        logger.info("Dispatcher configured")

        # Start polling
        logger.info("Starting bot...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

    except Exception as e:
        logger.error(f"Error starting bot: {e}", exc_info=True)
        raise
    finally:
        if "bot" in locals():
            try:
                session: AiohttpSession = bot.session
                if hasattr(session, "close"):
                    await session.close()
            except Exception:
                pass
        logger.info("Bot stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

