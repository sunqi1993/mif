# 插件配置系统

> 版本：v1.0   最后更新：2026-03-14

---

## 目录

1. [配置文件位置与优先级](#配置文件位置与优先级)
2. [文件格式说明](#文件格式说明)
3. [可配置的内容](#可配置的内容)
4. [在搜索框中配置（@settings）](#在搜索框中配置settings)
5. [手动编辑 JSON 配置文件](#手动编辑-json-配置文件)
6. [Python API（代码中调用）](#python-api代码中调用)
7. [开发新插件时如何声明配置项](#开发新插件时如何声明配置项)
8. [配置加载顺序图](#配置加载顺序图)

---

## 配置文件位置与优先级

AlfredPy 遵循 **"项目优先，用户兜底"** 的原则，在两个位置查找配置文件：

| 优先级 | 路径 | 用途 |
|--------|------|------|
| **1（最高）** | `<项目根>/config/plugin_configs.json` | 团队/项目级别，随代码库版本管理 |
| **2（兜底）** | `~/.mif/plugin_configs.json` | 个人本地，不进入版本库 |

**读取规则**：优先读取项目 `config/` 目录；若该目录不存在，则退到用户目录。  
**写入规则**：写回到*读取源*，保证写入和读取在同一个文件里。

工作流配置文件同理：

| 优先级 | 路径 |
|--------|------|
| 1 | `<项目根>/config/workflows.json` |
| 2 | `<项目根>/workflows.json`（遗留，向后兼容） |
| 3 | `~/.mif/workflows.json` |

---

## 文件格式说明

`plugin_configs.json` 是一个标准 JSON 对象，**顶层 key 为插件 ID**：

```json
{
  "_comment": "此行为注释，以 _comment 开头的键会被系统忽略",
  "_comment_keys": {
    "_keywords":   "list[str]  覆盖插件的前缀触发词",
    "_at_keyword": "str        覆盖插件的 @-触发关键词",
    "其他键":      "由插件在 config_options 中声明的参数"
  },

  "calculator": {
    "_keywords":    ["=", "c", "计算"],
    "_at_keyword":  "math",
    "angle_unit":   "degrees",
    "precision":    4,
    "thousands_sep": true
  }
}
```

**注意**：
- 以 `_comment` 开头的顶层键是文档注释，加载时自动忽略，写入时原样保留。
- 以 `_` 开头的**插件内部键**（`_keywords`、`_at_keyword`）是元数据覆盖，其余键是普通参数。

---

## 可配置的内容

### 元数据覆盖（特殊下划线键）

| 键 | 类型 | 说明 | 示例 |
|----|------|------|------|
| `_keywords` | `list[str]` | 替换插件的**前缀触发词**（输入 `=` 或 `calc` 时自动匹配） | `["=", "c", "计算"]` |
| `_at_keyword` | `str` | 替换插件的 **@-触发关键词**（在搜索框输入 `@xxx` 时激活） | `"math"` |

### 插件参数（由插件自己声明）

每个插件在 `get_meta()` 的 `config_options` 中声明可配置参数。

**内置 Calculator 插件：**

| 参数 | 类型 | 默认值 | 可选值 | 说明 |
|------|------|--------|--------|------|
| `angle_unit` | choice | `radians` | `radians` / `degrees` | 三角函数角度单位 |
| `precision` | int | `0` | 任意正整数，0=自动 | 结果小数位数 |
| `thousands_sep` | bool | `true` | `true` / `false` | 整数结果是否显示千位分隔符 |

---

## 在搜索框中配置（@settings）

所有配置操作都可以在搜索框里完成，无需手动编辑文件。

### 命令格式

```
@settings                                   列出所有插件的配置摘要
@settings <plugin_id>                       查看该插件的完整配置
@settings <plugin_id> <key> <value>         设置参数（按 Enter 确认）
@settings <plugin_id> reset                 重置为默认值（按 Enter 确认）
```

### 操作示例

```
# 查看 Calculator 插件配置
@settings calculator

# 将角度单位改为度数
@settings calculator angle_unit degrees

# 将 @calc 改为 @math
@settings calculator _at_keyword math

# 将前缀触发词改为 = 和 c
@settings calculator _keywords = c

# 恢复所有默认值
@settings calculator reset
```

执行后，更改会**立即生效**并**自动写入** `config/plugin_configs.json`（项目 config 目录存在时）或 `~/.mif/plugin_configs.json`（用户兜底目录）。

---

## 手动编辑 JSON 配置文件

直接编辑 `config/plugin_configs.json`，**重启 mif 后生效**。

```json
{
  "calculator": {
    "angle_unit": "degrees",
    "precision": 2,
    "thousands_sep": false
  }
}
```

也可以通过 `@settings` 搜索结果中点击 "📄 配置文件" 条目直接用系统编辑器打开。

---

## Python API（代码中调用）

```python
from mif.plugins import PluginManager
from mif.config import (
    effective_config_dir,    # 当前生效的 config 目录
    plugin_config_path,      # plugin_configs.json 的绝对路径
    workflow_config_path,    # workflows.json 的绝对路径
    project_config_dir,      # <project>/config/ (若存在)
    user_config_dir,         # ~/.mif/
)

pm = PluginManager()

# 查询配置
pm.get_plugin_config("calculator")
# → {'angle_unit': 'radians', 'precision': 0, 'thousands_sep': True}

# 设置参数
pm.set_plugin_config("calculator", "angle_unit", "degrees")

# 设置元数据（触发词）
pm.set_plugin_config("calculator", "_at_keyword", "math")
pm.set_plugin_config("calculator", "_keywords", ["=", "c", "计算"])

# 查看当前生效的原始配置（含下划线元数据键）
pm.full_config_snapshot("calculator")
# → {'angle_unit': 'degrees', '_at_keyword': 'math', ...}

# 重置
pm.reset_plugin_config("calculator")

# 查看配置文件路径
print(pm.CONFIG_PATH)
# → /path/to/project/config/plugin_configs.json  （或 ~/.mif/...）
```

---

## 开发新插件时如何声明配置项

```python
from mif.plugins.base import BasePlugin, ConfigOption, PluginMeta, PluginResult

class MyPlugin(BasePlugin):
    def get_meta(self) -> PluginMeta:
        return PluginMeta(
            id="myplugin",
            name="我的插件",
            description="...",
            icon="🔧",
            at_keyword="myplugin",       # @myplugin 触发
            keywords=["mp"],             # 前缀 mp 触发
            priority=50,
            config_options=[
                ConfigOption(
                    key="mode",
                    name="运行模式",
                    description="插件的工作模式",
                    type="choice",
                    default="fast",
                    choices=["fast", "accurate"],
                ),
                ConfigOption(
                    key="max_results",
                    name="最大结果数",
                    type="int",
                    default=5,
                ),
                ConfigOption(
                    key="verbose",
                    name="详细输出",
                    type="bool",
                    default=False,
                ),
            ],
        )

    def search(self, query: str):
        mode = self.get_config("mode")            # → "fast" 或用户设置的值
        max_n = self.get_config("max_results")    # → 5 或用户设置的值
        verbose = self.get_config("verbose")      # → False 或用户设置的值
        # ...
```

插件注册后，用户即可通过 `@settings myplugin mode accurate` 修改配置，无需重启。

---

## 配置加载顺序图

```
PluginManager 初始化
        │
        ▼
读取配置文件
    ┌───────────────────────────────────────┐
    │  1. <project>/config/ 目录存在？       │
    │     YES → 读 config/plugin_configs.json│
    │     NO  → 读 ~/.mif/plugin_...        │
    └───────────────────────────────────────┘
        │
        ▼
发现并注册插件
        │
        ├── 有 _keywords 覆盖？  → 替换 plugin.meta.keywords
        ├── 有 _at_keyword 覆盖？→ 替换 plugin.meta.at_keyword
        └── 有普通参数？         → 调用 plugin.configure({...})
        │
        ▼
用户运行 @settings calculator angle_unit degrees
        │
        ▼
PluginManager.set_plugin_config("calculator", "angle_unit", "degrees")
        │
        ├── 更新内存中的 plugin._config
        └── 写回同一个配置文件（读哪里写哪里）
```
