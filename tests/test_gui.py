"""Tests for GUI module."""

import pytest
from unittest.mock import MagicMock, patch


class TestHotkeyManager:
    """Tests for GlobalHotkeyManager."""

    def test_hotkey_manager_init(self):
        """Test hotkey manager initialization."""
        from mif.gui.hotkey import GlobalHotkeyManager

        manager = GlobalHotkeyManager("<alt>+<space>")

        assert manager.hotkey == "<alt>+<space>"
        assert manager.callback is None
        assert manager.active is False

    def test_hotkey_manager_register_without_pynput(self):
        """Test hotkey manager registration fails gracefully without pynput."""
        from mif.gui.hotkey import GlobalHotkeyManager, HAS_PYNPUT

        manager = GlobalHotkeyManager()

        if not HAS_PYNPUT:
            result = manager.register(lambda: None)
            assert result is False

    def test_hotkey_manager_unregister(self):
        """Test hotkey manager unregistration."""
        from mif.gui.hotkey import GlobalHotkeyManager

        manager = GlobalHotkeyManager()
        manager.unregister()

        assert manager.listener is None
        assert manager.active is False


class TestLauncherUI:
    """Tests for launcher UI functions."""

    def test_launcher_imports(self):
        """Test launcher module imports successfully."""
        from mif.gui import launcher

        assert hasattr(launcher, "launch_gui")

    def test_result_item_creation(self):
        """Test ResultItem creation."""
        from mif.gui.launcher import ResultItem

        item = ResultItem(title="Test", subtitle="Test Desc", icon="🚀")
        assert item is not None


class TestGUIIntegration:
    """Integration tests for GUI."""

    def test_gui_launch_function_exists(self):
        """Test GUI launch function exists."""
        from mif.gui.launcher import launch_gui

        assert callable(launch_gui)

    @patch("mif.config.load_config")
    @patch("mif.gui.launcher.ft.app")
    def test_gui_launch_with_workflows(self, mock_app, mock_load_config):
        """Test GUI launch with workflows."""
        from mif.gui.launcher import launch_gui
        from mif.workflow import WorkflowItem

        workflows = [
            WorkflowItem.from_dict(
                {
                    "id": "test1",
                    "name": "Test Workflow",
                    "description": "Test",
                    "action": "print",
                    "args": {"text": "Test"},
                }
            )
        ]

        mock_load_config.return_value = workflows
        launch_gui()
        mock_app.assert_called_once()
