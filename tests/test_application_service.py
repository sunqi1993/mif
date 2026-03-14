"""Tests for application service layer."""

from mif.application import ApplicationService
from mif.plugins.base import PluginMeta, PluginResult


class _FakePlugin:
    def __init__(self, plugin_id: str, icon: str, at_keyword: str = ""):
        self.meta = PluginMeta(
            id=plugin_id,
            name=plugin_id,
            description=f"{plugin_id} plugin",
            icon=icon,
            at_keyword=at_keyword,
            priority=10,
        )

    def execute(self, result):
        return result.title


class _FakeManager:
    def __init__(self):
        self.plugins = {
            "calculator": _FakePlugin("calculator", "🧮", at_keyword="calc"),
            "bookmarks": _FakePlugin("bookmarks", "📑", at_keyword="bm"),
        }

    def search(self, query: str):
        return [
            PluginResult(title="= 3", subtitle="1+2=3", plugin_id="calculator", score=1.0),
            PluginResult(title="GitHub", subtitle="https://github.com", plugin_id="bookmarks", score=0.8),
        ]

    def all_at_plugins(self):
        return list(self.plugins.values())

    def find_by_at_keyword(self, keyword: str):
        for p in self.plugins.values():
            if p.meta.at_keyword == keyword:
                return p
        return None

    def search_at(self, at_keyword: str, rest: str):
        if at_keyword == "calc":
            return [PluginResult(title="= 3", subtitle=f"{rest}=3", plugin_id="calculator", score=1.0)]
        return []


def test_search_normal_prioritizes_calculator():
    service = ApplicationService(_FakeManager())
    entries = service.search_normal("1+2")

    assert entries[0].title == "= 3"
    assert entries[0].icon == "🧮"
    assert entries[1].icon == "📑"


def test_list_at_plugins_filters_by_prefix():
    service = ApplicationService(_FakeManager())
    entries = service.list_at_plugins("c")
    assert len(entries) == 1
    assert entries[0].payload == ("at_select", "calc")


def test_execute_returns_success_message():
    service = ApplicationService(_FakeManager())
    payload = PluginResult(title="Open GitHub", plugin_id="bookmarks")

    ok, message = service.execute(payload)

    assert ok is True
    assert "已执行" in message
