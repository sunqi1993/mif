"""Plugin config persistence and application helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from mif.plugins.base import BasePlugin


class PluginConfigStore:
    """Persist and apply plugin runtime config buckets."""

    def __init__(self, config_path_getter):
        self._config_path_getter = config_path_getter
        self._raw_configs: Dict[str, dict] = {}
        self.load()

    @property
    def config_path(self) -> Path:
        return self._config_path_getter()

    def load(self) -> None:
        path = self.config_path
        if path.exists():
            try:
                with open(path, encoding="utf-8") as f:
                    raw = json.load(f)
                self._raw_configs = {
                    k: v for k, v in raw.items() if not k.startswith("_comment") and isinstance(v, dict)
                }
            except Exception:
                self._raw_configs = {}

    def save(self) -> None:
        path = self.config_path
        path.parent.mkdir(parents=True, exist_ok=True)

        existing: dict = {}
        if path.exists():
            try:
                with open(path, encoding="utf-8") as f:
                    existing = json.load(f)
            except Exception:
                pass
        doc_keys = {k: v for k, v in existing.items() if k.startswith("_comment")}
        merged = {**doc_keys, **self._raw_configs}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(merged, f, indent=2, ensure_ascii=False)

    @staticmethod
    def apply_saved(plugin: BasePlugin, saved: dict) -> None:
        if "_keywords" in saved and isinstance(saved["_keywords"], list):
            plugin.meta.keywords = list(saved["_keywords"])
        if "_at_keyword" in saved:
            plugin.meta.at_keyword = str(saved["_at_keyword"])

        regular = {k: v for k, v in saved.items() if not k.startswith("_")}
        if regular:
            plugin.configure(regular)

    def apply_to_plugin(self, plugin: BasePlugin) -> None:
        saved = self._raw_configs.get(plugin.meta.id, {})
        if saved:
            self.apply_saved(plugin, saved)

    def set_plugin_config(self, plugin: BasePlugin, key: str, value) -> None:
        bucket = self._raw_configs.setdefault(plugin.meta.id, {})
        bucket[key] = value
        self.apply_saved(plugin, bucket)
        self.save()

    def reset_plugin_config(self, plugin: BasePlugin) -> None:
        try:
            original = type(plugin)()
            plugin.meta.keywords = original.meta.keywords
            plugin.meta.at_keyword = original.meta.at_keyword
        except Exception:
            pass
        plugin.configure({})
        self._raw_configs.pop(plugin.meta.id, None)
        self.save()

    def snapshot(self, plugin_id: str) -> dict:
        return dict(self._raw_configs.get(plugin_id, {}))
