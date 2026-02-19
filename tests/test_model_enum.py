"""Tests for ModelEnum."""

import pytest

from codefox.api.base_api import BaseAPI
from codefox.api.gemini import Gemini
from codefox.api.model_enum import ModelEnum
from codefox.api.qwen import Qwen


def test_model_enum_members() -> None:
    assert ModelEnum.GEMINI is not None
    assert ModelEnum.QWEN is not None


def test_api_class_returns_type() -> None:
    assert ModelEnum.GEMINI.api_class is Gemini
    assert ModelEnum.QWEN.api_class is Qwen
    assert issubclass(ModelEnum.GEMINI.api_class, BaseAPI)


def test_by_name_valid() -> None:
    assert ModelEnum.by_name("gemini") == ModelEnum.GEMINI
    assert ModelEnum.by_name("GEMINI") == ModelEnum.GEMINI
    assert ModelEnum.by_name("qwen") == ModelEnum.QWEN


def test_by_name_invalid_raises() -> None:
    with pytest.raises(ValueError) as exc_info:
        ModelEnum.by_name("unknown")
    assert "Unknown provider" in str(exc_info.value)
    assert "unknown" in str(exc_info.value)
    assert "gemini" in str(exc_info.value).lower()
    assert "qwen" in str(exc_info.value).lower()


def test_names() -> None:
    names = ModelEnum.names()
    assert "gemini" in names
    assert "qwen" in names
    assert len(names) == 2
