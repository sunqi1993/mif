"""Tests for config module."""

import json

import pytest

from mif.config import ensure_config_exists, load_config, read_config


def test_ensure_config_exists_creates_default(tmp_path):
    config_file = tmp_path / "config.json"
    result = ensure_config_exists(str(config_file))
    assert result == str(config_file)
    assert config_file.exists()
    assert json.loads(config_file.read_text()) == {"workflows": []}


def test_ensure_config_exists_keeps_existing(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text('{"workflows":[{"id":"x"}]}')
    ensure_config_exists(str(config_file))
    assert json.loads(config_file.read_text()) == {"workflows": [{"id": "x"}]}


def test_load_config_custom_path_creates_when_missing(tmp_path):
    config_file = tmp_path / "missing.json"
    loaded = load_config(str(config_file))
    assert loaded == {"workflows": []}
    assert config_file.exists()


def test_read_config_without_create_raises_for_missing(tmp_path):
    config_file = tmp_path / "missing.json"
    with pytest.raises(FileNotFoundError):
        read_config(str(config_file), create_if_missing=False)


def test_read_config_with_create_returns_default(tmp_path):
    config_file = tmp_path / "create.json"
    loaded = read_config(str(config_file), create_if_missing=True)
    assert loaded == {"workflows": []}
    assert config_file.exists()


def test_read_config_invalid_json_raises_decode_error(tmp_path):
    config_file = tmp_path / "invalid.json"
    config_file.write_text("not valid json")
    with pytest.raises(json.JSONDecodeError):
        read_config(str(config_file))

