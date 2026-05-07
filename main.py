import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

from client import create_client, start_client
from filter import register_handler
from extractor import extract_text_info
from vision import analyze_image
from storage import save_aposta, download_image

load_dotenv()

GROUP_NAME = os.environ["TELEGRAM_GROUP_NAME"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]


async def process_message(client, message):
    now = datetime.now()
    text = message.text or ""

    info = extract_text_info(text)

    image_path = await download_image(client, message)

    visao = {"evento": None, "mercado": None, "odd": None}
    if image_path:
        visao = await analyze_image(image_path, OPENAI_API_KEY)

    aposta = {
        "id": message.id,
        "data": now.strftime("%Y-%m-%d"),
        "hora": now.strftime("%H:%M"),
        "texto_original": text,
        "evento": visao["evento"],
        "mercado": visao["mercado"],
        "odd": visao["odd"],
        "porcentagem_banca": info["porcentagem_banca"],
        "link_casa": info["link_casa"],
        "imagem_path": image_path,
        "mensagem_link": f"https://t.me/c/{message.peer_id.channel_id}/{message.id}",
    }

    await save_aposta(aposta)
    print(f"[{now.strftime('%H:%M:%S')}] Aposta salva: {aposta['evento']} | {aposta['porcentagem_banca']}%")


async def main():
    client = create_client()
    await start_client(client)
    register_handler(client, GROUP_NAME, process_message)
    print(f"Ouvindo reacoes no grupo: {GROUP_NAME}")
    print("Pressione Ctrl+C para parar.")
    await client.run_until_disconnected()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nEncerrado.")
        sys.exit(0)
