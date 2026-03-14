# 🤖 AlfredPy Agent 技能

## 技能目录

- [故障排查](troubleshooting.md) - 问题诊断和修复
- [开发指南](development.md) - 功能开发规范

## 使用场景

### 故障排查

当用户报告问题时:
1. 加载 `troubleshooting.md` 技能
2. 按流程收集日志
3. 定位问题根源
4. 提供修复方案

### 功能开发

开发新功能时:
1. 加载 `development.md` 技能
2. 遵循开发规范
3. 添加测试覆盖
4. 更新文档

## 快速命令

```bash
# 查看日志
./view_logs.sh

# 运行测试
pytest

# 启动 GUI
./run.sh gui
```

## 关键文件

| 文件 | 用途 |
|------|------|
| `logs/alfredpy.log` | 运行日志 |
| `logs/errors.log` | 错误日志 |
| `alfredpy/gui/launcher.py` | GUI 实现 |
| `alfredpy/workflow.py` | 工作流引擎 |

## 依赖版本

- Python: >=3.9
- Flet: >=0.21.0 (当前 0.82.2)
- pytest: >=7.0

---

**技能版本**: 1.0
**最后更新**: 2026-03-14
