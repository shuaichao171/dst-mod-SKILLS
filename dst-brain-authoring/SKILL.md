---
name: dst-brain-authoring
description: Create and tune Don't Starve Together creature brains and behaviour trees. Use when writing scripts/brains files, composing PriorityNode, SequenceNode, WhileNode, IfNode, DoAction, ChaseAndAttack, Wander, Follow or RunAway behavior, creating custom behaviour nodes, or fixing AI target selection, sleep, and performance.
---

# DST Brain 与 Behaviour Tree 编写

让 Brain 选择意图，让 Component 保存规则，让 SG 执行动画与不可分割动作。

## 工作流

1. 从同生态位原版 Brain 复制结构思路，列出最高优先级生存反应、战斗、工作、跟随和待机行为。
2. 在 Brain:OnStart 中构建 root，使用 PriorityNode 明确优先级；用 WhileNode 或 IfNode 包住状态条件。
3. 优先复用 behaviours/ 中的 ChaseAndAttack、DoAction、Follow、RunAway、Leash、Wander 等节点。
4. 目标搜索函数过滤死亡、不可见、无效、同阵营和超出领地对象，并使用适当 MUST、CANT、ONEOF 标签。
5. 让节点返回 READY、RUNNING、SUCCESS 或 FAILED 的正确状态；等待时使用 Sleep，避免每 tick 全图扫描。
6. 只有现有节点无法表达时才创建自定义 BehaviourNode，并实现 Visit、Reset、Stop 与睡眠语义。
7. 用 Brain 调试字符串和不同玩家距离测试苏醒、休眠、目标切换、失去目标及 SG 忙碌状态。

## 源码锚点

- brain.lua：Brain、BrainWrangler、启动、暂停、睡眠和更新。
- behaviourtree.lua：节点状态、组合节点、事件节点和 Sleep。
- behaviours/：29 个通用行为节点。
- brains/：同类生物、Boss、跟随者和被动生物范例。
- entityscript.lua：SetBrain、RestartBrain、StopBrain。

## 不变量

- Brain 不直接承担需要动画原子性的伤害时序；交给 SG。
- 不要在高频条件函数反复创建大表或无范围 FindEntities。
- 优先级必须让死亡、恐慌和逃跑等紧急行为能打断低优先级行为。
- Brain 只在主机运行，不依赖本地玩家或客户端 UI 状态。

## 验证

- 所有行为分支在成功、失败和中断后都能复位。
- 实体睡眠、唤醒、冻结、骑乘、失去目标和死亡后无残留行为。
- 大量同类实体存在时搜索频率和半径仍可接受。

## 按需资源

- 复制 assets/brain-template.lua 创建 Brain。
- 需要节点选择和性能规则时读取 references/brain-patterns.md。

