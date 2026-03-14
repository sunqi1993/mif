#!/usr/bin/env bash
# AlfredPy 单入口脚本（仅 Qt Widgets GUI）

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$PROJECT_DIR/.venv/bin/python"

usage() {
  echo "用法: ./run.sh [--no-tray] [--no-hotkey] [--hotkey <组合键>] [config_path]"
  echo "示例:"
  echo "  ./run.sh"
  echo "  ./run.sh --no-tray --no-hotkey"
  echo "  ./run.sh --hotkey '<alt>+<space>'"
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

cd "$PROJECT_DIR"

if [[ -x "$VENV_PYTHON" ]]; then
  PYTHON_BIN="$VENV_PYTHON"
else
  PYTHON_BIN="$(command -v python3 || command -v python || true)"
fi

if [[ -z "${PYTHON_BIN:-}" ]]; then
  echo "❌ 未找到 Python，请先安装 Python 3.10+"
  exit 1
fi

if ! "$PYTHON_BIN" -c "import PySide6" >/dev/null 2>&1; then
  echo "❌ 缺少 PySide6，请先安装："
  echo "   uv pip install -e '.[qml]'"
  echo "   或 pip install PySide6>=6.5.0"
  exit 1
fi

exec "$PYTHON_BIN" -m mif.gui_qml.launcher "$@"
