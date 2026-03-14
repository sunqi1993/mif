"""Base classes for alfredpy plugins."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional


# ── Config schema ─────────────────────────────────────────────────────────────

@dataclass
class ConfigOption:
    """Declares one configurable option for a plugin."""

    key: str
    name: str
    description: str = ""
    # Supported types: "str" | "int" | "float" | "bool" | "choice"
    type: str = "str"
    default: Any = None
    choices: List[str] = field(default_factory=list)

    def coerce(self, value: Any) -> Any:
        """Cast a raw value (e.g. from JSON) to the correct Python type."""
        if value is None:
            return self.default
        try:
            if self.type == "int":
                return int(value)
            if self.type == "float":
                return float(value)
            if self.type == "bool":
                if isinstance(value, str):
                    return value.lower() in ("1", "true", "yes")
                return bool(value)
            if self.type == "choice":
                return str(value) if str(value) in self.choices else self.default
        except (ValueError, TypeError):
            return self.default
        return value


# ── Plugin metadata ───────────────────────────────────────────────────────────

@dataclass
class PluginMeta:
    """Metadata that every plugin must declare."""

    id: str
    name: str
    description: str
    version: str = "1.0.0"
    author: str = ""
    icon: str = "🔌"                              # emoji shown in the UI
    keywords: List[str] = field(default_factory=list)  # prefix triggers ("=", "calc")
    at_keyword: str = ""                          # @-trigger in the search box, e.g. "calc"
    priority: int = 100                           # lower = higher priority
    config_options: List[ConfigOption] = field(default_factory=list)


# ── Plugin result ─────────────────────────────────────────────────────────────

@dataclass
class PluginResult:
    """A single search result returned by a plugin."""

    title: str
    subtitle: str = ""
    action: Optional[Callable] = None
    action_args: tuple = ()
    score: float = 0.0
    plugin_id: str = ""


# ── Base plugin ───────────────────────────────────────────────────────────────

class BasePlugin(ABC):
    """Abstract base class for all alfredpy plugins."""

    def __init__(self):
        self.meta: PluginMeta = self.get_meta()
        self._config: dict = {}          # runtime config (loaded by PluginManager)

    # ── Abstract interface ────────────────────────────────────────────────────

    @abstractmethod
    def get_meta(self) -> PluginMeta:
        """Return static plugin metadata."""

    @abstractmethod
    def search(self, query: str) -> List[PluginResult]:
        """Return results matching *query*."""

    # ── Config helpers ────────────────────────────────────────────────────────

    def configure(self, config: dict) -> None:
        """Apply a config dict (called by PluginManager after loading from disk)."""
        self._config = {k: v for k, v in config.items()}

    def get_config(self, key: str, default: Any = None) -> Any:
        """Return the current value for a config key.

        Priority: runtime config → option default → caller-supplied default.
        """
        if key in self._config:
            # Coerce to the declared type if a schema exists
            for opt in self.meta.config_options:
                if opt.key == key:
                    return opt.coerce(self._config[key])
            return self._config[key]
        for opt in self.meta.config_options:
            if opt.key == key:
                return opt.default
        return default

    def config_summary(self) -> dict:
        """Return {key: current_value} for every declared option."""
        return {opt.key: self.get_config(opt.key) for opt in self.meta.config_options}

    # ── Keyword helpers ───────────────────────────────────────────────────────

    def match_keyword(self, query: str) -> bool:
        """Return True if *query* starts with one of the plugin's trigger keywords."""
        if not self.meta.keywords:
            return True
        return any(query.startswith(kw) for kw in self.meta.keywords)

    def strip_keyword(self, query: str) -> str:
        """Remove the leading trigger keyword (+ optional space) from *query*."""
        for kw in sorted(self.meta.keywords, key=len, reverse=True):
            if query.startswith(kw + " "):
                return query[len(kw) + 1:]
            if query.startswith(kw):
                return query[len(kw):]
        return query

    # ── Execution ─────────────────────────────────────────────────────────────

    def execute(self, result: PluginResult) -> Any:
        """Run the action attached to a result."""
        if result.action:
            return result.action(*result.action_args)
        return None
