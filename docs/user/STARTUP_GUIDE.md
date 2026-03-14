# 📖 AlfredPy 启动指南

## 启动方式

### 1. Shell 脚本（推荐）

```bash
./run.sh                    # GUI 模式
./run.sh gui                # 同上
./run.sh tui                # 终端模式
./run.sh hotkey             # 热键监听
./run.sh list               # 列出工作流
./run.sh --help             # 显示帮助
```

### 2. Python 脚本

```bash
python start_gui.py         # GUI
python start_hotkey.py      # 热键
```

### 3. 直接命令

```bash
alfredpy --gui              # GUI
alfredpy                    # TUI
python -m alfredpy --gui    # 开发模式
```

### 4. 桌面快捷方式

- **macOS**: 双击 `AlfredPy.app`
- **Windows**: 双击 `alfredpy.bat`

## 常用参数

| 参数 | 说明 |
|------|------|
| `-c, --config` | 指定配置文件 |
| `-i, --install` | 安装依赖 |
| `-h, --help` | 显示帮助 |

## 示例

```bash
# 使用自定义配置
./run.sh -c ~/workflows.json gui

# 安装依赖
./run.sh -i

# 热键常驻后台
./run.sh hotkey &
```
