---
name: dst-status-buffs-survival
description: Implement Don't Starve Together survival stats, buffs, debuffs, timed modifiers, hunger, sanity, temperature, moisture, speed, damage-over-time, and status visuals. Use when creating status-effect prefabs, using debuffable, modifying player or creature stats, stacking timed effects, or synchronizing status UI and FX.
---

# DST 生存属性、Buff 与 Debuff

定义效果的权威状态、叠加策略、持续时间、移除条件和客户端表现，保证应用与撤销对称。

## 工作流

1. 写出效果目标、持续时间、叠加或刷新规则、数值来源、死亡/换角色/睡眠/下线行为和 UI 需求。
2. 优先使用 debuffable 与独立 Debuff Prefab 管理有生命周期的效果；简单瞬时变化直接调用对应组件。
3. 为 health、hunger、sanity、temperature、moisture、locomotor 或 combat 修改使用可移除的唯一 source key。
4. 在 attached、extended、detached 和 OnRemoveEntity 路径对称注册与撤销事件、任务、标签、数值和 FX。
5. 服务器维护剩余时间与玩法数值；客户端通过 netvar、Replica 或跟随 FX 显示。
6. 明确多个来源、重复施加、免疫、净化、离线时间和保存重载规则。
7. 测试死亡复活、换洞穴、骑乘、装备切换、极端数值和效果同时结束。

## 源码锚点

- components/debuff.lua、debuffable.lua 与 EntityScript:AddDebuff。
- components/health.lua、hunger.lua、sanity.lua、temperature.lua、moisture.lua。
- components/locomotor.lua、combat.lua 及状态类 Prefab。
- widgets 中 badge、overlay 与状态提示。

## 不变量

- 应用与撤销必须使用同一 source key，不能覆盖其他来源的修饰。
- 周期伤害和属性变化只由服务器执行。
- 视觉 FX 的移除不能反向决定权威 Buff 是否结束。
- 允许目标在回调期间死亡、移除或失去对应组件。

## 验证

- 叠加、刷新、替换、免疫和净化符合规格。
- 保存重载和跨分片后剩余时间与数值一致。
- 多个来源结束时只撤销各自贡献。

