"""Tests for BaseAPI config validation (via a concrete subclass)."""

from unittest.mock import patch

import pytest

from codefox.api.gemini import Gemini


def test_base_api_requires_model_key() -> None:
    with pytest.raises(ValueError, match="Missing required key 'model'"):
        Gemini(config={"other": 1})


def test_base_api_requires_model_name() -> None:
    with pytest.raises(ValueError, match="name"):
        Gemini(config={"model": {"temperature": 0.2}})


def test_base_api_rejects_empty_model_name() -> None:
    with pytest.raises(ValueError, match="cannot be empty"):
        Gemini(config={"model": {"name": "   "}})


def test_base_api_accepts_valid_structure(sample_config: dict) -> None:
    """Valid config completes BaseAPI init; Gemini client is mocked."""
    with patch("codefox.api.gemini.genai.Client"):
        try:
            Gemini(config=sample_config)
        except (ValueError, RuntimeError) as e:
            if "Missing required key" in str(e) or "name" in str(e):
                pytest.fail(
                    "Valid config must not raise config validation errors"
                )
            raise


def test_base_api_file_not_found_raises_runtime_error() -> None:
    """When config is None and .codefox.yml missing, RuntimeError is raised."""
    with patch(
        "codefox.api.base_api.Helper.read_yml",
        side_effect=FileNotFoundError(),
    ):
        with pytest.raises(RuntimeError, match="not found"):
            Gemini(config=None)
