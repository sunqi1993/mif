"""Plugin system for alfredpy — discovery, config persistence, @-keyword routing."""

from __future__ import annotations

import importlib
import json
import pkgutil
from pathlib import Path
from typing import Dict, List, Optional

from alfredpy.plugins.base import BasePlugin, ConfigOption, PluginMeta, PluginResult

__all__ = [
    "BasePlugin", "ConfigOption", "PluginMeta", "PluginResult",
    "PluginManager",
]


class PluginManager:
    """Discovers, configures, and queries plugins.

    Config is persisted to the *effective config directory*:
      priority 1 → <project_root>/config/plugin_configs.json
      priority 2 → ~/.alfredpy/plugin_configs.json  (user fallback)

    The active path is determined at runtime by ``alfredpy.config.plugin_config_path()``.
    """

    @property
    def CONFIG_PATH(self) -> Path:
        """Dynamic config path — project config/ dir takes priority over user dir."""
        from alfredpy.config import plugin_config_path
        return plugin_config_path()

    def __init__(self):
        self.plugins: Dict[str, BasePlugin] = {}
        self._raw_configs: Dict[str, dict] = {}   # plugin_id → {key: value}
        self._load_configs()
        self._discover_plugins()

    # ── Config persistence ────────────────────────────────────────────────────

    def _load_configs(self) -> None:
        """Load plugin configs from disk, ignoring documentation/comment keys."""
        if self.CONFIG_PATH.exists():
            try:
                with open(self.CONFIG_PATH, encoding="utf-8") as f:
                    raw = json.load(f)
                # Strip top-level documentation keys (e.g. "_comment", "_comment_keys")
                self._raw_configs = {
                    k: v for k, v in raw.items()
                    if not k.startswith("_comment") and isinstance(v, dict)
                }
            except Exception:
                self._raw_configs = {}

    def _save_configs(self) -> None:
        """Persist plugin configs to disk, preserving any documentation keys."""
        path = self.CONFIG_PATH
        path.parent.mkdir(parents=True, exist_ok=True)

        # Preserve existing documentation/comment keys from the current file
        existing: dict = {}
        if path.exists():
            try:
                with open(path, encoding="utf-8") as f:
                    existing = json.load(f)
            except Exception:
                pass
        doc_keys = {k: v for k, v in existing.items() if k.startswith("_comment")}

        # Merge: doc keys first (for readability), then plugin configs
        merged = {**doc_keys, **self._raw_configs}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(merged, f, indent=2, ensure_ascii=False)

    # ── Plugin discovery ──────────────────────────────────────────────────────

    def _discover_plugins(self) -> None:
        """Auto-discover every BasePlugin subclass inside this package."""
        plugins_dir = Path(__file__).parent   # alfredpy/plugins/

        for _, name, _ in pkgutil.iter_modules([str(plugins_dir)]):
            if name == "base":
                continue
            try:
                module = importlib.import_module(f"alfredpy.plugins.{name}")
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, BasePlugin)
                        and attr is not BasePlugin
                    ):
                        instance = attr()
                        if instance.meta.id not in self.plugins:
                            self.register(instance)
            except Exception as e:
                print(f"Failed to load plugin '{name}': {e}")

    # ── Registration ──────────────────────────────────────────────────────────

    def register(self, plugin: BasePlugin) -> None:
        """Register a plugin, inject manager reference, and apply saved config.

        Reserved keys in the config bucket (prefixed with ``_``) override plugin
        metadata fields:
          ``_keywords``   → list[str] that replaces PluginMeta.keywords
          ``_at_keyword`` → str      that replaces PluginMeta.at_keyword
        All other keys are forwarded to plugin.configure() as normal config.
        """
        self.plugins[plugin.meta.id] = plugin

        # Allow the plugin to hold a back-reference to the manager
        if hasattr(plugin, "set_manager"):
            plugin.set_manager(self)

        saved = self._raw_configs.get(plugin.meta.id, {})
        if saved:
            self._apply_saved(plugin, saved)

        print(f"✓ Loaded plugin: {plugin.meta.name} v{plugin.meta.version}")

    @staticmethod
    def _apply_saved(plugin: BasePlugin, saved: dict) -> None:
        """Apply a raw config bucket to a plugin instance."""
        # Metadata overrides (special underscore-prefixed keys)
        if "_keywords" in saved and isinstance(saved["_keywords"], list):
            plugin.meta.keywords = list(saved["_keywords"])
        if "_at_keyword" in saved:
            plugin.meta.at_keyword = str(saved["_at_keyword"])
        # Regular plugin config (everything else)
        regular = {k: v for k, v in saved.items() if not k.startswith("_")}
        if regular:
            plugin.configure(regular)

    def unregister(self, plugin_id: str) -> None:
        self.plugins.pop(plugin_id, None)

    # ── Config CRUD ───────────────────────────────────────────────────────────

    def get_plugin_config(self, plugin_id: str) -> dict:
        """Return the current effective config for a plugin (merged with defaults)."""
        plugin = self.plugins.get(plugin_id)
        if plugin is None:
            return {}
        return plugin.config_summary()

    def set_plugin_config(self, plugin_id: str, key: str, value) -> bool:
        """Set one config key (or metadata override) for a plugin and persist.

        Special underscore-prefixed keys:
          ``_keywords``   — list[str] replaces the plugin's trigger keywords
          ``_at_keyword`` — str       replaces the plugin's @-trigger keyword

        Returns True on success, False if the plugin_id is unknown.
        """
        plugin = self.plugins.get(plugin_id)
        if plugin is None:
            return False
        bucket = self._raw_configs.setdefault(plugin_id, {})
        bucket[key] = value
        self._apply_saved(plugin, bucket)
        self._save_configs()
        return True

    def reset_plugin_config(self, plugin_id: str) -> bool:
        """Reset all config (including keyword overrides) for a plugin to defaults."""
        plugin = self.plugins.get(plugin_id)
        if plugin is None:
            return False
        # Restore original meta from a fresh instance
        try:
            original = type(plugin)()
            plugin.meta.keywords = original.meta.keywords
            plugin.meta.at_keyword = original.meta.at_keyword
        except Exception:
            pass
        plugin.configure({})
        self._raw_configs.pop(plugin_id, None)
        self._save_configs()
        return True

    def full_config_snapshot(self, plugin_id: str) -> dict:
        """Return the complete raw config bucket (including ``_`` meta-overrides)."""
        return dict(self._raw_configs.get(plugin_id, {}))

    # ── @-keyword routing ─────────────────────────────────────────────────────

    def find_by_at_keyword(self, keyword: str) -> Optional[BasePlugin]:
        """Find a plugin whose ``at_keyword`` matches *keyword* (case-insensitive)."""
        kw = keyword.lower()
        for plugin in self.plugins.values():
            if plugin.meta.at_keyword and plugin.meta.at_keyword.lower() == kw:
                return plugin
        return None

    def all_at_plugins(self) -> List[BasePlugin]:
        """Return all plugins that declare an at_keyword."""
        return [p for p in self.plugins.values() if p.meta.at_keyword]

    def search_at(self, at_keyword: str, query: str) -> List[PluginResult]:
        """Invoke *one* plugin directly via its at_keyword."""
        plugin = self.find_by_at_keyword(at_keyword)
        if plugin is None:
            return []
        results = plugin.search(query)
        for r in results:
            r.plugin_id = plugin.meta.id
        return results

    # ── Normal fan-out search ─────────────────────────────────────────────────

    def search(self, query: str) -> List[PluginResult]:
        """Fan-out search across all matching plugins, sorted by priority → score."""
        all_results: List[PluginResult] = []
        for plugin in sorted(self.plugins.values(), key=lambda p: p.meta.priority):
            if plugin.match_keyword(query):
                clean = plugin.strip_keyword(query)
                results = plugin.search(clean)
                for r in results:
                    r.plugin_id = plugin.meta.id
                    if r.score == 0.0:
                        r.score = self._score(r, query)
                all_results.extend(results)
        return sorted(all_results, key=lambda r: r.score, reverse=True)

    @staticmethod
    def _score(result: PluginResult, query: str) -> float:
        try:
            from thefuzz import fuzz
            ts = fuzz.partial_ratio(query.lower(), result.title.lower())
            ss = fuzz.partial_ratio(query.lower(), result.subtitle.lower()) if result.subtitle else 0
            return max(ts, ss) * 0.01
        except ImportError:
            q = query.lower()
            if q in result.title.lower():
                return 1.0
            if result.subtitle and q in result.subtitle.lower():
                return 0.8
            return 0.5
