# 🛠️ AlfredPy 故障排查技能

## 技能描述

用于 AlfredPy 项目的故障诊断和问题排查。

## 排查流程

### 1. 收集信息

```bash
# 1. 查看错误日志
cat logs/errors.log

# 2. 查看运行日志
tail -100 logs/alfredpy.log

# 3. 运行测试
pytest -v --no-cov

# 4. 检查依赖
python -c "import flet; print(flet.__version__)"
```

### 2. 常见问题定位

#### GUI 无法启动

**症状**: 运行 `./run.sh gui` 报错

**排查步骤**:
1. 查看 `logs/errors.log`
2. 检查 Flet 版本：`python -c "import flet"`
3. 验证导入：`python -c "from alfredpy.gui.launcher import launch_gui"`

**常见错误**:
- `AttributeError: 'Page' object has no attribute 'window_close'`
  - 解决：使用 `page.window.close()`
- `'Page' object has no attribute 'snack_bars'`
  - 解决：使用 `page.overlay.append(snackbar)`

#### 点击事件报错

**症状**: 点击工作流后报错 `missing 1 required positional argument: 'e'`

**解决**:
```python
# ❌ 错误
def handler(e):
    self.workflow_action()

# ✅ 正确
def handler():
    self.workflow_action()
```

#### 工作流执行失败

**排查**:
1. 检查 `logs/alfredpy.log` 中的执行日志
2. 验证工作流动作是否注册
3. 检查参数是否正确

### 3. 日志分析

**日志文件**:
- `logs/alfredpy.log` - 完整运行日志
- `logs/errors.log` - 所有未处理异常

**关键日志点**:
```
🚀 AlfredPy 启动           # 程序启动
加载工作流：X 个            # 工作流加载
搜索查询：'xxx'           # 用户搜索
执行工作流：XXX           # 工作流执行
❌ 错误消息               # 发生错误
```

### 4. 测试验证

```bash
# 运行完整测试
pytest

# GUI 测试
pytest tests/test_gui.py

# 详细输出
pytest -v -s
```

## 修复检查清单

- [ ] 查看错误日志
- [ ] 复现问题
- [ ] 定位代码位置
- [ ] 修复并测试
- [ ] 更新日志
- [ ] 运行测试套件

## 工具脚本

```bash
# 查看日志
./view_logs.sh

# 启动 GUI
./run.sh gui

# 运行测试
pytest
```

## 联系支持

提供以下信息:
1. `logs/errors.log` 完整内容
2. `logs/alfredpy.log` 最后 100 行
3. 复现步骤
4. 系统信息 (OS, Python 版本)

---

**技能版本**: 1.0
**最后更新**: 2026-03-14
