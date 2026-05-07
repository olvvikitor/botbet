# Design: Varredura one-shot de mensagens do dia

## Objetivo

Trocar o listener em tempo real por uma varredura one-shot que processa todas as mensagens do dia atual onde o usuário reagiu com 👍, depois encerra.

## Mudanças

### filter.py

- Mantém `THUMBS_UP_EMOJIS` e `is_user_thumbs_up()`
- Remove `register_handler()`
- Adiciona `scan_thumbs_up(client, group_name, callback)`:
  1. Resolve a entidade do grupo por nome
  2. Itera mensagens com `client.iter_messages(chat, offset_date=hoje, reverse=True)` (onde `hoje` = início do dia atual)
  3. Para cada mensagem com reações, verifica se há 👍 do próprio usuário (`my=True`)
  4. Chama o callback com `(client, message)`
  5. Ao final, imprime quantas processou e encerra

### main.py

- Troca `register_handler(client, GROUP_NAME, process_message)` por `scan_thumbs_up(client, GROUP_NAME, process_message)`
- Mantém o restante igual

### Outros módulos

- `extractor.py`, `vision.py`, `storage.py` — sem alterações

## Comportamento

- Execução one-shot: varre, processa, imprime resumo, encerra
- Processa apenas mensagens do dia atual
