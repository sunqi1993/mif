# 🚀 AlfredPy 快速入门

## 30 秒开始

### 1. 安装

```bash
# 使用 UV（推荐）
uv pip install -e ".[dev,gui]"

# 或使用 pip
pip install -e ".[dev,gui]"
```

### 2. 启动

```bash
# GUI 模式（图形界面）
./run.sh gui

# 或
python start_gui.py
```

### 3. 使用

1. 输入关键词搜索工作流
2. 按 ↑↓ 选择
3. 按 Enter 执行
4. 按 Esc 关闭

## 5 种启动方式

| 方式 | 命令 | 说明 |
|------|------|------|
| GUI | `./run.sh gui` | 图形界面（推荐） |
| TUI | `./run.sh tui` | 终端界面 |
| 热键 | `./run.sh hotkey &` | Alt+Space 唤醒 |
| 列表 | `./run.sh list` | 查看工作流 |
| 帮助 | `./run.sh --help` | 显示帮助 |

## 配置工作流

编辑 `~/.alfredpy/workflows.json`:

```json
[
  {
    "id": "github",
    "name": "GitHub",
    "description": "打开 GitHub",
    "action": "open_url",
    "args": {"url": "https://github.com"}
  },
  {
    "id": "hello",
    "name": "问候",
    "description": "打印问候",
    "action": "print",
    "args": {"text": "Hello!"}
  }
]
```

## 内置动作

| 动作 | 描述 |
|------|------|
| `print` | 打印文本 |
| `open_url` | 打开 URL |
| `run` | 执行命令 |
| `open_file` | 打开文件 |
| `copy_to_clipboard` | 复制文本 |
| `notify` | 发送通知 |

## 查看日志

```bash
# 查看日志
./view_logs.sh

# 或
tail -f logs/alfredpy.log
```

## 常见问题

### GUI 无法启动？
```bash
# 检查依赖
./run.sh -i
```

### 热键不工作？
- **macOS**: 系统设置 > 隐私 > 辅助功能 > 添加终端
- **Linux**: 使用 X11 而非 Wayland
- **Windows**: 以管理员身份运行

### 找不到工作流？
确保 `~/.alfredpy/workflows.json` 存在

## 更多文档

- [启动指南](STARTUP_GUIDE.md) - 详细使用说明
- [日志系统](LOGGING_SYSTEM.md) - 查看和管理日志

---

**Happy Launching! 🚀**
