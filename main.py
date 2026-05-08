import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

from client import create_client, start_client
from filter import scan_messages
from extractor import extract_text_info
from vision import analyze_image
from storage import save_aposta, download_image, export_csv

load_dotenv()

GROUP_NAME = os.environ["TELEGRAM_GROUP_NAME"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]


async def process_message(client, message):
    now = datetime.now()
    text = message.text or ""

    info = extract_text_info(text)

    if "❌" in text:
        resultado = "red"
    elif "✅" in text:
        resultado = "green"
    else:
        resultado = "pending"

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
        "mensagem_link": f"https://t.me/c/{message.peer_id.chat_id}/{message.id}",
        "resultado": resultado,
    }

    await save_aposta(aposta)
    print(f"[{now.strftime('%H:%M:%S')}] Aposta salva: {aposta['evento']} | {aposta['porcentagem_banca']}%")


async def main():
    client = create_client()

    await start_client(client)
    await scan_messages(client, GROUP_NAME, process_message)
    export_csv()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nEncerrado.")
        sys.exit(0)
