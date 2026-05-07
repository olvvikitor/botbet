from telethon import events
from telethon.tl.types import UpdateMessageReactions, ReactionEmoji


THUMBS_UP_EMOJIS = {"👍", "👍🏻", "👍🏼", "👍🏽", "👍🏾", "👍🏿"}


def is_user_thumbs_up(emoji):
    return emoji in THUMBS_UP_EMOJIS


def register_handler(client, group_name, callback):
    @client.on(events.Raw)
    async def handler(update):
        if not isinstance(update, UpdateMessageReactions):
            return

        chat = await client.get_entity(update.peer)
        if chat.title != group_name:
            return

        reactions = update.reactions
        if not reactions.recent_reactions:
            return

        for r in reactions.recent_reactions:
            if r.my and isinstance(r.reaction, ReactionEmoji):
                if is_user_thumbs_up(r.reaction.emoticon):
                    message = await client.get_messages(chat, ids=update.msg_id)
                    if message:
                        await callback(client, message)
                    return

    return handler
