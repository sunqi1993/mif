# alfredpy

一个轻量级的 Python 项目，提供类似 Alfred 的快速启动与工作流支持。

## ✅ 特性

- 快速调用命令/工作流
- 支持自定义工作流（配置 JSON）
- 支持插件式扩展（通过 `actions` 定义）

## 🚀 运行

安装（可选，建议在虚拟环境中运行）：

```bash
python -m pip install -e .
```

运行：

```bash
alfredpy
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
