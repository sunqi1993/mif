#!/usr/bin/env python3
"""AlfredPy GUI 启动脚本 - 双击即可运行."""

import sys
import os
from pathlib import Path

# 添加项目目录到 Python 路径
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

def main():
    """启动 AlfredPy GUI."""
    print("🚀 AlfredPy - 正在启动 GUI...")
    print()
    
    try:
        # 尝试导入 Flet
        import flet as ft
        print(f"✅ Flet 版本：{ft.__version__}")
    except ImportError:
        print("❌ Flet 未安装！")
        print()
        print("请安装 GUI 依赖:")
        print("  pip install flet>=0.21.0 pynput>=1.7.6")
        print("  或")
        print("  uv pip install -e \".[gui]\"")
        print()
        input("按 Enter 退出...")
        return 1
    
    try:
        # 启动 GUI
        from alfredpy.gui.launcher import launch_gui
        
        # 支持配置文件参数
        config_path = None
        if len(sys.argv) > 1:
            config_path = sys.argv[1]
        
        launch_gui(config_path)
        return 0
        
    except Exception as e:
        print(f"❌ 启动失败：{e}")
        print()
        import traceback
        traceback.print_exc()
        input("按 Enter 退出...")
        return 1


if __name__ == "__main__":
    sys.exit(main())
