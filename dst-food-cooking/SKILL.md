---
name: dst-food-cooking
description: Create Don't Starve Together foods, cooking ingredients, crock-pot recipes, cooker variants, spices, drying behavior, cookbook entries, and edible effects. Use when calling AddIngredientValues or AddCookerRecipe, editing prepared food definitions, calculating recipe priorities and tests, or debugging cookbook and food-stat behavior.
---

# DST 食物与烹饪

先设计食材标签和候选配方竞争关系，再实现成品 Prefab、食用效果与食谱书表现。

## 工作流

1. 定义生食、熟食或料理的 hunger、sanity、health、perish time、foodtype、temperature 和额外效果。
2. 用 AddIngredientValues 给食材提供烹饪标签，避免与现有标签和数值产生非预期候选。
3. 用 AddCookerRecipe 定义 name、test、priority、weight、foodtype、cooktime、potlevel 和 cookbook 条目。模组料理在锅里的显示，默认是在 `cook_pot_food` build 里找与料理同名的 symbol（`prefabs/cookpot.lua` 的 SetProductSymbol），找不到就显示为空。要在配方里设置 `overridebuild` 和 `overridesymbolname`，并在 Assets 里声明该 build。
4. 食谱书图标：先找 `recipe.cookbook_tex`（默认 `<name>.tex`），再找 `recipe.cookbook_atlas`。没有设置 atlas 时，用 `GetInventoryItemAtlas(tex, true)` 查找，这时不会回退，所以要用 RegisterInventoryItemAtlas 注册料理图标，或者直接设置 cookbook_atlas。模组料理会被自动归到模组分类（`MOD_COOKBOOK_CATEGORY`）。
5. 同时检查所有会命中的原版与模组配方；更高 priority 必须有明确理由。
6. 成品 Prefab 配置 edible、perishable、inventoryitem、stackable 和 oneatenfn，并把权威效果放服务器。
7. 需要香料、沃利料理、晾晒或专用 cooker 时分别检查对应管线，不假设普通锅逻辑完全通用。
8. 用边界食材组合、重复标签、不可烹饪物、食谱书未知状态和保存重载测试。

## 源码锚点

- cooking.lua、preparedfoods.lua、preparedfoods_warly.lua、spicedfoods.lua。
- components/edible.lua、stewer.lua、cookable.lua、dryable.lua、perishable.lua。
- cookbookdata.lua、widgets 与 screens 中 cookbook 文件；widgets/redux/cookbookpage_crockpot.lua：cookbook_tex / cookbook_atlas 查找。
- prefabs/cookpot.lua：SetProductSymbol 与 overridebuild、overridesymbolname。

## 不变量

- 配方 test 只判断输入，不产生副作用。
- IngredientValues 与 priority 改动可能影响所有锅配方，必须做冲突扫描。
- 食用 Buff 在重复食用、死亡和移除时明确叠加或刷新规则。
- 客户端不直接应用属性变化。

## 验证

- 目标食材组合稳定得到预期料理，邻近组合不会误命中。
- 烹饪锅、便携锅和特殊 cooker 的支持范围明确。
- 料理属性、腐败、食谱书和食用副作用保存重载后正确。

