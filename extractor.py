import re


def extract_text_info(text):
    if text is None:
        return {"porcentagem_banca": None, "link_casa": None}

    pct_pattern = r"(\d+(?:[.,]\d+)?)\s*%"
    pct_match = re.search(pct_pattern, text)
    porcentagem = float(pct_match.group(1).replace(",", ".")) if pct_match else None

    url_pattern = r"https?://[^\s]+"
    url_match = re.search(url_pattern, text)
    link = url_match.group(0) if url_match else None
    if link:
        link = link.rstrip("),;:.\"'")

    return {
        "porcentagem_banca": porcentagem,
        "link_casa": link,
    }
