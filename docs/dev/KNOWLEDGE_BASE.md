# AlfredPy 知识库（上下文与术语）

> 本页汇总项目术语、配置路径、插件/工作流设计、内置能力与关键代码位置，供后续开发与资料库（RAG/Agent）检索使用。  
> 最后更新：2026-03-14

---

## 一、项目概览与术语

| 术语 | 含义 |
|------|------|
| **Workflow** | 由 JSON 配置的静态动作条目（如打开链接、运行命令），定义在 `workflows.json`，由 **WorkflowPlugin** 以插件形式统一暴露。 |
| **Plugin** | 由 Python 实现的动态能力，实现 `BasePlugin`，可返回与查询相关的多条结果、可配置、支持 `@keyword` 触发。 |
| **PluginResult** | 插件/工作流暴露给 GUI 的**统一结果类型**（title、subtitle、icon、action、score、extra）。GUI 只处理 `PluginResult`。 |
| **@-mode** | 搜索框输入 `@关键词` 时进入的「单插件模式」，仅展示该插件结果并显示橙色横幅。 |
| **有效配置目录** | 读写的配置根目录：优先 `<项目根>/config/`，否则 `~/.alfredpy/`。 |

---

## 二、配置文件与路径一览

所有路径均通过 `alfredpy.config` 解析，**项目 config 优先，用户目录兜底**。

| 文件 | 路径（优先级从高到低） | 用途 | 写入方 |
|------|------------------------|------|--------|
| 工作流 | `config/workflows.json` → `workflows.json`(根) → `~/.alfredpy/workflows.json` | 工作流条目（id/name/action/args/keywords/icon/priority） | 用户/脚本 |
| 插件配置 | `config/plugin_configs.json` → `~/.alfredpy/plugin_configs.json` | 插件参数与 `_keywords`/`_at_keyword` 覆盖 | PluginManager、@settings |
| Chrome 书签点击 | `config/chrome_bookmarks_clicks.json` → `~/.alfredpy/chrome_bookmarks_clicks.json` | URL → 点击次数，用于书签排序 | ChromeBookmarksPlugin |

- **config.py** 提供：`effective_config_dir()`、`plugin_config_path()`、`workflow_config_path()`、`project_config_dir()`、`user_config_dir()`。

---

## 三、插件系统（核心抽象）

- **基类**：`alfredpy.plugins.base`
  - `PluginMeta`：id、name、description、icon、keywords、at_keyword、priority、config_options
  - `PluginResult`：title、subtitle、action、action_args、score、plugin_id、icon、extra
  - `ConfigOption`：key、name、type（str/int/float/bool/choice）、default、choices
  - `BasePlugin`：`get_meta()`、`search(query)`、`match_keyword()`、`strip_keyword()`、`execute(result)`、`get_config()`、`configure()`

- **PluginManager**（`alfredpy.plugins`）
  - 启动时扫描 `alfredpy/plugins/*.py`（除 base），自动注册 `BasePlugin` 子类。
  - 配置：`get_plugin_config(id)`、`set_plugin_config(id, key, value)`、`reset_plugin_config(id)`；支持键 `_keywords`、`_at_keyword` 覆盖插件元数据。
  - 搜索：`search(query)` 对所有插件按 keyword 匹配后调用 `search()`，按 score 排序；`search_at(at_keyword, query)` 仅调用对应插件；`find_by_at_keyword(kw)`、`all_at_plugins()`。

- **触发方式**
  - **前缀关键词**：用户输入以 `keywords` 中某一项开头时，该插件参与 `search()`，传入的是去掉关键词后的 query。
  - **@-关键词**：输入 `@xxx` 时由 launcher 解析，直接调用 `search_at("xxx", rest)`，仅该插件返回结果。

详见 [PLUGIN_CONFIG.md](PLUGIN_CONFIG.md)。

---

## 四、工作流系统

- **WorkflowItem**（`alfredpy.workflow`）：id、name、description、action、args、icon、priority、keywords。`run(query)` 执行时会将 args 中的 `{query}` 替换为传入的 query 再调用 ActionRegistry。
- **ActionRegistry**：内置动作如 `print`、`open_url`、`run`、`copy_to_clipboard`、`notify`、`open_file`、`write_file`、`read_file`、`set_env`、`change_dir` 等，通过 `ActionRegistry.run(action_name, args)` 执行。
- **WorkflowPlugin**（`alfredpy.plugins.workflow_plugin`）：内置插件，读取 `workflows.json`，将每条工作流转为 PluginResult；支持每条的关键词前缀匹配与模糊搜索（thefuzz）；`@wf` 可浏览/筛选工作流。工作流结果 `action_args=(subst_query,)` 供 `run(query)` 使用。

---

## 五、内置插件速查

| 插件 id | 名称 | at_keyword | 说明 |
|---------|------|------------|------|
| calculator | Calculator | calc | 数学表达式求值，支持 sin/sqrt 等；可配置 angle_unit、precision、thousands_sep。 |
| settings | 插件设置 | settings | 管理所有插件的触发词与参数；`@settings`、`@settings <id>`、`@settings <id> <key> <value>`、`@settings <id> reset`。 |
| workflows | Workflows | wf | 将 workflows.json 转为结果，关键词+模糊匹配，支持 `{query}`。 |
| chrome_bookmarks | Chrome 书签 | bm | 读取 Chrome Bookmarks 文件，按标题/URL 搜索；排序融合模糊分与点击率；点击数据存 `chrome_bookmarks_clicks.json`；可配置 bookmarks_path、profile、max_results、click_weight。 |

---

## 六、GUI 启动器（launcher.py）

- **单一结果类型**：所有展示项均为 `PluginResult`，统一用 `make_result_handler(result)` 执行（`plugin.execute(result)`），再根据 `result.extra.get("action_type") == "open_url"` 决定是否延迟关窗。
- **搜索流程**：输入若匹配 `@(\w*)(?:\s+(.*))?$` 则进入 @-mode，否则 `PluginManager.search(query)`，得到混合列表。
- **特殊 UI**：`plugin_id == "calculator"` 时用 **CalcPanel** 大卡片展示；@-mode 下显示 **AtModeBanner** 和可选 **ConfigItem**；`@` 无关键词时列出 **AtPluginItem**。
- **Enter**：执行当前第一条结果的 action；**Esc**：@-mode 下清空并退出 @，否则关窗。

详见 [FLET_COMPATIBILITY.md](FLET_COMPATIBILITY.md) 做 UI 开发。

---

## 七、Chrome 书签插件补充

- **书签文件路径**：macOS `~/Library/Application Support/Google/Chrome/Default/Bookmarks`，Windows `%LOCALAPPDATA%\Google\Chrome\User Data\Default\Bookmarks`，Linux `~/.config/google-chrome/Default/Bookmarks`；可通过配置 `bookmarks_path`、`profile` 覆盖。
- **点击率**：每次通过本插件打开书签会调用 `_open_and_record(url)`，对 `chrome_bookmarks_clicks.json` 中该 URL 计数 +1。
- **排序**：`综合分 = (1 - click_weight) * 模糊分 + click_weight * 点击率分`，点击率分使用 `log(1+count) / log(1+max_count)` 归一化；空查询时按点击率排序。

---

## 八、关键代码位置

| 职责 | 文件 |
|------|------|
| 配置路径与工作流加载 | `alfredpy/config.py` |
| 工作流定义与动作注册 | `alfredpy/workflow.py` |
| 插件基类与结果类型 | `alfredpy/plugins/base.py` |
| 插件发现、配置持久化、搜索与 @ 路由 | `alfredpy/plugins/__init__.py` |
| 计算器 | `alfredpy/plugins/calc_plugin.py` |
| 工作流包装为插件 | `alfredpy/plugins/workflow_plugin.py` |
| 插件配置 UI（@settings） | `alfredpy/plugins/settings_plugin.py` |
| Chrome 书签与点击率 | `alfredpy/plugins/chrome_bookmarks_plugin.py` |
| GUI 主界面与统一结果处理 | `alfredpy/gui/launcher.py` |
| macOS 菜单栏托管（PyObjC：左键打开 GUI，右键退出菜单） | `alfredpy/gui/menubar.py`、`start_menubar.py` |

---

## 九、文档索引

- [DOCS_INDEX.md](../../DOCS_INDEX.md) — 全项目文档入口
- [ARCHITECTURE.md](ARCHITECTURE.md) — 架构与数据流
- [PLUGIN_CONFIG.md](PLUGIN_CONFIG.md) — 插件配置详解
- [FLET_COMPATIBILITY.md](FLET_COMPATIBILITY.md) — Flet 组件与踩坑
- [LOGGING_DESIGN.md](LOGGING_DESIGN.md) — 日志设计
