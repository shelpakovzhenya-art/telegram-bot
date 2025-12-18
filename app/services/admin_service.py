"""Admin service for checking admin rights."""
from aiogram import Bot
from aiogram.types import ChatMemberAdministrator, ChatMemberOwner, Message


async def is_admin(bot: Bot, chat_id: int, user_id: int) -> bool:
    """Check if user is admin in chat."""
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return isinstance(member, (ChatMemberAdministrator, ChatMemberOwner))
    except Exception:
        return False


async def can_restrict_members(bot: Bot, chat_id: int, user_id: int) -> bool:
    """Check if user can restrict members in chat."""
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        if isinstance(member, ChatMemberOwner):
            return True
        if isinstance(member, ChatMemberAdministrator):
            return member.can_restrict_members or False
        return False
    except Exception:
        return False


async def check_message_from_admin(message: Message) -> bool:
    """Check if message is from admin."""
    if not message.from_user:
        return False
    if not message.chat:
        return False

    return await is_admin(message.bot, message.chat.id, message.from_user.id)

