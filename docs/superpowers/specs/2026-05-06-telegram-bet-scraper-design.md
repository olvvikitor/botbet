# Telegram Bet Scraper — Design Spec

## Overview

Script Python contínuo que ouve mensagens de um grupo do Telegram e, quando detecta reação com 👍 do usuário, extrai dados da aposta combinando GPT Vision (imagem) e regex (texto), salvando tudo em JSON local.

## Arquitetura

```
Grupo Telegram  →  Telethon Client  →  Filtro 👍  →  Download imagem/texto
                                                          │
                                            ┌─────────────┴─────────────┐
                                            ▼                           ▼
                                      GPT Vision (imagem)         Regex (texto)
                                            │                           │
                                            ▼                           ▼
                                       evento, mercado, odd    porcentagem, link_casa
                                            │                           │
                                            └─────────────┬─────────────┘
                                                          ▼
                                                     Combina → JSON
```

3 componentes de pipeline após o filtro:
1. **Cliente Telegram** — conexão contínua via Telethon, autenticado como conta do usuário
2. **Filtro de reações** — escuta `events.MessageReaction`, processa só mensagens com 👍 do usuário
3. **Extrator + Storage** — baixa imagem e texto, extrai dados em paralelo (GPT Vision + regex), salva

## Fluxo de Dados

### Captura
- Telethon escuta eventos de reação (`MessageReaction`) no grupo alvo
- Quando uma reação 👍 do usuário é detectada, busca a mensagem completa (texto + mídia)

### Extração — Imagem (GPT Vision / OpenAI)
- Imagem enviada para modelo GPT Vision com prompt para extrair:
  - Evento (ex: "Flamengo x Palmeiras")
  - Mercado (ex: "Ambos marcam - Sim")
  - Odd do bilhete
- Timeout: 15 segundos
- Retry com backoff em caso de falha

### Extração — Texto (Regex)
- Porcentagem da banca (ex: "2% da unidade" → 2.0)
- Link da casa de aposta
- Odds complementares se presentes no texto

### Saída
Arquivo JSON incremental (`data/apostas.json`) — cada nova aposta é adicionada ao array.

Estrutura do registro:
```json
{
  "id": 12345,
  "data": "2026-05-06",
  "hora": "14:30",
  "texto_original": "Aposta do dia - 2% da unidade - bet365.com/...",
  "evento": "Flamengo x Palmeiras",
  "mercado": "Ambos marcam - Sim",
  "odd": 1.85,
  "porcentagem_banca": 2.0,
  "link_casa": "https://bet365.com/...",
  "imagem_path": "./data/images/12345.jpg",
  "mensagem_link": "https://t.me/grupo/12345"
}
```

## Estrutura de Arquivos

```
bet-scraper/
├── .env                   # credenciais (não versionar)
├── .env.example           # template sem valores reais
├── main.py                # entrypoint: conecta Telethon e inicia listener
├── client.py              # cliente Telethon (autenticação, reconexão)
├── filter.py              # handler de eventos de reação (filtra 👍)
├── extractor.py           # regex do texto (porcentagem, link)
├── vision.py              # GPT Vision para análise de imagem
├── storage.py             # salva/atualiza apostas.json + download de imagens
├── data/
│   ├── apostas.json
│   └── images/
├── requirements.txt
└── README.md
```

Cada módulo tem responsabilidade única e pode ser testado isoladamente.

## Tratamento de Erros

- Reconexão automática do Telethon com backoff exponencial
- Retry (3x) com backoff se GPT Vision falhar
- Log de erros (stderr + arquivo) para mensagens não processadas
- Timeout GPT Vision: 15s
- Se a imagem falhar mas o texto for extraído, salva com campos de imagem como `null`

## Configuração (.env)

```
TELEGRAM_API_ID=12345
TELEGRAM_API_HASH=abc123
TELEGRAM_PHONE=+5511999999999
TELEGRAM_GROUP_NAME=Nome do Grupo
OPENAI_API_KEY=sk-...
```

## Dependências (requirements.txt)

```
telethon>=1.36
openai>=1.0
python-dotenv>=1.0
```

## Execução

```bash
python main.py
```

Processo contínuo, rodando até interrupção manual (Ctrl+C). Logs no console com timestamp.
