"""Command-line entrypoint for mif."""

import argparse
import sys
from typing import List

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion, ThreadedCompleter
from prompt_toolkit.styles import Style

from mif.config import load_config
from mif.workflow import WorkflowItem


class WorkflowCompleter(Completer):
    def __init__(self, items: List[WorkflowItem]) -> None:
        self.items = items

    def get_completions(self, document, complete_event):
        text = document.text.strip().lower()
        for item in self.items:
            if not text or text in item.name.lower() or text in item.description.lower():
                yield Completion(item.name, start_position=-len(document.text))


def _load_workflows(config_path: str | None = None) -> List[WorkflowItem]:
    config = load_config(config_path)
    raw = config.get("workflows") or []
    return [WorkflowItem.from_dict(i) for i in raw if isinstance(i, dict)]


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mif")
    parser.add_argument("--config", "-c", help="Use a custom workflows config file")
    parser.add_argument("--list", "-l", action="store_true", help="List available workflows")
    parser.add_argument("--gui", "-g", action="store_true", help="Launch GUI mode")
    args = parser.parse_args(argv)

    # GUI mode - launch Qt Widgets application
    if args.gui:
        from mif.gui_qt.launcher import launch_gui
        launch_gui(args.config)
        return 0

    # TUI mode
    items = _load_workflows(args.config)
    if args.list:
        for item in items:
            print(f"- {item.name}: {item.description}")
        return 0

    if not items:
        print("No workflows found. Create ~/.mif/workflows.json and add workflows.")
        return 1

    style = Style.from_dict({"prompt": "bold #00ff00"})
    session = PromptSession(
        "> ", completer=ThreadedCompleter(WorkflowCompleter(items)), style=style
    )

    try:
        text = session.prompt("Select workflow: ")
    except KeyboardInterrupt:
        return 0

    for item in items:
        if item.name == text.strip():
            item.run()
            return 0

    print("No matching workflow selected.")
    return 1

