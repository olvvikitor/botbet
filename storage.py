import asyncio
import csv
import json
import os
from urllib.parse import urlparse

_lock = asyncio.Lock()

CSV_HEADERS = [
    "bet_date",
    "bookmaker",
    "event_name",
    "market",
    "sport",
    "tipster",
    "units_bet",
    "odds",
    "result",
]


def load_apostas(filepath="data/apostas.json"):
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read().strip()

    if not content:
        return []

    try:
        apostas = json.loads(content)
    except json.JSONDecodeError:
        return []

    return apostas if isinstance(apostas, list) else []


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


def clear_csv(csv_filepath="data/apostas.csv"):
    directory = os.path.dirname(csv_filepath)
    if directory:
        os.makedirs(directory, exist_ok=True)

    with open(csv_filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADERS)


def export_csv(json_filepath="data/apostas.json", csv_filepath="data/apostas.csv"):
    apostas = load_apostas(json_filepath)
    if not apostas:
        print("Nenhuma aposta para exportar.")
        return

    with open(csv_filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADERS)

        for a in apostas:
            data = a.get("data", "")
            if data and "-" in data:
                parts = data.split("-")
                data = f"{parts[2]}/{parts[1]}/{parts[0]}"

            link = a.get("link_casa") or ""
            bookmaker = ""
            if link:
                try:
                    domain = urlparse(link).netloc.replace("www.", "")
                    bookmaker = domain.split(".")[0].capitalize()
                except Exception:
                    pass

            writer.writerow([
                data,
                bookmaker,
                a.get("evento") or "",
                a.get("mercado") or "",
                "",
                "",
                "",
                a.get("odd") or "",
                a.get("resultado") or "pending",
            ])

    print(f"CSV exportado: {csv_filepath}")
