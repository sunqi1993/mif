"""Configuration loader for alfredpy."""

import json
import os
from pathlib import Path

DEFAULT_CONFIG = {
    "workflows": []
}

DEFAULT_CONFIG_PATH = os.path.expanduser("~/.alfredpy/workflows.json")


def ensure_config_exists(path: str = DEFAULT_CONFIG_PATH) -> str:
    """Ensure the config file exists; if not, create a default one."""
    config_path = Path(path)
    if not config_path.exists():
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(json.dumps(DEFAULT_CONFIG, indent=2, ensure_ascii=False))
    return str(config_path)


def load_config(path: str | None = None) -> dict:
    """Load workflow configuration from JSON."""
    if path is None:
        path = DEFAULT_CONFIG_PATH
    config_path = ensure_config_exists(path)
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load config from {config_path}: {e}")
