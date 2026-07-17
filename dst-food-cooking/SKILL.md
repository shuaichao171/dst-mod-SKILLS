---
name: dst-food-cooking
description: Create Don't Starve Together foods, cooking ingredients, crock-pot recipes, cooker variants, spices, drying behavior, cookbook entries, and edible effects. Use when calling AddIngredientValues or AddCookerRecipe, editing prepared food definitions, calculating recipe priorities and tests, or debugging cookbook and food-stat behavior.
---

# DST 食物与烹饪

先设计食材标签和候选配方竞争关系，再实现成品 Prefab、食用效果与食谱书表现。

## 工作流

1. 定义生食、熟食或料理的 hunger、sanity、health、perish time、foodtype、temperature 和额外效果。
2. 用 AddIngredientValues 给食材提供烹饪标签，避免与现有标签和数值产生非预期候选。
3. 用 AddCookerRecipe 定义 name、test、priority、weight、foodtype、cooktime、potlevel 和 cookbook 条目。
4. 同时检查所有会命中的原版与模组配方；更高 priority 必须有明确理由。
5. 成品 Prefab 配置 edible、perishable、inventoryitem、stackable 和 oneatenfn，并把权威效果放服务器。
6. 需要香料、沃利料理、晾晒或专用 cooker 时分别检查对应管线，不假设普通锅逻辑完全通用。
7. 用边界食材组合、重复标签、不可烹饪物、食谱书未知状态和保存重载测试。

## 源码锚点

- cooking.lua、preparedfoods.lua、preparedfoods_warly.lua、spicedfoods.lua。
- components/edible.lua、stewer.lua、cookable.lua、dryable.lua、perishable.lua。
- cookbookdata.lua、widgets 与 screens 中 cookbook 文件。

## 不变量

- 配方 test 只判断输入，不产生副作用。
- IngredientValues 与 priority 改动可能影响所有锅配方，必须做冲突扫描。
- 食用 Buff 在重复食用、死亡和移除时明确叠加或刷新规则。
- 客户端不直接应用属性变化。

## 验证

- 目标食材组合稳定得到预期料理，邻近组合不会误命中。
- 烹饪锅、便携锅和特殊 cooker 的支持范围明确。
- 料理属性、腐败、食谱书和食用副作用保存重载后正确。

