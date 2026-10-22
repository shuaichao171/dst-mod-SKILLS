# 世界设置选项与全局 PreInit 钩子

以下结论来自 `modutil.lua`、`map/customize.lua`、`map/level.lua`、`map/tasksets.lua`、`mods.lua` 和 `constants.lua`，游戏更新后先重新核对。

## 世界设置选项（Customize）

在 **modworldgenmain.lua** 中注册：建服界面会部分加载 modworldgenmain（`FrontendLoadMod`），世界生成也会加载它。

```lua
-- modworldgenmain.lua
local freq = GetCustomizeDescription("frequency_descriptions")  -- 返回原版描述列表的深拷贝

AddCustomizeGroup(LEVELCATEGORY.SETTINGS, "mymod_monsters",
    "我的模组生物", nil, "images/mymod_customization.xml", 20)

AddCustomizeItem(LEVELCATEGORY.SETTINGS, "mymod_monsters", "mymod_beast", {
    value = "default",            -- 默认值，必须是 desc 中某项的 data
    desc = freq,                  -- { {text=..., data=...}, ... }；不写时用组的 desc
    image = "mymod_beast.tex",
    atlas = "images/mymod_customization.xml",  -- 不写时用组的 atlas
    world = { "forest", "cave" }, -- 出现在哪种世界的设置页
    order = 1,
})
```

| API | 参数 | 说明 |
| --- | --- | --- |
| `AddCustomizeGroup(category, name, text, desc, atlas, order)` | `category` 取 `LEVELCATEGORY.SETTINGS` 或 `LEVELCATEGORY.WORLDGEN` | 同名组已存在时直接返回，不报错 |
| `AddCustomizeItem(category, group, name, itemsettings)` | `group` 可以是自己的组或原版组名 | 同名选项已存在时直接返回。`group` 为 `nil` 时只登记为 misc 选项，不出现在界面上 |
| `RemoveCustomizeGroup(category, name)` | | 删除自己的组；对原版组是按模组记录禁用 |
| `RemoveCustomizeItem(category, name)` | | 删除自己的选项；对原版选项是按模组记录禁用 |
| `GetCustomizeDescription(name)` | 如 `frequency_descriptions`、`yesno_descriptions`、`speed_descriptions` 等 | 返回深拷贝，修改不会影响原版 |

- 选项名是全局键，**必须加模组前缀**，否则会被同名原版或其他模组的选项挡掉（直接返回，不提示）。
- 加入原版组时，原版组的 atlas 里没有你的图，必须在 itemsettings 里写 `atlas`。
- 图集要能在建服前端加载，否则图标不显示。用 modservercreationmain 的 `FrontEndAssets` 加 `ReloadFrontEndAssets()` 声明（见 dst-client-frontend-mods）。
- 读取设置值：
  - 世界设置（SETTINGS）：运行时在服务器读 `TheWorld.topology.overrides`。原版写法是先判断 `TheWorld.topology.overrides ~= nil`，再判断具体值，例如 `overrides.terrariumchest == "never"`。
  - 世界生成（WORLDGEN）：在世界生成阶段读 `level.overrides[name]`，例如在下面的 LevelPreInit 回调里。
  - 两种都要处理 `nil`（旧存档或没开模组时创建的世界），把它当作默认值。

## AddLevelPreInitAny / AddTaskSetPreInitAny

`map/level.lua` 的 `Level:ChooseTasks()` 依次执行：

1. `tasksets.GetGenTasks(task_set)`，返回 TaskSet 数据的**深拷贝**。
2. `AddTaskSetPreInit(task_set, fn)`，然后是 `AddTaskSetPreInitAny(fn)`，参数都是这份拷贝。
3. 把拷贝的字段合并到 Level 对象上。
4. `AddLevelPreInit(level.id, fn)`，然后是 `AddLevelPreInitAny(fn)`，参数都是 Level 对象。

```lua
AddLevelPreInitAny(function(level)
    if level.location ~= "forest" then
        return
    end
    if (level.overrides.mymod_beast or "default") == "never" then
        return
    end
    level.set_pieces = level.set_pieces or {}
    -- 修改 tasks、set_pieces、numoptionaltasks 等
end)

AddTaskSetPreInitAny(function(taskset)
    -- 参数是当前世界 TaskSet 的拷贝；不知道 TaskSet 名，需要时判断 taskset.location 或其他字段
end)
```

- `AddLevelPreInit(id, fn)` 按 `level.id` 匹配。玩家用自定义预设创建的世界，id 不一定是原版预设 id（例如 `SURVIVAL_TOGETHER`），按 id 注册的钩子可能不会触发。要覆盖所有森林或洞穴世界时，用 `AddLevelPreInitAny` 加 `level.location` 判断。
- `level.location` 是必填字段（`Level` 构造时会断言），值为 `forest`、`cave` 或自定义 Location 名。
- 这两个回调只在世界生成环境中执行，不能访问 `TheWorld`、玩家或组件。
- 在这里修改的数据本来就是本次生成用的拷贝，不会污染原版定义。但回调里自己往共享常量表里插数据时，仍要先复制。
