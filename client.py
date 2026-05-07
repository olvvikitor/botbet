import os
from telethon import TelegramClient
from dotenv import load_dotenv

load_dotenv()


def create_client():
    api_id = int(os.environ["TELEGRAM_API_ID"])
    api_hash = os.environ["TELEGRAM_API_HASH"]
    return TelegramClient("bet-scraper-session", api_id, api_hash)


async def start_client(client):
    await client.start(phone=os.environ["TELEGRAM_PHONE"])
    return client
