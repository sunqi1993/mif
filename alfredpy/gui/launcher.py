"""Modern launcher window using Flet - Flutter-based Python UI framework."""

import flet as ft
from typing import List, Optional
import logging
import sys
from pathlib import Path

# 配置日志系统
log_dir = Path(__file__).parent.parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

# 创建 logger
logger = logging.getLogger("AlfredPy")
logger.setLevel(logging.DEBUG)

# 文件处理器 - 详细日志
file_handler = logging.FileHandler(
    log_dir / "alfredpy.log", 
    encoding="utf-8",
    mode="a"
)
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(file_formatter)

# 控制台处理器 - 错误日志
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
console_formatter = logging.Formatter(
    '❌ %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
console_handler.setFormatter(console_formatter)

# 添加处理器
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

# 异常日志文件
error_log_path = log_dir / "errors.log"


def log_exception(exc_type, exc_value, exc_traceback):
    """全局异常处理器"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logger.error("=" * 80)
    logger.error("Unhandled Exception", exc_info=(exc_type, exc_value, exc_traceback))
    logger.error("=" * 80)
    
    # 同时写入错误日志文件
    with open(error_log_path, "a", encoding="utf-8") as f:
        import traceback
        f.write("\n" + "=" * 80 + "\n")
        f.write(f"Time: {logging.Formatter.default_time_format}\n")
        f.write(f"Type: {exc_type.__name__}\n")
        f.write(f"Message: {exc_value}\n")
        f.write("Traceback:\n")
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)
        f.write("=" * 80 + "\n\n")


# 设置全局异常处理器
sys.excepthook = log_exception


logger.info("=" * 80)
logger.info("🚀 AlfredPy 启动")
logger.info(f"📁 日志目录：{log_dir}")
logger.info("=" * 80)


class SearchResultItem(ft.Container):
    """A single search result item with modern styling."""

    def __init__(
        self,
        title: str,
        subtitle: str = "",
        icon: str = "🚀",
        on_click=None,
        selected: bool = False,
    ):
        super().__init__()
        self.workflow_action = on_click
        self.selected = selected
        logger.debug(f"创建搜索结果项：{title}")

        self.content = ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Text(subtitle, size=12, color=ft.Colors.WHITE70) if subtitle else ft.Container(),
                    ],
                    spacing=4,
                    expand=True,
                ),
                ft.Text(icon, size=20),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        self.padding = ft.padding.all(15)
        self.margin = ft.margin.only(bottom=8)
        self.border_radius = 12
        self.bgcolor = "#3B82F6" if selected else "#1E293B"
        self.on_click = self._handle_click

    def _handle_click(self, e):
        """处理点击事件"""
        try:
            logger.debug(f"点击事件触发：{self.content.controls[0].controls[0].value if self.content.controls else 'Unknown'}")
            if self.workflow_action:
                # 不调用参数，直接执行
                self.workflow_action()
        except Exception as ex:
            logger.error(f"点击事件处理失败：{ex}", exc_info=True)
            raise

    def set_selected(self, selected: bool):
        self.selected = selected
        self.bgcolor = "#3B82F6" if selected else "#1E293B"
        self.update()


def show_snackbar(page: ft.Page, message: str, is_error: bool = False):
    """Show a snackbar notification using page.overlay."""
    try:
        logger.debug(f"显示 SnackBar: {message}")
        snackbar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.RED_600 if is_error else ft.Colors.GREEN_600,
            behavior=ft.SnackBarBehavior.FLOATING,
            duration=2000,
        )
        page.overlay.append(snackbar)
        snackbar.open = True
        page.update()
    except Exception as ex:
        logger.error(f"SnackBar 显示失败：{ex}", exc_info=True)


def create_launcher_ui(page: ft.Page, workflows: List):
    """Create the launcher UI."""
    logger.info(f"创建 GUI 界面，工作流数量：{len(workflows)}")
    
    def perform_search(query: str, results_column: ft.Column, result_actions: list):
        """Perform search and update results."""
        try:
            logger.debug(f"搜索查询：'{query}'")
            results_column.controls.clear()
            result_actions.clear()

            query_lower = query.lower().strip() if query else ""
            matched = []

            for workflow in workflows:
                if not query_lower:
                    matched.append((workflow, 100))
                else:
                    try:
                        from thefuzz import fuzz
                        name_score = fuzz.partial_ratio(query_lower, workflow.name.lower())
                        desc_score = fuzz.partial_ratio(query_lower, workflow.description.lower()) if workflow.description else 0
                        score = max(name_score, desc_score)
                        if score >= 50:
                            matched.append((workflow, score))
                    except ImportError:
                        if query_lower in workflow.name.lower():
                            matched.append((workflow, 100))

            matched.sort(key=lambda x: x[1], reverse=True)
            logger.debug(f"搜索匹配：{len(matched)} 个结果")

            icons = {
                "print": "📝", "open_url": "🌐", "run": "⚡", "open_file": "📁",
                "copy_to_clipboard": "📋", "notify": "🔔", "set_env": "⚙️",
                "change_dir": "📂", "write_file": "✍️", "read_file": "📖",
            }

            for workflow, score in matched[:20]:
                icon = icons.get(workflow.action, "🚀")
                
                def create_click_handler(w=workflow):
                    def handler():
                        try:
                            logger.info(f"执行工作流：{w.name} (动作：{w.action})")
                            w.run()
                            if w.action == "open_url":
                                show_snackbar(page, f"✅ 已打开：{w.name}")
                                def close_window():
                                    logger.info("关闭 GUI 窗口")
                                    page.window.close()
                                page.after(1500, close_window)
                            else:
                                show_snackbar(page, f"✅ 已执行：{w.name}")
                        except Exception as ex:
                            logger.error(f"工作流执行失败：{w.name} - {ex}", exc_info=True)
                            show_snackbar(page, f"❌ 执行失败：{str(ex)}", is_error=True)
                    return handler

                item = SearchResultItem(
                    title=workflow.name,
                    subtitle=workflow.description or "",
                    icon=icon,
                    on_click=create_click_handler(),
                    selected=(len(results_column.controls) == 0),
                )
                results_column.controls.append(item)
                result_actions.append(create_click_handler())

            page.update()
        except Exception as ex:
            logger.error(f"搜索执行失败：{ex}", exc_info=True)
            show_snackbar(page, f"❌ 搜索失败：{str(ex)}", is_error=True)

    def on_search_change(e):
        try:
            perform_search(e.control.value if hasattr(e, 'control') else "", 
                          results_column, result_actions)
        except Exception as ex:
            logger.error(f"搜索变更失败：{ex}", exc_info=True)

    def on_enter(e):
        try:
            if results_column.controls:
                results_column.controls[0].workflow_action and results_column.controls[0].workflow_action()
        except Exception as ex:
            logger.error(f"Enter 键执行失败：{ex}", exc_info=True)

    # Search field
    logger.debug("创建搜索框")
    search_field = ft.TextField(
        hint_text="搜索工作流... (Esc 关闭)",
        hint_style=ft.TextStyle(color=ft.Colors.WHITE54, size=16),
        text_style=ft.TextStyle(color=ft.Colors.WHITE, size=18),
        border_color=ft.Colors.TRANSPARENT,
        focused_border_color=ft.Colors.BLUE_400,
        cursor_color=ft.Colors.BLUE_400,
        fill_color=ft.Colors.WHITE10,
        filled=True,
        content_padding=ft.padding.only(left=20, top=15, bottom=15, right=20),
        border_radius=15,
        prefix_icon=ft.Icon(ft.Icons.SEARCH, color=ft.Colors.BLUE_400, size=28),
        on_change=on_search_change,
        on_submit=on_enter,
    )

    # Results
    result_actions = []
    results_column = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO)
    
    results_container = ft.Container(
        content=results_column,
        padding=ft.padding.all(10),
        border_radius=15,
        bgcolor=ft.Colors.WHITE10,
        expand=True,
    )

    # Footer
    def shortcut_badge(key: str, desc: str):
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    ft.Text(key, size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_300),
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    border_radius=6,
                    bgcolor=ft.Colors.WHITE10,
                ),
                ft.Text(desc, size=11, color=ft.Colors.WHITE54),
            ], spacing=6),
        )

    footer = ft.Row(
        controls=[
            shortcut_badge("↑↓", "导航"),
            shortcut_badge("Enter", "执行"),
            shortcut_badge("Esc", "关闭"),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=15,
    )

    def on_keyboard(e: ft.KeyboardEvent):
        try:
            if e.key == "Escape":
                logger.info("按 Esc 键关闭窗口")
                page.window.close()
        except Exception as ex:
            logger.error(f"键盘事件处理失败：{ex}", exc_info=True)

    page.on_keyboard_event = on_keyboard

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row([
                        ft.Text("🚀 AlfredPy", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Container(expand=True),
                        ft.IconButton(
                            ft.Icons.CLOSE, 
                            icon_color=ft.Colors.WHITE70, 
                            on_click=lambda e: page.window.close()
                        ),
                    ]),
                    padding=ft.padding.all(20),
                ),
                search_field,
                results_container,
                footer,
            ],
            spacing=15,
        ),
        padding=ft.padding.all(20),
        expand=True,
    )


def launch_gui(config_path: Optional[str] = None):
    """Launch the Flet GUI application."""
    logger.info(f"启动 GUI，配置文件：{config_path}")
    workflows = []
    
    try:
        from alfredpy.config import load_config
        from alfredpy.workflow import WorkflowItem
        config = load_config(config_path)
        raw = config.get("workflows") or []
        workflows = [WorkflowItem.from_dict(i) for i in raw if isinstance(i, dict)]
        logger.info(f"加载工作流：{len(workflows)} 个")
    except Exception as e:
        logger.error(f"加载工作流失败：{e}", exc_info=True)
        print(f"⚠️  Failed to load workflows: {e}")

    if not workflows:
        logger.warning("未找到工作流，使用演示模式")
        print("⚠️  No workflows found. Running in demo mode.")
        from alfredpy.workflow import WorkflowItem
        workflows = [
            WorkflowItem.from_dict({
                "id": "demo1",
                "name": "演示：打印问候",
                "description": "打印 Hello World",
                "action": "print",
                "args": {"text": "Hello from AlfredPy GUI!"}
            }),
            WorkflowItem.from_dict({
                "id": "demo2",
                "name": "演示：打开 GitHub",
                "description": "在浏览器中打开 GitHub",
                "action": "open_url",
                "args": {"url": "https://github.com"}
            }),
            WorkflowItem.from_dict({
                "id": "demo3",
                "name": "演示：运行测试",
                "description": "运行 pytest 测试",
                "action": "run",
                "args": {"command": ["pytest", "--no-cov", "-q"]}
            }),
        ]

    def main(page: ft.Page):
        try:
            logger.info("初始化页面")
            page.title = "AlfredPy Launcher"
            page.theme_mode = ft.ThemeMode.DARK
            page.bgcolor = "#0F172A"
            
            page.window.width = 750
            page.window.height = 550
            page.window.resizable = False
            page.window.on_close = lambda: logger.info("AlfredPy 窗口已关闭")
            
            page.padding = 0
            page.spacing = 0

            launcher_ui = create_launcher_ui(page, workflows)
            page.add(launcher_ui)
            page.update()
            
            logger.info("✅ GUI 界面初始化完成")
        except Exception as e:
            logger.error(f"页面初始化失败：{e}", exc_info=True)
            raise

    try:
        logger.info("启动 Flet 应用")
        ft.app(target=main, port=8550)
        logger.info("Flet 应用已退出")
    except Exception as e:
        logger.error(f"Flet 应用启动失败：{e}", exc_info=True)
        raise


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("AlfredPy GUI 启动")
    logger.info("=" * 80)
    launch_gui()
