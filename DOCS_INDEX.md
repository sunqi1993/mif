# 📚 AlfredPy 文档索引

## 👤 用户文档 (docs/user/)

适合最终用户使用：

| 文档 | 说明 |
|------|------|
| [快速入门](docs/user/QUICKSTART.md) | 30 秒开始使用 |
| [启动指南](docs/user/STARTUP_GUIDE.md) | 详细启动说明 |
| [日志系统](docs/user/LOGGING_SYSTEM.md) | 查看和管理日志 |

## 🛠️ 开发文档 (docs/dev/)

适合开发者参考：

| 文档 | 说明 |
|------|------|
| [知识库（上下文）](docs/dev/KNOWLEDGE_BASE.md) | 术语、配置与路径、插件/工作流、内置插件、GUI、代码位置（资料库/Agent 优先读） |
| [架构设计](docs/dev/ARCHITECTURE.md) | 项目结构、配置优先级、数据流、插件与工作流边界 |
| [插件配置系统](docs/dev/PLUGIN_CONFIG.md) | 配置文件位置、格式、@settings 命令、API 参考、新插件声明配置项 |
| [Flet API 参考](docs/dev/FLET_COMPATIBILITY.md) | v0.82.2 组件参数完整列表、踩坑记录、常用模式速查（Agent 必读） |
| [日志设计](docs/dev/LOGGING_DESIGN.md) | 日志系统实现 |

## 🤖 Agent 技能 (.opencode/skills/)

供 Agent 开发使用：

| 技能 | 说明 |
|------|------|
| [故障排查](.opencode/skills/troubleshooting.md) | 问题诊断和修复 |
| [开发指南](.opencode/skills/development.md) | 功能开发规范 |

## 快速链接

- **主 README**: [README.md](README.md)
- **启动脚本**: `./run.sh`
- **日志查看**: `./view_logs.sh`
- **测试命令**: `pytest`

## 文档结构

```
alfredpy/
├── README.md                  # 项目主文档
├── DOCS_INDEX.md              # 本文档索引
├── config/                    # ⭐ 项目级配置（优先于 ~/.alfredpy/）
│   ├── plugin_configs.json    #   插件参数 + 触发词覆盖
│   ├── workflows.json         #   工作流定义
│   └── chrome_bookmarks_clicks.json  # Chrome 书签点击统计（排序用）
├── docs/
│   ├── user/                  # 用户文档
│   │   ├── QUICKSTART.md
│   │   ├── STARTUP_GUIDE.md
│   │   └── LOGGING_SYSTEM.md
│   └── dev/                   # 开发文档
│       ├── KNOWLEDGE_BASE.md  #   知识库 / 上下文（资料库用）
│       ├── ARCHITECTURE.md
│       ├── PLUGIN_CONFIG.md
│       ├── FLET_COMPATIBILITY.md
│       └── LOGGING_DESIGN.md
└── .opencode/
    └── skills/                # Agent 技能
        ├── troubleshooting.md
        └── development.md
```

---

**最后更新**: 2026-03-14
