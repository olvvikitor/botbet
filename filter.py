from telethon import events


THUMBS_UP_EMOJIS = {"👍", "👍🏻", "👍🏼", "👍🏽", "👍🏾", "👍🏿"}


def is_user_thumbs_up(emoji):
    return emoji in THUMBS_UP_EMOJIS


def register_handler(client, group_name, callback):
    @client.on(events.MessageReaction)
    async def handler(event):
        chat = await event.get_chat()
        if chat.title != group_name:
            return

        for reaction in event.reactions:
            if is_user_thumbs_up(reaction.emoticon):
                message = await client.get_messages(chat, ids=event.msg_id)
                if message:
                    await callback(client, message)

    return handler
