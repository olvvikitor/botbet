# Telegram Bet Scraper — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Script contínuo que ouve reações 👍 do usuário em um grupo Telegram, extrai dados da aposta via GPT Vision (imagem) + regex (texto), e salva em JSON.

**Architecture:** 6 módulos Python com responsabilidades isoladas — storage (JSON+imagens), extractor (regex), vision (GPT Vision), client (Telethon), filter (handler de reações), main (entrypoint). Pipeline: reação detectada → download mídia/texto → extração paralela (vision + regex) → JSON.

**Tech Stack:** Python 3.10+, Telethon, OpenAI SDK, python-dotenv, pytest

---

## File Structure

```
bet-scraper/
├── .env.example           # Template de credenciais
├── main.py                # Entrypoint: wiring + start
├── client.py              # Telethon: create, connect, reconnect
├── filter.py              # Reaction handler: detect 👍, dispatch
├── extractor.py           # Regex: porcentagem, link casa
├── vision.py              # GPT Vision: evento, mercado, odd
├── storage.py             # JSON append + image download
├── data/
│   └── images/
├── tests/
│   ├── test_extractor.py
│   ├── test_storage.py
│   ├── test_vision.py
│   └── test_filter.py
├── requirements.txt
└── README.md
```

**Interfaces:**

| Module | Key Function | Input | Output |
|--------|-------------|-------|--------|
| `storage` | `save_aposta(data)` | `dict` | `None` |
| `storage` | `download_image(client, msg)` | Telethon client, message | `str \| None` (path) |
| `storage` | `load_apostas()` | — | `list[dict]` |
| `extractor` | `extract_text_info(text)` | `str` | `{"porcentagem_banca": float, "link_casa": str}` |
| `vision` | `analyze_image(path, api_key)` | `str, str` | `{"evento": str, "mercado": str, "odd": float \| None}` |
| `client` | `create_client(id, hash)` | `int, str` | `TelegramClient` |
| `filter` | `register_handler(client, group, cb)` | client, str, callback | `None` |

---

### Task 1: Project Setup

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`

- [ ] **Step 1: Write requirements.txt**

```bash
echo "telethon>=1.36" > requirements.txt
echo "openai>=1.0" >> requirements.txt
echo "python-dotenv>=1.0" >> requirements.txt
echo "pytest>=8.0" >> requirements.txt
echo "pytest-asyncio>=0.24" >> requirements.txt
```

- [ ] **Step 2: Write .env.example**

```bash
echo "TELEGRAM_API_ID=your_api_id" > .env.example
echo "TELEGRAM_API_HASH=your_api_hash" >> .env.example
echo "TELEGRAM_PHONE=+5511999999999" >> .env.example
echo "TELEGRAM_GROUP_NAME=Nome do Grupo" >> .env.example
echo "OPENAI_API_KEY=sk-your-key" >> .env.example
```

- [ ] **Step 3: Create directories**

```bash
mkdir -p tests data/images
```

- [ ] **Step 4: Install dependencies**

```bash
pip install -r requirements.txt
```

- [ ] **Step 5: Write .gitignore**

```bash
echo ".env" > .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo ".pytest_cache/" >> .gitignore
echo "data/apostas.json" >> .gitignore
echo "data/images/" >> .gitignore
```

- [ ] **Step 6: Commit**

```bash
git add requirements.txt .env.example .gitignore
git commit -m "chore: project setup with dependencies and config template"
```

---

### Task 2: Storage Module

**Files:**
- Create: `storage.py`
- Create: `tests/test_storage.py`

- [ ] **Step 1: Write failing test for load_apostas**

Create `tests/test_storage.py`:

```python
import json
import tempfile
import os
from storage import load_apostas, save_aposta


def test_load_apostas_empty_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("[]")
        tmp = f.name
    try:
        result = load_apostas(tmp)
        assert result == []
    finally:
        os.unlink(tmp)


def test_save_and_load():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("[]")
        tmp = f.name
    try:
        save_aposta({"id": 1, "evento": "FLA x PAL"}, tmp)
        result = load_apostas(tmp)
        assert len(result) == 1
        assert result[0]["id"] == 1
    finally:
        os.unlink(tmp)


def test_save_appends_to_existing():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump([{"id": 1}], f)
        tmp = f.name
    try:
        save_aposta({"id": 2}, tmp)
        result = load_apostas(tmp)
        assert len(result) == 2
        assert result[1]["id"] == 2
    finally:
        os.unlink(tmp)
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
python -m pytest tests/test_storage.py -v
```

Expected: FAIL — module not found.

- [ ] **Step 3: Implement storage.py**

```python
import json
import os
from datetime import datetime


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
```

- [ ] **Step 4: Run tests, verify pass**

```bash
python -m pytest tests/test_storage.py -v
```

Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add storage.py tests/test_storage.py
git commit -m "feat: add storage module with JSON save/load"
```

---

### Task 3: Storage — Image Download

**Files:**
- Modify: `storage.py`
- Modify: `tests/test_storage.py`

- [ ] **Step 1: Add failing async test for download_image**

Add to `tests/test_storage.py`:

```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from storage import download_image


@pytest.mark.asyncio
async def test_download_image_returns_path():
    mock_msg = AsyncMock()
    mock_msg.download_media = AsyncMock()
    mock_msg.id = 12345

    with patch("storage.os.makedirs"):
        path = await download_image(None, mock_msg, "data/images")
        assert path is not None
        assert "12345" in path
        mock_msg.download_media.assert_called_once()


@pytest.mark.asyncio
async def test_download_image_no_media_returns_none():
    mock_msg = AsyncMock()
    mock_msg.media = None

    path = await download_image(None, mock_msg, "data/images")
    assert path is None
```

- [ ] **Step 2: Run tests, verify fail**

```bash
python -m pytest tests/test_storage.py::test_download_image_returns_path -v
```

Expected: FAIL — `download_image` not defined.

- [ ] **Step 3: Implement download_image in storage.py**

Add to `storage.py`:

```python
import os


async def download_image(client, message, image_dir="data/images"):
    if message.media is None:
        return None
    os.makedirs(image_dir, exist_ok=True)
    ext = ".jpg"
    filename = f"{message.id}{ext}"
    filepath = os.path.join(image_dir, filename)
    await message.download_media(file=filepath)
    return filepath
```

- [ ] **Step 4: Run all storage tests**

```bash
python -m pytest tests/test_storage.py -v
```

Expected: PASS (5 tests).

- [ ] **Step 5: Commit**

```bash
git add storage.py tests/test_storage.py
git commit -m "feat: add image download to storage module"
```

---

### Task 4: Extractor Module (Regex)

**Files:**
- Create: `extractor.py`
- Create: `tests/test_extractor.py`

- [ ] **Step 1: Write failing test**

Create `tests/test_extractor.py`:

```python
from extractor import extract_text_info


def test_extract_percentage_and_link():
    text = "Aposta do dia - 2% da unidade - https://bet365.com/apoio"
    result = extract_text_info(text)
    assert result["porcentagem_banca"] == 2.0
    assert result["link_casa"] == "https://bet365.com/apoio"


def test_extract_percentage_with_comma():
    text = "1,5% da banca - stake.com"
    result = extract_text_info(text)
    assert result["porcentagem_banca"] == 1.5


def test_extract_no_percentage():
    text = "Aposta sem porcentagem"
    result = extract_text_info(text)
    assert result["porcentagem_banca"] is None


def test_extract_no_link():
    text = "3% da unidade aposta segura"
    result = extract_text_info(text)
    assert result["porcentagem_banca"] == 3.0
    assert result["link_casa"] is None


def test_extract_multiple_urls_picks_first():
    text = "2% - https://bet365.com e https://1xbet.com"
    result = extract_text_info(text)
    assert result["link_casa"] == "https://bet365.com"


def test_extract_percentage_with_dot():
    text = "aposta 2.5% da unidade"
    result = extract_text_info(text)
    assert result["porcentagem_banca"] == 2.5
```

- [ ] **Step 2: Run tests, verify fail**

```bash
python -m pytest tests/test_extractor.py -v
```

Expected: FAIL — module not found.

- [ ] **Step 3: Implement extractor.py**

```python
import re


def extract_text_info(text):
    pct_pattern = r"(\d+(?:[.,]\d+)?)\s*%"
    pct_match = re.search(pct_pattern, text)
    porcentagem = float(pct_match.group(1).replace(",", ".")) if pct_match else None

    url_pattern = r"https?://[^\s]+"
    url_match = re.search(url_pattern, text)
    link = url_match.group(0) if url_match else None

    return {
        "porcentagem_banca": porcentagem,
        "link_casa": link,
    }
```

- [ ] **Step 4: Run tests, verify pass**

```bash
python -m pytest tests/test_extractor.py -v
```

Expected: PASS (6 tests).

- [ ] **Step 5: Commit**

```bash
git add extractor.py tests/test_extractor.py
git commit -m "feat: add extractor module with regex for percentage and link"
```

---

### Task 5: Vision Module (GPT Vision)

**Files:**
- Create: `vision.py`
- Create: `tests/test_vision.py`

- [ ] **Step 1: Write failing test**

Create `tests/test_vision.py`:

```python
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from vision import analyze_image


@pytest.mark.asyncio
async def test_analyze_image_returns_structured_data():
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content='{"evento": "Flamengo x Palmeiras", "mercado": "Ambos marcam - Sim", "odd": 1.85}'
            )
        )
    ]

    with patch("vision.AsyncOpenAI") as mock_client_class:
        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client

        result = await analyze_image("test.jpg", "fake-key")

        assert result["evento"] == "Flamengo x Palmeiras"
        assert result["mercado"] == "Ambos marcam - Sim"
        assert result["odd"] == 1.85


@pytest.mark.asyncio
async def test_analyze_image_handles_api_error():
    with patch("vision.AsyncOpenAI") as mock_client_class:
        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock(
            side_effect=Exception("API error")
        )
        mock_client_class.return_value = mock_client

        result = await analyze_image("test.jpg", "fake-key")

        assert result["evento"] is None
        assert result["mercado"] is None
        assert result["odd"] is None
```

- [ ] **Step 2: Run tests, verify fail**

```bash
python -m pytest tests/test_vision.py -v
```

Expected: FAIL — module not found.

- [ ] **Step 3: Implement vision.py**

```python
import base64
import json
from openai import AsyncOpenAI


SYSTEM_PROMPT = """Extraia desta imagem de bilhete de aposta as seguintes informacoes:

- evento: o nome do evento esportivo (ex: "Flamengo x Palmeiras")
- mercado: o tipo de mercado apostado (ex: "Ambos marcam - Sim", "Over 2.5 gols")
- odd: a odd/cotacao do bilhete (numero decimal, ex: 1.85)

Retorne APENAS um objeto JSON com os campos "evento", "mercado", "odd".
Se nao conseguir identificar algum campo, use null.
Exemplo: {"evento": "Flamengo x Palmeiras", "mercado": "Ambos marcam - Sim", "odd": 1.85}"""


async def analyze_image(image_path, api_key):
    client = AsyncOpenAI(api_key=api_key)
    try:
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}",
                                "detail": "high",
                            },
                        }
                    ],
                },
            ],
            max_tokens=300,
            timeout=15,
        )

        raw = response.choices[0].message.content
        data = json.loads(raw)
        return {
            "evento": data.get("evento"),
            "mercado": data.get("mercado"),
            "odd": data.get("odd"),
        }
    except Exception:
        return {"evento": None, "mercado": None, "odd": None}
```

- [ ] **Step 4: Run tests, verify pass**

```bash
python -m pytest tests/test_vision.py -v
```

Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add vision.py tests/test_vision.py
git commit -m "feat: add vision module with GPT-4o-mini image analysis"
```

---

### Task 6: Client Module

**Files:**
- Create: `client.py`

- [ ] **Step 1: Implement client.py**

```python
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
```

No unit test for this — it's a thin wrapper over Telethon. Tested via integration when running main.py.

- [ ] **Step 2: Commit**

```bash
git add client.py
git commit -m "feat: add Telethon client wrapper"
```

---

### Task 7: Filter Module (Reaction Handler)

**Files:**
- Create: `filter.py`
- Create: `tests/test_filter.py`

- [ ] **Step 1: Write failing test**

Create `tests/test_filter.py`:

```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from filter import is_user_thumbs_up, ReactionInfo


def test_is_user_thumbs_up_positive():
    assert is_user_thumbs_up("👍") is True


def test_is_user_thumbs_up_negative():
    assert is_user_thumbs_up("❤️") is False
    assert is_user_thumbs_up("") is False
    assert is_user_thumbs_up(None) is False
```

- [ ] **Step 2: Run tests, verify fail**

```bash
python -m pytest tests/test_filter.py -v
```

Expected: FAIL — module not found.

- [ ] **Step 3: Implement filter.py**

```python
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
```

- [ ] **Step 4: Run tests, verify pass**

```bash
python -m pytest tests/test_filter.py -v
```

Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add filter.py tests/test_filter.py
git commit -m "feat: add filter module for thumbs-up reaction detection"
```

---

### Task 8: Main Entrypoint

**Files:**
- Create: `main.py`

- [ ] **Step 1: Implement main.py**

```python
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

    save_aposta(aposta)
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
```

- [ ] **Step 2: Commit**

```bash
git add main.py
git commit -m "feat: add main entrypoint wiring all modules"
```

---

### Task 9: README

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write README.md**

```bash
cat > README.md << 'EOF'
# Bet Scraper

Script que monitora um grupo de Telegram, detecta reações com 👍 do usuário e extrai automaticamente dados de apostas usando GPT Vision e regex.

## Como usar

1. Copie `.env.example` para `.env` e preencha suas credenciais:

```
TELEGRAM_API_ID=12345          # obtido em my.telegram.org
TELEGRAM_API_HASH=abc123       # obtido em my.telegram.org
TELEGRAM_PHONE=+5511999999999  # seu número
TELEGRAM_GROUP_NAME=Nome Grupo # nome exato do grupo
OPENAI_API_KEY=sk-...          # chave da OpenAI
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Execute:

```bash
python main.py
```

Na primeira execução, o Telegram pedirá o código de verificação enviado no app.

4. Pare com Ctrl+C.

Os dados são salvos em `data/apostas.json` e as imagens em `data/images/`.
EOF
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README with setup and usage instructions"
```

---

### Task 10: Smoke Test

- [ ] **Step 1: Verify all tests pass**

```bash
python -m pytest tests/ -v
```

Expected: All 14 tests pass.

- [ ] **Step 2: Verify import chain**

```bash
python -c "from storage import save_aposta, load_apostas, download_image; from extractor import extract_text_info; from vision import analyze_image; from filter import is_user_thumbs_up, register_handler; print('All imports OK')"
```

Expected: "All imports OK"

- [ ] **Step 3: Final commit if needed**

```bash
git status
```
