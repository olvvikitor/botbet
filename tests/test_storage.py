import csv
import json
import tempfile
import os
import pytest
from unittest.mock import AsyncMock, patch
from storage import CSV_HEADERS, clear_csv, load_apostas, save_aposta, download_image


def test_load_apostas_empty_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("[]")
        tmp = f.name
    try:
        result = load_apostas(tmp)
        assert result == []
    finally:
        os.unlink(tmp)


def test_load_apostas_blank_file_returns_empty_list():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("   \n")
        tmp = f.name
    try:
        result = load_apostas(tmp)
        assert result == []
    finally:
        os.unlink(tmp)


def test_clear_csv_keeps_only_header():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
        f.write("old,line\n1,2\n")
        tmp = f.name
    try:
        clear_csv(tmp)
        with open(tmp, newline="", encoding="utf-8") as csv_file:
            rows = list(csv.reader(csv_file))
        assert rows == [CSV_HEADERS]
    finally:
        os.unlink(tmp)


@pytest.mark.asyncio
async def test_save_and_load():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("[]")
        tmp = f.name
    try:
        await save_aposta({"id": 1, "evento": "FLA x PAL"}, tmp)
        result = load_apostas(tmp)
        assert len(result) == 1
        assert result[0]["id"] == 1
    finally:
        os.unlink(tmp)


@pytest.mark.asyncio
async def test_save_appends_to_existing():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump([{"id": 1}], f)
        tmp = f.name
    try:
        await save_aposta({"id": 2}, tmp)
        result = load_apostas(tmp)
        assert len(result) == 2
        assert result[1]["id"] == 2
    finally:
        os.unlink(tmp)


@pytest.mark.asyncio
async def test_download_image_returns_path():
    mock_msg = AsyncMock()
    mock_msg.download_media = AsyncMock()
    mock_msg.id = 12345

    with patch("storage.os.makedirs"):
        path = await download_image(None, mock_msg, "data/images")
        assert path is not None
        assert "12345" in path
        mock_msg.download_media.assert_called_once_with(file=path)


@pytest.mark.asyncio
async def test_download_image_no_media_returns_none():
    mock_msg = AsyncMock()
    mock_msg.media = None

    path = await download_image(None, mock_msg, "data/images")
    assert path is None
