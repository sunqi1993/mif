#!/bin/bash
# AlfredPy 启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目目录
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"
PYTHON=""

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查 Python 环境
check_python() {
    if [ -d "$VENV_DIR" ]; then
        # 使用虚拟环境
        if [ -f "$VENV_DIR/bin/activate" ]; then
            source "$VENV_DIR/bin/activate"
            PYTHON="$VENV_DIR/bin/python"
            print_success "使用虚拟环境: $VENV_DIR"
        else
            print_error "虚拟环境不完整，请重新安装"
            exit 1
        fi
    elif command -v python3 &> /dev/null; then
        # 使用系统 Python
        PYTHON="python3"
        print_warning "未找到虚拟环境，使用系统 Python3"
    elif command -v python &> /dev/null; then
        PYTHON="python"
        print_warning "未找到虚拟环境，使用系统 Python"
    else
        print_error "未找到 Python，请先安装 Python 3.9+"
        exit 1
    fi
}

# 检查依赖
check_dependencies() {
    print_info "检查依赖..."
    
    if ! $PYTHON -c "import flet" 2>/dev/null; then
        print_warning "Flet 未安装，正在安装 GUI 依赖..."
        if command -v uv &> /dev/null; then
            uv pip install "flet>=0.21.0" "pynput>=1.7.6"
        else
            pip3 install "flet>=0.21.0" "pynput>=1.7.6"
        fi
        print_success "GUI 依赖安装完成"
    fi
    
    if ! $PYTHON -c "import prompt_toolkit" 2>/dev/null; then
        print_warning "prompt_toolkit 未安装，正在安装 TUI 依赖..."
        if command -v uv &> /dev/null; then
            uv pip install "prompt_toolkit>=3.0" "thefuzz>=0.22.0"
        else
            pip3 install "prompt_toolkit>=3.0" "thefuzz>=0.22.0"
        fi
        print_success "TUI 依赖安装完成"
    fi
}

# 显示使用帮助
show_help() {
    echo ""
    echo "🚀 AlfredPy - Alfred 类快速启动工具"
    echo ""
    echo "用法:"
    echo "  ./run.sh [选项] [模式]"
    echo ""
    echo "模式:"
    echo "  gui      启动图形界面 (默认)"
    echo "  menubar  macOS 菜单栏托管，点击图标打开搜索 (仅 macOS)"
    echo "  tui      启动终端界面"
    echo "  hotkey   启动热键监听"
    echo "  list     列出工作流"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示帮助"
    echo "  -c, --config   指定配置文件路径"
    echo "  -i, --install  安装/更新依赖"
    echo "  -v, --verbose  显示详细信息"
    echo ""
    echo "示例:"
    echo "  ./run.sh                    # 启动 GUI"
    echo "  ./run.sh gui                # 启动 GUI"
    echo "  ./run.sh tui                # 启动 TUI"
    echo "  ./run.sh menubar            # macOS 菜单栏托管"
    echo "  ./run.sh hotkey             # 启动热键监听"
    echo "  ./run.sh list               # 列出工作流"
    echo "  ./run.sh -c ~/workflows.json gui"
    echo ""
}

# 安装依赖
install_dependencies() {
    print_info "安装依赖..."
    
    if command -v uv &> /dev/null; then
        print_info "使用 UV 安装..."
        uv pip install -e ".[dev,gui]"
    else
        print_info "使用 pip 安装..."
        pip3 install -e ".[dev,gui]"
    fi
    
    print_success "依赖安装完成"
}

# 启动 GUI 模式
start_gui() {
    local config_arg=""
    if [ -n "$CONFIG_PATH" ]; then
        config_arg="--config $CONFIG_PATH"
    fi
    
    print_info "启动 GUI 模式..."
    $PYTHON -m mif --gui $config_arg
}

# 启动 TUI 模式
start_tui() {
    local config_arg=""
    if [ -n "$CONFIG_PATH" ]; then
        config_arg="--config $CONFIG_PATH"
    fi
    
    print_info "启动 TUI 模式..."
    $PYTHON -m mif $config_arg
}

# 启动热键监听
start_hotkey() {
    print_info "启动热键监听..."
    print_success "按 Alt+Space 启动 AlfredPy"
    print_info "按 Ctrl+C 退出"
    $PYTHON -m mif.gui.hotkey
}

# 启动菜单栏托管 (仅 macOS)
start_menubar() {
    if [ "$(uname -s)" != "Darwin" ]; then
        print_error "menubar 模式仅支持 macOS"
        exit 1
    fi
    if ! $PYTHON -c "from AppKit import NSApplication" 2>/dev/null; then
        print_warning "PyObjC Cocoa 未安装，正在安装菜单栏依赖..."
        if command -v uv &> /dev/null; then
            uv pip install "pyobjc-framework-Cocoa>=10.0"
        else
            pip3 install "pyobjc-framework-Cocoa>=10.0"
        fi
    fi
    print_info "启动菜单栏 — 左键打开搜索（窗口不占 Dock），右键退出"
    $PYTHON start_menubar.py
}

# 列出工作流
list_workflows() {
    local config_arg=""
    if [ -n "$CONFIG_PATH" ]; then
        config_arg="--config $CONFIG_PATH"
    fi
    
    $PYTHON -m mif --list $config_arg
}

# 主函数
main() {
    # 解析参数
    MODE="menubar"
    CONFIG_PATH=""
    INSTALL=false
    VERBOSE=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -c|--config)
                CONFIG_PATH="$2"
                shift 2
                ;;
            -i|--install)
                INSTALL=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            gui)
                MODE="gui"
                shift
                ;;
            tui)
                MODE="tui"
                shift
                ;;
            menubar)
                MODE="menubar"
                shift
                ;;
            hotkey)
                MODE="hotkey"
                shift
                ;;
            list)
                MODE="list"
                shift
                ;;
            *)
                print_error "未知参数：$1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 切换到项目目录
    cd "$PROJECT_DIR"
    
    # 如果需要安装
    if [ "$INSTALL" = true ]; then
        install_dependencies
        exit 0
    fi
    
    # 检查环境
    check_python
    check_dependencies
    
    # 执行对应模式
    case $MODE in
        gui)
            start_gui
            ;;
        tui)
            start_tui
            ;;
        menubar)
            start_menubar
            ;;
        hotkey)
            start_hotkey
            ;;
        list)
            list_workflows
            ;;
        *)
            print_error "未知模式：$MODE"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"
