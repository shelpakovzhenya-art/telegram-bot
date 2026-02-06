"""Greeting handlers."""
from datetime import datetime, timedelta

from aiogram import Router
from aiogram.filters import ChatMemberUpdatedFilter, KICKED, LEFT, MEMBER, RESTRICTED
from aiogram.types import ChatMemberUpdated, Message

from app.core.settings import Settings
from app.db.models import Greeting
from app.db.session import get_db_session

router = Router()


def get_greeting_router(settings: Settings) -> Router:
    """Get greeting router with settings."""
    cooldown_minutes = settings.GREETING_COOLDOWN_MINUTES
    greeting_chat_ids = settings.get_greeting_chat_ids()

    @router.chat_member(ChatMemberUpdatedFilter(member_status_changed=(LEFT | KICKED) >> MEMBER))
    async def greet_new_member(event: ChatMemberUpdated) -> None:
        """Greet new member."""
        if not event.new_chat_member.user:
            return

        user = event.new_chat_member.user
        chat = event.chat

        # Restrict greetings to configured chats only
        if greeting_chat_ids is not None and chat.id not in greeting_chat_ids:
            return

        # Skip bots
        if user.is_bot:
            return

        # Check cooldown
        async with get_db_session(settings) as session:
            cooldown_time = datetime.utcnow() - timedelta(minutes=cooldown_minutes)
            from sqlalchemy import select

            stmt = select(Greeting).where(
                Greeting.user_id == user.id,
                Greeting.chat_id == chat.id,
                Greeting.created_at >= cooldown_time,
            )

            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                return  # Cooldown active

            # Add greeting record
            greeting = Greeting(user_id=user.id, chat_id=chat.id)
            session.add(greeting)
            await session.commit()

        # Send greeting
        greeting_text = f"👋 Добро пожаловать, {user.first_name or 'пользователь'}!"
        if user.username:
            greeting_text += f" (@{user.username})"

        # Send greeting message
        await event.bot.send_message(chat.id, greeting_text)

    return router

