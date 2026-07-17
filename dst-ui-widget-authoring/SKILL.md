---
name: dst-ui-widget-authoring
description: Create reusable Don't Starve Together UI widgets. Use when subclassing Widget, Image, Text, UIAnim, buttons, lists, grids, spinners, badges, overlays, or custom controls, arranging anchors and scale modes, implementing focus navigation and controller support, or cleaning up UI update and event callbacks.
---

# DST UI Widget 编写

构建可组合 Widget 树，明确父子关系、坐标空间、焦点、输入、更新和销毁生命周期。

## 工作流

1. 从相同交互类型的原版 Widget 继承，列出子节点、数据输入、视觉状态、鼠标和手柄行为。
2. 在构造函数中通过 AddChild 建立所有权；区分本地坐标、世界坐标、anchor、region point 与 scale mode。
3. 使用 Image、Text、UIAnim、ImageButton 等最小组件，避免为静态元素启动 OnUpdate。
4. 实现 OnControl、OnRawKey、OnMouseButton、OnGainFocus、OnLoseFocus，并建立完整 controller focus 邻接关系。
5. 数据变化优先事件驱动或显式 Refresh；需要更新时在隐藏、暂停和销毁阶段停止。
6. HookCallback、世界事件、输入处理器和任务保存解除方法，在 Kill 或 OnHide 的正确阶段清理。
7. 测试不同分辨率、UI scale、长文本、鼠标、键盘、手柄、暂停和重复打开关闭。

## 源码锚点

- widgets/widget.lua、image.lua、text.lua、uianim.lua、button.lua、imagebutton.lua。
- widgets/grid.lua、pagedlist.lua、dropdown.lua、spinner 类 Widget。
- widgets/controls.lua 与 screens/screen.lua：父级、焦点和输入。
- frontend.lua、input.lua：前端与输入分发。

## 不变量

- 不要混用屏幕坐标、父节点局部坐标和世界坐标。
- Widget 销毁后不能保留输入、事件或更新回调。
- 焦点路径必须允许手柄进入和离开自定义区域。
- 客户端 UI 只显示 Replica 或 RPC 允许的数据，不读取服务器 Component。

## 验证

- 重复创建和 Kill 不产生重复控件、回调或报错。
- 所有支持的输入方式都能完成主要操作并返回上一层。
- 不同宽高比和 UI scale 下无遮挡、越界或不可聚焦控件。

## 按需资源

- 复制 assets/widget-template.lua 创建 Widget。
- 需要坐标、焦点和生命周期时读取 references/widget-contract.md。

