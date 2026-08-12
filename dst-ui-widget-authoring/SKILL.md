---
name: dst-ui-widget-authoring
description: Create reusable Don't Starve Together UI widgets. Use when subclassing Widget, Image, Text, UIAnim, buttons, lists, grids, spinners, badges, overlays, or custom controls; arranging anchors and scale modes; implementing mouse, keyboard, and controller focus; or managing UI refresh, events, and cleanup. Use dst-hud-screens-input instead for PlayerHud injection, Screen stacks, popups, and global input integration.
---

# DST UI Widget 编写

构建可组合、事件驱动且支持手柄焦点的 `Widget` 树。以当前安装的 `data/scripts` 为事实基线；不要把旧教程当作 API 契约。

## 工作流

1. 先从用途相近的原版控件开始：静态图文查 `image.lua`、`text.lua`，交互查 `button.lua`、`imagebutton.lua`，集合查 `grid.lua`、`scrollablelist.lua` 或 `pagedlist.lua`。
2. 用 `Class(Widget, ...)` 和 `AddChild` 建立唯一的父子树。让构造函数只创建稳定节点；把可变数据放进 `Refresh`、`SetValue` 或 `SetDataSource`。
3. 为根节点选择屏幕锚点和 `ScaleMode`，为子节点使用父级局部 `SetPosition`。全屏背景、比例布局和固定屏幕布局不要混用。
4. 让装饰节点 `SetClickable(false)`；为可交互节点实现视觉状态、鼠标行为和可达的焦点路径。
5. 在 `OnControl`、`OnRawKey`、`OnMouseButton` 中先调用基类。仅在实际处理后返回 `true`；为手柄使用 `SetFocusChangeDir` 建立进出区域的路径。
6. 优先监听 replica 或本地 UI 数据事件并显式 `Refresh`。只有连续动画、按住重复或跟随效果才调用 `StartUpdating`。
7. 换绑实体时先移除旧事件回调；全局输入句柄必须显式移除。`Kill` 会销毁子树并停止更新，但不能替你修复重复注入或错误的数据源所有权。
8. 在鼠标、键盘、手柄、长文本、不同宽高比、不同 UI scale、隐藏/显示和重复创建/销毁下验证。

## 关键约束

- `Hide()` 只改变可见性，不能停止已注册的 `OnUpdate`；按需在 `OnHide` 中停止，在 `OnShow` 中恢复。
- `AddChild` 建立 Lua 与实体层级；`RemoveChild` 只脱离父级，不会销毁子项。
- 基类仅向当前焦点子树分发输入。不可见或禁用的焦点目标不会被方向导航选中。
- `SetHAnchor` / `SetVAnchor` 属于 `UITransform`；图片的 `SetHRegPoint` / `SetVRegPoint` 和文本的 `SetHAlign` / `SetVAlign` 属于内容对齐，三者不要混淆。
- 客户端界面只读取客户端可用的数据（通常为 `replica`），将改动请求经由合适的 RPC 或原版入口发送给服务器。

## 源码锚点

- `widgets/widget.lua`：树、可见性、更新、焦点、输入与 `Kill`。
- `widgets/image.lua`、`widgets/text.lua`：图片原点、文本区域、换行和截断。
- `widgets/grid.lua`、`widgets/scrollablelist.lua`、`widgets/spinner.lua`：焦点网格、滚动移交和按需更新。
- `frontend.lua`、`input.lua`：已注册 Widget 的更新和全局输入句柄。
- `constants.lua`：锚点与 `SCALEMODE_*` 常量。

## 按需资源

- 复制 `assets/widget-template.lua` 作为事件驱动的自定义 Widget 起点。
- 遇到布局、焦点、更新、文本或清理问题时读取 `references/widget-contract.md`。
- 需要注入 `PlayerHud`、Push/Pop `Screen`、Popup 或全局输入时改用 `$dst-hud-screens-input`。