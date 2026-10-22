# StateGraph 契约

## 状态责任

State 负责短期、可中断的动作与动画时序。持久数值、阶段和冷却放 Component 或 Prefab。

## 状态结构

- name 必须在该 SG 内唯一。
- tags 描述当前能力，不是永久实体标签。
- onenter 设置动画、移动、timeout 和 statemem。
- timeline 在明确帧执行服务器副作用。
- events 处理 animover、attacked 等实体事件。
- ontimeout 处理 inst.sg:SetTimeout 设置的计时到期；该计时不会发送 timeout 事件。
- onexit 撤销进入时创建的临时状态。

临时数据放 inst.sg.statemem。不要依赖 onexit 只在动画自然结束时调用。

## 玩家预测

自定义玩家动作同时检查：

- SGwilson 的服务器 ActionHandler
- 客户端玩家 SG
- 动作预览和 BufferedAction
- ServerStateMatches
- 服务器拒绝后的复位

伤害、消耗、生成和掉落只在服务器发生。

## 玩家碰撞

玩家 State 临时取消与其他角色的碰撞时，复用 SGwilson 的直接 Physics 模式：

```lua
-- onenter
inst.Physics:ClearCollidesWith(COLLISION.CHARACTERS)

-- onexit
inst.Physics:Stop()
inst.Physics:CollidesWith(COLLISION.CHARACTERS)
inst.Physics:Teleport(inst.Transform:GetWorldPosition())
```

- 不要在玩家 SG State 中调用 ToggleOffCharacterCollisions 或 ToggleOnCharacterCollisions。这两个通用辅助函数会操作 inst.sg.mem.ischaracterpassthrough、radius 和 physicstask；恢复时还会启动周期任务。
- death 或其他强制状态切换可能清理或覆盖 sg.mem.physicstask，但已调度的 OnUpdatePhysicsRadius 仍可能运行，随后对 nil physicstask 调用 Cancel 并使服务器崩溃。
- 除非明确把碰撞所有权移交给相邻状态，否则在 onexit 对称恢复碰撞。链式状态应仿照 SGwilson 用 statemem 标记是否由下一状态继续持有碰撞修改。

## 独立 SG 的装载与动作

- 将模块保存为 scripts/stategraphs/SGmod_entity.lua，并调用 inst:SetStateGraph('SGmod_entity')；entityscript.lua 会 require stategraphs/SGmod_entity。
- 返回值可使用 StateGraph('mod_entity', ...)。内部名称用于 AddStategraphPostInit、AddStategraphActionHandler 等注册，不必带文件名前缀 SG。
- 在 SG 模块加载前注册自定义 Action，使 ACTIONS.MOD_INTERACT 已存在。
- 把 ActionHandler 放入 StateGraph 的第五个 actionhandlers 参数。EntityScript:PushBufferedAction 会调用 StateGraphInstance:StartAction；没有匹配处理器时，非 instant 动作会失败。
- 不要用顶层 EventHandler('doaction', ...) 冒充 ActionHandler；PushBufferedAction 不发送该事件。

## 向已有 SG 注入状态与事件

`stategraph.lua` 的 `StateGraph` 构造函数按以下顺序合并 modmain 中的注册：

1. 原版 actionhandlers，然后是 `AddStategraphActionHandler(sg, handler)`（断言 `is_a(ActionHandler)`）。
2. 原版 events，然后是 `AddStategraphEvent(sg, EventHandler(...))`（断言 `is_a(EventHandler)`）。
3. 原版 states，然后是 `AddStategraphState(sg, State{...})`（断言 `is_a(State)`）。
4. 最后执行 `AddStategraphPostInit(sg, fn)`，参数是 StateGraph 对象本身。

```lua
-- modmain.lua：sg 参数是 StateGraph 的内部名称，不是文件名
-- State、EventHandler 没有注入入口环境，未设置 GLOBAL 继承时写 GLOBAL.State
AddStategraphState("wilson", State{ name = "mymod_cast", tags = { "busy", "doing" }, ... })
AddStategraphState("wilson_client", State{ name = "mymod_cast", tags = { "busy", "doing" }, ... })
AddStategraphEvent("wilson", EventHandler("mymod_stun", function(inst, data) ... end))

-- 修改现有状态：在 PostInit 里包装，而不是用同名 State 整体替换
AddStategraphPostInit("wilson", function(sg)
    local state = sg.states.idle
    local old_onenter = state.onenter
    state.onenter = function(inst, ...)
        old_onenter(inst, ...)
        -- 追加逻辑
    end
end)
```

- 名称使用 `StateGraph("wilson", ...)` 的第一个参数：玩家是 `wilson` 与 `wilson_client`，生物看对应 SG 文件末尾的 `return StateGraph(...)`。
- 按名称写入表，**同名会覆盖**：同名 State 或 EventHandler 会替换原版，多个模组注册同名时，按 enabledmods 顺序最后一个生效。新增内容一律加模组前缀；确实要替换时，写清冲突范围，或者改用 PostInit 包装。
- 合并只在 SG 模块第一次被 `require` 时发生一次（各实体共享同一个 StateGraph 对象）。注册必须写在 modmain 顶层；不要在 modmain 里提前 `require("stategraphs/SGwilson")`，否则在你之后注册的模组可能不会生效。
- 预测动作要在 `wilson` 和 `wilson_client` 里各添加一份对应状态，并保持 tags 一致，否则客户端会进不去状态或被服务器纠正。

## 对称清理

进入时改变以下内容，退出时必须恢复：

- locomotor 和 Physics
- 控制锁与 state tag
- 碰撞和无敌
- 颜色、Bloom、Light
- 循环声音与 FX
- 任务和跨实体事件
