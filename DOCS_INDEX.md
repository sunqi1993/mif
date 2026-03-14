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
| [架构设计](docs/dev/ARCHITECTURE.md) | 项目架构说明 |
| [Flet 兼容性](docs/dev/FLET_COMPATIBILITY.md) | Flet API 适配指南 |
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
├── DOCS_INDEX.md             # 本文档索引
├── docs/
│   ├── user/                 # 用户文档
│   │   ├── QUICKSTART.md
│   │   ├── STARTUP_GUIDE.md
│   │   └── LOGGING_SYSTEM.md
│   └── dev/                  # 开发文档
│       ├── ARCHITECTURE.md
│       ├── FLET_COMPATIBILITY.md
│       └── LOGGING_DESIGN.md
└── .opencode/
    └── skills/               # Agent 技能
        ├── troubleshooting.md
        └── development.md
```

---

**最后更新**: 2026-03-14
