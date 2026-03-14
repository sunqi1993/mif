"""Unified configuration path resolver and loader for alfredpy.

Config directory priority (highest → lowest):
  1. <project_root>/config/          ← team / project-level settings
  2. ~/.alfredpy/                    ← per-user fallback

Writing always goes to the same directory that was used for reading,
so project-level configs stay in the repo and user configs stay local.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

# ── Project layout ─────────────────────────────────────────────────────────────
# This file lives at  <project_root>/alfredpy/config.py
_PROJECT_ROOT: Path = Path(__file__).parent.parent

_DEFAULT_WORKFLOW_CONFIG: dict = {"workflows": []}
_DEFAULT_PLUGIN_CONFIG: dict = {}


# ── Config directory resolution ────────────────────────────────────────────────

def project_config_dir() -> Optional[Path]:
    """Return <project_root>/config/ if the directory exists, else None."""
    d = _PROJECT_ROOT / "config"
    return d if d.exists() else None


def user_config_dir() -> Path:
    """Return ~/.alfredpy/, creating it if necessary."""
    d = Path.home() / ".alfredpy"
    d.mkdir(parents=True, exist_ok=True)
    return d


def effective_config_dir() -> Path:
    """Return the active config directory.

    Priority: <project>/config/  >  ~/.alfredpy/
    """
    return project_config_dir() or user_config_dir()


# ── Specific file paths ────────────────────────────────────────────────────────

def plugin_config_path() -> Path:
    """Absolute path to plugin_configs.json in the effective config dir."""
    return effective_config_dir() / "plugin_configs.json"


def workflow_config_path() -> Path:
    """Absolute path to the workflow config file.

    Priority:
      1. <project>/config/workflows.json
      2. <project>/workflows.json          (legacy, project-root location)
      3. ~/.alfredpy/workflows.json
    """
    cfg = project_config_dir()
    if cfg:
        p = cfg / "workflows.json"
        if p.exists():
            return p

    # Legacy: project-root workflows.json (kept for backward compatibility)
    legacy = _PROJECT_ROOT / "workflows.json"
    if legacy.exists():
        return legacy

    return user_config_dir() / "workflows.json"


# ── Workflow config loader ─────────────────────────────────────────────────────

def load_config(path: str | None = None) -> Any:
    """Load and return workflow configuration as a Python object.

    Priority when *path* is None:
      1. <project>/config/workflows.json
      2. <project>/workflows.json  (legacy)
      3. ~/.alfredpy/workflows.json
    """
    if path is not None:
        config_path = Path(path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        if not config_path.exists():
            config_path.write_text(
                json.dumps(_DEFAULT_WORKFLOW_CONFIG, indent=2, ensure_ascii=False)
            )
    else:
        config_path = workflow_config_path()
        if not config_path.exists():
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(
                json.dumps(_DEFAULT_WORKFLOW_CONFIG, indent=2, ensure_ascii=False)
            )

    with open(config_path, encoding="utf-8") as f:
        return json.load(f)


def ensure_config_exists(path: str | None = None) -> str:
    """Ensure a workflow config file exists (create with defaults if absent).

    Returns the resolved absolute path as a string.
    """
    resolved = Path(path) if path else workflow_config_path()
    if not resolved.exists():
        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(
            json.dumps(_DEFAULT_WORKFLOW_CONFIG, indent=2, ensure_ascii=False)
        )
    return str(resolved)
