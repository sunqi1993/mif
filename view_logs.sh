#!/usr/bin/env bash
# 查看 mif 日志

LOGS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/logs"

echo "📁 日志目录：$LOGS_DIR"
echo
echo "可用的日志文件:"
ls -lh "$LOGS_DIR"
echo
echo "选择要查看的日志:"
echo "  1. mif_qt.log (Qt GUI 日志)"
echo "  2. mif.log (兼容旧日志)"
echo "  3. errors.log (错误日志)"
echo "  4. tail -f mif_qt.log (实时跟踪)"
echo "  5. 清除常用日志"
echo

read -p "请选择 [1-5]: " choice

case $choice in
    1)
        echo "=== mif_qt.log (最近 120 行) ==="
        tail -120 "$LOGS_DIR/mif_qt.log"
        ;;
    2)
        echo "=== mif.log (最近 120 行) ==="
        tail -120 "$LOGS_DIR/mif.log"
        ;;
    3)
        echo "=== errors.log (所有错误) ==="
        if [ -f "$LOGS_DIR/errors.log" ]; then
            cat "$LOGS_DIR/errors.log"
        else
            echo "errors.log 不存在"
        fi
        ;;
    4)
        echo "实时跟踪 mif_qt.log ... (Ctrl+C 退出)"
        tail -f "$LOGS_DIR/mif_qt.log"
        ;;
    5)
        echo "清除日志文件..."
        [ -f "$LOGS_DIR/mif_qt.log" ] && > "$LOGS_DIR/mif_qt.log"
        [ -f "$LOGS_DIR/mif.log" ] && > "$LOGS_DIR/mif.log"
        [ -f "$LOGS_DIR/errors.log" ] && > "$LOGS_DIR/errors.log"
        echo "✅ 日志已清除"
        ;;
    *)
        echo "无效选择"
        ;;
esac
