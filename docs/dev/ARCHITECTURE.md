# 🏗️ AlfredPy 架构文档

## 项目结构

```
alfredpy/
├── alfredpy/
│   ├── main.py              # 主程序入口
│   ├── workflow.py          # 工作流引擎
│   ├── config.py            # 配置管理
│   └── gui/
│       ├── launcher.py      # GUI 界面
│       └── hotkey.py        # 热键管理
├── tests/
├── logs/
└── docs/
```

## 核心模块

### 1. main.py

- TUI/GUI 双模式入口
- 命令行参数解析
- 模糊搜索集成

### 2. workflow.py

- ActionRegistry 动作注册
- 10 个内置动作
- 工作流执行引擎

### 3. config.py

- JSON 配置加载
- ConfigWatcher 热重载
- 配置缓存

### 4. gui/launcher.py

- Flet GUI 实现
- 实时搜索
- SnackBar 通知

### 5. gui/hotkey.py

- pynput 热键监听
- GlobalHotkeyManager
- 全局快捷键支持

## 数据流

```
用户输入 → 搜索匹配 → 工作流选择 → 动作执行 → 结果反馈
    ↓                                            ↓
模糊搜索                                    SnackBar/日志
```

## 插件系统

```python
from alfredpy.plugins.base import BasePlugin

class MyPlugin(BasePlugin):
    def search(self, query: str) -> list:
        # 实现搜索逻辑
        pass
```

## 测试架构

- `test_workflow.py` - 工作流动作测试
- `test_config.py` - 配置管理测试
- `test_main.py` - 主程序测试
- `test_gui.py` - GUI 模块测试

---

**最后更新**: 2026-03-14
