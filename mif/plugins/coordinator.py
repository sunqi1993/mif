"""Search coordination across plugins."""

from __future__ import annotations

from typing import List, Optional

from mif.plugins.base import BasePlugin, PluginResult


class PluginSearchCoordinator:
    """Route @-queries and aggregate normal searches."""

    def __init__(self, plugins: dict[str, BasePlugin]):
        self._plugins = plugins

    def find_by_at_keyword(self, keyword: str) -> Optional[BasePlugin]:
        kw = keyword.lower()
        for plugin in self._plugins.values():
            if plugin.meta.at_keyword and plugin.meta.at_keyword.lower() == kw:
                return plugin
        return None

    def all_at_plugins(self) -> List[BasePlugin]:
        return [p for p in self._plugins.values() if p.meta.at_keyword]

    def search_at(self, at_keyword: str, query: str) -> List[PluginResult]:
        plugin = self.find_by_at_keyword(at_keyword)
        if plugin is None:
            return []
        results = plugin.search(query)
        for result in results:
            result.plugin_id = plugin.meta.id
        return results

    def search(self, query: str) -> List[PluginResult]:
        all_results: List[PluginResult] = []
        for plugin in sorted(self._plugins.values(), key=lambda p: p.meta.priority):
            if plugin.match_keyword(query):
                clean = plugin.strip_keyword(query)
                results = plugin.search(clean)
                for result in results:
                    result.plugin_id = plugin.meta.id
                    if result.score == 0.0:
                        result.score = self._score(result, query)
                all_results.extend(results)
        return sorted(all_results, key=lambda r: r.score, reverse=True)

    @staticmethod
    def _score(result: PluginResult, query: str) -> float:
        try:
            from thefuzz import fuzz

            title_score = fuzz.partial_ratio(query.lower(), result.title.lower())
            subtitle_score = fuzz.partial_ratio(query.lower(), result.subtitle.lower()) if result.subtitle else 0
            return max(title_score, subtitle_score) * 0.01
        except ImportError:
            q = query.lower()
            if q in result.title.lower():
                return 1.0
            if result.subtitle and q in result.subtitle.lower():
                return 0.8
            return 0.5
