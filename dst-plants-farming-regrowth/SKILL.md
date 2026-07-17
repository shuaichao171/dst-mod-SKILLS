---
name: dst-plants-farming-regrowth
description: Create Don't Starve Together plants, crops, farm-soil interactions, growth stages, stress, nutrients, tending, harvesting, and world regrowth. Use when working with growable, pickable, farmplantstress, farming_manager, plantregrowth, regrowthmanager, crop stage data, seasonal growth, or plant save and long-update behavior.
---

# DST 植物、农作物与再生

把生长阶段、环境输入、收获、枯萎、离线推进和世界再生分别建模。

## 工作流

1. 选择普通可采集植物、Growable 多阶段实体、农田作物或世界再生资源中的正确模型。
2. 定义阶段表、动画、持续时间、季节条件、产物、工作动作和阶段切换回调。
3. 农作物按 farming_manager、farmplantstress、养分、水分、照料和家庭/拥挤规则接入。
4. 服务器推进生长与压力；客户端只复制阶段、动画和可见提示。
5. 实现 OnSave、OnLoad 与 LongUpdate，限制长时间离线推进并防止重复收获。
6. 世界资源使用 plantregrowth 或 regrowthmanager，明确最大密度、合法地形、玩家距离和旧实例登记。
7. 测试季节切换、干旱、积雪、过熟、铲除、燃烧、保存重载和大规模农田性能。

## 源码锚点

- components/growable.lua、pickable.lua、harvestable.lua、plantable.lua。
- components/farming_manager.lua、farmplantstress.lua、farmplanttendable.lua、farmsoildrinker.lua。
- components/plantregrowth.lua、regrowthmanager.lua。
- 原版 farm_plant 与普通植物 Prefab。

## 不变量

- 阶段切换回调必须允许实体在回调中被替换或移除。
- 客户端动画不能推进服务器生长状态。
- 再生搜索限制范围、密度和尝试次数。
- 离线推进不可绕过季节、环境或一次性奖励规则。

## 验证

- 所有阶段可达且动画、可采集性和产物匹配。
- LongUpdate 与在线经过同等时间产生兼容结果。
- 大量植物和长期世界运行不会造成任务或实体无限增长。

