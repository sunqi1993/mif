#!/usr/bin/env bash
# AlfredPy 单入口脚本（仅 Qt Widgets GUI）

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$PROJECT_DIR/.venv/bin/python"

usage() {
  echo "用法: ./run.sh [--config <路径>] [--no-tray] [--no-hotkey] [--hotkey <组合键>]"
  echo "示例:"
  echo "  ./run.sh"
  echo "  ./run.sh --no-tray --no-hotkey"
  echo "  ./run.sh --config ./workflows.json"
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

# uv pip install -e .

exec uv run mif --gui "$@"
