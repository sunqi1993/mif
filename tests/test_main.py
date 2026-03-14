"""Tests for main module."""

import pytest
from unittest.mock import MagicMock, patch


class TestLoadWorkflows:
    """Tests for _load_workflows function."""

    @patch("mif.main.load_config")
    def test_load_workflows(self, mock_load_config):
        """Test loading workflows from config."""
        from mif.workflow import WorkflowItem
        from mif.main import _load_workflows

        mock_load_config.return_value = {
            "workflows": [
                {"id": "1", "name": "Test", "description": "Test", "action": "print", "args": {}}
            ]
        }

        workflows = _load_workflows()

        assert len(workflows) == 1
        assert isinstance(workflows[0], WorkflowItem)
        assert workflows[0].name == "Test"

    @patch("mif.main.load_config")
    def test_load_workflows_empty_config(self, mock_load_config):
        """Test loading workflows from empty config."""
        from mif.main import _load_workflows

        mock_load_config.return_value = {}

        workflows = _load_workflows()

        assert len(workflows) == 0

    @patch("mif.main.load_config")
    def test_load_workflows_with_config_path(self, mock_load_config):
        """Test loading workflows with custom config path."""
        from mif.main import _load_workflows

        mock_load_config.return_value = {"workflows": []}

        _load_workflows("/custom/path.json")

        mock_load_config.assert_called_once_with("/custom/path.json")


class TestMain:
    """Tests for main function."""

    @patch("mif.main._load_workflows")
    @patch("builtins.print")
    def test_main_list_flag(self, mock_print, mock_load):
        """Test main with --list flag."""
        from mif.workflow import WorkflowItem
        from mif.main import main

        mock_load.return_value = [
            WorkflowItem(id="1", name="Test", description="Test Desc", action="print", args={})
        ]

        result = main(["--list"])

        assert result == 0
        assert mock_print.call_count >= 1

    @patch("mif.main._load_workflows")
    @patch("builtins.print")
    def test_main_no_workflows(self, mock_print, mock_load):
        """Test main when no workflows available."""
        from mif.main import main

        mock_load.return_value = []

        result = main([])

        assert result == 1
        assert mock_print.call_count >= 1

    @patch("mif.main._load_workflows")
    @patch("mif.gui.launcher.launch_gui")
    def test_main_gui_flag(self, mock_launch_gui, mock_load):
        """Test main with --gui flag."""
        from mif.main import main

        mock_load.return_value = []

        result = main(["--gui"])

        assert result == 0
        mock_launch_gui.assert_called_once()

    @patch("mif.main._load_workflows")
    def test_main_version_flag(self, mock_load):
        """Test main with --version flag."""
        from mif.main import main

        mock_load.return_value = []

        with pytest.raises(SystemExit):
            main(["--version"])
