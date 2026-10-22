# 全局 PostInit 钩子、玩家初始化与函数包装

以下结论来自 `modutil.lua`、`mods.lua`、`mainfunctions.lua`、`entityscript.lua` 和 `prefabs/player_common.lua`，游戏更新后先重新核对。

> 示例里的 modmain 代码假设已经按 dst-mod-scaffolding 在文件顶部设置了 `__index → GLOBAL` 环境继承。没有设置时，入口环境里未注入的全局变量（TheNet、net_tinybyte 等）要从 `GLOBAL` 读取。

## 钩子执行时机

| API | 执行位置 | 频率 | 回调参数 |
| --- | --- | --- | --- |
| `AddPrefabPostInit(name, fn)` | `SpawnPrefabFromSim`，Prefab 构造函数返回后 | 只在该 Prefab 生成时调用；函数列表在 RegisterPrefabs 时缓存 | `inst` |
| `AddPrefabPostInitAny(fn)` | 同上，在指定 Prefab 的 PostInit 之后 | **所有实体每次生成都会调用**，包括主机和所有客户端 | `inst` |
| `AddPlayerPostInit(fn)` | 等价于 `AddPrefabPostInitAny` 加 `HasTag("player")` | 同 PrefabPostInitAny | `inst` |
| `AddComponentPostInit(name, fn)` | `EntityScript:AddComponent` 构造组件之后 | 只在该组件被添加时调用 | `self, inst` |
| `AddSimPostInit(fn)` | `gamelogic.lua` 中世界填充完成后，`TheWorld:PostInit()` 之前 | 每次进入世界一次 | 历史参数，恒为 `nil` |
| `AddGamePostInit(fn)` | `ModWrangler:SetPostEnv`，启动流程末尾 | 每次 Lua 环境启动一次（主菜单和进入世界都会触发） | 无 |
| `AddClassPostConstruct(path, fn)` | 类构造函数末尾 | 每个实例一次 | `self, ...` |
| `AddGlobalClassPostConstruct(path, classname, fn)` | 同上，但从 `_G[classname]` 取类 | 每个实例一次 | `self, ...` |

## AddPlayerPostInit 与 AddPrefabPostInitAny 的问题

`modutil.lua` 里的原文实现：

```lua
env.AddPlayerPostInit = function(fn)
    env.AddPrefabPostInitAny( function(inst)
        if inst and inst:HasTag("player") then fn(inst) end
    end)
end
```

Klei 的注释也说明它只是 PrefabPostInitAny 的"示例"。实际问题有这些：

1. **每生成一个实体都要执行一次**：`SpawnPrefabFromSim` 每次生成都会调用 `ModManager:GetPostInitFns("PrefabPostInitAny")`。这个函数每次都要遍历所有已启用模组，并为每个已注册函数新建一个 `runmodfn` 闭包。调用时还会额外做一次 `xpcall`、新建一个闭包和一个 `arg` 表。物品、FX、classified、音效辅助实体等所有实体，在主机和每个客户端上都会付出这份开销。
2. **开销随注册数量增加**：每调用一次 `AddPlayerPostInit`，就多注册一个 Any 回调。N 个模组各注册一次，每生成一个实体就要多做 N 次闭包分配和 `HasTag` 调用。
3. **只按标签判断**：只要实体带 `player` 标签就会命中，回调里并不知道它是哪个角色。
4. 与之相比，`AddPrefabPostInit(name)` 的函数列表在 `RegisterPrefabs` 时就缓存在 `modprefabinitfns` 里，只有生成目标 Prefab 时才会执行。

它唯一的优点是执行得最晚：Prefab 构造函数（包括角色的 `master_postinit`）已经执行完，`inst.prefab` 也已设置。

结论：**优先用下面的组件钩子，只有它们的时机满足不了需求时才用 `AddPlayerPostInit` / `AddPrefabPostInitAny`**。典型情况：必须在角色 `master_postinit` 之后、并且在同步阶段（`OnLoad` 之前）拿到完整构造的玩家实例；或者确实要处理所有 Prefab（例如给所有物品统一加标签）。这时可以正常使用，但回调里先做最便宜的判断，再尽早 return，并在代码注释里说明为什么需要这个时机。审查现有模组时，只有其他钩子就能实现的用法才记为性能问题并给出替换方案。

## 推荐：通过玩家专属组件挂载

在只有玩家才会添加的组件上使用 `AddComponentPostInit`。这样每个玩家实体只触发一次，生成其他实体时完全不会调用。

```lua
-- 所有端、每个玩家实体：标签、netvar、客户端监听
AddComponentPostInit("playervision", function(self, inst)
    inst:AddTag("mymod_player")
    inst.mymod_level = net_tinybyte(inst.GUID, "mymod.level", "mymod_leveldirty")
    if not TheNet:IsDedicated() then
        inst:ListenForEvent("mymod_leveldirty", OnLevelDirty)
    end
end)

-- 仅服务器：在其他服务器组件就绪后添加权威组件
AddComponentPostInit("playerlightningtarget", function(self, inst)
    inst:AddComponent("mymod_playerdata")
end)

-- 仅服务器与本机玩家：输入、相机、动作选择
AddComponentPostInit("playercontroller", function(self, inst)
    -- 必须可重复执行：该组件可能被移除后重新添加
end)
```

### player_common.lua 中各组件的添加顺序

| 阶段 | 组件（玩家专属，原版其他 Prefab 不添加） | 执行端 | 回调时已存在 / 尚不存在 |
| --- | --- | --- | --- |
| 公共部分、`common_postinit` 之前 | `playervision`、`playerspeedmult`、`skilltreeupdater`、`cookbookupdater`、`plantregistryupdater` | 主机和所有客户端，每个玩家实体 | 已有 AnimState、Physics、`player` 标签。**尚未**执行 `common_postinit`、`SetPristine`、服务器组件；`inst.prefab` 为 `nil` |
| `SetPristine` 之后、`master_postinit` 之前 | `playerinspectable`、`playerlightningtarget`（位于 health/hunger/sanity/builder/inventory 之后） | 仅服务器 | 已有基础服务器组件；**尚未**执行角色的 `master_postinit`，角色专属数值可能会覆盖你的修改 |
| `OnSetOwner`（`setowner` 事件）之中 | `playercontroller`、`playeractionpicker`、`playervoter`、`playermetrics` | 仅服务器和该玩家自己的客户端 | 构造已完成；**其他客户端上的该玩家不会触发**；所有权变化时会经 `RemovePlayerComponents` 移除后重新添加 |

选择规则：

- netvar 和需要在 pristine 状态里的标签：用 `playervision`。它在 `SetPristine` 之前执行，并且所有端都会执行，符合 netvar 必须在所有端以相同顺序创建的要求。
- 服务器权威组件和存档数据：用 `playerlightningtarget` 或 `playerinspectable`。之后角色的 `master_postinit` 仍会执行，所以不要在这里设置会被角色覆盖的数值（例如最大生命）。
- 本机输入、相机、HUD 相关：用 `playercontroller`，它只在拥有者一端执行。回调必须可以重复执行，并且要清理自己注册的监听。
- 需要知道角色名，或需要角色数值已定：在上面的回调里 `inst:DoTaskInTime(0, fn)`。此时 Prefab 构造与 `SetPrefabName` 已完成，但存档加载（`OnLoad`）可能早于该任务。如果修改必须在同步阶段完成（会影响加载），而且必须在 `master_postinit` 之后，就用 `AddPlayerPostInit`，这正是它适用的时机。
- 只针对少数已知角色：直接 `AddPrefabPostInit("wilson", fn)`，比任何全局钩子都精确。不要遍历 `DST_CHARACTERLIST`/`MODCHARACTERLIST` 批量注册，加载较晚的模组角色会被漏掉。

钩子组件的风险：其他模组也可能给非玩家实体添加 `playervision` 之类的组件。对关键逻辑可以加 `inst:HasTag("player")` 防御；这里的判断只在组件添加时执行一次，开销可以忽略。原版更新后，用 `grep AddComponent("playervision")` 重新确认组件仍然只在 player_common.lua 里添加，添加顺序也没有变。

## AddSimPostInit / AddGamePostInit

- `AddSimPostInit(fn)`：每次进入世界，在实体加载完、`TheWorld:PostInit()` 之前执行一次，主机和客户端都会执行。适合初始化依赖 `TheWorld` 的一次性数据。回调参数是历史遗留的 `wilson`，现在恒为 `nil`，不要依赖它获取玩家。玩家此时可能尚未生成，处理玩家请监听 `TheWorld` 的 `ms_playerspawn` / `playeractivated`，或使用上面的组件钩子。
- `AddGamePostInit(fn)`：在 `SetPostEnv` 中执行，执行前模组环境会被注入 `TheFrontEnd`、`TheSim`、`Point`、`TheGlobalInstance`。主菜单与世界的每次 Lua 环境启动都会触发，不能假设 `TheWorld` 存在。

## AddGlobalClassPostConstruct

```lua
AddGlobalClassPostConstruct("entityscript", "EntityScript", function(self) ... end)
```

- 用于不通过 `return` 导出、而是直接写入全局变量的类文件（例如 `entityscript.lua` 定义的全局 `EntityScript`）。实现是先 `require(package)`，再 `rawget(_G, classname)`，取不到时回退到 `require` 的返回值。
- 普通的 `widgets/*`、`screens/*`、`components/*` 文件会返回类表，用 `AddClassPostConstruct(path, fn)`。
- 两者都只包装构造函数（`_ctor`），对已经创建的实例无效。需要修改方法时，改类表上的方法，并遵守"保存旧函数并原样转发参数"的规则。

## 包装原函数：必须带 `...`

hook 原版或其他模组的函数时，包装函数**必须用 `...` 接收并原样转发全部参数**，返回值也要原样返回。即使当前版本只有一两个参数，也不能只写自己知道的那几个。

```lua
-- 正确：已知参数可以单独命名，后面仍然要带 ...
local old_DoDelta = self.DoDelta
self.DoDelta = function(self, amount, ...)
    if self.inst:HasTag("mymod_immune") and amount < 0 then
        amount = 0
    end
    return old_DoDelta(self, amount, ...)
end

-- 错误：丢掉了 overtime、cause、ignore_invincible、afflicter、ignore_absorb 等后续参数，也丢掉了返回值
self.DoDelta = function(self, amount)
    old_DoDelta(self, amount)
end
```

原因：

- Klei 更新时经常在参数列表**末尾追加**新参数。只写固定参数的包装会把新参数吞掉，原函数拿到 `nil`，行为悄悄改变，不会报错。
- 其他模组可能也包装了同一个函数，并传入额外参数。参数链只要有一层截断，后面所有层都会收不到。
- 很多函数有多个返回值，或者调用方依赖返回值（例如 `Combat:GetAttacked` 返回是否受击，`Widget:OnControl` 返回"已处理"标志）。不写 `return` 会导致调用方逻辑出错。

### 写法规则

- 先保存旧函数：`local old_fn = obj.Fn`；不确定它是否存在时，判断 `nil`，或者回退到空函数。
- 签名写成 `function(self, 需要用的参数, ...)`，调用写成 `old_fn(self, 需要用的参数, ...)`。修改参数时，只替换自己命名的那几个，`...` 原样传下去。
- 只需要在原函数**之前**加逻辑时，用尾调用 `return old_fn(self, ...)`，所有返回值都会保留。
- 需要在原函数**之后**处理返回值时，先把返回值完整收集起来，再原样返回。不要只取第一个值，也不要用 `{old_fn(...)}` 加 `unpack`，那样遇到中间的 nil 会截断：

```lua
-- select、unpack 没有注入模组入口环境；未设置 GLOBAL 继承时，从 GLOBAL 局部化
local select, unpack = GLOBAL.select, GLOBAL.unpack
local function pack(...) return { n = select("#", ...), ... } end

local old_GetAttacked = self.GetAttacked
self.GetAttacked = function(self, ...)
    local ret = pack(old_GetAttacked(self, ...))
    -- 在这里做后处理
    return unpack(ret, 1, ret.n)
end
```

- 同样的规则适用于各种回调字段的包装：`fn`、`onenter`/`onexit`、`testfn`、`ListenForEvent` 的回调、Widget 的 `OnControl`/`OnGainFocus`。例如 `state.onenter = function(inst, ...) old_onenter(inst, ...) end`（`GoToState(name, params)` 会把 params 传给 `onenter`）。
- `AddClassPostConstruct` 的回调是 `fn(self, ...)`，构造参数会原样传进来。需要用构造参数时，按原类构造函数的签名命名，后面仍然要带 `...`。
- 不要依赖 Lua 5.0 风格的隐式 `arg` 表（虽然 DST 的 Lua 5.1 仍兼容），统一用 `...`；`arg` 遇到 nil 会截断，也会额外分配一张表。

