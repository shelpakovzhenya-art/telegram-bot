"""Bot utility functions."""
from typing import Optional

from aiogram.types import Message


def get_topic_reply_kwargs(message: Message) -> dict:
    """
    Get kwargs for replying in the same topic if message is from a topic.
    
    Args:
        message: The message to check for topic
        
    Returns:
        Dictionary with message_thread_id if message is from a topic, empty dict otherwise
    """
    if message.message_thread_id is not None:
        return {"message_thread_id": message.message_thread_id}
    return {}


async def reply_in_topic(message: Message, text: str, **kwargs) -> None:
    """
    Reply to message in the same topic if message is from a topic.
    
    Args:
        message: The message to reply to
        text: Text to send
        **kwargs: Additional arguments for answer method
    """
    reply_kwargs = get_topic_reply_kwargs(message)
    reply_kwargs.update(kwargs)
    
    # Use answer with reply_to_message_id to maintain reply context
    if message.reply_to_message:
        reply_kwargs["reply_to_message_id"] = message.reply_to_message.message_id
    
    await message.answer(text, **reply_kwargs)

