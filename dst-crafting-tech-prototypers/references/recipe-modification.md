# 修改已有配方、拆解配方与过滤器移除

以下结论来自 `modutil.lua`、`recipe.lua`、`mods.lua`、`main.lua`、`components/lootdropper.lua` 和 `prefabs/staff.lua`，游戏更新后先重新核对。

> 示例里的 modmain 代码假设已经按 dst-mod-scaffolding 在文件顶部设置了 `__index → GLOBAL` 环境继承。没有设置时，入口环境里未注入的全局变量（TechTree、TECH 等；Ingredient 已注入）要从 `GLOBAL` 读取。

## AddRecipePostInit / AddRecipePostInitAny

```lua
-- 修改原版配方：注册时立即执行
AddRecipePostInit("spear", function(recipe)
    recipe.ingredients = { Ingredient("twigs", 2), Ingredient("rope", 1), Ingredient("flint", 2) }
end)

-- 处理所有配方，包括其他模组之后添加的配方
AddRecipePostInitAny(function(recipe)
    if recipe.name ~= "othermod_item" or recipe.mymod_patched then
        return
    end
    recipe.mymod_patched = true
    recipe.numtogive = 2
end)
```

### 执行时机（源码核对结论）

| API | 对已存在的配方 | 对之后新建的配方 |
| --- | --- | --- |
| `AddRecipePostInit(name, fn)` | `AllRecipes[name]` 存在时**立即**执行一次 | **不会执行**（见下） |
| `AddRecipePostInitAny(fn)` | 立即遍历 `AllRecipes` 全部执行 | 在 `Recipe._ctor` 末尾执行 |

- `main.lua` 先 `require("recipes")` 再 `ModManager:LoadMods()`，所以原版配方在 modmain 执行时都已存在，`AddRecipePostInit("原版名", fn)` 可以直接使用。
- **原版缺陷**：`Recipe._ctor` 调用的是 `GetPostInitFns("RecipePostInit")`，没有传配方名。`mods.lua` 拿到的是按名字索引的表，再用 `ipairs` 遍历，一个函数都取不到。因此对之后才创建的配方（加载顺序靠后的其他模组、你自己稍后创建的配方），`AddRecipePostInit` 不会生效。要修改其他模组的配方，用 `AddRecipePostInitAny` 加名称判断，或在 modinfo 里调整 `priority`，确保对方先加载。
- `AddRecipePostInitAny` 对新配方的回调在 `Recipe._ctor` 末尾执行，此时 **`Recipe2` 还没有把 `is_deconstruction_recipe` 改回 `false`**（基类按 `tab == nil` 先置为 `true`），`AddRecipe2` 也还没有把配方加入过滤器，`SetModRPCID` 也还没调用。回调里不要依赖这些字段，需要时用 `recipe.name`、`recipe.product` 判断。
- Any 回调同时会作用于拆解配方和角色配方，必须先过滤再修改，并保证可以重复执行。
- 配方表由 modmain 在每一端分别构建，所以修改必须在所有端以相同方式执行。不要用 `TheWorld.ismastersim`、`TheNet:GetIsServer()` 之类条件包住，否则客户端界面显示的材料会和服务器实际扣除的不一致。

### 常改字段

`ingredients`、`character_ingredients`、`tech_ingredients`、`level`、`numtogive`、`builder_tag`、`builder_skill`、`nounlock`、`testfn`、`atlas`/`image`。

- 构造配方时会按 `IsCharacterIngredient` / `IsTechIngredient` 把材料分进三个列表。替换材料时，生命、理智等角色材料要放进 `character_ingredients`，不要混进 `ingredients`。
- `level` 是 `TechTree.Create(...)` 生成的副本。修改时写 `recipe.level = TechTree.Create(TECH.SCIENCE_TWO)`，不要直接引用 `TECH` 里的共享表。修改 `level` 或 `builder_tag` 等可见性字段后，要测试制作菜单的缓存和已解锁配方的表现。

## AddDeconstructRecipe

```lua
AddDeconstructRecipe("mymod_statue", { Ingredient("marble", 4), Ingredient("goldnugget", 2) })
```

- 它创建的是 `DeconstructRecipe`：`is_deconstruction_recipe = true`、`nounlock = true`、科技为 `TECH.NONE`，也不加入任何过滤器。`GetValidRecipe` 会排除它，所以它不会出现在制作菜单里。
- 用途：为**不能制作**的 Prefab 指定拆解与掉落返还。分解法杖（`prefabs/staff.lua` 通过 `AllRecipes[target.prefab]` 判断目标能否拆解并计算返还）和 `lootdropper.droprecipeloot`（锤毁时按配方返还）都按 `AllRecipes[prefab名]` 查找。
- **名称与 Prefab 名相同，并且会覆盖同名配方**：`Recipe._ctor` 直接执行 `AllRecipes[name] = self`。对一个已有制作配方的 Prefab 调用它，会把制作配方替换掉，那个物品就做不出来了。可制作的物品本来就按制作配方返还，不需要再加拆解配方。

## RemoveRecipeFromFilter / AddRecipeToFilter

```lua
RemoveRecipeFromFilter("spear", "WEAPONS")
AddRecipeToFilter("spear", "MYMOD_FILTER")
```

- `filter_name` 是 `CRAFTING_FILTERS` 的键，必须是**大写**（`AddRecipeFilter` 会把 `name` 转成大写后存储，`AddRecipeToFilter` 和 `RemoveRecipeFromFilter` 不会转换）。名字写错时静默失败，不报错。
- 移除后会重建 `default_sort_values`，只影响显示。配方仍然可以制作，权限检查仍以 builder 和科技为准。
- `AddRecipe2` 会自动把配方加入 `MODS` 过滤器（`nounlock` 配方加入 `CRAFTING_STATION`），`AddCharacterRecipe` 会加入 `CHARACTER`。不想显示在这些分类里时，用 `RemoveRecipeFromFilter` 移除。
