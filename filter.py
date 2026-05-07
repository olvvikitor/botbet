from telethon import events


THUMBS_UP_EMOJIS = {"👍", "👍🏻", "👍🏼", "👍🏽", "👍🏾", "👍🏿"}


def is_user_thumbs_up(emoji):
    return emoji in THUMBS_UP_EMOJIS


def register_handler(client, group_name, callback):
    me = None

    @client.on(events.MessageReaction)
    async def handler(event):
        nonlocal me
        if me is None:
            me = await client.get_me()

        chat = await event.get_chat()
        if chat.title != group_name:
            return

        # Only process if the reaction came from our user
        if event.peer_id.user_id != me.id:
            return

        for reaction in event.reactions:
            if is_user_thumbs_up(reaction.emoticon):
                message = await client.get_messages(chat, ids=event.msg_id)
                if message:
                    await callback(client, message)

    return handler
