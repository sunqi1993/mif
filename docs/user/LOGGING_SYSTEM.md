# 📝 AlfredPy 日志系统

## 日志位置

```
alfredpy/
└── logs/
    ├── alfredpy.log    # 完整运行日志
    └── errors.log      # 错误日志
```

## 查看日志

```bash
# 交互式查看
./view_logs.sh

# 实时跟踪
tail -f logs/alfredpy.log

# 查看错误
cat logs/errors.log

# 查看最近 100 行
tail -100 logs/alfredpy.log
```

## 日志级别

| 级别 | 说明 | 输出位置 |
|------|------|---------|
| DEBUG | 调试信息 | alfredpy.log |
| INFO | 运行信息 | alfredpy.log |
| ERROR | 错误信息 | alfredpy.log + errors.log |

## 故障排查

遇到问题时：
1. 查看 `logs/errors.log`
2. 运行 `./view_logs.sh`
3. 提供日志文件给开发者
