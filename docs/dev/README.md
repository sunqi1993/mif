# 🛠️ AlfredPy 开发文档

## 文档目录

- [架构设计](ARCHITECTURE.md) - 项目架构说明
- [Flet 兼容性](FLET_COMPATIBILITY.md) - Flet API 适配
- [日志设计](LOGGING_DESIGN.md) - 日志系统实现
- [变更日志](CHANGELOG.md) - 版本更新记录

## 快速链接

- 用户文档：`docs/user/`
- Agent 技能：`.opencode/skills/`

## 开发环境

```bash
# 安装依赖
uv pip install -e ".[dev,gui]"

# 运行测试
pytest

# 查看覆盖率
pytest --cov=alfredpy
```

## 代码规范

- Python 3.9+
- 类型提示
- 日志记录
- 异常处理

---

**最后更新**: 2026-03-14
