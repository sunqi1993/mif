#!/usr/bin/env python3
"""AlfredPy 热键启动脚本 - 后台监听全局热键."""

import sys
import os
from pathlib import Path

# 添加项目目录到 Python 路径
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

def main():
    """启动热键监听."""
    print("🚀 AlfredPy - 热键监听")
    print("=" * 50)
    print()
    
    try:
from mif.gui.hotkey import GlobalHotkeyManager
from mif.gui.launcher import launch_gui
    except ImportError as e:
        print(f"❌ 导入失败：{e}")
        print()
        print("请安装依赖:")
        print("  pip install pynput flet")
        print()
        input("按 Enter 退出...")
        return 1
    
    launcher_window = None
    
    def show_launcher():
        """显示启动器窗口."""
        nonlocal launcher_window
        print("🔔 Alt+Space 触发！启动 AlfredPy...")
        
        import threading
        def launch():
            try:
                launch_gui()
            except Exception as e:
                print(f"❌ 启动失败：{e}")
        
        if launcher_window is None or not launcher_window.is_alive():
            launcher_window = threading.Thread(target=launch, daemon=True)
            launcher_window.start()
        else:
            print("⚠️  窗口已打开")
    
    # 注册热键
    manager = GlobalHotkeyManager("<alt>+<space>")
    
    if manager.register(show_launcher):
        print("✅ 热键已注册：Alt+Space")
        print()
        print("使用说明:")
        print("  • 按 Alt+Space 启动 AlfredPy")
        print("  • 按 Esc 关闭启动器窗口")
        print("  • 按 Ctrl+C 退出热键监听")
        print()
        
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print()
            manager.unregister()
            print("✅ 热键监听已停止")
            return 0
    else:
        print("❌ 热键注册失败")
        print()
        print("可能原因:")
        print("  • macOS: 需要辅助功能权限")
        print("  • Linux: 可能需要禁用 Wayland")
        print("  • Windows: 需要管理员权限")
        return 1


if __name__ == "__main__":
    sys.exit(main())
