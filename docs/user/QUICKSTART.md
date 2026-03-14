# 🚀 AlfredPy 快速入门

## 30 秒开始

### 1. 安装

```bash
# 使用 UV（推荐）
uv pip install -e ".[all]"

# 或使用 pip
pip install -e ".[all]"
```

### 2. 启动

```bash
# GUI 模式（图形界面）
./run.sh

# 可选参数
./run.sh --no-tray --no-hotkey
```

### 3. 使用

1. 输入关键词搜索工作流
2. 按 ↑↓ 选择
3. 按 Enter 执行
4. 按 Esc 关闭

## 4 种启动方式

| 方式 | 命令 | 说明 |
|------|------|------|
| GUI | `./run.sh` | 图形界面（推荐） |
| GUI(统一入口) | `python -m mif --gui` | 图形界面 |
| TUI | `python -m mif` | 终端界面 |
| 列表 | `python -m mif --list` | 查看工作流 |
| 帮助 | `./run.sh --help` | 显示帮助 |

## 配置工作流

编辑 `~/.mif/workflows.json`:

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
tail -f logs/mif_qt.log
```

## 常见问题

### GUI 无法启动？
```bash
# 安装 Qt 依赖
uv pip install -e ".[qt]"
```

### 热键不工作？
- **macOS**: 系统设置 > 隐私 > 辅助功能 > 添加终端
- **Linux**: 使用 X11 而非 Wayland
- **Windows**: 以管理员身份运行

### 找不到工作流？
确保 `~/.mif/workflows.json` 存在

## 更多文档

- [启动指南](STARTUP_GUIDE.md) - 详细使用说明
- [日志系统](LOGGING_SYSTEM.md) - 查看和管理日志

---

**Happy Launching! 🚀**
