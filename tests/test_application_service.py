"""Tests for application service layer."""

import pytest
from unittest.mock import MagicMock, Mock
from mif.application.service import ApplicationService, UiEntry
from mif.plugins.base import PluginMeta, PluginResult, ConfigOption


class TestApplicationServiceSearchNormal:
    """Tests for search_normal method."""

    @pytest.fixture
    def mock_manager(self):
        """Create a mock plugin manager."""
        manager = MagicMock()
        manager.search.return_value = [
            PluginResult(
                title="= 3",
                subtitle="1+2=3",
                plugin_id="calculator",
                score=1.0,
                icon="🧮",
            ),
            PluginResult(
                title="GitHub",
                subtitle="https://github.com",
                plugin_id="bookmarks",
                score=0.8,
                icon="📑",
            ),
        ]
        return manager

    def test_search_normal_returns_ui_entries(self, mock_manager):
        """Test that search_normal returns UiEntry objects."""
        service = ApplicationService(mock_manager)
        entries = service.search_normal("1+2")

        assert len(entries) == 2
        assert all(isinstance(entry, UiEntry) for entry in entries)

    def test_search_normal_prioritizes_calculator(self, mock_manager):
        """Test calculator results appear first."""
        service = ApplicationService(mock_manager)
        entries = service.search_normal("1+2")

        assert entries[0].title == "= 3"
        assert entries[0].icon == "🧮"

    def test_search_normal_limits_others_to_40(self):
        """Test that non-calculator results are limited to 40."""
        mock_manager = MagicMock()
        many_results = [
            PluginResult(title=f"Result {i}", plugin_id="other", score=0.5)
            for i in range(50)
        ]
        mock_manager.search.return_value = many_results

        service = ApplicationService(mock_manager)
        entries = service.search_normal("test")

        assert len(entries) == 40

    def test_search_normal_resolves_missing_icons(self):
        """Test icon resolution for results without icons."""
        mock_manager = MagicMock()
        mock_manager.plugins = {
            "test_plugin": MagicMock(
                meta=PluginMeta(
                    id="test_plugin",
                    name="Test",
                    description="Test",
                    icon="🔧",
                    priority=10,
                )
            )
        }
        mock_manager.search.return_value = [
            PluginResult(title="Test", plugin_id="test_plugin")
        ]

        service = ApplicationService(mock_manager)
        entries = service.search_normal("test")

        assert len(entries) == 1
        assert entries[0].icon == "🔧"

    def test_search_normal_default_icon_for_unknown_plugin(self):
        """Test default icon for unknown plugin."""
        mock_manager = MagicMock()
        mock_manager.plugins = {}
        mock_manager.search.return_value = [
            PluginResult(title="Test", plugin_id="unknown_plugin")
        ]

        service = ApplicationService(mock_manager)
        entries = service.search_normal("test")

        assert entries[0].icon == "🔌"

    def test_search_normal_empty_results(self):
        """Test handling of empty search results."""
        mock_manager = MagicMock()
        mock_manager.search.return_value = []

        service = ApplicationService(mock_manager)
        entries = service.search_normal("nonexistent")

        assert len(entries) == 0


class TestApplicationServiceAtPlugins:
    """Tests for @ plugin related methods."""

    @pytest.fixture
    def mock_manager(self):
        """Create mock manager with multiple @ plugins."""
        manager = MagicMock()
        calculator_plugin = MagicMock()
        calculator_plugin.meta = PluginMeta(
            id="calculator",
            name="Calculator",
            description="Calculate",
            icon="🧮",
            at_keyword="calc",
            priority=10,
        )
        bookmark_plugin = MagicMock()
        bookmark_plugin.meta = PluginMeta(
            id="bookmarks",
            name="Bookmarks",
            description="Search bookmarks",
            icon="📑",
            at_keyword="bm",
            priority=20,
        )
        workflow_plugin = MagicMock()
        workflow_plugin.meta = PluginMeta(
            id="workflow",
            name="Workflow",
            description="Workflows",
            icon="⚡",
            at_keyword="wf",
            priority=30,
        )
        manager.all_at_plugins.return_value = [
            calculator_plugin,
            bookmark_plugin,
            workflow_plugin,
        ]
        manager.find_by_at_keyword.side_effect = lambda kw: {
            "calc": calculator_plugin,
            "bm": bookmark_plugin,
            "wf": workflow_plugin,
        }.get(kw)
        return manager

    def test_list_at_plugins_no_filter(self, mock_manager):
        """Test listing all @ plugins without filter."""
        service = ApplicationService(mock_manager)
        entries = service.list_at_plugins("")

        assert len(entries) == 3
        assert all(isinstance(entry, UiEntry) for entry in entries)
        assert entries[0].payload[0] == "at_select"

    def test_list_at_plugins_filters_by_prefix(self, mock_manager):
        """Test filtering @ plugins by prefix."""
        service = ApplicationService(mock_manager)
        entries = service.list_at_plugins("c")

        assert len(entries) == 1
        assert entries[0].payload == ("at_select", "calc")

    def test_list_at_plugins_case_insensitive(self, mock_manager):
        """Test prefix filtering is case insensitive."""
        service = ApplicationService(mock_manager)
        entries_c = service.list_at_plugins("c")
        entries_C = service.list_at_plugins("C")

        assert len(entries_c) == len(entries_C)

    def test_list_at_plugins_no_matches(self, mock_manager):
        """Test when no plugins match prefix."""
        service = ApplicationService(mock_manager)
        entries = service.list_at_plugins("xyz")

        assert len(entries) == 0

    def test_find_at_plugin_exists(self, mock_manager):
        """Test finding existing @ plugin."""
        service = ApplicationService(mock_manager)
        plugin = service.find_at_plugin("calc")

        assert plugin is not None
        assert plugin.meta.id == "calculator"

    def test_find_at_plugin_not_exists(self, mock_manager):
        """Test finding non-existent @ plugin."""
        service = ApplicationService(mock_manager)
        plugin = service.find_at_plugin("nonexistent")

        assert plugin is None


class TestApplicationServiceSearchAt:
    """Tests for search_at method."""

    @pytest.fixture
    def mock_manager(self):
        """Create mock manager."""
        manager = MagicMock()
        calculator_plugin = MagicMock()
        calculator_plugin.meta = PluginMeta(
            id="calculator",
            name="Calculator",
            description="Calculate",
            icon="🧮",
            at_keyword="calc",
            priority=10,
        )
        manager.find_by_at_keyword.return_value = calculator_plugin
        manager.search_at.return_value = [
            PluginResult(
                title="= 5", subtitle="2+3", plugin_id="calculator", icon="🧮"
            ),
        ]
        return manager

    def test_search_at_with_plugin(self, mock_manager):
        """Test search with explicit plugin parameter."""
        service = ApplicationService(mock_manager)
        entries = service.search_at("calc", "2+3")

        assert len(entries) == 1
        assert entries[0].title == "= 5"

    def test_search_at_without_plugin(self, mock_manager):
        """Test search without explicit plugin (auto-find)."""
        service = ApplicationService(mock_manager)
        entries = service.search_at("calc", "2+3", plugin=None)

        assert len(entries) == 1
        mock_manager.find_by_at_keyword.assert_called_once_with("calc")

    def test_search_at_plugin_not_found(self):
        """Test search when plugin not found."""
        mock_manager = MagicMock()
        mock_manager.find_by_at_keyword.return_value = None

        service = ApplicationService(mock_manager)
        entries = service.search_at("nonexistent", "query")

        assert len(entries) == 0

    def test_search_at_empty_results(self, mock_manager):
        """Test search with empty results."""
        mock_manager.search_at.return_value = []

        service = ApplicationService(mock_manager)
        entries = service.search_at("calc", "")

        assert len(entries) == 0

    def test_search_at_uses_result_icon_or_plugin_icon(self, mock_manager):
        """Test icon priority: result icon > plugin icon."""
        mock_manager.search_at.return_value = [
            PluginResult(title="Result 1", plugin_id="calculator", icon="⭐"),
            PluginResult(title="Result 2", plugin_id="calculator"),
        ]

        service = ApplicationService(mock_manager)
        entries = service.search_at("calc", "test")

        assert entries[0].icon == "⭐"
        assert entries[1].icon == "🧮"


class TestApplicationServicePluginConfig:
    """Tests for plugin_config_entries method."""

    def test_plugin_config_entries_with_options(self):
        """Test plugin with config options."""
        mock_manager = MagicMock()
        plugin = MagicMock()
        plugin.meta = PluginMeta(
            id="test",
            name="Test",
            description="Test",
            icon="🔧",
            at_keyword="test",
            priority=10,
            config_options=[
                ConfigOption(
                    key="opt1",
                    name="Option 1",
                    description="First option",
                    type="str",
                    default="default",
                ),
                ConfigOption(
                    key="opt2",
                    name="Option 2",
                    description="Second option",
                    type="int",
                    default=42,
                ),
            ],
        )
        plugin.get_config.side_effect = lambda k: {"opt1": "current", "opt2": 100}.get(
            k
        )

        service = ApplicationService(mock_manager)
        entries = service.plugin_config_entries(plugin)

        assert len(entries) == 2
        assert "Option 1" in entries[0].title
        assert "Option 2" in entries[1].title

    def test_plugin_config_entries_no_options(self):
        """Test plugin without config options."""
        mock_manager = MagicMock()
        plugin = MagicMock()
        plugin.meta = PluginMeta(
            id="test",
            name="Test",
            description="Test",
            icon="🔧",
            at_keyword="test",
            priority=10,
            config_options=[],
        )

        service = ApplicationService(mock_manager)
        entries = service.plugin_config_entries(plugin)

        assert len(entries) == 1
        assert "已就绪" in entries[0].title

    def test_plugin_config_entries_choice_type_hint(self):
        """Test choice type shows available choices."""
        mock_manager = MagicMock()
        plugin = MagicMock()
        plugin.meta = PluginMeta(
            id="test",
            name="Test",
            description="Test",
            icon="🔧",
            at_keyword="test",
            priority=10,
            config_options=[
                ConfigOption(
                    key="mode",
                    name="Mode",
                    description="Select mode",
                    type="choice",
                    default="auto",
                    choices=["auto", "manual", "expert"],
                ),
            ],
        )
        plugin.get_config.return_value = "auto"

        service = ApplicationService(mock_manager)
        entries = service.plugin_config_entries(plugin)

        assert "auto / manual / expert" in entries[0].subtitle

    def test_plugin_config_entries_bool_type_hint(self):
        """Test bool type shows true/false hint."""
        mock_manager = MagicMock()
        plugin = MagicMock()
        plugin.meta = PluginMeta(
            id="test",
            name="Test",
            description="Test",
            icon="🔧",
            at_keyword="test",
            priority=10,
            config_options=[
                ConfigOption(
                    key="enabled",
                    name="Enabled",
                    description="Enable feature",
                    type="bool",
                    default=True,
                ),
            ],
        )
        plugin.get_config.return_value = True

        service = ApplicationService(mock_manager)
        entries = service.plugin_config_entries(plugin)

        assert "true / false" in entries[0].subtitle


class TestApplicationServiceExecute:
    """Tests for execute method."""

    @pytest.fixture
    def mock_manager(self):
        """Create mock manager with plugin."""
        manager = MagicMock()
        plugin = MagicMock()
        plugin.execute.return_value = "Execution result"
        manager.plugins = {"test_plugin": plugin}
        return manager

    def test_execute_with_at_select_payload(self):
        """Test executing @ select payload."""
        mock_manager = MagicMock()
        service = ApplicationService(mock_manager)

        ok, message = service.execute(("at_select", "calc"))

        assert ok is True
        assert "切换插件" in message
        assert "@calc" in message

    def test_execute_with_normal_payload(self, mock_manager):
        """Test executing normal payload."""
        service = ApplicationService(mock_manager)
        payload = PluginResult(title="Test Action", plugin_id="test_plugin")

        ok, message = service.execute(payload)

        assert ok is True
        assert "已执行" in message
        assert "Test Action" in message
        mock_manager.plugins["test_plugin"].execute.assert_called_once()

    def test_execute_with_none_payload(self):
        """Test executing None payload."""
        mock_manager = MagicMock()
        service = ApplicationService(mock_manager)

        ok, message = service.execute(None)

        assert ok is False
        assert "无可执行项" in message

    def test_execute_with_unknown_plugin(self):
        """Test executing payload with unknown plugin."""
        mock_manager = MagicMock()
        mock_manager.plugins = {}
        service = ApplicationService(mock_manager)

        payload = PluginResult(title="Test", plugin_id="unknown")
        ok, message = service.execute(payload)

        assert ok is False
        assert "插件不存在" in message

    def test_execute_plugin_raises_exception(self):
        """Test handling plugin execution exceptions."""
        mock_manager = MagicMock()
        plugin = MagicMock()
        plugin.execute.side_effect = RuntimeError("Execution failed")
        mock_manager.plugins = {"test_plugin": plugin}
        service = ApplicationService(mock_manager)

        payload = PluginResult(title="Test", plugin_id="test_plugin")

        with pytest.raises(RuntimeError):
            service.execute(payload)


class TestApplicationServiceBanner:
    """Tests for banner_for_plugin method."""

    def test_banner_for_plugin_returns_dict(self):
        """Test banner returns correct dict structure."""
        mock_manager = MagicMock()
        plugin = MagicMock()
        plugin.meta = PluginMeta(
            id="test",
            name="Test Plugin",
            description="Test Description",
            icon="🔧",
            at_keyword="test",
            priority=10,
        )

        service = ApplicationService(mock_manager)
        banner = service.banner_for_plugin(plugin)

        assert isinstance(banner, dict)
        assert banner["icon"] == "🔧"
        assert banner["title"] == "@test - Test Plugin"
        assert banner["hint"] == "Test Description"

    def test_banner_for_plugin_empty_at_keyword(self):
        """Test banner with empty @ keyword."""
        mock_manager = MagicMock()
        plugin = MagicMock()
        plugin.meta = PluginMeta(
            id="test",
            name="Test",
            description="Test",
            icon="🔧",
            at_keyword="",
            priority=10,
        )

        service = ApplicationService(mock_manager)
        banner = service.banner_for_plugin(plugin)

        assert banner["title"] == "@ - Test"


class TestUiEntry:
    """Tests for UiEntry dataclass."""

    def test_ui_entry_creation(self):
        """Test creating UiEntry instance."""
        entry = UiEntry(
            title="Test Title",
            subtitle="Test Subtitle",
            icon="🔧",
            payload={"key": "value"},
        )

        assert entry.title == "Test Title"
        assert entry.subtitle == "Test Subtitle"
        assert entry.icon == "🔧"
        assert entry.payload == {"key": "value"}

    def test_ui_entry_default_icon(self):
        """Test UiEntry with default icon."""
        entry = UiEntry(title="Test", subtitle="Test", icon="", payload=None)

        assert entry.icon == ""
