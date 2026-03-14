# 💻 AlfredPy 开发技能

## 技能描述

用于 AlfredPy 项目的功能开发和新特性实现。

## 项目结构

```
alfredpy/
├── alfredpy/
│   ├── main.py           # TUI/GUI 入口
│   ├── workflow.py       # 工作流引擎
│   ├── config.py         # 配置管理
│   └── gui/
│       ├── launcher.py   # GUI 界面
│       └── hotkey.py     # 热键管理
├── tests/                # 测试用例
├── logs/                 # 日志文件
└── docs/                 # 文档
```

## 开发规范

### 1. 代码风格

- Python 3.9+
- 类型提示
- 日志记录
- 异常处理

### 2. 日志使用

```python
import logging
logger = logging.getLogger("AlfredPy")

logger.debug("调试信息")
logger.info("运行信息")
logger.error("错误信息", exc_info=True)
```

### 3. 异常处理

```python
try:
    # 业务逻辑
    pass
except Exception as e:
    logger.error(f"操作失败：{e}", exc_info=True)
    raise
```

## 添加新功能

### 1. 新增工作流动作

```python
# alfredpy/workflow.py
@ActionRegistry.register("my_action")
def action_my_action(args: dict) -> None:
    """动作描述"""
    # 实现逻辑
    pass
```

### 2. 新增插件

```python
# alfredpy/plugins/my_plugin.py
from alfredpy.plugins.base import BasePlugin, PluginMeta, PluginResult

class MyPlugin(BasePlugin):
    def get_meta(self) -> PluginMeta:
        return PluginMeta(
            id="my_plugin",
            name="My Plugin",
            keywords=["my"],
        )
    
    def search(self, query: str) -> list[PluginResult]:
        # 实现搜索
        pass
```

### 3. GUI 更新

```python
# alfredpy/gui/launcher.py
def show_snackbar(page, message):
    snackbar = ft.SnackBar(...)
    page.overlay.append(snackbar)
    snackbar.open = True
    page.update()
```

## 测试要求

- 新增功能必须添加测试
- 保持测试覆盖率 >50%
- 核心模块 >90%

```bash
# 运行测试
pytest

# 查看覆盖率
pytest --cov=alfredpy --cov-report=html
```

## Flet API 注意事项

- 使用 `page.window.close()` 关闭
- 使用 `page.overlay.append()` 显示 SnackBar
- 不要调用 `window.center()` (协程)
- 参考 `docs/dev/FLET_COMPATIBILITY.md`

## 提交检查清单

- [ ] 代码通过测试
- [ ] 添加必要日志
- [ ] 更新文档
- [ ] 无类型错误
- [ ] 异常正确处理

---

**技能版本**: 1.0
**最后更新**: 2026-03-14
