# 📝 mif 日志系统

## 日志位置

```
project/
└── logs/
    ├── mif_qt.log      # Qt GUI 主日志
    ├── mif.log         # 兼容旧日志
    └── errors.log      # 错误日志
```

## 查看日志

```bash
# 交互式查看
./view_logs.sh

# 实时跟踪 Qt GUI 日志
tail -f logs/mif_qt.log

# 查看错误
cat logs/errors.log

# 查看最近 100 行
tail -100 logs/mif_qt.log
```

## 日志级别

| 级别 | 说明 | 输出位置 |
|------|------|---------|
| DEBUG | 调试信息 | mif_qt.log |
| INFO | 运行信息 | mif_qt.log |
| ERROR | 错误信息 | mif_qt.log + errors.log |

## 故障排查

遇到问题时：
1. 查看 `logs/errors.log`
2. 运行 `./view_logs.sh`
3. 提供日志文件给开发者
