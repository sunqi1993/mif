# 🔧 Flet API 兼容性指南

## Flet 版本要求

- **最低版本**: 0.21.0
- **推荐版本**: 0.82.2+
- **当前版本**: 0.82.2

## API 变更汇总

### 1. 关闭窗口

```python
# ❌ 旧 API (< 0.21.0)
page.window_close()

# ✅ 新 API (>= 0.21.0)
page.window.close()
```

### 2. 窗口居中

```python
# ❌ 旧 API (协程，需要 await)
await page.window.center()

# ✅ 新 API (手动设置或移除)
# 方式 1: 移除，Flet 自动居中
# 方式 2: 手动设置位置
page.window.left = 100
page.window.top = 100
```

### 3. SnackBar

```python
# ❌ 旧 API
page.snack_bars.append(snackbar)

# ✅ 新 API
def show_snackbar(page, message, is_error=False):
    snackbar = ft.SnackBar(
        content=ft.Text(message, color=ft.Colors.WHITE),
        bgcolor=ft.Colors.RED_600 if is_error else ft.Colors.GREEN_600,
        behavior=ft.SnackBarBehavior.FLOATING,
        duration=2000,
    )
    page.overlay.append(snackbar)
    snackbar.open = True
    page.update()
```

### 4. 屏幕尺寸

```python
# ❌ 旧 API
width = page.window.screen_width

# ✅ 新 API
# 移除该属性，使用固定值或让 Flet 自动处理
page.window.width = 750
page.window.height = 550
```

## 修复清单

| API | 状态 | 备注 |
|-----|------|------|
| `window_close()` | ✅ 已修复 | 使用 `window.close()` |
| `window.center()` | ✅ 已修复 | 移除或手动设置 |
| `snack_bars` | ✅ 已修复 | 使用 `overlay` |
| `screen_width` | ✅ 已修复 | 移除 |

## 测试验证

```bash
# GUI 测试
pytest tests/test_gui.py

# 所有测试
pytest
```

## 向后兼容

代码已适配 Flet 0.21.0+，向下兼容。

---

**最后更新**: 2026-03-14
