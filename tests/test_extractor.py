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


def test_extract_none_text():
    result = extract_text_info(None)
    assert result["porcentagem_banca"] is None
    assert result["link_casa"] is None
