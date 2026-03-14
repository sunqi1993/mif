"""Plugin system for alfredpy."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Any, Callable
import importlib
import pkgutil
from pathlib import Path


@dataclass
class PluginMeta:
    """Plugin metadata."""

    id: str
    name: str
    description: str
    version: str = "1.0.0"
    author: str = ""
    keywords: List[str] = field(default_factory=list)
    priority: int = 100  # Lower number = higher priority


@dataclass
class PluginResult:
    """Plugin search result."""

    title: str
    subtitle: str = ""
    action: Optional[Callable] = None
    action_args: tuple = ()
    score: float = 0.0
    plugin_id: str = ""


class BasePlugin(ABC):
    """Base plugin class."""

    def __init__(self):
        self.meta = self.get_meta()

    @abstractmethod
    def get_meta(self) -> PluginMeta:
        """Return plugin metadata."""
        pass

    @abstractmethod
    def search(self, query: str) -> List[PluginResult]:
        """Search for items matching the query."""
        pass

    def match_keyword(self, query: str) -> bool:
        """Check if query matches plugin keywords."""
        if not self.meta.keywords:
            return True
        return any(query.startswith(kw) for kw in self.meta.keywords)

    def strip_keyword(self, query: str) -> str:
        """Remove keyword prefix from query."""
        for kw in sorted(self.meta.keywords, key=len, reverse=True):
            if query.startswith(kw + " "):
                return query[len(kw) + 1 :]
            elif query.startswith(kw):
                return query[len(kw) :]
        return query

    def execute(self, result: PluginResult) -> Any:
        """Execute the selected result."""
        if result.action:
            return result.action(*result.action_args)
        return None


class PluginManager:
    """Plugin manager for discovering and managing plugins."""

    def __init__(self):
        self.plugins: dict[str, BasePlugin] = {}
        self._discover_plugins()

    def _discover_plugins(self):
        """Automatically discover and load plugins."""
        plugins_dir = Path(__file__).parent / "plugins"

        if not plugins_dir.exists():
            return

        for _, name, _ in pkgutil.iter_modules([str(plugins_dir)]):
            if name == "base":
                continue

            try:
                module = importlib.import_module(f"alfredpy.plugins.{name}")

                # Find Plugin classes
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, BasePlugin)
                        and attr is not BasePlugin
                    ):
                        self.register(attr())
            except Exception as e:
                print(f"Failed to load plugin {name}: {e}")

    def register(self, plugin: BasePlugin):
        """Register a plugin."""
        self.plugins[plugin.meta.id] = plugin
        print(f"✓ Loaded plugin: {plugin.meta.name} v{plugin.meta.version}")

    def unregister(self, plugin_id: str):
        """Unregister a plugin."""
        if plugin_id in self.plugins:
            del self.plugins[plugin_id]

    def search(self, query: str) -> List[PluginResult]:
        """Search all matching plugins."""
        all_results = []

        for plugin in self.plugins.values():
            if plugin.match_keyword(query):
                clean_query = plugin.strip_keyword(query)
                results = plugin.search(clean_query)

                for result in results:
                    result.plugin_id = plugin.meta.id
                    result.score = self._calculate_score(result, query)

                all_results.extend(results)

        # Sort by score descending
        return sorted(all_results, key=lambda x: x.score, reverse=True)

    def _calculate_score(self, result: PluginResult, query: str) -> float:
        """Calculate relevance score for a result."""
        try:
            from thefuzz import fuzz

            title_score = fuzz.partial_ratio(query.lower(), result.title.lower())
            subtitle_score = (
                fuzz.partial_ratio(query.lower(), result.subtitle.lower())
                if result.subtitle
                else 0
            )

            return max(title_score, subtitle_score) * 0.01
        except ImportError:
            # Fallback to simple matching
            query_lower = query.lower()
            if query_lower in result.title.lower():
                return 1.0
            elif result.subtitle and query_lower in result.subtitle.lower():
                return 0.8
            return 0.5
