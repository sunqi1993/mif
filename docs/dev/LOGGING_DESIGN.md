# 📝 日志系统设计

## 设计目标

1. 自动记录所有操作
2. 异常自动捕获
3. 错误落盘存储
4. 性能影响最小

## 日志结构

### 文件位置

```
logs/
├── mif_qt.log      # Qt GUI 日志
├── mif.log         # 兼容旧日志
└── errors.log      # 错误日志
```

### 日志格式

**mif_qt.log**:
```
2026-03-14 14:39:00 - AlfredPy - INFO - 消息内容
```

**errors.log**:
```
================================================================================
Time: 2026-03-14 14:39:00
Type: ExceptionName
Message: 错误消息
Traceback:
  File "file.py", line XX, in function
    code...
================================================================================
```

## 实现要点

### 1. Logger 配置

```python
logger = logging.getLogger("AlfredPy")
logger.setLevel(logging.DEBUG)

# 文件处理器 - DEBUG 级别
file_handler = logging.FileHandler("logs/mif_qt.log")
file_handler.setLevel(logging.DEBUG)

# 控制台处理器 - ERROR 级别
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
```

### 2. 全局异常处理

```python
def log_exception(exc_type, exc_value, exc_traceback):
    logger.error("Unhandled Exception", exc_info=(...))
    # 写入 errors.log

sys.excepthook = log_exception
```

### 3. 关键日志点

- 启动/关闭
- 工作流加载
- 搜索查询
- 点击事件
- 工作流执行
- 所有异常

## 性能考虑

- 异步写入（不阻塞主线程）
- 日志轮转（避免文件过大）
- 级别控制（生产环境减少 DEBUG）

---

**最后更新**: 2026-03-14
