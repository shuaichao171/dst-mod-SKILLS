---
name: dst-hud-screens-input
description: Integrate Don't Starve Together HUD elements, screens, popups, overlays, and input. Use when extending PlayerHud or Controls, opening and closing screens, adding keyboard or controller handlers, managing focus and pause behavior, injecting badges or overlays, or fixing UI that breaks on reconnect and player replacement.
---

# DST HUD、Screen 与输入集成

先选择 Widget、HUD 子控件、Screen 或 Popup 的正确层级，再通过窄范围 ClassPostConstruct 接入。

## 工作流

1. 确定界面是否依附玩家 HUD、独立 Screen、Popup、世界跟随控件还是前端页面。
2. 读取 playerhud.lua、controls.lua 和相近 Screen 的构造、打开、关闭、焦点与暂停契约。
3. 通过 AddClassPostConstruct 或公开入口添加单个容器节点，避免重排原版整个 HUD 树。
4. 输入优先在目标 Widget 或 Screen 的 OnControl 处理；必须使用全局输入处理器时保存句柄并在关闭时移除。
5. 打开 Screen 时设置默认焦点、返回路径、是否暂停和是否隐藏 HUD；关闭时恢复原状态。
6. 玩家替换、死亡、重连和 HUD 重建时检测旧实例，避免重复注入。
7. 测试键鼠、手柄、聊天框、地图、制作栏、暂停菜单和多个屏幕叠放。

## 源码锚点

- screens/playerhud.lua、widgets/screen.lua、screens/popupdialog.lua。
- widgets/controls.lua、widgets/badge.lua、widgets/overlay 类文件。
- input.lua、frontend.lua。
- modutil.lua：AddClassPostConstruct、AddPopup、SetModHUDFocus。

## 不变量

- 不要永久吞掉未处理的控制输入，返回值遵守父类契约。
- 全局输入处理器、事件和任务必须随 HUD 或 Screen 清理。
- 不能假设 ThePlayer 永远存在或始终是同一个实例。
- HUD 注入应与其他模组并存，不依赖固定 child 索引。

## 验证

- 打开关闭、死亡重建和断线重连后只有一个 UI 实例。
- 聊天、制作、地图和暂停界面仍能正常获得焦点。
- 远端客户端界面不访问主机专属数据。
