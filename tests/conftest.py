"""Pytest fixtures for codefox tests."""

from pathlib import Path

import pytest


@pytest.fixture
def tmp_yaml_path(tmp_path: Path) -> Path:
    """Return path to a temporary YAML file."""
    return tmp_path / "config.yml"


@pytest.fixture
def sample_config() -> dict:
    """Minimal valid .codefox.yml-like config."""
    return {
        "model": {
            "name": "gemini-2.0-flash",
            "temperature": 0.2,
            "max_tokens": 4000,
            "timeout": 600,
        },
        "review": {
            "severity": "high",
            "max_issues": None,
            "suggest_fixes": True,
            "diff_only": False,
        },
        "baseline": {"enable": True},
        "ruler": {"security": True, "performance": True, "style": True},
        "prompt": {"system": None, "extra": None},
    }


@pytest.fixture
def tmp_codefoxignore(tmp_path: Path) -> Path:
    """Create a temporary .codefoxignore and return its path."""
    p = tmp_path / ".codefoxignore"
    p.write_text("node_modules/\nvendor/\n# comment\n", encoding="utf-8")
    return p
