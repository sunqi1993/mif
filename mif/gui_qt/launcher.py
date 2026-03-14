"""Qt Widgets GUI Launcher（不使用 QML）。"""

from __future__ import annotations

import argparse
import logging
import os
import re
import socket
import sys
import threading
from typing import Any, Optional, Tuple

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QPushButton,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from mif.application import ApplicationService
from mif.gui_qt import singleton
from mif.logging_setup import setup_file_logger

logger = setup_file_logger("AlfredPy-QtWidgets", "mif_qt.log", level=logging.DEBUG)


_AT_RE = re.compile(r"^@(\w*)(?:\s+(.*))?$", re.DOTALL)
_show_callback: list = [None]


def _parse_at(query: str) -> Tuple[Optional[str], str]:
    m = _AT_RE.match(query.strip())
    if m:
        return (m.group(1) or ""), (m.group(2) or "").strip()
    return None, query.strip()


def _claim_socket_and_start_listener() -> bool:
    path = singleton.get_socket_path()
    cmd = singleton.get_show_cmd()

    if os.path.exists(path):
        try:
            probe = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            probe.settimeout(0.3)
            probe.connect(path)
            probe.close()
            return False
        except (ConnectionRefusedError, socket.error, OSError):
            pass
        try:
            os.unlink(path)
        except OSError:
            return False

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        sock.bind(path)
        sock.listen(1)
        sock.settimeout(1.0)
    except OSError:
        try:
            sock.close()
        except Exception:
            pass
        return False

    def loop() -> None:
        while True:
            try:
                conn, _ = sock.accept()
                try:
                    data = conn.recv(64)
                    if data and data.strip() == cmd and _show_callback[0]:
                        _show_callback[0]()
                finally:
                    conn.close()
            except socket.timeout:
                continue
            except (OSError, BrokenPipeError, ConnectionResetError):
                break
            except Exception as ex:
                logger.debug("show listener error: %s", ex)

    threading.Thread(target=loop, daemon=True).start()
    return True


class ResultRowWidget(QFrame):
    """列表行组件，支持正常/选中两种视觉状态。"""

    def __init__(self, icon: str, title: str, subtitle: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setFrameShape(QFrame.NoFrame)
        self.setLineWidth(0)
        self._icon_label = QLabel(icon, self)
        self._title_label = QLabel(title, self)
        self._subtitle_label = QLabel(subtitle, self)

        self._title_label.setWordWrap(False)
        self._subtitle_label.setWordWrap(False)
        # 让鼠标事件交给 QListWidget 处理，避免“点击无效”
        self._icon_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self._title_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self._subtitle_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)
        text_layout.addWidget(self._title_label)
        text_layout.addWidget(self._subtitle_label)

        root = QHBoxLayout(self)
        root.setContentsMargins(10, 8, 10, 8)
        root.setSpacing(10)
        root.addWidget(self._icon_label)
        root.addLayout(text_layout, 1)

        self._title_label.setToolTip(title)
        self._subtitle_label.setToolTip(subtitle)
        self.set_selected(False)

    def set_selected(self, selected: bool) -> None:
        if selected:
            self.setStyleSheet(
                """
                QFrame {
                    background: rgba(79, 142, 247, 0.28);
                    border: 1px solid rgba(143, 185, 255, 0.65);
                    border-radius: 10px;
                }
                QLabel {
                    background: transparent;
                    border: none;
                    padding: 0;
                    margin: 0;
                }
                """
            )
            self._title_label.setStyleSheet(
                "color: rgba(255,255,255,0.99); font-size: 16px; font-weight: 700; border: none; background: transparent;"
            )
            self._subtitle_label.setStyleSheet(
                "color: rgba(230,240,255,0.95); font-size: 13px; font-weight: 500; border: none; background: transparent;"
            )
            self._icon_label.setStyleSheet(
                "color: rgba(255,255,255,0.98); font-size: 20px; border: none; background: transparent;"
            )
        else:
            self.setStyleSheet(
                """
                QFrame {
                    background: rgba(255, 255, 255, 0.03);
                    border: 1px solid rgba(255, 255, 255, 0.04);
                    border-radius: 10px;
                }
                QLabel {
                    background: transparent;
                    border: none;
                    padding: 0;
                    margin: 0;
                }
                """
            )
            self._title_label.setStyleSheet(
                "color: rgba(245,248,255,0.94); font-size: 16px; font-weight: 600; border: none; background: transparent;"
            )
            self._subtitle_label.setStyleSheet(
                "color: rgba(196,207,230,0.78); font-size: 13px; font-weight: 450; border: none; background: transparent;"
            )
            self._icon_label.setStyleSheet(
                "color: rgba(255,255,255,0.90); font-size: 20px; border: none; background: transparent;"
            )


class MainWindow(QWidget):
    """主窗口：QLineEdit + QListWidget 的稳定布局。"""

    def __init__(self, app_service: ApplicationService):
        super().__init__()
        self._app_service = app_service
        self._entries: list[Any] = []
        self._row_widgets: list[ResultRowWidget] = []
        self._tray: Optional[SystemTray] = None
        self._is_at_mode = False
        self._banner_timer = QTimer(self)
        self._banner_timer.setSingleShot(True)
        self._banner_timer.timeout.connect(self._hide_exec_banner)

        self.setWindowTitle("AlfredPy")
        self.resize(820, 640)
        self._build_ui()
        self._bind_events()
        self.refresh_results("")

    def set_tray(self, tray: Optional["SystemTray"]) -> None:
        self._tray = tray

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(8)

        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("输入关键字，或 @插件名 ...")
        self.search_input.setClearButtonEnabled(True)
        root.addWidget(self.search_input)

        self.at_banner = QFrame(self)
        self.at_banner.setVisible(False)
        banner_layout = QHBoxLayout(self.at_banner)
        banner_layout.setContentsMargins(10, 8, 10, 8)
        banner_layout.setSpacing(8)

        self.at_banner_icon = QLabel("", self.at_banner)
        self.at_banner_title = QLabel("", self.at_banner)
        self.at_banner_hint = QLabel("", self.at_banner)
        self.at_exit_btn = QPushButton("退出 @ 模式", self.at_banner)
        self.at_exit_btn.setCursor(Qt.PointingHandCursor)

        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(2)
        text_col.addWidget(self.at_banner_title)
        text_col.addWidget(self.at_banner_hint)

        banner_layout.addWidget(self.at_banner_icon)
        banner_layout.addLayout(text_col, 1)
        banner_layout.addWidget(self.at_exit_btn)
        root.addWidget(self.at_banner)

        self.list_widget = QListWidget(self)
        self.list_widget.setSelectionMode(QListWidget.SingleSelection)
        self.list_widget.setAlternatingRowColors(False)
        self.list_widget.setSpacing(6)
        root.addWidget(self.list_widget, 1)

        self.hint_label = QLabel("无结果", self)
        self.hint_label.setAlignment(Qt.AlignCenter)
        root.addWidget(self.hint_label)

        self.exec_banner = QLabel("", self)
        self.exec_banner.setAlignment(Qt.AlignCenter)
        self.exec_banner.setVisible(False)
        self.exec_banner.setFixedHeight(28)
        root.addWidget(self.exec_banner)

        self._apply_styles()

    def _bind_events(self) -> None:
        self.search_input.textChanged.connect(self.refresh_results)
        self.search_input.returnPressed.connect(self.execute_current)
        self.list_widget.itemClicked.connect(lambda _: self.execute_current())
        self.list_widget.itemDoubleClicked.connect(lambda _: self.execute_current())
        self.list_widget.itemSelectionChanged.connect(self._on_selection_changed)
        self.at_exit_btn.clicked.connect(self.exit_at_mode)

        QShortcut(QKeySequence(Qt.Key_Escape), self, activated=self._on_escape)
        QShortcut(QKeySequence(Qt.Key_Down), self, activated=self._select_next)
        QShortcut(QKeySequence(Qt.Key_Up), self, activated=self._select_prev)

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QWidget {
                background: rgba(24, 28, 52, 0.96);
                color: rgba(245, 248, 255, 0.95);
                font-family: "SF Pro Text", "PingFang SC", "Helvetica Neue", sans-serif;
            }
            QLineEdit {
                min-height: 40px;
                border: 1px solid rgba(129, 162, 255, 0.30);
                border-radius: 12px;
                padding: 0 12px;
                background: rgba(10, 16, 38, 0.74);
                color: rgba(251, 253, 255, 0.97);
                font-size: 17px;
                font-weight: 550;
                selection-background-color: rgba(96, 159, 255, 0.70);
                selection-color: rgba(255, 255, 255, 1.0);
            }
            QLineEdit:focus {
                border: 1px solid rgba(120, 167, 255, 0.80);
                background: rgba(12, 20, 46, 0.84);
            }
            QListWidget {
                border: 1px solid rgba(122, 156, 248, 0.20);
                border-radius: 12px;
                background: rgba(15, 18, 34, 0.68);
                outline: none;
                padding: 8px;
            }
            QListWidget::item {
                border: none;
                padding: 0px;
            }
            QListWidget::item:selected {
                background: transparent;
            }
            QFrame {
                border: 1px solid rgba(245, 183, 71, 0.45);
                border-radius: 10px;
                background: rgba(51, 32, 9, 0.76);
            }
            QPushButton {
                border: 1px solid rgba(255, 199, 103, 0.50);
                border-radius: 6px;
                padding: 4px 10px;
                background: rgba(94, 62, 19, 0.65);
                color: rgba(255, 219, 140, 0.98);
                font-weight: 600;
            }
            QPushButton:hover {
                background: rgba(120, 78, 20, 0.72);
            }
            QLabel {
                color: rgba(220, 229, 245, 0.88);
            }
            """
        )
        self.hint_label.setStyleSheet("color: rgba(180, 192, 214, 0.72); font-size: 15px;")
        self.at_banner_title.setStyleSheet("color: rgba(255, 221, 160, 0.98); font-size: 14px; font-weight: 700;")
        self.at_banner_hint.setStyleSheet("color: rgba(240, 224, 190, 0.78); font-size: 12px;")
        self.exec_banner.setStyleSheet(
            "background: rgba(34, 180, 98, 0.92);"
            "color: rgba(245, 255, 249, 0.98);"
            "border: 1px solid rgba(122, 245, 172, 0.82);"
            "border-radius: 8px;"
            "font-size: 13px;"
            "font-weight: 700;"
            "padding: 0 10px;"
        )

    def refresh_results(self, text: str) -> None:
        q = text.strip()
        self._entries.clear()
        self._row_widgets.clear()
        self.list_widget.clear()

        at_kw, rest = _parse_at(q)
        if at_kw is None:
            self._is_at_mode = False
            self._set_banner(None)
            self._populate_normal_mode(q)
        else:
            self._is_at_mode = True
            self._populate_at_mode(at_kw, rest)

        has_any = self.list_widget.count() > 0
        self.hint_label.setVisible(not has_any)
        if has_any:
            self.list_widget.setCurrentRow(0)

    def _populate_normal_mode(self, q: str) -> None:
        for result in self._app_service.search_normal(q):
            self._append_entry(
                title=result.title,
                subtitle=result.subtitle,
                icon=result.icon,
                payload=result.payload,
            )

    def _populate_at_mode(self, at_kw: str, rest: str) -> None:
        if at_kw == "":
            self._set_banner(None)
            self._show_at_listing(partial="")
            return

        plugin = self._app_service.find_at_plugin(at_kw)
        if plugin is None:
            self._set_banner(None)
            self._show_at_listing(at_kw)
            return

        self._set_banner(self._app_service.banner_for_plugin(plugin))

        if not rest:
            for entry in self._app_service.plugin_config_entries(plugin):
                self._append_entry(
                    title=entry.title,
                    subtitle=entry.subtitle,
                    icon=entry.icon,
                    payload=entry.payload,
                )
            return

        for result in self._app_service.search_at(at_kw, rest, plugin=plugin):
            self._append_entry(
                title=result.title,
                subtitle=result.subtitle,
                icon=result.icon,
                payload=result.payload,
            )

    def _show_at_listing(self, partial: str) -> None:
        for plugin in self._app_service.list_at_plugins(partial):
            self._append_entry(
                title=plugin.title,
                subtitle=plugin.subtitle,
                icon=plugin.icon,
                payload=plugin.payload,
            )

    def _append_entry(self, title: str, subtitle: str, icon: str, payload: Any) -> None:
        title_text = title.strip()
        icon_text = (icon or "").strip()
        if icon_text and title_text.startswith(icon_text):
            title_text = title_text[len(icon_text):].lstrip()

        item = QListWidgetItem("")
        row_widget = ResultRowWidget(icon_text or "•", title_text, subtitle, self.list_widget)
        item.setSizeHint(row_widget.sizeHint())
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, row_widget)
        self._entries.append(payload)
        self._row_widgets.append(row_widget)

    def _on_selection_changed(self) -> None:
        selected_row = self.list_widget.currentRow()
        for idx, row_widget in enumerate(self._row_widgets):
            row_widget.set_selected(idx == selected_row)

    def execute_current(self) -> None:
        row = self.list_widget.currentRow()
        if row < 0 and self.list_widget.count() > 0:
            row = 0
        if row < 0 or row >= len(self._entries):
            return

        payload = self._entries[row]
        if payload is None:
            return
        if isinstance(payload, tuple) and payload and payload[0] == "at_select":
            keyword = payload[1]
            self.search_input.setText(f"@{keyword} ")
            self.search_input.setFocus()
            self.search_input.setCursorPosition(len(self.search_input.text()))
            return

        try:
            ok, message = self._app_service.execute(payload)
            if ok and self._tray:
                self._tray.show_message("AlfredPy", message)
            self._flash_exec_banner(message, is_error=not ok)
            if hasattr(payload, "plugin_id") and hasattr(payload, "title"):
                logger.debug("execute result: plugin=%s title=%s", payload.plugin_id, payload.title)
        except Exception as ex:
            logger.error("执行失败: %s", ex, exc_info=True)
            if self._tray:
                self._tray.show_message("AlfredPy", f"执行失败: {ex}")
            self._flash_exec_banner(f"执行失败: {ex}", is_error=True)

    def exit_at_mode(self) -> None:
        self.search_input.clear()
        self.search_input.setFocus()

    def _set_banner(self, info: Optional[dict]) -> None:
        if not info:
            self.at_banner.setVisible(False)
            return
        self.at_banner_icon.setText(info["icon"])
        self.at_banner_title.setText(info["title"])
        self.at_banner_hint.setText(info["hint"])
        self.at_banner.setVisible(True)

    def _on_escape(self) -> None:
        if self._is_at_mode and self.search_input.text().strip():
            self.exit_at_mode()
            return
        self.hide()

    def _select_next(self) -> None:
        count = self.list_widget.count()
        if count == 0:
            return
        row = self.list_widget.currentRow()
        self.list_widget.setCurrentRow(min(count - 1, row + 1))

    def _select_prev(self) -> None:
        count = self.list_widget.count()
        if count == 0:
            return
        row = self.list_widget.currentRow()
        self.list_widget.setCurrentRow(max(0, row - 1))

    def show_and_focus(self) -> None:
        self.show()
        self.raise_()
        self.activateWindow()
        self.search_input.setFocus()

    def _flash_exec_banner(self, text: str, is_error: bool = False) -> None:
        if is_error:
            self.exec_banner.setStyleSheet(
                "background: rgba(200, 62, 62, 0.92);"
                "color: rgba(255, 246, 246, 0.98);"
                "border: 1px solid rgba(255, 160, 160, 0.82);"
                "border-radius: 8px;"
                "font-size: 13px;"
                "font-weight: 700;"
                "padding: 0 10px;"
            )
        else:
            self.exec_banner.setStyleSheet(
                "background: rgba(34, 180, 98, 0.92);"
                "color: rgba(245, 255, 249, 0.98);"
                "border: 1px solid rgba(122, 245, 172, 0.82);"
                "border-radius: 8px;"
                "font-size: 13px;"
                "font-weight: 700;"
                "padding: 0 10px;"
            )
        self.exec_banner.setText(text)
        self.exec_banner.setVisible(True)
        self._banner_timer.start(5000)

    def _hide_exec_banner(self) -> None:
        self.exec_banner.setVisible(False)


class SystemTray:
    def __init__(self, app: QApplication, on_show_window, on_quit):
        self._app = app
        self._on_show = on_show_window
        self._on_quit = on_quit
        self._tray_icon = QSystemTrayIcon()
        self._setup()

    def _setup(self) -> None:
        self._tray_icon.setIcon(self._create_text_icon("◆"))
        self._tray_icon.setToolTip("AlfredPy")
        menu = QMenu()

        show_action = QAction("显示窗口", self._app)
        show_action.triggered.connect(self._on_show)
        menu.addAction(show_action)

        menu.addSeparator()
        quit_action = QAction("退出", self._app)
        quit_action.triggered.connect(self._on_quit)
        menu.addAction(quit_action)

        self._tray_icon.setContextMenu(menu)
        self._tray_icon.activated.connect(self._on_activated)
        self._tray_icon.show()

    def _create_text_icon(self, text: str) -> QIcon:
        from PySide6.QtGui import QColor, QFont, QPainter, QPixmap

        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(0, 0, 0, 0))
        painter = QPainter(pixmap)
        font = QFont()
        font.setPixelSize(20)
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, text)
        painter.end()
        return QIcon(pixmap)

    def _on_activated(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self._on_show()

    def show_message(self, title: str, message: str) -> None:
        self._tray_icon.showMessage(title, message, QSystemTrayIcon.Information, 2000)


class GlobalHotkey:
    def __init__(self, hotkey: str, on_triggered):
        self._hotkey = hotkey
        self._on_triggered = on_triggered
        self._listener = None

    def start(self):
        try:
            from pynput import keyboard
            from pynput.keyboard import Key, KeyCode

            keys = []
            for part in self._hotkey.split("+"):
                part = part.strip().lower()
                if part.startswith("<") and part.endswith(">"):
                    key_name = part[1:-1]
                    keys.append(getattr(Key, key_name, None))
                else:
                    keys.append(KeyCode.from_char(part))

            if None in keys:
                logger.warning("无法解析热键: %s", self._hotkey)
                return

            current = set()

            def on_press(key):
                current.add(key)
                if all(k in current for k in keys):
                    self._on_triggered()

            def on_release(key):
                current.discard(key)

            self._listener = keyboard.Listener(on_press=on_press, on_release=on_release)
            self._listener.start()
            logger.info("全局热键已注册: %s", self._hotkey)
        except ImportError:
            logger.warning("pynput 未安装，全局热键不可用")
        except Exception as ex:
            logger.error("注册全局热键失败: %s", ex, exc_info=True)


def launch_gui(
    config_path: Optional[str] = None,
    show_tray: bool = True,
    hotkey: str = "<alt>+<space>",
):
    if singleton.try_show_existing():
        logger.info("已有 GUI 实例在运行，已发送唤起信号")
        return

    if not _claim_socket_and_start_listener():
        if singleton.try_show_existing():
            logger.info("已有 GUI 实例在运行，已发送唤起信号")
        return

    logger.info("启动 Qt Widgets GUI，配置参数：%s", config_path)

    from mif.plugins import PluginManager

    plugin_manager = PluginManager()
    logger.info("已加载插件：%s", list(plugin_manager.plugins.keys()))
    app_service = ApplicationService(plugin_manager)

    app = QApplication([sys.argv[0]])
    app.setApplicationName("AlfredPy")
    app.setOrganizationName("AlfredPy")
    app.setQuitOnLastWindowClosed(False)

    window = MainWindow(app_service)

    def show_window():
        window.show_and_focus()

    def quit_app():
        app.quit()

    _show_callback[0] = show_window

    tray = None
    if show_tray:
        tray = SystemTray(app, show_window, quit_app)
    window.set_tray(tray)

    if hotkey:
        hotkey_manager = GlobalHotkey(hotkey, show_window)
        hotkey_manager.start()

    window.show_and_focus()
    logger.info("Qt Widgets GUI 启动完成")
    sys.exit(app.exec())


def _main() -> None:
    parser = argparse.ArgumentParser(description="AlfredPy Qt Widgets GUI")
    parser.add_argument("--no-tray", action="store_true", help="不显示系统托盘图标")
    parser.add_argument("--no-hotkey", action="store_true", help="禁用全局热键")
    parser.add_argument("--hotkey", default="<alt>+<space>", help="自定义热键 (默认: <alt>+<space>)")
    parser.add_argument("config", nargs="?", help="配置文件路径")
    args = parser.parse_args()

    launch_gui(
        config_path=args.config,
        show_tray=not args.no_tray,
        hotkey="" if args.no_hotkey else args.hotkey,
    )


if __name__ == "__main__":
    _main()