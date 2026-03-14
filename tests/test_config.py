"""Tests for config module."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from alfredpy.config import (
    DEFAULT_CONFIG,
    DEFAULT_CONFIG_PATH,
    ensure_config_exists,
    load_config,
)


class TestEnsureConfigExists:
    """Tests for ensure_config_exists function."""

    def test_create_config_if_not_exists(self, tmp_path):
        """Test that config is created if it doesn't exist."""
        config_file = tmp_path / "config.json"
        config_path = str(config_file)

        result = ensure_config_exists(config_path)

        assert result == config_path
        assert config_file.exists()
        content = json.loads(config_file.read_text())
        assert content == DEFAULT_CONFIG

    def test_not_overwrite_existing_config(self, tmp_path):
        """Test that existing config is not overwritten."""
        config_file = tmp_path / "config.json"
        config_file.write_text('{"workflows": [{"id": "test"}]}')

        result = ensure_config_exists(str(config_file))

        assert result == str(config_file)
        content = json.loads(config_file.read_text())
        assert content == {"workflows": [{"id": "test"}]}

    def test_creates_parent_directories(self, tmp_path):
        """Test that parent directories are created."""
        nested_dir = tmp_path / "nested" / "path"
        config_file = nested_dir / "config.json"
        config_path = str(config_file)

        result = ensure_config_exists(config_path)

        assert result == config_path
        assert nested_dir.exists()
        assert config_file.exists()


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_config_default_path(self):
        """Test loading config with default path."""
        with patch(
            "alfredpy.config.DEFAULT_CONFIG_PATH", "/tmp/test_alfredpy_config.json"
        ):
            # Create a temporary config file
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False
            ) as f:
                json.dump({"workflows": [{"id": "test"}]}, f)
                temp_path = f.name

            try:
                with patch("alfredpy.config.DEFAULT_CONFIG_PATH", temp_path):
                    config = load_config()
                    assert "workflows" in config
                    assert len(config["workflows"]) == 1
            finally:
                os.unlink(temp_path)

    def test_load_config_custom_path(self, tmp_path):
        """Test loading config with custom path."""
        config_file = tmp_path / "custom_config.json"
        config_file.write_text('{"workflows": [{"id": "custom"}]}')

        config = load_config(str(config_file))

        assert "workflows" in config
        assert len(config["workflows"]) == 1
        assert config["workflows"][0]["id"] == "custom"

    def test_load_config_nonexistent_file(self):
        """Test loading config from nonexistent file creates it."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "new_config.json")
            config = load_config(config_path)
            assert config == DEFAULT_CONFIG

    def test_load_config_invalid_json(self, tmp_path):
        """Test loading invalid JSON raises RuntimeError."""
        config_file = tmp_path / "invalid.json"
        config_file.write_text("not valid json")

        with pytest.raises(RuntimeError, match="Failed to load config"):
            load_config(str(config_file))

