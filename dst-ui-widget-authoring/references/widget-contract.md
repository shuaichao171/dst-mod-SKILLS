# Widget 契约与原版模式

来源基线：`DST_DATA_DIR\scripts`，于 2026-08-06 查阅。下面的文件与行号描述当前安装版本；游戏更新后重新核对。

## 树与生命周期

`Widget` 在构造时创建带 `UITransform` 的实体、`children` 集合和焦点状态（`widgets/widget.lua:1-32`）。使用 `parent:AddChild(child)`，它同时设置 Lua 父子关系和实体父级（`widget.lua:300-308`）。

- `RemoveChild(child)` 仅断开父子关系，不调用 `child:Kill()`（`widget.lua:282-289`）。缓存池或临时替换节点必须自行决定是否销毁。
- `Kill()` 会停止更新、递归 `KillAllChildren()`、脱离父级、停止内置鼠标跟随并移除实体（`widget.lua:325-334`）。
- 实体移除会取消其任务、停止世界状态监听并清除它作为监听者/事件源的事件回调（`entityscript.lua:1714-1721`）。但在同一个存活 Widget 上换绑 `owner`、`item` 或其他 source 时，先对旧 source 调用 `RemoveEventCallback`；可参考 `containerwidget.lua:311-320`。
- Widget 任务默认在暂停期间仍运行；`UpdateWhilePaused(false)` 才改用模拟时间任务（`widget.lua:8-44`）。为游戏时间相关的展示效果明确选择这一行为。

## 布局与层级

`SetPosition` 使用父节点局部坐标；`GetWorldPosition` 是跨父树定位时才需要的世界 UI 坐标（`widget.lua:336-370`）。

| 目标 | 使用方式 | 原版依据 |
| --- | --- | --- |
| 固定到屏幕边缘或中心 | 根节点调用 `SetHAnchor` / `SetVAnchor`，再以局部偏移 `SetPosition` | `widget.lua:416-422`；`playerhud.lua:233-238` |
| 保持内容比例 | 在容器根节点用 `SCALEMODE_PROPORTIONAL` | `constants.lua:83-87`；`playerhud.lua:233-238` |
| 铺满全屏背景 | 图片同时设置 H/V anchor、H/V region point 和 `SCALEMODE_FILLSCREEN` | `scripterrorwidget.lua:23-29` |
| 固定屏幕比例且考虑控制台安全区域 | 采用 `SCALEMODE_FIXEDPROPORTIONAL` | `constants.lua:85-87` |
| 文本框内对齐 | `SetRegionSize` 后用 `SetHAlign` / `SetVAlign` | `text.lua:102-103,305-314` |
| 图片自身对齐点 | `Image:SetHRegPoint` / `SetVRegPoint` | `image.lua:154-160` |

`SCALEMODE_FILLSCREEN` 会拉伸美术；`SCALEMODE_PROPORTIONAL` 保留宽高比并选较小缩放；`SCALEMODE_FIXEDSCREEN_NONDYNAMIC` 以 1280x720 窗口缩放为基准（`constants.lua:83-87`）。不要仅靠固定像素假定所有 HUD 缩放和宽高比。

同一父级的视觉前后次序可用 `MoveToFront` / `MoveToBack` 调整（`widget.lua:64-70`）。不要让纯装饰层抢鼠标：调用 `SetClickable(false)`（`widget.lua:526-528`）。

## 焦点与输入

`OnControl`、`OnRawKey`、`OnMouseButton` 先检查自身焦点，再递归交给已获焦点的子节点（`widget.lua:56-62,105-138`）。因此自定义覆写应先调用基类：

```lua
function MyWidget:OnControl(control, down)
    if MyWidget._base.OnControl(self, control, down) then
        return true
    end

    if control == CONTROL_ACCEPT and down then
        self:Activate()
        return true
    end

    return false
end
```

用 `SetFocusChangeDir(MOVE_UP, target)` 等建立方向关系（`widget.lua:577-590`）。移动时目标必须同时 `IsVisible()` 且 `enabled`，否则导航不会切换（`widget.lua:72-98`）。集合控件重建、分页或隐藏条目后重算路径；`grid.lua:51-80` 和 `scrollablelist.lua:689-706` 都这样做。

让父 Screen 或 HUD 给予初始焦点；普通 Widget 不要伪装为 Screen。Screen/HUD 的焦点保存、栈和玩家重建属于 `$dst-hud-screens-input`。

全局 `TheInput:Add*Handler` 不归 Widget 树管理。保存返回的 handler，并用对应输入对象的 `RemoveHandler(handler)` 移除；原版特殊错误界面在关闭前分别移除 control 和 mouse handler（`scripterrorwidget.lua:19-20,95-103`）。优先使用 Widget 或 Screen 的输入覆写，避免全局 handler。

## 更新、事件与清理

`StartUpdating()` 将 Widget 放入 `TheFrontEnd.updating_widgets`，`StopUpdating()` 才移除它（`widget.lua:485-490`；`frontend.lua:941-946`）。前端循环只检查 `enabled`，不检查 `shown`（`frontend.lua:879-891`），所以隐藏 Widget 仍会收到 `OnUpdate`。

- 首选实体事件、replica dirty event 或公开 `Refresh`，而不是轮询。
- 仅为动画、按住重复、连续跟随或其他真实逐帧任务调用 `StartUpdating`。
- 在 `OnHide` 停止不需要的更新；若显示后仍需要，在 `OnShow` 恢复。
- 已有更新状态时避免重复注册；`Spinner` 会按虚拟控制器提示是否需要刷新来开始或停止更新（`spinner.lua:245-271,673-675`）。
- 自己注册 `inst:ListenForEvent` 时保存函数引用，以便在 source 更换时精确解绑；最终 `Kill` 会随实体移除而清除剩余监听。

## 文本与集合

为可变长文本先设置区域、对齐和换行：`SetRegionSize`、`SetHAlign`、`SetVAlign`、`EnableWordWrap`（`text.lua:102-103,305-318`）。原版错误界面将文本限制在明确区域中并开启换行（`scripterrorwidget.lua:48-67`）。

- 单行空间有限时使用 `SetTruncatedString`；它会修改字符串直到满足宽度（`text.lua:123-165`）。该方法的原版注释明确标为未优化，且不能与 `SetRegionSize` 混用。
- 多行有限空间时使用 `SetMultilineTruncatedString`；它支持最大行数、宽度、每行字符数和可选缩小字体（`text.lua:260-285`）。
- 不要把 `SetAutoSizingString` 作为默认方案；源码明确建议改用多行截断（`text.lua:287-303`）。
- 动态 Grid/List 清空时先 `Kill` 旧项，再重建数据与方向焦点；`Grid:Clear` 的做法见 `grid.lua:42-49`。

## 查找范例

| 需求 | 优先范例 |
| --- | --- |
| 纯显示状态、事件刷新 | `widgets/badge.lua`、`widgets/bloodover.lua` |
| 键鼠与手柄按钮 | `widgets/button.lua`、`widgets/imagebutton.lua` |
| 方向网格 | `widgets/grid.lua` |
| 滚动列表与焦点移交 | `widgets/scrollablelist.lua` |
| 分页或按住重复 | `widgets/pagedlist.lua`、`widgets/spinner.lua` |
| 响应式根节点和文本区域 | `widgets/scripterrorwidget.lua` |
| HUD 节点和缩放根 | `widgets/controls.lua`、`screens/playerhud.lua`；随后使用 `$dst-hud-screens-input` |

## 提交前检查

- 创建、隐藏、显示、销毁和重建后没有遗留 `OnUpdate`、输入 handler 或旧 source 回调。
- 鼠标、键盘和手柄都能完成主操作，并能从自定义区域离开。
- 本地化长文本、窄宽屏、超宽屏和不同 UI scale 下没有重叠、截断错误或失焦。
- 客户端代码只读可用 replica 数据；服务器变更经由合适的网络入口。