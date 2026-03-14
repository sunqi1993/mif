#!/usr/bin/env python3
"""AlfredPy 启动入口 — macOS 下启动一个进程：GUI 窗口 + 菜单栏图标（单任务栏图标）。"""

import sys
from pathlib import Path

# 确保项目根在 path 中
project_dir = Path(__file__).resolve().parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))


def main():
    if sys.platform != "darwin":
        print("❌ 菜单栏模式仅支持 macOS。")
        print("   当前系统: %s" % sys.platform)
        return 1

    try:
        from AppKit import NSApplication, NSStatusBar
        from objc import super  # 来自 pyobjc-core
    except ImportError as e:
        print("❌ 未安装 PyObjC，请先安装菜单栏依赖：")
        print("   pip install pyobjc-framework-Cocoa")
        print("   或  uv pip install 'alfredpy[menubar]'")
        print("   错误: %s" % e)
        return 1

    # 托盘独立进程（Flet 与 NSApplication 不同步，同进程托盘不显示）；GUI 子进程不占 Dock
    try:
        from alfredpy.gui.menubar import run_menubar
        run_menubar()
        return 0
    except Exception as e:
        print("❌ 启动失败：%s" % e)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
