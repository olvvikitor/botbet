from datetime import datetime


async def scan_messages(client, group_name, callback):
    chat = await client.get_entity(int(group_name))
    hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    count = 0
    async for message in client.iter_messages(chat, offset_date=hoje, reverse=True):
        await callback(client, message)
        count += 1

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Scan concluido: {count} mensagens processadas.")
