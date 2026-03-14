"""Workflow and action definitions."""

import json
import subprocess
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type


class ActionRegistry:
    """Registry for available workflow actions."""

    _registry: Dict[str, Callable[[dict], None]] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(fn: Callable[[dict], None]):
            cls._registry[name] = fn
            return fn

        return decorator

    @classmethod
    def run(cls, name: str, args: dict | None = None) -> None:
        if args is None:
            args = {}
        if name not in cls._registry:
            raise KeyError(f"Unknown action '{name}'")
        cls._registry[name](args)


@dataclass
class WorkflowItem:
    id: str
    name: str
    description: str
    action: str
    args: dict

    @classmethod
    def from_dict(cls, item: dict) -> "WorkflowItem":
        return cls(
            id=item.get("id", ""),
            name=item.get("name", ""),
            description=item.get("description", ""),
            action=item.get("action", ""),
            args=item.get("args", {}) or {},
        )

    def run(self) -> None:
        ActionRegistry.run(self.action, self.args)


def _run_subprocess(command: list[str], cwd: str | Path | None = None) -> None:
    """Run a subprocess and wait for it to complete."""
    subprocess.run(command, cwd=cwd, check=False)


@ActionRegistry.register("print")
def action_print(args: dict) -> None:
    """Print text to stdout."""
    text = args.get("text", "")
    print(text)


@ActionRegistry.register("open_url")
def action_open_url(args: dict) -> None:
    """Open a URL in the default browser."""
    url = args.get("url")
    if not url:
        raise ValueError("`url` is required for open_url action")
    webbrowser.open(url)


@ActionRegistry.register("run")
def action_run(args: dict) -> None:
    """Run a shell command."""
    command = args.get("command")
    if not command:
        raise ValueError("`command` is required for run action")
    if isinstance(command, str):
        command = [command]
    _run_subprocess(command)


@ActionRegistry.register("open_file")
def action_open_file(args: dict) -> None:
    """Open a file with the default application."""
    file_path = args.get("path")
    if not file_path:
        raise ValueError("`path` is required for open_file action")
    Path(file_path).expanduser().resolve().open()
