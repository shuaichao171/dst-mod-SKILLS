---
name: dst-crafting-tech-prototypers
description: Create Don't Starve Together recipes, crafting filters, technology requirements, prototypers, character recipes, deconstruction returns, and crafting-station behavior. Use when working with AddRecipe2, AddCharacterRecipe, AddRecipeFilter, TechTree, Ingredient, builder tags or skills, recipe atlases, or crafting UI visibility.
---

# DST 制作、科技与制作站

分别定义配方成本、解锁条件、显示过滤器和制作站范围，避免把 UI 分类当作权限。

## 工作流

1. 定义产物、数量、Ingredients、科技等级、制作站、角色标签或技能、过滤器、图标和放置需求。
2. 使用 AddRecipe2；角色专属使用 AddCharacterRecipe 或明确 builder_tag、builder_skill。
3. 需要新分类时先 AddRecipeFilter，再把配方加入过滤器；过滤器只影响展示，不替代服务器权限。
4. 制作站通过 prototyper 与 PROTOTYPER_DEFS 提供科技，明确范围、动画、开启关闭和树等级。
5. 为建筑配方接入 placer 和 min_spacing；为拆解行为定义可接受的返回材料。
6. 检查已废弃 AddRecipe 与 AddRecipeTab 用法并迁移到当前 API。
7. 测试已知/未知配方、靠近/远离制作站、角色限制、技能解锁、手柄菜单和远端客户端制作。

## 源码锚点

- recipe.lua、recipes.lua、recipes_filter.lua、techtree.lua。
- components/builder.lua、builder_replica.lua、prototyper.lua。
- widgets/crafting.lua、crafting_sorting.lua。
- modutil.lua：AddRecipe2、AddCharacterRecipe、AddRecipeFilter、AddPrototyperDef。

## 不变量

- 配方 ID、Prefab 名和库存图标名保持一致或显式配置。
- 服务器重新检查材料、科技、角色和技能条件。
- 不要依赖旧版 RecipeTab API。
- 配置关闭配方时同时处理已缓存菜单与旧存档已有物品。

## 验证

- 配方在正确过滤器、角色和制作站条件下显示。
- 制作、重复制作、材料不足和网络延迟不会重复扣料或产物。
- 放置类配方在无效地形和阻挡位置被服务器拒绝。

