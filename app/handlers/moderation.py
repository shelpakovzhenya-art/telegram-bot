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
        """Handle /warn command. Usage: /warn [reply]"""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"/warn command received from user {message.from_user.id if message.from_user else 'unknown'} in chat {message.chat.id if message.chat else 'unknown'}")
        
        if not message.from_user or not message.chat:
            logger.warning("No from_user or chat in message")
            return

        # Check admin rights
        try:
            is_admin = await check_message_from_admin(message)
            logger.info(f"Admin check result: {is_admin}")
            if not is_admin:
                await message.reply("❌ Эта команда доступна только администраторам!")
                return
        except Exception as e:
            logger.error(f"Error checking admin: {e}", exc_info=True)
            await message.reply("❌ Ошибка при проверке прав администратора.")
            return

        # Must have reply
        if not message.reply_to_message:
            await message.reply(
                "❌ Ответьте на сообщение пользователя, которому хотите выдать предупреждение.\n"
                "Использование: /warn [ответ на сообщение]"
            )
            return

        if not message.reply_to_message.from_user:
            await message.reply("❌ Не удалось определить пользователя.")
            return

        target_user_id = message.reply_to_message.from_user.id
        target_name = (
            message.reply_to_message.from_user.first_name
            or message.reply_to_message.from_user.username
            or "пользователь"
        )

        # Can't warn yourself
        if target_user_id == message.from_user.id:
            await message.reply("❌ Нельзя выдать предупреждение самому себе!")
            return

        # Can't warn bots
        if message.reply_to_message.from_user.is_bot:
            await message.reply("❌ Нельзя выдать предупреждение боту!")
            return

        # Add warning
        try:
            async with get_db_session(settings) as session:
                warn_count = await warn_service.add_warning(
                    session,
                    target_user_id,
                    message.chat.id,
                    message.from_user.id,
                    None,  # No reason
                )

            # Beautiful response message
            remaining = settings.WARN_LIMIT - warn_count
            if remaining > 0:
                response = (
                    f"⚠️ <b>Предупреждение выдано</b>\n\n"
                    f"👤 Пользователь: {target_name}\n"
                    f"📊 У вас <b>{warn_count} из {settings.WARN_LIMIT}</b> предупреждений до мута.\n"
                    f"⚠️ Осталось предупреждений: <b>{remaining}</b>\n\n"
                    f"💬 Пожалуйста, соблюдайте правила группы."
                )
            else:
                # Reached limit - will be muted
                response = (
                    f"⚠️ <b>Предупреждение выдано</b>\n\n"
                    f"👤 Пользователь: {target_name}\n"
                    f"📊 У вас <b>{warn_count} из {settings.WARN_LIMIT}</b> предупреждений.\n\n"
                    f"🔇 Лимит предупреждений достигнут!"
                )

            # Check if should mute
            if warn_count >= settings.WARN_LIMIT:
                # Try to mute user
                can_mute = await can_restrict_members(
                    bot, message.chat.id, message.from_user.id
                )
                if can_mute:
                    try:
                        from aiogram.types import ChatPermissions
                        
                        # Create permissions that restrict sending messages
                        mute_permissions = ChatPermissions(
                            can_send_messages=False,  # Cannot send messages
                            can_send_audios=False,
                            can_send_documents=False,
                            can_send_photos=False,
                            can_send_videos=False,
                            can_send_video_notes=False,
                            can_send_voice_notes=False,
                            can_send_polls=False,
                            can_send_other_messages=False,
                            can_add_web_page_previews=False,
                            can_change_info=False,
                            can_invite_users=False,
                            can_pin_messages=False,
                        )
                        
                        mute_until = (
                            message.date + timedelta(hours=settings.MUTE_HOURS)
                        ).timestamp()
                        await bot.restrict_chat_member(
                            message.chat.id,
                            target_user_id,
                            until_date=int(mute_until),
                            permissions=mute_permissions,
                        )
                        response += f"\n\n🔇 Пользователь получил мут на {settings.MUTE_HOURS} часов."
                    except Exception as e:
                        logger.error(f"Failed to mute user: {e}", exc_info=True)
                        response += f"\n\n⚠️ Не удалось замутить пользователя: {str(e)}"
                else:
                    response += "\n\n⚠️ У бота нет прав для ограничения участников."

            await message.reply(response)
        except Exception as e:
            logger.error(f"Error in /warn: {e}", exc_info=True)
            await message.reply(f"❌ Ошибка при выдаче предупреждения: {str(e)}")

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

    @router.message(Command("mute"))
    async def cmd_mute(message: Message) -> None:
        """Handle /mute command. Usage: /mute [reply] [hours] or /mute @username [hours]"""
        if not message.from_user or not message.chat:
            return

        # Check admin rights
        if not await check_message_from_admin(message):
            await message.reply("❌ Эта команда доступна только администраторам!")
            return

        # Check if bot can restrict members
        can_mute = await can_restrict_members(
            bot, message.chat.id, message.from_user.id
        )
        if not can_mute:
            await message.reply("❌ У бота нет прав для ограничения участников!")
            return

        # Parse command arguments
        target_user_id = None
        target_name = None
        mute_hours = 1  # Default 1 hour

        # Check reply first
        if message.reply_to_message and message.reply_to_message.from_user:
            target_user_id = message.reply_to_message.from_user.id
            target_name = (
                message.reply_to_message.from_user.first_name
                or message.reply_to_message.from_user.username
                or "пользователь"
            )
            # Parse hours from command text
            if message.text:
                parts = message.text.split()
                if len(parts) > 1:
                    try:
                        mute_hours = int(parts[1])
                        if mute_hours < 1:
                            mute_hours = 1
                        elif mute_hours > 24:
                            mute_hours = 24
                    except ValueError:
                        mute_hours = 1  # Default if invalid
        # Check username in command
        elif message.text:
            parts = message.text.split()
            if len(parts) >= 2:
                username = parts[1].lstrip("@")
                # Try to find user by username
                try:
                    # For now, require reply - username lookup would need more complex logic
                    await message.reply(
                        "❌ Ответьте на сообщение пользователя.\n"
                        "Использование: /mute [reply] [часы 1-24]"
                    )
                    return
                except Exception:
                    pass
            if len(parts) > 2:
                try:
                    mute_hours = int(parts[2])
                    if mute_hours < 1:
                        mute_hours = 1
                    elif mute_hours > 24:
                        mute_hours = 24
                except ValueError:
                    mute_hours = 1

        if not target_user_id:
            await message.reply(
                "❌ Ответьте на сообщение пользователя.\n"
                "Использование: /mute [reply] [часы 1-24]"
            )
            return

        # Can't mute yourself
        if target_user_id == message.from_user.id:
            await message.reply("❌ Нельзя замутить самого себя!")
            return

        # Can't mute bots
        try:
            target_member = await bot.get_chat_member(message.chat.id, target_user_id)
            if target_member.user.is_bot:
                await message.reply("❌ Нельзя замутить бота!")
                return
        except Exception:
            pass

        # Mute user - create ChatPermissions with no send messages permission
        try:
            from aiogram.types import ChatPermissions
            from datetime import datetime

            # Create permissions that restrict sending messages
            mute_permissions = ChatPermissions(
                can_send_messages=False,  # Cannot send messages
                can_send_audios=False,
                can_send_documents=False,
                can_send_photos=False,
                can_send_videos=False,
                can_send_video_notes=False,
                can_send_voice_notes=False,
                can_send_polls=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False,
            )

            mute_until = (message.date + timedelta(hours=mute_hours)).timestamp()
            await bot.restrict_chat_member(
                message.chat.id,
                target_user_id,
                until_date=int(mute_until),
                permissions=mute_permissions,
            )

            hours_text = (
                "час"
                if mute_hours == 1
                else "часа"
                if 2 <= mute_hours <= 4
                else "часов"
            )

            response = (
                f"🔇 <b>Пользователь замучен</b>\n\n"
                f"👤 Пользователь: {target_name}\n"
                f"⏰ Время мута: <b>{mute_hours} {hours_text}</b>\n\n"
                f"⏳ Пользователь не сможет писать сообщения до окончания мута."
            )

            await message.reply(response)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error muting user: {e}", exc_info=True)
            await message.reply(f"❌ Не удалось замутить пользователя: {str(e)}")

    @router.message(Command("unmute"))
    async def cmd_unmute(message: Message) -> None:
        """Handle /unmute command. Usage: /unmute [reply]"""
        if not message.from_user or not message.chat:
            return

        # Check admin rights
        if not await check_message_from_admin(message):
            await message.reply("❌ Эта команда доступна только администраторам!")
            return

        # Check if bot can restrict members
        can_mute = await can_restrict_members(
            bot, message.chat.id, message.from_user.id
        )
        if not can_mute:
            await message.reply("❌ У бота нет прав для ограничения участников!")
            return

        # Get target user
        target_user_id = None

        if message.reply_to_message and message.reply_to_message.from_user:
            target_user_id = message.reply_to_message.from_user.id
        elif message.text:
            parts = message.text.split()
            if len(parts) > 1:
                username = parts[1].lstrip("@")
                await message.reply("❌ Ответьте на сообщение пользователя")
                return

        if not target_user_id:
            await message.reply("❌ Ответьте на сообщение пользователя")
            return

        # Unmute user (restore permissions)
        try:
            from aiogram.types import ChatPermissions

            # Restore all permissions
            permissions = ChatPermissions(
                can_send_messages=True,
                can_send_audios=True,
                can_send_documents=True,
                can_send_photos=True,
                can_send_videos=True,
                can_send_video_notes=True,
                can_send_voice_notes=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_change_info=True,
                can_invite_users=True,
                can_pin_messages=True,
            )

            await bot.restrict_chat_member(
                message.chat.id,
                target_user_id,
                permissions=permissions,
            )

            target_name = "пользователю"
            if message.reply_to_message and message.reply_to_message.from_user:
                target_name = (
                    message.reply_to_message.from_user.first_name or "пользователю"
                )

            await message.reply(f"✅ Мут снят с {target_name}.")
        except Exception as e:
            await message.reply(f"❌ Не удалось снять мут: {e}")

    return router

