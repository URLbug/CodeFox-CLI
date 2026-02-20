"""Tests for CLIManager."""

from unittest.mock import patch

from codefox.api.model_enum import ModelEnum
from codefox.cli_manager import CLIManager


@patch("codefox.cli_manager.load_dotenv", return_value=True)
def test_get_api_class_returns_gemini_by_default(
    mock_load_dotenv: object,
) -> None:
    with patch("codefox.cli_manager.Helper") as mock_helper:
        mock_helper.read_yml.return_value = {"provider": "gemini"}
        manager = CLIManager(command="scan")
        api_class = manager._get_api_class()
        assert api_class is ModelEnum.GEMINI.api_class


@patch("codefox.cli_manager.load_dotenv", return_value=True)
def test_get_api_class_uses_provider_from_config(
    mock_load_dotenv: object,
) -> None:
    with patch("codefox.cli_manager.Helper") as mock_helper:
        mock_helper.read_yml.return_value = {"provider": "qwen"}
        manager = CLIManager(command="scan")
        api_class = manager._get_api_class()
        assert api_class is ModelEnum.QWEN.api_class


@patch("codefox.cli_manager.load_dotenv", return_value=True)
def test_get_api_class_default_provider_when_missing(
    mock_load_dotenv: object,
) -> None:
    with patch("codefox.cli_manager.Helper") as mock_helper:
        mock_helper.read_yml.return_value = {}
        manager = CLIManager(command="scan")
        api_class = manager._get_api_class()
        assert api_class is ModelEnum.GEMINI.api_class
