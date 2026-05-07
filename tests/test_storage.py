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
