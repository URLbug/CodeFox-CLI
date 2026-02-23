"""Tests for Helper."""

import os
from pathlib import Path

import pytest

from codefox.utils.helper import Helper


def test_read_yml_missing_file_raises() -> None:
    with pytest.raises(FileNotFoundError):
        Helper.read_yml("/nonexistent/path.yml")


def test_read_yml_valid(tmp_path: Path, sample_config: dict) -> None:
    import yaml

    path = tmp_path / "config.yml"
    path.write_text(
        yaml.dump(sample_config, default_flow_style=False),
        encoding="utf-8",
    )
    result = Helper.read_yml(str(path))
    assert result["model"]["name"] == "gemini-2.0-flash"
    assert result["model"]["temperature"] == 0.2


def test_read_codefoxignore_missing_returns_empty(tmp_path: Path) -> None:
    prev = os.getcwd()
    try:
        os.chdir(tmp_path)
        out = Helper.read_codefoxignore()
        assert out == []
    finally:
        os.chdir(prev)


def test_read_codefoxignore_with_file(tmp_path: Path) -> None:
    (tmp_path / ".codefoxignore").write_text(
        "node_modules/\nvendor/\n# comment\n\n",
        encoding="utf-8",
    )
    prev = os.getcwd()
    try:
        os.chdir(tmp_path)
        out = Helper.read_codefoxignore()
        assert "node_modules/" in out
        assert "vendor/" in out
        assert "# comment" not in out
    finally:
        os.chdir(prev)


def test_get_all_files_skips_unsupported_ext(tmp_path: Path) -> None:
    (tmp_path / "foo.py").write_text("x", encoding="utf-8")
    (tmp_path / "bar.txt").write_text("y", encoding="utf-8")
    (tmp_path / "baz.js").write_text("z", encoding="utf-8")
    prev = os.getcwd()
    try:
        os.chdir(tmp_path)
        (tmp_path / ".codefoxignore").write_text("", encoding="utf-8")
        files = Helper.get_all_files(str(tmp_path))
        paths = [Path(p) for p in files]
        assert any("foo.py" in str(p) for p in paths)
        assert any("baz.js" in str(p) for p in paths)
        assert not any("bar.txt" in str(p) for p in paths)
    finally:
        os.chdir(prev)


def test_get_all_files_skips_ignore_dirs(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("x", encoding="utf-8")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "x.js").write_text("y", encoding="utf-8")
    prev = os.getcwd()
    try:
        os.chdir(tmp_path)
        (tmp_path / ".codefoxignore").write_text("", encoding="utf-8")
        files = Helper.get_all_files(str(tmp_path))
        assert any("a.py" in p for p in files)
        assert not any("node_modules" in p for p in files)
    finally:
        os.chdir(prev)


def test_supported_extensions_contains_common() -> None:
    assert ".py" in Helper.SUPPORTED_EXTENSIONS
    assert ".js" in Helper.SUPPORTED_EXTENSIONS
    assert ".ts" in Helper.SUPPORTED_EXTENSIONS
