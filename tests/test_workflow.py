"""Tests for workflow module."""

import json
import subprocess
import webbrowser
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from alfredpy.workflow import ActionRegistry, WorkflowItem


class TestActionRegistry:
    """Tests for ActionRegistry class."""

    def test_register_action(self):
        """Test registering a new action."""
        # Clear registry for clean test
        ActionRegistry._registry.clear()

        @ActionRegistry.register("test_action")
        def test_func(args):
            pass

        assert "test_action" in ActionRegistry._registry

    def test_run_registered_action(self):
        """Test running a registered action."""
        ActionRegistry._registry.clear()
        called_with = {}

        @ActionRegistry.register("mock_action")
        def mock_func(args):
            called_with.update(args)

        ActionRegistry.run("mock_action", {"key": "value"})
        assert called_with == {"key": "value"}

    def test_run_unknown_action(self):
        """Test running an unknown action raises KeyError."""
        ActionRegistry._registry.clear()
        with pytest.raises(KeyError, match="Unknown action 'unknown'"):
            ActionRegistry.run("unknown")

    def test_run_action_with_no_args(self):
        """Test running action without arguments."""
        ActionRegistry._registry.clear()
        called = False

        @ActionRegistry.register("no_args_action")
        def no_args_func(args):
            nonlocal called
            called = True

        ActionRegistry.run("no_args_action")
        assert called


class TestWorkflowItem:
    """Tests for WorkflowItem class."""

    def test_from_dict(self):
        """Test creating WorkflowItem from dictionary."""
        data = {
            "id": "test_id",
            "name": "Test Name",
            "description": "Test Description",
            "action": "print",
            "args": {"text": "Hello"},
        }
        item = WorkflowItem.from_dict(data)

        assert item.id == "test_id"
        assert item.name == "Test Name"
        assert item.description == "Test Description"
        assert item.action == "print"
        assert item.args == {"text": "Hello"}

    def test_from_dict_with_missing_fields(self):
        """Test creating WorkflowItem with missing fields."""
        data = {"id": "test_id", "name": "Test"}
        item = WorkflowItem.from_dict(data)

        assert item.id == "test_id"
        assert item.name == "Test"
        assert item.description == ""
        assert item.action == ""
        assert item.args == {}

    def test_from_dict_with_none_args(self):
        """Test creating WorkflowItem with None args."""
        data = {
            "id": "test_id",
            "name": "Test",
            "args": None,
        }
        item = WorkflowItem.from_dict(data)
        assert item.args == {}

    @patch.object(ActionRegistry, "run")
    def test_run_workflow_item(self, mock_run):
        """Test running a workflow item."""
        item = WorkflowItem(
            id="test",
            name="Test",
            description="Test Desc",
            action="print",
            args={"text": "Hello"},
        )
        item.run()
        mock_run.assert_called_once_with("print", {"text": "Hello"})


class TestBuiltInActions:
    """Tests for built-in action implementations."""

    def test_action_print(self, capsys):
        """Test print action outputs to stdout."""
        from alfredpy.workflow import action_print

        action_print({"text": "Hello World"})
        captured = capsys.readouterr()
        assert "Hello World\n" == captured.out

    def test_action_print_with_empty_text(self, capsys):
        """Test print action with empty text."""
        from alfredpy.workflow import action_print

        action_print({"text": ""})
        captured = capsys.readouterr()
        assert "\n" == captured.out

    @patch.object(webbrowser, "open")
    def test_action_open_url(self, mock_open):
        """Test open_url action opens browser."""
        from alfredpy.workflow import action_open_url

        action_open_url({"url": "https://example.com"})
        mock_open.assert_called_once_with("https://example.com")

    def test_action_open_url_missing_url(self):
        """Test open_url action raises error without URL."""
        from alfredpy.workflow import action_open_url

        with pytest.raises(ValueError, match="`url` is required"):
            action_open_url({})

    @patch.object(subprocess, "run")
    def test_action_run(self, mock_run):
        """Test run action executes command."""
        from alfredpy.workflow import action_run

        action_run({"command": ["echo", "hello"]})
        mock_run.assert_called_once_with(["echo", "hello"], cwd=None, check=False)

    def test_action_run_missing_command(self):
        """Test run action raises error without command."""
        from alfredpy.workflow import action_run

        with pytest.raises(ValueError, match="`command` is required"):
            action_run({})

    def test_action_run_with_string_command(self):
        """Test run action converts string command to list."""
        from alfredpy.workflow import action_run

        with patch.object(subprocess, "run") as mock_run:
            action_run({"command": "echo hello"})
            mock_run.assert_called_once_with(["echo hello"], cwd=None, check=False)

    @patch.object(Path, "open")
    def test_action_open_file(self, mock_open):
        """Test open_file action opens file."""
        from alfredpy.workflow import action_open_file

        action_open_file({"path": "~/test.txt"})
        # Path.open() is called on expanded path
        assert mock_open.called

    def test_action_open_file_missing_path(self):
        """Test open_file action raises error without path."""
        from alfredpy.workflow import action_open_file

        with pytest.raises(ValueError, match="`path` is required"):
            action_open_file({})
    def test_action_open_file_missing_path(self):
        """Test open_file action raises error without path."""
        from alfredpy.workflow import action_open_file

        with pytest.raises(ValueError, match="`path` is required"):
            action_open_file({})


class TestExtendedActions:
    """Tests for extended action implementations."""

    @patch("alfredpy.workflow.HAS_PYPERCLIP", True)
    @patch("alfredpy.workflow.pyperclip")
    def test_action_copy_to_clipboard(self, mock_pyperclip):
        """Test copy_to_clipboard action."""
        from alfredpy.workflow import action_copy_to_clipboard

        action_copy_to_clipboard({"text": "Hello Clipboard"})
        mock_pyperclip.copy.assert_called_once_with("Hello Clipboard")

    @patch("alfredpy.workflow.HAS_PYPERCLIP", False)
    def test_action_copy_to_clipboard_no_pyperclip(self, capsys):
        """Test copy_to_clipboard warns when pyperclip not installed."""
        from alfredpy.workflow import action_copy_to_clipboard

        action_copy_to_clipboard({"text": "Test"})
        captured = capsys.readouterr()
        assert "Warning: pyperclip not installed" in captured.out

    @patch("subprocess.run")
    @patch("platform.system", return_value="Darwin")
    def test_action_notify_macos(self, mock_platform, mock_run):
        """Test notify action on macOS."""
        from alfredpy.workflow import action_notify

        action_notify({"title": "Test", "message": "Hello"})
        mock_run.assert_called()
        call_args = mock_run.call_args[0][0]
        assert "osascript" in call_args
        assert "display notification" in str(call_args)

    @patch("subprocess.run")
    @patch("platform.system", return_value="Linux")
    def test_action_notify_linux(self, mock_platform, mock_run):
        """Test notify action on Linux."""
        from alfredpy.workflow import action_notify

        action_notify({"title": "Test", "message": "Hello"})
        mock_run.assert_called_with(["notify-send", "Test", "Hello"])

    def test_action_notify_missing_message(self):
        """Test notify action raises error without message."""
        from alfredpy.workflow import action_notify

        with pytest.raises(ValueError, match="`message` is required"):
            action_notify({"title": "Test"})

    def test_action_set_env(self):
        """Test set_env action sets environment variable."""
        from alfredpy.workflow import action_set_env
        import os

        action_set_env({"name": "TEST_VAR", "value": "test_value"})
        assert os.environ.get("TEST_VAR") == "test_value"

    def test_action_set_env_missing_name(self):
        """Test set_env action raises error without name."""
        from alfredpy.workflow import action_set_env

        with pytest.raises(ValueError, match="`name` is required"):
            action_set_env({"value": "test"})

    def test_action_set_env_missing_value(self):
        """Test set_env action raises error without value."""
        from alfredpy.workflow import action_set_env

        with pytest.raises(ValueError, match="`value` is required"):
            action_set_env({"name": "TEST"})

    @patch("os.chdir")
    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.is_dir", return_value=True)
    def test_action_change_dir(self, mock_is_dir, mock_exists, mock_chdir):
        """Test change_dir action."""
        from alfredpy.workflow import action_change_dir

        action_change_dir({"path": "/tmp/test"})
        mock_chdir.assert_called()

    def test_action_change_dir_missing_path(self):
        """Test change_dir action raises error without path."""
        from alfredpy.workflow import action_change_dir

        with pytest.raises(ValueError, match="`path` is required"):
            action_change_dir({})

    @patch("pathlib.Path.mkdir")
    def test_action_write_file(self, mock_mkdir):
        """Test write_file action writes content."""
        from alfredpy.workflow import action_write_file
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            temp_path = f.name

        try:
            action_write_file({"path": temp_path, "content": "Test content"})
            with open(temp_path, "r") as f:
                assert f.read() == "Test content"
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_action_write_file_missing_path(self):
        """Test write_file action raises error without path."""
        from alfredpy.workflow import action_write_file

        with pytest.raises(ValueError, match="`path` is required"):
            action_write_file({"content": "test"})

    @patch("builtins.print")
    def test_action_read_file(self, mock_print):
        """Test read_file action reads content."""
        from alfredpy.workflow import action_read_file
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("Line 1\nLine 2\nLine 3")
            temp_path = f.name

        try:
            action_read_file({"path": temp_path})
            mock_print.assert_called()
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_action_read_file_missing_path(self):
        """Test read_file action raises error without path."""
        from alfredpy.workflow import action_read_file

        with pytest.raises(ValueError, match="`path` is required"):
            action_read_file({})
