"""Tests for PluginManager facade after internal split."""

from pathlib import Path


def test_plugin_manager_loads_and_routes(monkeypatch, tmp_path: Path):
    import mif.config
    from mif.plugins import PluginManager

    cfg_path = tmp_path / "plugin_configs.json"
    monkeypatch.setattr(mif.config, "plugin_config_path", lambda: cfg_path)

    manager = PluginManager()

    assert "calculator" in manager.plugins
    assert manager.find_by_at_keyword("calc") is not None
    assert len(manager.search_at("calc", "1+2")) >= 1


def test_plugin_manager_config_crud(monkeypatch, tmp_path: Path):
    import mif.config
    from mif.plugins import PluginManager

    cfg_path = tmp_path / "plugin_configs.json"
    monkeypatch.setattr(mif.config, "plugin_config_path", lambda: cfg_path)

    manager = PluginManager()
    assert manager.set_plugin_config("calculator", "precision", 4) is True

    snapshot = manager.full_config_snapshot("calculator")
    assert snapshot.get("precision") == 4

    assert manager.reset_plugin_config("calculator") is True
