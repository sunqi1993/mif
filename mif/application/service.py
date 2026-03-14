"""Application service layer: thin facade between UI and plugin system."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class UiEntry:
    title: str
    subtitle: str
    icon: str
    payload: Any


class ApplicationService:
    """High-level application operations for GUI and other frontends."""

    def __init__(self, plugin_manager):
        self._plugin_manager = plugin_manager

    def search_normal(self, query: str) -> list[UiEntry]:
        all_results = self._plugin_manager.search(query)
        entries: list[UiEntry] = []

        calc_result = None
        others = []
        for result in all_results:
            if result.plugin_id == "calculator" and calc_result is None:
                calc_result = result
            else:
                others.append(result)

        if calc_result is not None:
            entries.append(
                UiEntry(
                    title=calc_result.title,
                    subtitle=calc_result.subtitle,
                    icon=calc_result.icon or "🧮",
                    payload=calc_result,
                )
            )

        for result in others[:40]:
            entries.append(
                UiEntry(
                    title=result.title,
                    subtitle=result.subtitle,
                    icon=self._resolve_icon(result),
                    payload=result,
                )
            )
        return entries

    def find_at_plugin(self, at_keyword: str):
        return self._plugin_manager.find_by_at_keyword(at_keyword)

    def list_at_plugins(self, partial: str) -> list[UiEntry]:
        matched = [
            plugin
            for plugin in self._plugin_manager.all_at_plugins()
            if not partial or plugin.meta.at_keyword.lower().startswith(partial.lower())
        ]
        return [
            UiEntry(
                title=f"@{plugin.meta.at_keyword}  {plugin.meta.name}",
                subtitle=plugin.meta.description,
                icon=plugin.meta.icon,
                payload=("at_select", plugin.meta.at_keyword),
            )
            for plugin in matched
        ]

    def plugin_config_entries(self, plugin) -> list[UiEntry]:
        if not plugin.meta.config_options:
            return [
                UiEntry(
                    title=f"@{plugin.meta.at_keyword} 已就绪",
                    subtitle="继续输入参数以搜索",
                    icon=plugin.meta.icon,
                    payload=None,
                )
            ]

        entries: list[UiEntry] = []
        for option in plugin.meta.config_options:
            type_hint = {
                "choice": f"可选: {' / '.join(option.choices)}",
                "bool": "true / false",
                "int": "整数",
                "float": "小数",
            }.get(option.type, "")
            entries.append(
                UiEntry(
                    title=f"配置: {option.name}",
                    subtitle=f"{option.description}  当前值={plugin.get_config(option.key)}  {type_hint}".strip(),
                    icon="⚙️",
                    payload=None,
                )
            )
        return entries

    def search_at(self, at_keyword: str, rest: str, plugin=None) -> list[UiEntry]:
        target = plugin if plugin is not None else self.find_at_plugin(at_keyword)
        if target is None:
            return []
        results = self._plugin_manager.search_at(at_keyword, rest)
        return [
            UiEntry(
                title=result.title,
                subtitle=result.subtitle,
                icon=result.icon or target.meta.icon,
                payload=result,
            )
            for result in results
        ]

    def execute(self, payload: Any) -> tuple[bool, str]:
        if payload is None:
            return False, "无可执行项"
        if isinstance(payload, tuple) and payload and payload[0] == "at_select":
            return True, f"切换插件: @{payload[1]}"

        plugin = self._plugin_manager.plugins.get(payload.plugin_id)
        if plugin is None:
            return False, "插件不存在或已卸载"
        plugin.execute(payload)
        return True, f"已执行: {payload.title}"

    @staticmethod
    def banner_for_plugin(plugin) -> dict[str, str]:
        return {
            "icon": plugin.meta.icon,
            "title": f"@{plugin.meta.at_keyword} - {plugin.meta.name}",
            "hint": plugin.meta.description,
        }

    def _resolve_icon(self, result) -> str:
        if result.icon:
            return result.icon
        plugin = self._plugin_manager.plugins.get(result.plugin_id)
        if plugin:
            return plugin.meta.icon
        return "🔌"
