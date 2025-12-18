"""Moderation handlers."""
from datetime import timedelta

from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message

from app.core.settings import Settings
from app.db.session import get_db_session
from app.services.admin_service import can_restrict_members, check_message_from_admin
from app.services.warn_service import WarnService

router = Router()


def get_moderation_router(bot: Bot, settings: Settings) -> Router:
    """Get moderation router with bot and settings."""
    warn_service = WarnService(settings)

    @router.message(Command("warn"))
    async def cmd_warn(message: Message) -> None:
        """Handle /warn command."""
        if not message.from_user or not message.chat:
            return

        # Check admin rights
        if not await check_message_from_admin(message):
            await message.reply("❌ Эта команда доступна только администраторам!")
            return

        # Get target user
        target_user_id = None
        reason = None

        if message.reply_to_message and message.reply_to_message.from_user:
            target_user_id = message.reply_to_message.from_user.id
            # Extract reason from command text
            if message.text:
                parts = message.text.split(maxsplit=1)
                if len(parts) > 1:
                    reason = parts[1]
        elif message.text:
            parts = message.text.split(maxsplit=2)
            if len(parts) >= 2:
                username = parts[1].lstrip("@")
                # Try to resolve username (simplified)
                # For now, require reply
                await message.reply(
                    "❌ Ответьте на сообщение пользователя или укажите @username"
                )
                return
            if len(parts) > 2:
                reason = parts[2]

        if not target_user_id:
            await message.reply(
                "❌ Ответьте на сообщение пользователя или укажите @username"
            )
            return

        # Can't warn yourself
        if target_user_id == message.from_user.id:
            await message.reply("❌ Нельзя выдать предупреждение самому себе!")
            return

        # Add warning
        async with get_db_session(settings) as session:
            warn_count = await warn_service.add_warning(
                session,
                target_user_id,
                message.chat.id,
                message.from_user.id,
                reason,
            )

        target_name = "пользователю"
        if message.reply_to_message and message.reply_to_message.from_user:
            target_name = (
                message.reply_to_message.from_user.first_name or "пользователю"
            )

        response = f"⚠️ Предупреждение выдано {target_name}. Всего предупреждений: {warn_count}/{settings.WARN_LIMIT}"

        # Check if should mute
        if warn_count >= settings.WARN_LIMIT:
            # Try to mute user
            can_mute = await can_restrict_members(
                bot, message.chat.id, message.from_user.id
            )
            if can_mute:
                try:
                    mute_until = (
                        message.date + timedelta(hours=settings.MUTE_HOURS)
                    ).timestamp()
                    await bot.restrict_chat_member(
                        message.chat.id,
                        target_user_id,
                        until_date=int(mute_until),
                        permissions=None,  # No permissions = mute
                    )
                    response += f"\n🔇 Пользователь получил мут на {settings.MUTE_HOURS} часов."
                except Exception as e:
                    response += f"\n⚠️ Не удалось замутить пользователя: {e}"
            else:
                response += "\n⚠️ У бота нет прав для ограничения участников."

        await message.reply(response)

    @router.message(Command("warns"))
    async def cmd_warns(message: Message) -> None:
        """Handle /warns command."""
        if not message.from_user or not message.chat:
            return

        # Get target user
        target_user_id = None

        if message.reply_to_message and message.reply_to_message.from_user:
            target_user_id = message.reply_to_message.from_user.id
        elif message.text:
            parts = message.text.split()
            if len(parts) > 1:
                username = parts[1].lstrip("@")
                # Try to resolve username (simplified)
                # For now, require reply
                await message.reply("❌ Ответьте на сообщение пользователя")
                return
        else:
            target_user_id = message.from_user.id

        if not target_user_id:
            target_user_id = message.from_user.id

        async with get_db_session(settings) as session:
            warn_count = await warn_service.get_warn_count(
                session, target_user_id, message.chat.id
            )

        target_name = message.from_user.first_name or "пользователь"
        if message.reply_to_message and message.reply_to_message.from_user:
            target_name = (
                message.reply_to_message.from_user.first_name or "пользователь"
            )

        await message.reply(
            f"⚠️ У {target_name} предупреждений: {warn_count}/{settings.WARN_LIMIT}"
        )

    @router.message(Command("unwarn"))
    async def cmd_unwarn(message: Message) -> None:
        """Handle /unwarn command."""
        if not message.from_user or not message.chat:
            return

        # Check admin rights
        if not await check_message_from_admin(message):
            await message.reply("❌ Эта команда доступна только администраторам!")
            return

        # Get target user
        target_user_id = None

        if message.reply_to_message and message.reply_to_message.from_user:
            target_user_id = message.reply_to_message.from_user.id
        elif message.text:
            parts = message.text.split()
            if len(parts) > 1:
                username = parts[1].lstrip("@")
                # Try to resolve username (simplified)
                # For now, require reply
                await message.reply("❌ Ответьте на сообщение пользователя")
                return

        if not target_user_id:
            await message.reply("❌ Ответьте на сообщение пользователя")
            return

        # Remove warning
        async with get_db_session(settings) as session:
            warn_count = await warn_service.remove_warning(
                session, target_user_id, message.chat.id
            )

        target_name = "пользователю"
        if message.reply_to_message and message.reply_to_message.from_user:
            target_name = (
                message.reply_to_message.from_user.first_name or "пользователю"
            )

        await message.reply(
            f"✅ Предупреждение снято с {target_name}. Осталось предупреждений: {warn_count}/{settings.WARN_LIMIT}"
        )

    return router

