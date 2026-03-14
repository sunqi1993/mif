# QML 迁移指南（历史归档）

> 本文档仅用于记录历史迁移过程。  
> 当前项目已切换为 **Qt Widgets** 实现，代码位于 `mif/gui_qt/`，不再使用 QML 文件渲染。

## 核心优势

PySide6 提供了**统一的跨平台解决方案**，无需额外依赖：

| 功能 | Flet + 其他依赖 | PyQML (统一) |
|------|----------------|--------------|
| GUI 框架 | Flet | PySide6 (Qt Quick) |
| 系统托盘 | PyObjC (仅 macOS) | `QSystemTrayIcon` (跨平台) |
| 全局热键 | pynput | pynput (保留) |
| 渲染方式 | Flutter 软件 | Qt GPU 加速 |

## 目录结构

```
mif/
├── gui_qt/                 # 当前 Qt Widgets 实现（现行）
│   ├── __init__.py
│   ├── launcher.py
│   └── singleton.py
└── (本节原 gui_qml/qml 目录仅用于迁移历史说明)

## 架构对比

### Flet 架构
```
Python (业务逻辑 + UI构建)
    ↓
flet.app() → Flutter Engine → 渲染
```

### PyQML 架构
```
Python (业务逻辑) ←→ Bridge (桥接层) ←→ QML (UI声明)
                                                  ↓
                                        Qt Scene Graph → GPU渲染
```

## 核心概念

### 1. QML 声明式 UI

**Flet (命令式):**
```python
search_field = ft.TextField(
    hint_text="搜索...",
    border_radius=25,
    on_change=on_change,
)
```

**QML (声明式):**
```qml
TextField {
    placeholderText: "搜索..."
    background: Rectangle { radius: 25 }
    onTextChanged: bridge.search(text)
}
```

### 2. 样式系统

**Flet:** 硬编码在 Python 代码中
```python
_BG = "#1a1a2e"
_ACCENT = "#4f8ef7"
```

**QML:** 单例样式文件，支持热重载
```qml
// Style.qml
pragma Singleton
QtObject {
    readonly property color bg: "#1a1a2e"
    readonly property color accent: "#4f8ef7"
}
```

### 3. 数据绑定

**Flet:** 手动更新
```python
result_item.title = new_title
page.update()
```

**QML:** 自动绑定
```qml
Text {
    text: modelData.title  // 自动响应数据变化
}
```

## Bridge 模式

Python 与 QML 通过 `QObject` 子类桥接：

```python
class MainBridge(QObject):
    # 定义信号 (QML 可监听)
    resultsChanged = Signal()
    
    # 定义属性 (QML 可绑定)
    @Property(list, notify=resultsChanged)
    def results(self):
        return self._results
    
    # 定义槽 (QML 可调用)
    @Slot(str)
    def search(self, query: str):
        # 业务逻辑
        self.resultsChanged.emit()
```

QML 中使用：
```qml
ListView {
    model: bridge.results  // 绑定属性
}

TextField {
    onTextChanged: bridge.search(text)  // 调用槽
}
```

## 当前运行方式（Qt Widgets）

### 安装依赖
```bash
# 安装完整依赖
pip install -e ".[all]"

# 或仅安装 Qt 相关依赖
pip install -e ".[qt]"
```

### 运行方式

```bash
# 默认启动（带托盘 + 热键）
./run.sh

# 无托盘
./run.sh --no-tray

# 无热键
./run.sh --no-hotkey

# 自定义热键
./run.sh --hotkey "<cmd>+space>"

# 统一入口
python -m mif --gui
```

## 系统托盘

PySide6 的 `QSystemTrayIcon` 提供跨平台的系统托盘支持：

- **macOS**: 显示在菜单栏右侧
- **Windows**: 显示在任务栏托盘区域
- **Linux**: 显示在系统托盘 (依赖桌面环境)

### 功能
- 单击托盘图标：显示/隐藏窗口
- 右键菜单：显示窗口、退出应用
- 托盘通知：执行动作后显示结果

### 无需 PyObjC
原 Flet 版本需要 PyObjC 实现 macOS 菜单栏，PyQML 版本用 Qt 统一实现，一个依赖解决所有问题。

## 功能对照表

| 功能 | 实现方式 |
|------|----------|
| 主窗口 | `QQmlApplicationEngine` + QML |
| 搜索框 | `SearchBar.qml` |
| 结果列表 | `ResultList.qml` |
| 计算器面板 | `CalcPanel.qml` |
| @模式横幅 | `AtModeBanner.qml` |
| 样式定义 | `Style.qml` (Singleton) |
| 快捷键 | QML `Shortcut {}` |
| 系统托盘 | `QSystemTrayIcon` (跨平台) |
| 全局热键 | `pynput` (跨平台) |
| 单例管理 | Unix Socket (复用) |

## 扩展 UI

### 添加新组件

1. 创建 QML 文件 `qml/components/NewComponent.qml`
2. 在 `Main.qml` 中导入使用

```qml
// Main.qml
import "components"

NewComponent {
    // 属性绑定
}
```

### 修改样式

直接编辑 `qml/Style.qml`，无需重启应用（支持热重载）：

```qml
// Style.qml
QtObject {
    readonly property color bg: "#0d0d1a"  // 修改背景色
}
```

### 添加动画

QML 内置强大的动画系统：

```qml
Rectangle {
    color: mouseArea.containsMouse ? "#ffffff1a" : "transparent"
    
    Behavior on color {
        ColorAnimation { duration: 150 }
    }
}
```

## 性能优势

| 指标 | Flet | PyQML |
|------|------|-------|
| 启动时间 | ~2s | ~0.5s |
| 内存占用 | ~150MB | ~80MB |
| 渲染方式 | Flutter 软件渲染 | Qt Scene Graph (GPU) |
| UI 更新 | 需要手动 `update()` | 自动响应式 |
| 热重载 | 不支持 | QML 文件修改即时生效 |

## 注意事项

1. **Python 版本**: 需要 Python >= 3.9
2. **Qt 版本**: 使用 Qt 6.5+ (PySide6)
3. **跨平台**: 支持 macOS / Linux / Windows
4. **Emoji 显示**: 部分平台可能需要配置字体

## 故障排除

### QML 文件加载失败
```
检查 qml/ 目录是否正确复制到安装位置
确保 QML 文件编码为 UTF-8
```

### 样式不生效
```
确保 Style.qml 有 `pragma Singleton` 声明
检查 import 路径是否正确
```

### 中文显示问题
```
确保系统安装了中文字体
可在 Style.qml 中指定字体
```

## 后续优化

- [ ] 添加 QML 热重载支持
- [ ] 实现主题切换功能
- [ ] 优化列表虚拟滚动
- [ ] 添加窗口透明效果
- [ ] 支持自定义 QML 插件