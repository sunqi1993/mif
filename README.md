# alfredpy

一个轻量级的 Python 项目，提供类似 Alfred 的快速启动与工作流支持。

## ✅ 特性

- 快速调用命令/工作流
- 支持自定义工作流（配置 JSON）
- 支持插件式扩展（通过 `actions` 定义）

## 🚀 安装与运行

### 使用 uv（推荐）

```bash
# 安装所有依赖
uv pip install -e ".[all]"

# 或仅安装核心依赖
uv pip install -e .

# 运行
alfredpy
```

### 使用 pip

```bash
# 安装核心依赖
python -m pip install -e .

# 安装所有依赖（包括 GUI 和模糊搜索）
python -m pip install -e ".[all]"

# 运行
alfredpy
```

### 依赖说明

- **核心依赖**：`prompt_toolkit`（CLI 交互）、`flet`（GUI 界面）、`pynput`（全局热键）
- **可选依赖**：
  - `thefuzz`（模糊搜索增强，通过 `.[search]` 安装）
  - `pyperclip`（剪贴板支持，通过 `.[clipboard]` 安装）

- **核心依赖**：`prompt_toolkit`（CLI 交互）、`flet`（GUI 界面）、`pynput`（全局热键）
- **可选依赖**：`thefuzz`（模糊搜索增强，通过 `.[search]` 安装）

### GUI 启动

```bash
# 启动 GUI 界面
python start_gui.py

# 启动全局热键监听（Alt+Space 触发）
python start_hotkey.py
```

## 🧩 工作流配置

默认配置文件：`~/.alfredpy/workflows.json`

示例：

```json
[
  {
    "id": "open_google",
    "name": "打开 Google",
    "description": "在默认浏览器中打开 Google",
    "action": "open_url",
    "args": { "url": "https://www.google.com" }
  },
  {
    "id": "say_hello",
    "name": "显示问候",
    "description": "在终端中输出一句话",
    "action": "print",
    "args": { "text": "Hello from alfredpy!" }
  }
]
```

## 🛠️ 扩展工作流类型

工作流通过 `alfredpy/workflow.py` 中的 `ActionRegistry` 进行注册，可自定义更多操作类型。
