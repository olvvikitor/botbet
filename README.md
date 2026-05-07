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
