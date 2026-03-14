"""Plugin discovery and registration."""

from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path
from typing import Dict

from mif.plugins.base import BasePlugin


class PluginRegistry:
    """Discover and store plugin instances."""

    def __init__(self):
        self.plugins: Dict[str, BasePlugin] = {}

    def discover(self, package_dir: Path, package_prefix: str, register_callback) -> None:
        for _, name, _ in pkgutil.iter_modules([str(package_dir)]):
            if name in {"base", "registry", "config_store", "coordinator"}:
                continue
            try:
                module = importlib.import_module(f"{package_prefix}.{name}")
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, BasePlugin) and attr is not BasePlugin:
                        instance = attr()
                        if instance.meta.id not in self.plugins:
                            register_callback(instance)
            except Exception as e:
                print(f"Failed to load plugin '{name}': {e}")

    def register(self, plugin: BasePlugin) -> None:
        self.plugins[plugin.meta.id] = plugin

    def unregister(self, plugin_id: str) -> None:
        self.plugins.pop(plugin_id, None)
