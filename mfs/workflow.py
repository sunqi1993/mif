"""Workflow and action definitions."""

import os
import platform
import subprocess
import webbrowser
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import quote

# Try to import pyperclip for clipboard support
try:
    import pyperclip

    HAS_PYPERCLIP = True
except ImportError:
    HAS_PYPERCLIP = False


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
    icon: str = "🚀"                              # per-workflow emoji icon
    priority: int = 100                           # lower = shown first
    keywords: List[str] = field(default_factory=list)  # prefix keywords, e.g. ["g", "google"]

    @classmethod
    def from_dict(cls, item: dict) -> "WorkflowItem":
        return cls(
            id=item.get("id", ""),
            name=item.get("name", ""),
            description=item.get("description", ""),
            action=item.get("action", ""),
            args=item.get("args", {}) or {},
            icon=item.get("icon", "🚀"),
            priority=item.get("priority", 100),
            keywords=item.get("keywords", []),
        )

    def run(self, query: str = "") -> None:
        """Execute the action, substituting ``{query}`` placeholders in args."""
        resolved: dict = {}
        for k, v in self.args.items():
            if isinstance(v, str):
                resolved[k] = v.replace("{query}", query)
            elif isinstance(v, list):
                resolved[k] = [
                    i.replace("{query}", query) if isinstance(i, str) else i
                    for i in v
                ]
            else:
                resolved[k] = v
        ActionRegistry.run(self.action, resolved)


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
    """Open a URL in the default browser. 非 ASCII 字符会按 UTF-8 做百分号编码，避免乱码。"""
    url = args.get("url")
    if not url:
        raise ValueError("`url` is required for open_url action")
    # 只传 ASCII URL，避免系统/浏览器对中文等字符误解释为 Latin-1 导致 ?q= 乱码
    url_ascii = quote(url, safe="/?:@!$&'()*+,;=", encoding="utf-8")
    webbrowser.open(url_ascii)


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


@ActionRegistry.register("copy_to_clipboard")
def action_copy_to_clipboard(args: dict) -> None:
    """Copy text to clipboard."""
    text = args.get("text", "")
    if not HAS_PYPERCLIP:
        print("Warning: pyperclip not installed. Clipboard content:", text)
        return
    pyperclip.copy(text)


@ActionRegistry.register("notify")
def action_notify(args: dict) -> None:
    """Send a system notification."""
    message = args.get("message")
    if not message:
        raise ValueError("`message` is required for notify action")
    title = args.get("title", "Notification")

    system = platform.system()
    if system == "Darwin":  # macOS
        subprocess.run(
            [
                "osascript",
                "-e",
                f'display notification "{message}" with title "{title}"',
            ]
        )
    elif system == "Linux":
        subprocess.run(["notify-send", title, message])
    else:  # Windows
        # Fallback: print to console
        print(f"[{title}] {message}")


@ActionRegistry.register("set_env")
def action_set_env(args: dict) -> None:
    """Set an environment variable."""
    name = args.get("name")
    value = args.get("value")
    if not name:
        raise ValueError("`name` is required for set_env action")
    if value is None:
        raise ValueError("`value` is required for set_env action")
    os.environ[name] = value


@ActionRegistry.register("change_dir")
def action_change_dir(args: dict) -> None:
    """Change current working directory."""
    path = args.get("path")
    if not path:
        raise ValueError("`path` is required for change_dir action")
    target_path = Path(path).expanduser().resolve()
    if target_path.exists() and target_path.is_dir():
        os.chdir(target_path)
    else:
        raise FileNotFoundError(f"Directory not found: {path}")


@ActionRegistry.register("write_file")
def action_write_file(args: dict) -> None:
    """Write content to a file."""
    path = args.get("path")
    content = args.get("content", "")
    if not path:
        raise ValueError("`path` is required for write_file action")
    file_path = Path(path).expanduser().resolve()
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")


@ActionRegistry.register("read_file")
def action_read_file(args: dict) -> None:
    """Read and print content from a file."""
    path = args.get("path")
    if not path:
        raise ValueError("`path` is required for read_file action")
    file_path = Path(path).expanduser().resolve()
    content = file_path.read_text(encoding="utf-8")
    print(content)
