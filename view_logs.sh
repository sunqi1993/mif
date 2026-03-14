#!/bin/bash
# 查看 AlfredPy 日志

LOGS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/logs"

echo "📁 日志目录：$LOGS_DIR"
echo
echo "可用的日志文件:"
ls -lh "$LOGS_DIR"
echo
echo "选择要查看的日志:"
echo "  1. mif.log (完整日志)"
echo "  2. errors.log (错误日志)"
echo "  3. tail -f mif.log (实时跟踪)"
echo "  4. 清除所有日志"
echo

read -p "请选择 [1-4]: " choice

case $choice in
    1)
        echo "=== mif.log (最近 100 行) ==="
        tail -100 "$LOGS_DIR/mif.log"
        ;;
    2)
        echo "=== errors.log (所有错误) ==="
        cat "$LOGS_DIR/errors.log"
        ;;
    3)
        echo "实时跟踪日志... (Ctrl+C 退出)"
        tail -f "$LOGS_DIR/mif.log"
        ;;
    4)
        echo "清除日志文件..."
        > "$LOGS_DIR/mif.log"
        > "$LOGS_DIR/errors.log"
        echo "✅ 日志已清除"
        ;;
    *)
        echo "无效选择"
        ;;
esac
