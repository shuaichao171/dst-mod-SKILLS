---
name: dst-stategraph-authoring
description: Create and extend Don't Starve Together stategraphs. Use when writing SG files, State, EventHandler, TimeEvent, ActionHandler, onenter or onexit logic, state tags, timeouts, animation timelines, server and client player states, or debugging entities stuck in animation and action states.
---

# DST StateGraph 编写

让 SG 负责可中断的动作与动画时序，并把持久玩法状态留在 Component 或 Prefab。

## 工作流

1. 从相同实体类型和相同动作的原版 SG 状态开始，记录进入条件、标签、动画、时间线、退出路径和事件。
2. 独立 SG 使用 stategraphs/SGmod_entity.lua 模块名，并让 inst:SetStateGraph('SGmod_entity') 与文件名一致；StateGraph 内部名称使用 mod_entity。
3. 用 State 定义唯一名称、tags、onenter、timeline、events、ontimeout 和 onexit；所有临时数据放入 inst.sg.statemem。
4. 为非 instant BufferedAction 提供 ActionHandler。PushBufferedAction 调用 StartAction 查找 actionhandlers，普通 doaction EventHandler 不能替代它。
5. onenter 验证参数与组件并启动动作；TimeEvent 使用 FRAMES 或明确秒数，权威副作用只在服务器 SG 的单一时间点执行。
6. 为动画结束、timeout、attacked、death 和动作取消提供明确转移；onexit 对称撤销物理、控制、视觉、任务、声音和临时标签。
7. 修改玩家动作时同时检查 SGwilson 与客户端 SG，验证预测、回正和 ServerStateMatches。

## 源码锚点

- stategraph.lua：StateGraphInstance、GoToState、timeout、state tag 与事件处理。
- stategraphs/commonstates.lua：可复用状态构造。
- stategraphs/SGwilson.lua 和客户端玩家 SG：预测动作。
- stategraphs/ 中同类生物或物件 SG。

## 不变量

- 不要把永久玩法数据只存入 statemem。
- 每个改变物理、控制、速度或视觉状态的 onenter 都必须有对称 onexit。
- 不要依赖动画一定自然结束；攻击、冻结、死亡和实体移除都可能中断。
- 避免在客户端和服务器两边重复造成伤害、扣耐久或生成掉落。

## 验证

- 每个状态都有可达入口和至少一条可靠退出路径。
- 提前中断、连续事件、动画缺失和目标失效不会卡住实体。
- 高延迟远端客户端的预测状态能被服务器接受或平滑纠正。

## 按需资源

- 复制 assets/stategraph-template.lua 创建独立 SG。
- 需要状态契约和玩家预测时读取 references/stategraph-contract.md。
