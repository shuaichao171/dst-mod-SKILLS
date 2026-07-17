# Brain 组合模式

## 职责边界

- Brain 选择下一意图。
- Behaviour 执行可持续的决策步骤。
- Component 保存玩法规则与冷却。
- SG 执行动画和原子动作。

## 常见优先级

1. 死亡或禁用状态。
2. 恐慌、逃跑、紧急防御。
3. 当前战斗与技能。
4. 主人、家或领地约束。
5. 工作、采集或社交。
6. 待机与 Wander。

## 节点选择

| 目标 | 节点 |
| --- | --- |
| 按优先级尝试 | PriorityNode |
| 顺序完成 | SequenceNode |
| 条件包裹 | WhileNode、IfNode |
| 执行动作 | DoAction、ActionNode |
| 战斗 | ChaseAndAttack、StandAndAttack |
| 跟随 | Follow、Leash |
| 逃离 | RunAway、Panic |
| 待机 | Wander、StandStill |

## 性能

搜索函数限制半径和标签，缓存静态 home，使用节点 Sleep，并让 PriorityNode 有合理检查周期。不要在每个条件函数里创建新闭包、大表或执行全图搜索。

## 自定义 Behaviour

仅在 behaviours/ 无法表达需求时创建。实现 Visit、Reset、Stop 和睡眠；返回 READY、RUNNING、SUCCESS、FAILED 的正确状态，并确保中断时撤销任务和事件。

