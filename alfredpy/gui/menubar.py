"""macOS 菜单栏 — 可与 GUI 同进程（单任务栏图标），或独立进程运行。

• attach_menubar_to_current_process(on_show_window)：在当前进程挂载托盘图标，左键回调唤起窗口，
  右键「退出」结束应用。供 launcher 在 main(page) 内调用，实现「一个进程 = 一个 Dock 图标 + 托盘」。
• run_menubar()：独立进程模式（仅保留兼容），阻塞运行托盘并子进程启动 GUI；不推荐，会出两个任务栏。
"""

from __future__ import annotations

import sys
import subprocess
import os
from pathlib import Path
from typing import Callable

if sys.platform != "darwin":
    raise RuntimeError("menubar 仅支持 macOS，当前系统: %s" % sys.platform)

# PyObjC
from AppKit import (
    NSApplication,
    NSStatusBar,
    NSVariableStatusItemLength,
    NSMenu,
    NSMenuItem,
    NSEvent,
    NSRightMouseUp,
)
NSEventMaskLeftMouseUp = 1 << 2
NSEventMaskRightMouseUp = 1 << 4
from Foundation import NSObject
from objc import super

from alfredpy.gui import singleton

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def _launch_gui_subprocess() -> None:
    """若已有 GUI 在跑则只唤起；否则子进程启动 GUI。仅用于 run_menubar() 独立进程模式。"""
    if singleton.try_show_existing():
        return
    cmd = [sys.executable, "-c", "from alfredpy.gui.launcher import launch_gui; launch_gui()"]
    subprocess.Popen(
        cmd,
        cwd=str(_PROJECT_ROOT),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


class StatusBarDelegate(NSObject):
    """左键：回调 on_show；右键：弹出「退出」菜单。"""

    def init(self):
        self = super().init()
        if self is None:
            return None
        self._status_item = None
        self._quit_menu = None
        self._on_show: Callable[[], None] | None = None
        return self

    def setStatusItem_(self, item):
        self._status_item = item

    def setQuitMenu_(self, menu):
        self._quit_menu = menu

    def setOnShow_(self, fn):
        self._on_show = fn

    def onClick_(self, sender):
        event = NSApplication.sharedApplication().currentEvent()
        if event.type() == NSRightMouseUp:
            if self._status_item and self._quit_menu:
                self._status_item.popUpStatusItemMenu_(self._quit_menu)
        elif self._on_show:
            self._on_show()
        else:
            _launch_gui_subprocess()

    def onQuit_(self, sender):
        NSApplication.sharedApplication().terminate_(None)


def attach_menubar_to_current_process(on_show_window: Callable[[], None]) -> None:
    """在当前进程挂载菜单栏图标，不启动子进程、不阻塞。左键调用 on_show_window，右键退出本进程。
    供 GUI 进程在 main(page) 内调用，实现单进程 = 一个 Dock/任务栏图标 + 托盘。
    """
    app = NSApplication.sharedApplication()
    status_bar = NSStatusBar.systemStatusBar()
    status_item = status_bar.statusItemWithLength_(NSVariableStatusItemLength)
    status_item.setTitle_("◆")
    status_item.setHighlightMode_(True)

    quit_menu = NSMenu.alloc().init()
    quit_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
        "退出", "onQuit:", ""
    )
    quit_menu.addItem_(quit_item)

    delegate = StatusBarDelegate.alloc().init()
    delegate.setStatusItem_(status_item)
    delegate.setQuitMenu_(quit_menu)
    delegate.setOnShow_(on_show_window)
    quit_item.setTarget_(delegate)

    attach_menubar_to_current_process._delegate = delegate  # type: ignore[attr-defined]

    btn = status_item.button()
    btn.setTarget_(delegate)
    btn.setAction_("onClick:")
    btn.sendActionOn_(NSEventMaskLeftMouseUp | NSEventMaskRightMouseUp)


def run_menubar() -> None:
    """独立进程模式：本进程仅托盘（不占 Dock），左键子进程启动 GUI（Dock 只显示 GUI 一个图标）。"""
    app = NSApplication.sharedApplication()
    # 托盘进程设为 Accessory，不占 Dock；只保留 GUI 进程在 Dock
    try:
        from AppKit import NSApplicationActivationPolicyAccessory
        app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
    except Exception:
        pass

    status_bar = NSStatusBar.systemStatusBar()
    status_item = status_bar.statusItemWithLength_(NSVariableStatusItemLength)
    status_item.setTitle_("◆")
    status_item.setHighlightMode_(True)

    quit_menu = NSMenu.alloc().init()
    quit_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
        "退出", "onQuit:", ""
    )
    quit_menu.addItem_(quit_item)

    delegate = StatusBarDelegate.alloc().init()
    delegate.setStatusItem_(status_item)
    delegate.setQuitMenu_(quit_menu)
    delegate.setOnShow_(None)  # 左键走 _launch_gui_subprocess
    quit_item.setTarget_(delegate)
    run_menubar._delegate = delegate  # type: ignore[attr-defined]

    btn = status_item.button()
    btn.setTarget_(delegate)
    btn.setAction_("onClick:")
    btn.sendActionOn_(NSEventMaskLeftMouseUp | NSEventMaskRightMouseUp)

    app.run()
