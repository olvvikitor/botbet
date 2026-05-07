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

    mock_file = MagicMock()
    mock_file.__enter__.return_value.read.return_value = b"fake-image-data"

    with patch("vision.AsyncOpenAI") as mock_client_class, \
            patch("builtins.open", return_value=mock_file):
        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client

        result = await analyze_image("test.jpg", "fake-key")

        assert result["evento"] == "Flamengo x Palmeiras"
        assert result["mercado"] == "Ambos marcam - Sim"
        assert result["odd"] == 1.85


@pytest.mark.asyncio
async def test_analyze_image_handles_api_error():
    mock_file = MagicMock()
    mock_file.__enter__.return_value.read.return_value = b"fake-image-data"

    with patch("vision.AsyncOpenAI") as mock_client_class, \
            patch("builtins.open", return_value=mock_file):
        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock(
            side_effect=Exception("API error")
        )
        mock_client_class.return_value = mock_client

        result = await analyze_image("test.jpg", "fake-key")

        assert result["evento"] is None
        assert result["mercado"] is None
        assert result["odd"] is None
