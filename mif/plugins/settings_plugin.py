"""Built-in settings plugin — manage plugin configuration from the search box.

Usage (type in the AlfredPy search field):
  @settings                              — list all plugins with config summary
  @settings <plugin_id>                  — show that plugin's full config
  @settings <plugin_id> <key> <value>    — set a config value (↩ to confirm)
  @settings <plugin_id> reset            — reset all config to defaults (↩ to confirm)

Special keys (prefixed with _) override plugin metadata:
  _keywords   <kw1> <kw2> …             — replace prefix-trigger keywords
  _at_keyword <new_kw>                   — replace @-trigger keyword

Examples:
  @settings calculator angle_unit degrees
  @settings calculator _at_keyword math
  @settings calculator _keywords = calc 计算
  @settings calculator precision 4
  @settings calculator reset
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from mif.plugins.base import BasePlugin, PluginMeta, PluginResult

if TYPE_CHECKING:
    from mif.plugins import PluginManager


class SettingsPlugin(BasePlugin):
    """Interactive plugin configuration manager."""

    def __init__(self):
        super().__init__()
        self._manager: Optional[PluginManager] = None

    # ── Manager injection (called by PluginManager.register) ──────────────────

    def set_manager(self, manager: PluginManager) -> None:
        self._manager = manager

    # ── Metadata ──────────────────────────────────────────────────────────────

    def get_meta(self) -> PluginMeta:
        return PluginMeta(
            id="settings",
            name="插件设置",
            description="配置插件的触发词、@关键词及参数  (@settings <plugin> <key> <value>)",
            version="1.0.0",
            author="mif",
            icon="⚙️",
            keywords=[],          # no prefix-keyword trigger (only via @settings)
            at_keyword="settings",
            priority=10,
        )

    # ── match_keyword: only reachable via @settings, not fan-out search ───────

    def match_keyword(self, query: str) -> bool:
        return False   # prevent showing in normal search results

    # ── Search dispatcher ─────────────────────────────────────────────────────

    def search(self, query: str) -> List[PluginResult]:
        if not self._manager:
            return [self._err("Settings plugin not initialised")]

        q = query.strip()

        # ── @settings  (no args) → list all plugins ──────────────────────────
        if not q:
            return self._list_plugins()

        # Split into: plugin_id  [key  [value…]]
        parts = q.split(None, 2)
        plugin_id = parts[0].lower()
        plugin = self._manager.plugins.get(plugin_id)

        # ── @settings <partial>  → fuzzy list ────────────────────────────────
        if plugin is None:
            return self._list_plugins(filter_prefix=plugin_id)

        # ── @settings <id>  → show full config ───────────────────────────────
        if len(parts) == 1:
            return self._show_config(plugin)

        key = parts[1]

        # ── @settings <id> reset  → reset confirmation ────────────────────────
        if key == "reset" and len(parts) == 2:
            return self._confirm_reset(plugin)

        # ── @settings <id> <key>  → prompt for value ─────────────────────────
        if len(parts) == 2:
            return self._prompt_value(plugin, key)

        # ── @settings <id> <key> <value>  → set confirmation ─────────────────
        value_str = parts[2]
        return self._confirm_set(plugin, key, value_str)

    # ── Renderers ─────────────────────────────────────────────────────────────

    def _list_plugins(self, filter_prefix: str = "") -> List[PluginResult]:
        """Show all plugins (or those matching a prefix) with their config summary."""
        results = []
        mgr = self._manager
        for plugin in sorted(mgr.plugins.values(), key=lambda p: p.meta.priority):
            if plugin.meta.id == "settings":
                continue
            if filter_prefix and not plugin.meta.id.startswith(filter_prefix):
                continue

            # Build a one-line summary of the current config
            cfg = plugin.config_summary()
            kw_str = f"触发词: {', '.join(plugin.meta.keywords) or '—'}"
            at_str = f"@{plugin.meta.at_keyword}" if plugin.meta.at_keyword else ""
            param_str = "  ".join(f"{k}={v}" for k, v in cfg.items()) if cfg else ""
            subtitle_parts = [p for p in [kw_str, at_str, param_str] if p]

            results.append(PluginResult(
                title=f"{plugin.meta.icon}  {plugin.meta.name}  [{plugin.meta.id}]",
                subtitle="  |  ".join(subtitle_parts),
                action=None,
                plugin_id=self.meta.id,
                score=1.0,
            ))

        if not results:
            results.append(self._err(
                f"没有匹配 '{filter_prefix}' 的插件" if filter_prefix
                else "尚未加载任何插件"
            ))
        return results

    def _show_config(self, plugin: BasePlugin) -> List[PluginResult]:
        """Show one plugin's full config (keywords + all options)."""
        results = []
        pid = plugin.meta.id

        # ── Trigger keywords ─────────────────────────────────────────────────
        results.append(PluginResult(
            title=f"🔑  触发词: {', '.join(plugin.meta.keywords) or '（无）'}",
            subtitle=f"修改示例: @settings {pid} _keywords = calc 计算",
            action=None, plugin_id=self.meta.id,
        ))

        # ── @-keyword ────────────────────────────────────────────────────────
        at_display = f"@{plugin.meta.at_keyword}" if plugin.meta.at_keyword else "（未设置）"
        results.append(PluginResult(
            title=f"📌  @关键词: {at_display}",
            subtitle=f"修改示例: @settings {pid} _at_keyword <新关键词>",
            action=None, plugin_id=self.meta.id,
        ))

        # ── Config params ────────────────────────────────────────────────────
        if plugin.meta.config_options:
            for opt in plugin.meta.config_options:
                cur = plugin.get_config(opt.key)
                type_hint = (
                    f"可选: {' / '.join(opt.choices)}" if opt.type == "choice"
                    else {"bool": "true/false", "int": "整数", "float": "小数"}.get(opt.type, "")
                )
                results.append(PluginResult(
                    title=f"⚙  {opt.name}: {cur}",
                    subtitle=(
                        f"{opt.description}  |  {type_hint}  |  "
                        f"修改: @settings {pid} {opt.key} <值>"
                    ),
                    action=None, plugin_id=self.meta.id,
                ))
        else:
            results.append(PluginResult(
                title="（该插件没有可配置参数）",
                subtitle="", action=None, plugin_id=self.meta.id,
            ))

        # ── Reset hint ────────────────────────────────────────────────────────
        results.append(PluginResult(
            title=f"🔄  重置所有配置",
            subtitle=f"@settings {pid} reset   ↩ 恢复默认值",
            action=None, plugin_id=self.meta.id,
        ))

        # ── Config file path ──────────────────────────────────────────────────
        results.append(PluginResult(
            title=f"📄  配置文件: {self._manager.CONFIG_PATH}",
            subtitle="可直接编辑 JSON 文件，重启后生效",
            action=lambda: self._open_config_file(),
            action_args=(),
            plugin_id=self.meta.id,
        ))

        return results

    def _prompt_value(self, plugin: BasePlugin, key: str) -> List[PluginResult]:
        """User typed key but not value yet — show what the current value is."""
        if key.startswith("_"):
            meta_key = {"_keywords": "触发词列表", "_at_keyword": "@关键词"}.get(key, key)
            cur = (
                ", ".join(plugin.meta.keywords) if key == "_keywords"
                else plugin.meta.at_keyword
            )
            return [PluginResult(
                title=f"✏️  设置 {meta_key}（当前: {cur}）",
                subtitle=f"继续输入: @settings {plugin.meta.id} {key} <新值>",
                action=None, plugin_id=self.meta.id,
            )]

        opt = next((o for o in plugin.meta.config_options if o.key == key), None)
        if opt:
            cur = plugin.get_config(key)
            type_hint = (
                f"可选: {' / '.join(opt.choices)}" if opt.type == "choice"
                else {"bool": "true/false", "int": "整数"}.get(opt.type, "")
            )
            return [PluginResult(
                title=f"✏️  {opt.name}（当前: {cur}）",
                subtitle=f"继续输入: @settings {plugin.meta.id} {key} <{type_hint}>",
                action=None, plugin_id=self.meta.id,
            )]

        return [self._err(f"插件 '{plugin.meta.id}' 没有配置项 '{key}'")]

    def _confirm_set(self, plugin: BasePlugin, key: str,
                     value_str: str) -> List[PluginResult]:
        """Parse and confirm a set-config action."""
        pid = plugin.meta.id

        # ── Metadata overrides ────────────────────────────────────────────────
        if key == "_keywords":
            # value_str may start with "=" for clarity, strip it
            raw = value_str.lstrip("= ").strip()
            new_value = raw.split() if raw else []
            old_value = list(plugin.meta.keywords)
            label = "触发词"

        elif key == "_at_keyword":
            new_value = value_str.strip().lstrip("@")
            old_value = plugin.meta.at_keyword
            label = "@关键词"

        # ── Regular config option ─────────────────────────────────────────────
        else:
            opt = next((o for o in plugin.meta.config_options if o.key == key), None)
            if opt is None:
                return [self._err(f"未知配置项 '{key}'（插件: {pid}）")]
            new_value = opt.coerce(value_str.strip())
            old_value = plugin.get_config(key)
            label = opt.name

        def do_set():
            self._manager.set_plugin_config(pid, key, new_value)

        return [PluginResult(
            title=f"✅  {plugin.meta.icon} {plugin.meta.name}  →  {label} = {new_value!r}",
            subtitle=f"旧值: {old_value!r}    ↩ 按 Enter 或点击确认",
            action=do_set,
            action_args=(),
            plugin_id=self.meta.id,
            score=1.0,
        )]

    def _confirm_reset(self, plugin: BasePlugin) -> List[PluginResult]:
        """Return a reset-confirmation result."""
        def do_reset():
            self._manager.reset_plugin_config(plugin.meta.id)

        return [PluginResult(
            title=f"🔄  重置 {plugin.meta.icon} {plugin.meta.name} 所有配置",
            subtitle="将恢复触发词、@关键词和所有参数为默认值    ↩ 确认",
            action=do_reset,
            action_args=(),
            plugin_id=self.meta.id,
            score=1.0,
        )]

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _open_config_file(self) -> None:
        """Open the config file in the system default editor."""
        import subprocess, sys
        path = str(self._manager.CONFIG_PATH)
        try:
            if sys.platform == "darwin":
                subprocess.Popen(["open", path])
            elif sys.platform.startswith("linux"):
                subprocess.Popen(["xdg-open", path])
            else:
                subprocess.Popen(["notepad", path])
        except Exception:
            pass

    @staticmethod
    def _err(msg: str) -> PluginResult:
        return PluginResult(
            title=f"⚠️  {msg}",
            subtitle="",
            action=None,
            plugin_id="settings",
        )
