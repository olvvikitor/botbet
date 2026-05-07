import asyncio
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
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    client = AsyncOpenAI(api_key=api_key)

    for attempt in range(3):
        try:
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
        except Exception as e:
            print(f"[vision] attempt {attempt + 1}/3: {type(e).__name__}: {e}", flush=True)
            if attempt < 2:
                await asyncio.sleep(2 ** attempt)

    print(f"[vision] all retries exhausted for {image_path}", flush=True)
    return {"evento": None, "mercado": None, "odd": None}
