# Flet API 参考手册（v0.82.2）

> **自动生成于 2026-03-14**，基于 `inspect.signature` 对已安装版本的实际反射。  
> 后续 Agent 开发 GUI 功能时，**以本文件为准**，不要依赖旧版文档或凭印象猜测参数名。

---

## 目录

1. [已知不兼容项（踩坑记录）](#已知不兼容项踩坑记录)
2. [通用基础参数（所有控件共享）](#通用基础参数所有控件共享)
3. [布局辅助函数](#布局辅助函数)
4. [枚举常量](#枚举常量)
5. [组件参数详表](#组件参数详表)

---

## 已知不兼容项（踩坑记录）

| 错误用法 | 正确替代 | 说明 |
|----------|----------|------|
| `ft.Color("#hex")` | 直接用字符串 `"#4f8ef7"` | `ft.Color` 类不存在 |
| `ft.Text(..., letter_spacing=1.2)` | 去掉该参数 | `ft.Text` 不支持 `letter_spacing` |
| `ft.NavigationDestination` | `ft.NavigationBarDestination` | 类名不同 |
| `ft.Padding.symmetric(...)` | `ft.padding.symmetric(...)` | 小写模块，非类方法 |
| `ft.Margin.only(...)` | `ft.margin.only(...)` | 同上 |

---

## 通用基础参数（所有控件共享）

以下参数几乎所有控件都支持，下方各组件表中不再重复列出：

```
key, ref, data, expand, expand_loose, col, opacity, tooltip, badge,
visible, disabled, rtl, adaptive,
width, height, left, top, right, bottom, align, margin,
rotate, scale, offset, flip, transform, aspect_ratio,
animate_opacity, animate_size, animate_position, animate_align,
animate_margin, animate_rotation, animate_scale, animate_offset,
size_change_interval, on_size_change, on_animation_end
```

---

## 布局辅助函数

### `ft.padding`
```python
ft.padding.all(value)
ft.padding.symmetric(horizontal=0, vertical=0)
ft.padding.only(left=0, top=0, right=0, bottom=0)
```

### `ft.margin`
```python
ft.margin.all(value)
ft.margin.symmetric(horizontal=0, vertical=0)
ft.margin.only(left=0, top=0, right=0, bottom=0)
```

### `ft.border`
```python
ft.border.all(width, color)
ft.border.only(left=None, top=None, right=None, bottom=None)
# BorderSide: ft.BorderSide(width, color)
```

### `ft.border_radius`
```python
ft.border_radius.all(radius)
ft.border_radius.only(top_left=0, top_right=0, bottom_right=0, bottom_left=0)
ft.border_radius.horizontal(left=0, right=0)
ft.border_radius.vertical(top=0, bottom=0)
```

---

## 枚举常量

### `ft.FontWeight`
`BOLD`, `NORMAL`, `W_100`, `W_200`, `W_300`, `W_400`, `W_500`, `W_600`, `W_700`, `W_800`, `W_900`

### `ft.TextAlign`
`CENTER`, `END`, `JUSTIFY`, `LEFT`, `RIGHT`, `START`

### `ft.TextOverflow`
`CLIP`, `ELLIPSIS`, `FADE`, `VISIBLE`

### `ft.MainAxisAlignment`
`CENTER`, `END`, `SPACE_AROUND`, `SPACE_BETWEEN`, `SPACE_EVENLY`, `START`

### `ft.CrossAxisAlignment`
`BASELINE`, `CENTER`, `END`, `START`, `STRETCH`

### `ft.ScrollMode`
`ADAPTIVE`, `ALWAYS`, `AUTO`, `HIDDEN`

### `ft.ThemeMode`
`DARK`, `LIGHT`, `SYSTEM`

### `ft.SnackBarBehavior`
`FIXED`, `FLOATING`

### `ft.Colors`（常用色值，完整列表见源码）
- 基础色：`WHITE`, `BLACK`, `TRANSPARENT`
- 透明度变体：`WHITE10`, `WHITE24`, `WHITE30`, `WHITE38`, `WHITE54`, `WHITE60`, `WHITE70`
- Material 色系：`RED`, `RED_600`，`GREEN`, `GREEN_600`, `GREEN_700`，`BLUE`, `BLUE_200`，`AMBER` …（后缀 `_50`~`_900` 及 `_ACCENT`）
- 自定义颜色：直接传十六进制字符串，如 `"#1a1a2e"`

### `ft.Icons`（图标名称）
全部使用大写下划线格式，如 `ft.Icons.SEARCH`、`ft.Icons.CLOSE`、`ft.Icons.CALCULATE`。

---

## 组件参数详表

> ⚠️ 下列参数列表通过 `inspect.signature` 实时采集，**不含**上方"通用基础参数"。

---

### `ft.Text`

```
value, spans, text_align, font_family, font_family_fallback,
size, weight, italic, style, theme_style,
max_lines, overflow, selectable, no_wrap,
color, bgcolor, semantics_label,
show_selection_cursor, enable_interactive_selection,
selection_cursor_width, selection_cursor_height, selection_cursor_color,
on_tap, on_selection_change
```

> **不支持**：`letter_spacing`（直接去掉即可）

---

### `ft.TextField`

```
value, selection, keyboard_type, multiline, min_lines, max_lines,
max_length, password, can_reveal_password, read_only,
shift_enter, ignore_up_down_keys, text_align,
autofocus, capitalization, autocorrect, enable_suggestions,
smart_dashes_type, smart_quotes_type,
show_cursor, cursor_color, cursor_error_color,
cursor_width, cursor_height, cursor_radius,
selection_color, input_filter, obscuring_character,
enable_interactive_selection, enable_ime_personalized_learning,
can_request_focus, ignore_pointers, enable_stylus_handwriting,
animate_cursor_opacity, always_call_on_tap, scroll_padding,
clip_behavior, keyboard_brightness, mouse_cursor,
strut_style, autofill_hints,
on_change, on_selection_change, on_click, on_submit,
on_focus, on_blur, on_tap_outside,
-- 装饰参数（InputDecoration）--
text_size, text_style, text_vertical_align,
label, label_style,
icon, border, color, bgcolor,
border_radius, border_width, border_color,
focused_color, focused_bgcolor,
focused_border_width, focused_border_color,
content_padding, dense, filled, fill_color, focus_color,
align_label_with_hint, hover_color,
hint_text, hint_style, hint_fade_duration, hint_max_lines,
helper, helper_style, helper_max_lines,
counter, counter_style, error, error_style, error_max_lines,
prefix, prefix_icon, prefix_icon_size_constraints, prefix_style,
suffix, suffix_icon, suffix_icon_size_constraints, suffix_style,
size_constraints, collapsed, fit_parent_size
```

---

### `ft.Container`

```
content, padding, alignment, bgcolor, gradient, blend_mode,
border, border_radius, shape, clip_behavior,
ink, image, ink_color, animate, blur, shadow,
url, theme, dark_theme, theme_mode, color_filter,
ignore_interactions, foreground_decoration,
on_click, on_tap_down, on_long_press, on_hover
```

---

### `ft.Row`

```
controls, alignment, vertical_alignment, spacing, tight,
wrap, run_spacing, run_alignment, intrinsic_height,
scroll, auto_scroll, scroll_interval, on_scroll
```

---

### `ft.Column`

```
controls, alignment, horizontal_alignment, spacing, tight,
wrap, run_spacing, run_alignment, intrinsic_width,
scroll, auto_scroll, scroll_interval, on_scroll
```

---

### `ft.Icon`

```
icon, color, size, semantics_label, shadows,
fill, apply_text_scaling, grade, weight, optical_size,
blend_mode
```

---

### `ft.IconButton`

```
icon, icon_color, icon_size, selected, selected_icon, selected_icon_color,
bgcolor, highlight_color, style, autofocus, disabled_color,
hover_color, focus_color, splash_color, splash_radius,
alignment, padding, enable_feedback, url, mouse_cursor,
visual_density, size_constraints,
on_click, on_long_press, on_hover, on_focus, on_blur
```

---

### `ft.ElevatedButton`

```
content, icon, icon_color, color, bgcolor, elevation,
style, autofocus, clip_behavior, url,
on_click, on_long_press, on_hover, on_focus, on_blur
```

---

### `ft.TextButton`

```
content, icon, icon_color, style, autofocus, url, clip_behavior,
on_click, on_long_press, on_hover, on_focus, on_blur
```

---

### `ft.FilledButton`

```
content, icon, icon_color, color, bgcolor, elevation,
style, autofocus, clip_behavior, url,
on_click, on_long_press, on_hover, on_focus, on_blur
```

---

### `ft.Divider`

```
color, height, leading_indent, thickness, trailing_indent, radius
```

---

### `ft.SnackBar`

```
content, behavior, dismiss_direction, show_close_icon,
action, close_icon_color, bgcolor, duration,
margin, padding, width, elevation, shape, clip_behavior,
action_overflow_threshold, persist,
on_action, on_visible,
open, on_dismiss
```

---

### `ft.Image`

```
src, error_content, repeat, fit, border_radius,
color, color_blend_mode, gapless_playback,
semantics_label, exclude_from_semantics, filter_quality,
placeholder_src, placeholder_fit,
fade_in_animation, placeholder_fade_out_animation,
cache_width, cache_height, anti_alias
```

---

### `ft.ListTile`

```
title, subtitle, is_three_line, leading, trailing,
content_padding, bgcolor, splash_color, hover_color,
selected, dense, autofocus, toggle_inputs,
selected_color, selected_tile_color, style, enable_feedback,
horizontal_spacing, min_leading_width, min_vertical_padding,
url, title_alignment, icon_color, text_color, shape,
visual_density, mouse_cursor,
title_text_style, subtitle_text_style, leading_and_trailing_text_style,
min_height, on_click, on_long_press
```

---

### `ft.ListView`

```
controls, horizontal, spacing, item_extent, first_item_prototype,
divider_thickness, padding, clip_behavior, semantic_child_count,
cache_extent, scroll, auto_scroll, scroll_interval, on_scroll
```

---

### `ft.GridView`

```
controls, horizontal, runs_count, max_extent, spacing,
run_spacing, child_aspect_ratio, padding, clip_behavior,
semantic_child_count, cache_extent,
scroll, auto_scroll, scroll_interval, on_scroll
```

---

### `ft.Stack`

```
controls, alignment, fit, clip_behavior
```

---

### `ft.Tabs`

```
tabs, selected_index, animation_duration, tab_alignment,
divider_color, indicator_color, indicator_border_radius,
indicator_border_side, indicator_padding, indicator_tab_size,
is_secondary, label_color, label_padding, label_style,
overlay_color, unselected_label_color, unselected_label_style,
mouse_cursor, enable_feedback, padding, splash_border_radius,
clip_behavior, on_change
```

---

### `ft.Tab`

```
label, icon, height, icon_margin
```

---

### `ft.NavigationBar`

```
destinations, selected_index, bgcolor, label_behavior, label_padding,
elevation, shadow_color, indicator_color, indicator_shape,
border, animation_duration, overlay_color, on_change
```

---

### `ft.NavigationBarDestination`

```
icon, label, selected_icon, bgcolor
```

---

### `ft.AppBar`

```
leading, leading_width, automatically_imply_leading,
title, center_title, toolbar_height,
color, bgcolor, elevation, elevation_on_scroll, shadow_color,
clip_behavior, force_material_transparency, secondary,
title_spacing, exclude_header_semantics,
actions, actions_padding, toolbar_opacity,
title_text_style, toolbar_text_style, shape
```

---

### `ft.FloatingActionButton`

```
content, icon, bgcolor, shape, autofocus, mini,
foreground_color, focus_color, clip_behavior,
elevation, disabled_elevation, focus_elevation,
highlight_elevation, hover_elevation, hover_color,
splash_color, enable_feedback, url, mouse_cursor, on_click
```

---

### `ft.Checkbox`

```
label, value, label_position, label_style, tristate, autofocus,
fill_color, overlay_color, check_color, active_color,
hover_color, focus_color, semantics_label, shape,
splash_radius, border_side, error, visual_density, mouse_cursor,
on_change, on_focus, on_blur
```

---

### `ft.Switch`

```
adaptive, label, label_position, label_text_style, value, autofocus,
active_color, active_track_color, focus_color,
inactive_thumb_color, inactive_track_color,
thumb_color, thumb_icon, track_color, hover_color,
splash_radius, overlay_color,
track_outline_color, track_outline_width,
mouse_cursor, padding, on_change, on_focus, on_blur
```

---

### `ft.Dropdown`

```
value, options, text, autofocus, text_align, elevation,
enable_filter, enable_search, editable,
menu_height, menu_width, menu_style, expanded_insets,
selected_suffix, input_filter, capitalization,
trailing_icon, leading_icon, selected_trailing_icon,
bgcolor, on_select, on_text_change, on_focus, on_blur,
-- 装饰参数 --
error_style, error_text, text_size, text_style,
label, label_style, border, color, border_width, border_color,
border_radius, focused_border_width, focused_border_color,
content_padding, dense, filled, fill_color, hover_color,
hint_text, hint_style, helper_text, helper_style
```

---

### `ft.ProgressBar`

```
value, bar_height, color, bgcolor, border_radius,
semantics_label, semantics_value,
stop_indicator_color, stop_indicator_radius,
track_gap, year_2023
```

---

### `ft.ProgressRing`

```
value, stroke_width, color, bgcolor, stroke_align, stroke_cap,
semantics_label, semantics_value, track_gap,
size_constraints, padding, year_2023
```

---

### `ft.Card`

```
content, elevation, bgcolor, shadow_color, shape,
clip_behavior, semantic_container,
show_border_on_foreground, variant
```

---

### `ft.DataTable`

```
columns, rows, sort_ascending, show_checkbox_column,
sort_column_index, show_bottom_border,
border, border_radius, horizontal_lines, vertical_lines,
checkbox_horizontal_margin, column_spacing,
data_row_color, data_row_min_height, data_row_max_height,
data_text_style, bgcolor, gradient, divider_thickness,
heading_row_color, heading_row_height, heading_text_style,
horizontal_margin, clip_behavior, on_select_all
```

### `ft.DataColumn`
```
label, numeric, heading_row_alignment, on_sort
```

### `ft.DataRow`
```
cells, color, selected, on_long_press, on_select_change
```

### `ft.DataCell`
```
content, placeholder, show_edit_icon,
on_tap, on_double_tap, on_long_press, on_tap_cancel, on_tap_down
```

---

### `ft.AlertDialog`

```
content, modal, title, actions, bgcolor, elevation, icon,
title_padding, content_padding, actions_padding,
actions_alignment, shape, inset_padding, icon_padding,
action_button_padding, shadow_color, icon_color, scrollable,
actions_overflow_button_spacing, alignment,
content_text_style, title_text_style, clip_behavior,
semantics_label, barrier_color,
open, on_dismiss
```

---

### `ft.BottomSheet`

```
content, elevation, bgcolor, dismissible, draggable,
show_drag_handle, use_safe_area, scrollable, fullscreen,
maintain_bottom_view_insets_padding, animation_style,
size_constraints, clip_behavior, shape, barrier_color,
open, on_dismiss
```

---

### `ft.Banner`

```
content, actions, leading, leading_padding, content_padding,
force_actions_below, bgcolor, shadow_color, divider_color,
elevation, margin, content_text_style,
min_action_bar_height, on_visible,
open, on_dismiss
```

---

### `ft.Markdown`

```
value, selectable, extension_set, code_theme,
auto_follow_links, shrink_wrap, fit_content, soft_line_break,
auto_follow_links_target, image_error_content,
code_style_sheet, md_style_sheet,
latex_scale_factor, latex_style,
on_tap_text, on_selection_change, on_tap_link
```

---

### `ft.ResponsiveRow`

```
controls, columns, alignment, vertical_alignment,
spacing, run_spacing, breakpoints
```

---

## 常见模式速查

### 深色主题 + 自定义颜色

```python
page.theme_mode = ft.ThemeMode.DARK
page.bgcolor = "#1a1a2e"
container.bgcolor = "#16213e"
container.border = ft.border.all(1, "#ffffff1a")
```

### 文本样式

```python
ft.Text("标题", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
ft.Text("副标题", size=13, color=ft.Colors.WHITE54, overflow=ft.TextOverflow.ELLIPSIS, no_wrap=True)
# ❌ 不支持 letter_spacing 参数
```

### 搜索框（TextField 常用配置）

```python
ft.TextField(
    hint_text="搜索…",
    hint_style=ft.TextStyle(color=ft.Colors.WHITE38, size=16),
    text_style=ft.TextStyle(color=ft.Colors.WHITE, size=18),
    border_color=ft.Colors.WHITE24,
    focused_border_color="#4f8ef7",   # 十六进制字符串
    border_radius=25,
    fill_color=ft.Colors.WHITE10,
    filled=True,
    content_padding=ft.padding.symmetric(horizontal=25, vertical=15),
    prefix_icon=ft.Icons.SEARCH,
    on_change=handler,
    on_submit=enter_handler,
)
```

### 可点击卡片（Container）

```python
ft.Container(
    content=...,
    padding=ft.padding.symmetric(horizontal=15, vertical=12),
    bgcolor="#16213e",
    border=ft.border.all(1, "#1e3a6e"),
    border_radius=12,
    ink=True,           # 涟漪效果
    on_click=handler,
)
```

### SnackBar 提示

```python
snack = ft.SnackBar(
    content=ft.Text("操作成功", color=ft.Colors.WHITE),
    bgcolor=ft.Colors.GREEN_700,
    behavior=ft.SnackBarBehavior.FLOATING,
    duration=2000,
)
page.overlay.append(snack)
snack.open = True
page.update()
```
