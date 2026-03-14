# AlfredPy 架构说明

> 与 [KNOWLEDGE_BASE.md](KNOWLEDGE_BASE.md) 互补：本文侧重结构与数据流，知识库侧重术语与速查。

---

## 1. 项目结构

```
项目根/
├── alfredpy/
│   ├── __init__.py
│   ├── __main__.py
│   ├── main.py           # TUI/GUI 入口
│   ├── config.py         # 配置路径与 workflow 加载
│   ├── workflow.py       # WorkflowItem、ActionRegistry
│   ├── gui/
│   │   ├── launcher.py   # Flet 主界面，统一 PluginResult 处理
│   │   └── hotkey.py     # 全局热键
│   └── plugins/
│       ├── base.py       # PluginMeta、PluginResult、BasePlugin、ConfigOption
│       ├── __init__.py   # PluginManager
│       ├── calc_plugin.py
│       ├── workflow_plugin.py   # 将 workflows.json 转为插件结果
│       ├── settings_plugin.py   # @settings 配置管理
│       └── chrome_bookmarks_plugin.py
├── config/               # 项目级配置（优先）
│   ├── workflows.json
│   ├── plugin_configs.json
│   └── chrome_bookmarks_clicks.json
├── docs/
│   ├── user/
│   └── dev/
├── tests/
├── run.sh
└── workflows.json        # 遗留，仍参与路径优先级
```

---

## 2. 配置目录优先级

- **有效配置目录**：`config/` 存在则用项目下 `config/`，否则用 `~/.alfredpy/`。
- 工作流：`load_config()` 依次查找 `config/workflows.json`、根目录 `workflows.json`、`~/.alfredpy/workflows.json`。
- 插件配置与 Chrome 点击数据：均放在「有效配置目录」下对应 JSON 文件。

---

## 3. 数据流（当前设计）

```
用户输入
    │
    ├─ 匹配 "@关键词" ──→ 解析 (at_kw, rest)
    │                        │
    │                        ├─ at_kw 为空 → 列出所有 @-插件
    │                        └─ at_kw 有值 → PluginManager.search_at(at_kw, rest)
    │                                            │
    │                                            └─→ 单插件结果 + AtModeBanner（可含配置面板）
    │
    └─ 普通输入 ──→ PluginManager.search(query)
                         │
                         ├─ WorkflowPlugin  → 来自 workflows.json，模糊+关键词
                         ├─ CalcPlugin      → 表达式求值（可置顶 CalcPanel）
                         ├─ ChromeBookmarksPlugin → 书签 + 点击率排序
                         ├─ SettingsPlugin  → match_keyword 恒为 False，不参与
                         └─ 其他插件
                         │
                         └─→ 合并为 List[PluginResult]，按 score 排序
                                    │
                                    └─→ launcher 统一用 make_result_handler(result)
                                             执行 plugin.execute(result)，必要时关窗
```

---

## 4. 插件与工作流的边界

| 维度 | Workflow（JSON） | Plugin（Python） |
|------|------------------|------------------|
| 定义 | workflows.json，静态条目 | 代码，BasePlugin 子类 |
| 结果 | 由 WorkflowPlugin 转成 PluginResult | 直接返回 List[PluginResult] |
| 参数 | args 固定，支持 `{query}` 占位 | 可任意逻辑、可配置 |
| 适用 | 简单动作、团队可编辑 JSON | 动态搜索、复杂逻辑、需状态/配置 |

工作流通过 **WorkflowPlugin** 接入统一搜索与执行路径，GUI 不区分来源，只认 PluginResult。

---

## 5. 核心模块职责

- **config.py**：解析有效配置目录、workflow/plugin 配置文件路径，提供 `load_config()`。
- **workflow.py**：WorkflowItem 数据结构与 `run(query)` 的 `{query}` 替换；ActionRegistry 注册与执行。
- **plugins/base.py**：插件契约（meta、result、config_options、match/strip/execute）。
- **plugins/__init__.py**：插件发现、配置读写、`search`/`search_at` 路由。
- **gui/launcher.py**：Flet 页面、输入解析、@-mode 与普通搜索、统一结果渲染与执行（含 CalcPanel、AtModeBanner 等）。

---

## 6. 测试与入口

- 测试：`pytest`，见 `tests/`。
- 启动：`./run.sh`（gui/tui/hotkey/list），或 `python -m alfredpy`。

---

**最后更新**：2026-03-14
