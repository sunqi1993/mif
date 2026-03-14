"""AlfredPy GUI — Unified launcher: all results are PluginResult.

Search flow
───────────
  user input
      │
      ├─ starts with @keyword  → route directly to one plugin (@-mode)
      │
      └─ normal text           → fan-out via PluginManager.search()
                                      │
                                      ├─ CalcPlugin   → CalcPanel  (special UI)
                                      ├─ WorkflowPlugin → ResultItem
                                      └─ other plugins  → ResultItem

All results share one handler factory (make_result_handler), one UI component
(ResultItem), and one execution path (plugin.execute(result)).
"""

import flet as ft
import logging
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple

# ── Logging ───────────────────────────────────────────────────────────────────
log_dir = Path(__file__).parent.parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

logger = logging.getLogger("AlfredPy")
logger.setLevel(logging.DEBUG)

_fh = logging.FileHandler(log_dir / "alfredpy.log", encoding="utf-8", mode="a")
_fh.setLevel(logging.DEBUG)
_fh.setFormatter(logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
))
_ch = logging.StreamHandler()
_ch.setLevel(logging.ERROR)
_ch.setFormatter(logging.Formatter("❌ %(levelname)s: %(message)s"))
if not logger.handlers:
    logger.addHandler(_fh)
    logger.addHandler(_ch)

_error_log = log_dir / "errors.log"


def _log_exception(exc_type, exc_value, exc_tb):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return
    logger.error("Unhandled Exception", exc_info=(exc_type, exc_value, exc_tb))
    import traceback
    with open(_error_log, "a", encoding="utf-8") as f:
        f.write("\n" + "=" * 80 + "\n")
        f.write(f"Type: {exc_type.__name__}\nMessage: {exc_value}\nTraceback:\n")
        traceback.print_exception(exc_type, exc_value, exc_tb, file=f)
        f.write("=" * 80 + "\n\n")


sys.excepthook = _log_exception
logger.info("=" * 80)
logger.info("🚀 AlfredPy 启动")
logger.info("=" * 80)

# ── Palette ───────────────────────────────────────────────────────────────────
_BG          = "#1a1a2e"
_BG_CALC     = "#0d1f3c"
_ACCENT      = "#4f8ef7"
_ACCENT_DIM  = "#1e3a6e"
_ACCENT_WARM = "#f5a623"
_DIVIDER     = "#ffffff1a"

# ── @-query parser ────────────────────────────────────────────────────────────
_AT_RE = re.compile(r"^@(\w*)(?:\s+(.*))?$", re.DOTALL)


def _parse_at(query: str) -> Tuple[Optional[str], str]:
    """Return (at_keyword_or_None, rest).  '@calc 1+2' → ('calc', '1+2')."""
    m = _AT_RE.match(query.strip())
    if m:
        return (m.group(1) or ""), (m.group(2) or "").strip()
    return None, query.strip()


# ── Reusable UI components ────────────────────────────────────────────────────

class _SectionLabel(ft.Container):
    def __init__(self, label: str):
        super().__init__(
            content=ft.Row(
                controls=[
                    ft.Text(label, size=10, weight=ft.FontWeight.W_600,
                            color=ft.Colors.WHITE38),
                    ft.Divider(height=1, color=_DIVIDER, thickness=1),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.only(left=15, right=15, top=8, bottom=2),
        )


class ResultItem(ft.Container):
    """Universal result row — used for both workflows and plugins."""

    def __init__(self, title: str, subtitle: str = "",
                 icon: str = "🚀", on_click=None):
        super().__init__()
        self.workflow_action = on_click

        self.content = ft.Row(
            controls=[
                ft.Text(icon, size=20),
                ft.Column(
                    controls=[
                        ft.Text(title, size=14, weight=ft.FontWeight.W_500,
                                color=ft.Colors.WHITE, no_wrap=True,
                                overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(subtitle, size=12, color=ft.Colors.WHITE54,
                                no_wrap=True,
                                overflow=ft.TextOverflow.ELLIPSIS)
                        if subtitle else ft.Container(height=0),
                    ],
                    spacing=2, expand=True,
                ),
            ],
            spacing=10,
        )
        self.padding = ft.padding.symmetric(horizontal=15, vertical=11)
        self.bgcolor = ft.Colors.TRANSPARENT
        self.border_radius = 8
        self.ink = True
        self.on_click = self._handle_click

    def _handle_click(self, e):
        try:
            if self.workflow_action:
                self.workflow_action()
        except Exception as ex:
            logger.error(f"ResultItem 点击失败：{ex}", exc_info=True)


class CalcPanel(ft.Container):
    """Prominent real-time calculator result panel."""

    def __init__(self, expression: str, result_title: str, on_execute=None):
        super().__init__()
        self.workflow_action = on_execute
        display = result_title.removeprefix("= ").strip()

        self.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("🧮", size=16),
                        ft.Text("计算器", size=11, weight=ft.FontWeight.W_600,
                                color=_ACCENT),
                    ],
                    spacing=6,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Container(
                    content=ft.Text(expression, size=13, color=ft.Colors.WHITE54,
                                    font_family="monospace", no_wrap=True,
                                    overflow=ft.TextOverflow.ELLIPSIS),
                    margin=ft.margin.only(top=6),
                ),
                ft.Container(
                    content=ft.Text(display, size=40, weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE, font_family="monospace"),
                    margin=ft.margin.only(top=4, bottom=6),
                ),
                ft.Text("↩  点击或按 Enter 复制到剪贴板", size=11,
                        color=ft.Colors.WHITE38),
            ],
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.START,
        )
        self.padding = ft.padding.symmetric(horizontal=20, vertical=14)
        self.bgcolor = _BG_CALC
        self.border = ft.border.all(1, _ACCENT_DIM)
        self.border_radius = 12
        self.margin = ft.margin.only(left=15, right=15, top=8, bottom=2)
        self.ink = True
        self.on_click = lambda e: self.workflow_action() if self.workflow_action else None


class AtModeBanner(ft.Container):
    """Orange banner shown when @keyword mode is active."""

    def __init__(self, plugin_icon: str, plugin_name: str,
                 at_keyword: str, hint: str = "", on_exit=None):
        super().__init__(
            content=ft.Row(
                controls=[
                    ft.Text(plugin_icon, size=18),
                    ft.Column(
                        controls=[
                            ft.Text(f"@{at_keyword}  —  {plugin_name} 模式",
                                    size=13, weight=ft.FontWeight.W_600,
                                    color=_ACCENT_WARM),
                            ft.Text(hint, size=11, color=ft.Colors.WHITE54)
                            if hint else ft.Container(height=0),
                        ],
                        spacing=2, expand=True,
                    ),
                    ft.TextButton("× 退出",
                                  style=ft.ButtonStyle(color=ft.Colors.WHITE38),
                                  on_click=lambda e: on_exit() if on_exit else None),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=15, vertical=10),
            bgcolor="#1a1200",
            border=ft.border.all(1, "#3a2800"),
            border_radius=10,
            margin=ft.margin.only(left=15, right=15, top=6, bottom=2),
        )


class AtPluginItem(ft.Container):
    """One row in the @-plugin listing."""

    def __init__(self, icon: str, at_keyword: str, name: str,
                 description: str, on_click=None):
        super().__init__()
        self.workflow_action = on_click

        self.content = ft.Row(
            controls=[
                ft.Text(icon, size=22),
                ft.Column(
                    controls=[
                        ft.Row(controls=[
                            ft.Text(f"@{at_keyword}", size=14,
                                    weight=ft.FontWeight.W_600, color=_ACCENT_WARM),
                            ft.Text(f"  {name}", size=14, color=ft.Colors.WHITE70),
                        ], spacing=0),
                        ft.Text(description, size=12, color=ft.Colors.WHITE54,
                                no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                    ],
                    spacing=2, expand=True,
                ),
                ft.Text("↩ 选择", size=11, color=ft.Colors.WHITE24),
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.padding = ft.padding.symmetric(horizontal=15, vertical=11)
        self.bgcolor = ft.Colors.TRANSPARENT
        self.border_radius = 8
        self.ink = True
        self.on_click = lambda e: self.workflow_action() if self.workflow_action else None


class ConfigItem(ft.Container):
    """Displays one plugin config key-value pair."""

    def __init__(self, option, current_value):
        type_hint = {
            "choice": f"可选: {' / '.join(option.choices)}",
            "bool": "true / false", "int": "整数", "float": "小数",
        }.get(option.type, "")

        super().__init__(
            content=ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text(option.name, size=13,
                                    weight=ft.FontWeight.W_500, color=ft.Colors.WHITE),
                            ft.Text(option.description, size=11, color=ft.Colors.WHITE38),
                            ft.Text(type_hint, size=10, color=ft.Colors.WHITE24)
                            if type_hint else ft.Container(height=0),
                        ],
                        spacing=2, expand=True,
                    ),
                    ft.Text(str(current_value), size=13,
                            weight=ft.FontWeight.W_600, color=_ACCENT_WARM),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=15, vertical=10),
            bgcolor=ft.Colors.TRANSPARENT,
            border_radius=8,
        )


# ── Main launcher ─────────────────────────────────────────────────────────────

def launch_gui(config_path: Optional[str] = None):
    """Launch the Flet GUI."""
    logger.info(f"启动 GUI，配置参数：{config_path}")

    from alfredpy.plugins import PluginManager
    plugin_manager = PluginManager()
    logger.info(f"已加载插件：{list(plugin_manager.plugins.keys())}")

    def main(page: ft.Page):
        page.title = "AlfredPy"
        page.theme_mode = ft.ThemeMode.DARK
        page.bgcolor = _BG
        page.padding = 0
        page.spacing = 0
        page.window.width = 800
        page.window.height = 620
        page.window.resizable = True
        page.window.always_on_top = True

        results_column = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)
        _first_action: list = [None]    # mutable ref for Enter key

        # ── Snackbar ──────────────────────────────────────────────────────────
        def show_snackbar(message: str, is_error: bool = False):
            try:
                snack = ft.SnackBar(
                    content=ft.Text(message, color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.RED_600 if is_error else ft.Colors.GREEN_700,
                    behavior=ft.SnackBarBehavior.FLOATING,
                    duration=2000,
                )
                page.overlay.append(snack)
                snack.open = True
                page.update()
            except Exception as ex:
                logger.error(f"SnackBar 失败：{ex}", exc_info=True)

        # ── Unified result handler ────────────────────────────────────────────
        def make_result_handler(result):
            """Single handler factory for ALL PluginResult types."""
            def handler():
                try:
                    plugin = plugin_manager.plugins.get(result.plugin_id)
                    if plugin:
                        plugin.execute(result)
                    show_snackbar(f"✅ {result.title}")
                    # Close window after URL-opening actions
                    if result.extra.get("action_type") == "open_url":
                        import threading, time
                        def _close():
                            time.sleep(1.5)
                            page.window.close()
                        threading.Thread(target=_close, daemon=True).start()
                except Exception as ex:
                    logger.error(f"执行失败：{ex}", exc_info=True)
                    show_snackbar(f"❌ {ex}", is_error=True)
            return handler

        def make_at_select_handler(at_kw: str):
            def handler():
                search_field.value = f"@{at_kw} "
                search_field.focus()
                perform_search(f"@{at_kw} ")
                page.update()
            return handler

        # ── Helpers ───────────────────────────────────────────────────────────
        def _add_result(result):
            """Add a single PluginResult as a ResultItem."""
            icon = result.icon or (
                plugin_manager.plugins[result.plugin_id].meta.icon
                if result.plugin_id in plugin_manager.plugins else "🔌"
            )
            handler = make_result_handler(result)
            item = ResultItem(title=result.title, subtitle=result.subtitle,
                              icon=icon, on_click=handler)
            results_column.controls.append(item)
            if _first_action[0] is None:
                _first_action[0] = handler

        def _section(label: str):
            results_column.controls.append(_SectionLabel(label))

        # ── Main search dispatcher ────────────────────────────────────────────
        def perform_search(query: str = ""):
            results_column.controls.clear()
            _first_action[0] = None
            q = query.strip()

            at_kw, rest = _parse_at(q)
            if at_kw is not None:
                _handle_at_mode(at_kw, rest)
            else:
                _handle_normal_mode(q)

            page.update()

        # ── Normal mode ───────────────────────────────────────────────────────
        def _handle_normal_mode(q: str):
            all_results = plugin_manager.search(q)

            # Split off calc result (special panel) from everything else
            calc_result = None
            other: List = []
            for r in all_results:
                if r.plugin_id == "calculator" and calc_result is None:
                    calc_result = r
                else:
                    other.append(r)

            # Calculator panel (top, special UI)
            if calc_result:
                handler = make_result_handler(calc_result)
                panel = CalcPanel(expression=q, result_title=calc_result.title,
                                  on_execute=handler)
                results_column.controls.append(panel)
                if _first_action[0] is None:
                    _first_action[0] = handler

            # All remaining results — unified flat list, sorted by score
            if other:
                for r in other[:20]:
                    _add_result(r)

            # Empty-state hint
            if not q and plugin_manager.all_at_plugins():
                results_column.controls.append(ft.Container(
                    content=ft.Text("💡  输入 @ 查看所有可用插件",
                                    size=11, color=ft.Colors.WHITE24),
                    padding=ft.padding.only(left=18, top=8),
                ))

        # ── @-mode ────────────────────────────────────────────────────────────
        def _handle_at_mode(at_kw: str, rest: str):
            if at_kw == "":
                _show_at_listing("")
                return

            plugin = plugin_manager.find_by_at_keyword(at_kw)
            if plugin is None:
                _show_at_listing(at_kw)
                return

            # Mode banner
            def _exit():
                search_field.value = rest
                search_field.focus()
                perform_search(rest)
                page.update()

            results_column.controls.append(AtModeBanner(
                plugin_icon=plugin.meta.icon,
                plugin_name=plugin.meta.name,
                at_keyword=at_kw,
                hint=plugin.meta.description,
                on_exit=_exit,
            ))

            if not rest:
                _show_plugin_config(plugin)
                return

            results = plugin_manager.search_at(at_kw, rest)
            if results:
                _section("结果")
                for r in results:
                    _add_result(r)
            else:
                results_column.controls.append(ft.Container(
                    content=ft.Text(f"「{rest}」暂无结果", size=13,
                                    color=ft.Colors.WHITE38),
                    padding=ft.padding.symmetric(horizontal=20, vertical=12),
                ))

        def _show_at_listing(partial: str):
            matched = [
                p for p in plugin_manager.all_at_plugins()
                if not partial or p.meta.at_keyword.lower().startswith(partial.lower())
            ]
            if matched:
                _section("可用插件  —  输入 @关键词 直接调用")
                for p in matched:
                    handler = make_at_select_handler(p.meta.at_keyword)
                    item = AtPluginItem(icon=p.meta.icon,
                                        at_keyword=p.meta.at_keyword,
                                        name=p.meta.name,
                                        description=p.meta.description,
                                        on_click=handler)
                    results_column.controls.append(item)
                    if _first_action[0] is None:
                        _first_action[0] = handler
            else:
                results_column.controls.append(ft.Container(
                    content=ft.Text(f"没有匹配 @{partial} 的插件",
                                    size=13, color=ft.Colors.WHITE38),
                    padding=ft.padding.symmetric(horizontal=20, vertical=12),
                ))

        def _show_plugin_config(plugin):
            if not plugin.meta.config_options:
                results_column.controls.append(ft.Container(
                    content=ft.Text("该插件没有可配置项", size=12,
                                    color=ft.Colors.WHITE38),
                    padding=ft.padding.symmetric(horizontal=20, vertical=8),
                ))
                return
            _section("当前配置")
            for opt in plugin.meta.config_options:
                results_column.controls.append(ConfigItem(opt, plugin.get_config(opt.key)))
            results_column.controls.append(ft.Container(
                content=ft.Text(f"配置文件：{plugin_manager.CONFIG_PATH}",
                                size=10, color=ft.Colors.WHITE24),
                padding=ft.padding.only(left=15, top=6, bottom=4),
            ))

        # ── Events ────────────────────────────────────────────────────────────
        def on_change(e):
            try:
                perform_search(e.control.value)
            except Exception as ex:
                logger.error(f"搜索失败：{ex}", exc_info=True)

        def on_submit(e):
            if _first_action[0]:
                try:
                    _first_action[0]()
                except Exception as ex:
                    logger.error(f"Enter 执行失败：{ex}", exc_info=True)

        def on_keyboard(e: ft.KeyboardEvent):
            if e.key == "Escape":
                if search_field.value and search_field.value.startswith("@"):
                    search_field.value = ""
                    perform_search("")
                    page.update()
                else:
                    page.window.close()

        page.on_keyboard_event = on_keyboard

        # ── Search field ──────────────────────────────────────────────────────
        search_field = ft.TextField(
            hint_text="搜索…  1+2  g Python  @calc  @wf  @settings",
            hint_style=ft.TextStyle(color=ft.Colors.WHITE24, size=15),
            text_style=ft.TextStyle(color=ft.Colors.WHITE, size=18,
                                    weight=ft.FontWeight.W_300),
            border_color=ft.Colors.WHITE24,
            focused_border_color=_ACCENT,
            border_radius=25,
            cursor_color=ft.Colors.WHITE,
            fill_color=ft.Colors.WHITE10,
            filled=True,
            content_padding=ft.padding.symmetric(horizontal=25, vertical=15),
            on_change=on_change,
            on_submit=on_submit,
            prefix_icon=ft.Icons.SEARCH,
        )

        page.add(ft.Column(
            controls=[
                ft.Container(content=search_field, bgcolor=_BG,
                             padding=ft.padding.symmetric(horizontal=15, vertical=15)),
                ft.Container(content=results_column, bgcolor=_BG, expand=True),
            ],
            expand=True, spacing=0,
        ))

        perform_search()
        search_field.focus()
        logger.info("✅ GUI 启动完成")

    try:
        ft.app(target=main)
    except Exception as e:
        logger.error(f"GUI 启动失败：{e}", exc_info=True)
        raise


if __name__ == "__main__":
    launch_gui()
