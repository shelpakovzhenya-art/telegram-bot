"""Karma handlers."""
import re

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.core.settings import Settings
from app.db.session import get_db_session
from app.services.karma_service import KarmaService

router = Router()

# Keywords for karma
KARMA_KEYWORDS = [
    "спасибо",
    "спс",
    "спасиб",
    "спасибочки",
    "спасибо большое",
    "большое спасибо",
    "огромное спасибо",
    "спасибо огромное",
    "благодарю",
    "благодарствую",
    "благодарность",
    "благодарный",
    "thx",
    "thanks",
    "thank you",
    "thank",
    "thanks a lot",
    "thank you very much",
    "мерси",
    "дякую",
    "дякуємо",
    "дякую тобі",
    "респект",
    "респект и уважуха",
    "уважуха",
    "красавчик",
    "красава",
    "молодец",
    "молодчина",
]


def get_karma_router(settings: Settings) -> Router:
    """Get karma router with settings."""
    karma_service = KarmaService(settings)

    @router.message(Command("karma"))
    async def cmd_karma(message: Message) -> None:
        """Handle /karma command."""
        if not message.from_user or not message.chat:
            return

        target_user_id = message.from_user.id

        # Check if reply or mention
        if message.reply_to_message and message.reply_to_message.from_user:
            target_user_id = message.reply_to_message.from_user.id
        elif message.text:
            # Try to extract username from command
            parts = message.text.split()
            if len(parts) > 1:
                username = parts[1].lstrip("@")
                # Try to get user by username (simplified - would need bot.get_chat_member)
                # For now, just use current user
                pass

        async with get_db_session(settings) as session:
            karma = await karma_service.get_karma(
                session, target_user_id, message.chat.id
            )

        target_name = message.from_user.first_name or "пользователь"
        if message.reply_to_message and message.reply_to_message.from_user:
            target_name = (
                message.reply_to_message.from_user.first_name or "пользователь"
            )

        await message.answer(f"📊 Карма {target_name}: {karma}")

    @router.message(Command("top"))
    async def cmd_top(message: Message) -> None:
        """Handle /top command."""
        if not message.chat:
            return

        async with get_db_session(settings) as session:
            top_users = await karma_service.get_top_karma(
                session, message.chat.id, limit=10
            )

        if not top_users:
            await message.answer("📊 Пока нет данных о карме в этом чате.")
            return

        # Build top list
        top_text = "🏆 <b>Топ-10 по карме:</b>\n\n"
        for idx, (user_id, karma) in enumerate(top_users, 1):
            # Try to get user info
            try:
                member = await message.bot.get_chat_member(message.chat.id, user_id)
                user_name = member.user.first_name or f"User {user_id}"
            except Exception:
                user_name = f"User {user_id}"

            top_text += f"{idx}. {user_name}: {karma} 🎯\n"

        await message.answer(top_text)

    @router.message()
    async def handle_karma_message(message: Message) -> None:
        """Handle karma from messages."""
        if not message.from_user or not message.chat or not message.text:
            return

        # Skip bots
        if message.from_user.is_bot:
            return

        # Skip commands
        if message.text.startswith("/"):
            return

        text_lower = message.text.lower()

        # Check if message contains karma keywords
        has_keyword = any(keyword in text_lower for keyword in KARMA_KEYWORDS)
        if not has_keyword:
            return

        # Determine target user
        target_user_id = None

        # Check reply
        if message.reply_to_message and message.reply_to_message.from_user:
            target_user_id = message.reply_to_message.from_user.id
        else:
            # Check mentions
            mentions = re.findall(r"@(\w+)", message.text)
            if mentions:
                # Try to resolve username (simplified - would need proper user lookup)
                # For now, skip username mentions in non-reply messages
                return

        if not target_user_id:
            return

        # Can't give karma to yourself
        if target_user_id == message.from_user.id:
            await message.reply("❌ Нельзя начислить карму самому себе!")
            return

        # Can't give karma to bots
        try:
            target_member = await message.bot.get_chat_member(
                message.chat.id, target_user_id
            )
            if target_member.user.is_bot:
                return
        except Exception:
            return

        # Add karma
        async with get_db_session(settings) as session:
            success = await karma_service.add_karma(
                session,
                message.from_user.id,
                target_user_id,
                message.chat.id,
            )

        if success:
            target_name = (
                message.reply_to_message.from_user.first_name
                if message.reply_to_message
                else "пользователю"
            )
            await message.reply(f"✅ Карма начислена {target_name}! (+1)")

    return router

