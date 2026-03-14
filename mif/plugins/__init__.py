"""Plugin system façade for mif."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from mif.plugins.base import BasePlugin, ConfigOption, PluginMeta, PluginResult
from mif.plugins.config_store import PluginConfigStore
from mif.plugins.coordinator import PluginSearchCoordinator
from mif.plugins.registry import PluginRegistry

__all__ = [
    "BasePlugin",
    "ConfigOption",
    "PluginMeta",
    "PluginResult",
    "PluginManager",
]


class PluginManager:
    """Facade that coordinates registry, config store, and search routing."""

    @property
    def CONFIG_PATH(self) -> Path:
        from mif.config import plugin_config_path

        return plugin_config_path()

    def __init__(self):
        self._registry = PluginRegistry()
        self._config_store = PluginConfigStore(lambda: self.CONFIG_PATH)
        self._coordinator = PluginSearchCoordinator(self._registry.plugins)
        self._discover_plugins()

    @property
    def plugins(self):
        return self._registry.plugins

    def _discover_plugins(self) -> None:
        plugins_dir = Path(__file__).parent
        self._registry.discover(plugins_dir, "mif.plugins", self.register)

    def register(self, plugin: BasePlugin) -> None:
        self._registry.register(plugin)

        if hasattr(plugin, "set_manager"):
            plugin.set_manager(self)

        self._config_store.apply_to_plugin(plugin)
        print(f"✓ Loaded plugin: {plugin.meta.name} v{plugin.meta.version}")

    def unregister(self, plugin_id: str) -> None:
        self._registry.unregister(plugin_id)

    def get_plugin_config(self, plugin_id: str) -> dict:
        plugin = self.plugins.get(plugin_id)
        if plugin is None:
            return {}
        return plugin.config_summary()

    def set_plugin_config(self, plugin_id: str, key: str, value) -> bool:
        plugin = self.plugins.get(plugin_id)
        if plugin is None:
            return False
        self._config_store.set_plugin_config(plugin, key, value)
        return True

    def reset_plugin_config(self, plugin_id: str) -> bool:
        plugin = self.plugins.get(plugin_id)
        if plugin is None:
            return False
        self._config_store.reset_plugin_config(plugin)
        return True

    def full_config_snapshot(self, plugin_id: str) -> dict:
        return self._config_store.snapshot(plugin_id)

    def find_by_at_keyword(self, keyword: str) -> Optional[BasePlugin]:
        return self._coordinator.find_by_at_keyword(keyword)

    def all_at_plugins(self) -> List[BasePlugin]:
        return self._coordinator.all_at_plugins()

    def search_at(self, at_keyword: str, query: str) -> List[PluginResult]:
        return self._coordinator.search_at(at_keyword, query)

    def search(self, query: str) -> List[PluginResult]:
        return self._coordinator.search(query)
