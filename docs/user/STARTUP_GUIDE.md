# 📖 AlfredPy 启动指南

## 启动方式

### 1. Shell 脚本（推荐）

```bash
./run.sh                    # GUI 模式
./run.sh --no-tray          # 关闭托盘
./run.sh --no-hotkey        # 关闭全局热键
./run.sh --hotkey "<alt>+<space>"
./run.sh --help             # 显示帮助
```

### 2. Python 命令

```bash
python -m mif --gui         # GUI
python -m mif               # TUI
python -m mif --list        # 列出工作流
```

### 3. 脚本入口（安装后）

```bash
mif --gui                   # GUI
mif                         # TUI
```

### 4. 桌面快捷方式

- **macOS**: 双击 `AlfredPy.app`
- **Windows**: 双击 `alfredpy.bat`

## 常用参数

| 参数 | 说明 |
|------|------|
| `-c, --config` | 指定配置文件 |
| `--no-tray` | GUI 模式下禁用托盘 |
| `--no-hotkey` | GUI 模式下禁用全局热键 |
| `--hotkey` | 自定义 GUI 全局热键 |
| `-h, --help` | 显示帮助 |

## 示例

```bash
# 使用自定义配置
./run.sh --config ~/workflows.json
```
