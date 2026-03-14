# mif 架构说明（当前）

> 与 [KNOWLEDGE_BASE.md](KNOWLEDGE_BASE.md) 互补：本文侧重分层与数据流。

---

## 1. 项目结构

```
项目根/
├── mif/
│   ├── main.py                 # 统一 CLI 入口（--gui / --list / TUI）
│   ├── config.py               # 配置路径与配置读写
│   ├── workflow.py             # WorkflowItem、ActionRegistry
│   ├── logging_setup.py        # 统一日志初始化
│   ├── application/
│   │   └── service.py          # UI 与插件系统之间的应用服务层
│   ├── gui_qt/
│   │   ├── launcher.py         # Qt Widgets GUI
│   │   └── singleton.py        # GUI 单例唤起
│   └── plugins/
│       ├── base.py             # PluginMeta、PluginResult、BasePlugin
│       ├── registry.py         # 插件发现/注册
│       ├── config_store.py     # 插件配置持久化
│       ├── coordinator.py      # 搜索聚合与 @ 路由
│       ├── __init__.py         # PluginManager facade（兼容外部 API）
│       └── *_plugin.py         # 内置插件实现
├── config/                     # 项目级配置（存在时优先）
├── tests/
├── run.sh                      # GUI 快速入口（代理到 `python -m mif --gui`）
└── view_logs.sh
```

---

## 2. 分层与边界

- **UI 层**：`mif/gui_qt/launcher.py`
  - 负责交互、样式、窗口生命周期
  - 通过 `ApplicationService` 获取结果与执行动作
- **应用层**：`mif/application/service.py`
  - 负责将插件结果转换为 UI 可消费的结构
  - 统一执行消息格式（成功/失败提示）
- **领域层（插件系统）**：`mif/plugins/*`
  - `PluginManager` 保持外观 API 稳定
  - 内部分工为注册/配置/路由
- **基础设施层**：`mif/config.py`、`mif/logging_setup.py`
  - 配置路径策略、日志落盘策略

---

## 3. 主数据流

```
用户输入
  -> GUI（launcher）
  -> ApplicationService
  -> PluginManager facade
      -> PluginSearchCoordinator
      -> BasePlugin.search()/execute()
  -> ApplicationService 转换为 UiEntry
  -> GUI 渲染并执行反馈
```

`@` 模式路径：
```
GUI 解析 @keyword -> ApplicationService.find_at_plugin/search_at
```

---

## 4. 配置优先级

- 生效目录：`<project>/config`（存在时）优先，否则 `~/.mif`
- 工作流文件：
  1. `<project>/config/workflows.json`
  2. `<project>/workflows.json`（兼容）
  3. `~/.mif/workflows.json`
- 插件配置：`plugin_configs.json` 位于生效目录

---

## 5. 入口与运行

- 标准入口：`python -m mif`
- GUI：`python -m mif --gui`
- 快速脚本：`./run.sh`（内部转发到 `python -m mif --gui`）

---

**最后更新**：2026-03-15
