import json
import os


def load_apostas(filepath="data/apostas.json"):
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_aposta(data, filepath="data/apostas.json"):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    apostas = load_apostas(filepath)
    apostas.append(data)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(apostas, f, ensure_ascii=False, indent=2)
