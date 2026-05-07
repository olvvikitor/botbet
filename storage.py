import asyncio
import json
import os

_lock = asyncio.Lock()


def load_apostas(filepath="data/apostas.json"):
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


async def download_image(client, message, image_dir="data/images"):
    if message.media is None:
        return None
    os.makedirs(image_dir, exist_ok=True)
    ext = ".jpg"
    filename = f"{message.id}{ext}"
    filepath = os.path.join(image_dir, filename)
    await message.download_media(file=filepath)
    return filepath


async def save_aposta(data, filepath="data/apostas.json"):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    async with _lock:
        apostas = load_apostas(filepath)
        apostas.append(data)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(apostas, f, ensure_ascii=False, indent=2)
