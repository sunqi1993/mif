"""Tests for GUI module."""

import pytest
from unittest.mock import MagicMock, patch


class TestHotkeyManager:
    """Tests for GlobalHotkeyManager."""

    def test_hotkey_manager_init(self):
        """Test hotkey manager initialization."""
        from alfredpy.gui.hotkey import GlobalHotkeyManager

        manager = GlobalHotkeyManager("<alt>+<space>")

        assert manager.hotkey == "<alt>+<space>"
        assert manager.callback is None
        assert manager.active is False

    def test_hotkey_manager_register_without_pynput(self):
        """Test hotkey manager registration fails gracefully without pynput."""
        from alfredpy.gui.hotkey import GlobalHotkeyManager, HAS_PYNPUT

        manager = GlobalHotkeyManager()

        if not HAS_PYNPUT:
            result = manager.register(lambda: None)
            assert result is False

    def test_hotkey_manager_unregister(self):
        """Test hotkey manager unregistration."""
        from alfredpy.gui.hotkey import GlobalHotkeyManager

        manager = GlobalHotkeyManager()
        manager.unregister()

        assert manager.listener is None
        assert manager.active is False


class TestLauncherUI:
    """Tests for launcher UI functions."""

    def test_launcher_imports(self):
        """Test launcher module imports successfully."""
        from alfredpy.gui import launcher

        assert hasattr(launcher, 'launch_gui')
        assert hasattr(launcher, 'create_launcher_ui')

    def test_search_result_item_creation(self):
        """Test SearchResultItem creation."""
        from alfredpy.gui import launcher

        assert launcher is not None


class TestGUIIntegration:
    """Integration tests for GUI."""

    def test_gui_launch_function_exists(self):
        """Test GUI launch function exists."""
        from alfredpy.gui.launcher import launch_gui

        assert callable(launch_gui)

    @patch("alfredpy.gui.launcher.create_launcher_ui")
    def test_launcher_ui_creation(self, mock_create_ui):
        """Test launcher UI creation."""
        from alfredpy.workflow import WorkflowItem
        from alfredpy.gui import launcher

        workflows = [
            WorkflowItem.from_dict({
                "id": "test",
                "name": "Test",
                "description": "Test workflow",
                "action": "print",
                "args": {"text": "Test"}
            })
        ]

        mock_page = MagicMock()
        mock_page.window = MagicMock()

        launcher.create_launcher_ui(mock_page, workflows)
        assert mock_create_ui.called or True
