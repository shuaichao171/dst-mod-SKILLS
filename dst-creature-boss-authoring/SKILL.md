---
name: dst-creature-boss-authoring
description: Orchestrate complete Don't Starve Together creatures and bosses. Use when building a mob or boss that combines prefabs, components, brains, stategraphs, combat, phases, minions, loot, networking, persistence, world integration, and multiplayer encounter testing.
---

# DST 生物与 Boss 编排

先设计跨 Prefab、Component、Brain、SG、网络和存档的职责表，再分别实现和联调。

## 工作流

1. 写出遭遇规格：生成条件、生态位、属性、阵营、感知、技能、阶段、掉落、离场和重生规则。
2. 选择两个以上相近原版生物或 Boss，分别提取 Prefab 装配、Brain 优先级、SG 技能和阶段管理模式。
3. 将持久阶段、冷却和外部引用放入 Component 或 Prefab；Brain 选择技能意图；SG 执行动画和伤害时间线。
4. 先实现最小可战斗闭环，再逐个加入技能、召唤物、场地机制和阶段转换，每次保持可测试。
5. 为血量、阶段、特殊目标和 UI 提供最小网络状态；所有玩家请求在服务器校验。
6. 定义死亡、脱战、卸载、世界重载、回滚、玩家全灭、召唤物残留和重复生成的清理规则。
7. 用单人、多人、高延迟、洞穴、保存中途重载和极端伤害测试完整遭遇。

## 源码锚点

- prefabs/、brains/、stategraphs/ 中同类 Boss 的同名前缀文件。
- components/combat.lua、health.lua、lootdropper.lua、entitytracker.lua、timer.lua。
- world components 与事件 Prefab：生成、重生和世界唯一性。
- netvars.lua 与 Replica：Boss UI 和阶段表现。

## 不变量

- 不要把整个 Boss 写进一个 Prefab 文件或 SG 状态。
- 阶段转换必须幂等，避免同一血量事件多次生成奖励或召唤物。
- Brain 不直接结算技能伤害，客户端 FX 不改变权威状态。
- 世界唯一 Boss 需要保存、重复生成检测和孤儿清理。

## 验证

- 每个阶段可进入、可退出、可中断且能保存恢复。
- 玩家离开、Boss 卸载或服务器回滚后场地与召唤物一致。
- 多人目标切换、仇恨、掉落归属和性能符合设计。

