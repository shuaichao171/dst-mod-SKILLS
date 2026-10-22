# 模组容器注册

以下结论来自 `containers.lua`、`components/container.lua`、`components/container_replica.lua` 和 `prefabs/container_classified.lua`，游戏更新后先重新核对。

> 示例里的 modmain 代码假设已经按 dst-mod-scaffolding 设置了 `__index → GLOBAL` 环境继承。没有设置时，`Vector3` 等全局变量要从 `GLOBAL` 读取。

## 注册方式

```lua
-- modmain.lua：在所有端执行
local containers = require("containers")

local params = {
    widget = {
        slotpos = {},
        animbank = "ui_chest_3x3",
        animbuild = "ui_chest_3x3",
        pos = Vector3(0, 200, 0),
        side_align_tip = 160,
    },
    type = "chest",
    itemtestfn = function(container, item, slot)
        return not item:HasTag("irreplaceable")
    end,
}
for y = 2, 0, -1 do
    for x = 0, 2 do
        table.insert(params.widget.slotpos, Vector3(80 * x - 80 * 2 + 80, 80 * y - 80 * 2 + 80, 0))
    end
end
containers.params.mymod_chest = params

-- containers.lua 只在文件末尾计算一次 MAXITEMSLOTS，后来加入的 params 不会自动更新它
containers.MAXITEMSLOTS = math.max(containers.MAXITEMSLOTS, #params.widget.slotpos)
```

```lua
-- Prefab 主机分支
inst:AddComponent("container")
inst.components.container:WidgetSetup("mymod_chest")
```

## 契约

- **`MAXITEMSLOTS` 必须手动更新**：`container_classified` 按 `containers.MAXITEMSLOTS` 创建每个槽位的网络变量。新容器的槽位数超过原版最大值，又没有更新它时，超出的槽位在客户端不会同步。
- **params 的键尽量和 Prefab 名一致**：客户端的 `container_replica` 构造时调用 `containers.widgetsetup(self)`，这里不传名字，默认按 `params[inst.prefab]` 查找。服务器 `WidgetSetup` 用的键和 Prefab 名不一样时，客户端要在非主机分支（或 `inst.OnEntityReplicated`）里自己调用 `inst.replica.container:WidgetSetup("键名")`。原版 firepit 就是这样做的。
- **`itemtestfn` 会在两端执行**：服务器 `container:CanTakeItemInSlot` 和客户端 `container_replica` 都会调用 `self:itemtestfn(item, slot)`，所以它只能使用客户端也能拿到的信息（标签、`prefab`、replica），不能读取服务器组件。
- `widgetsetup` 会把 params 的字段直接复制到 container 对象上。不要在 params 里放每个实例各自的状态，要放的话先 `deepcopy`。
- 复用原版布局时，复制一份再修改，例如 `containers.params.mymod_chest = deepcopy(containers.params.treasurechest)`，不要直接改原版表。
- 容器 UI 使用的 `animbank` / `animbuild` 来自 UI 动画资源。自定义背景要在 Assets 里声明对应的 anim。
