---
name: dst-world-systems-events-weather
description: Build Don't Starve Together world-level systems, seasons, weather, day and night reactions, global events, spawn managers, and world-state listeners. Use when adding world components, watching world states, controlling periodic world events, weather or temperature, scheduling global encounters, or persisting one-per-world systems.
---

# DST 世界系统、事件与天气

让 TheWorld 上的主机组件管理全局权威状态，以世界状态和事件向实体发布最小变化。

## 工作流

1. 定义系统是世界组件、世界 Prefab 附件、独立管理器还是一次性事件，并明确地表/洞穴范围。
2. 从 TheWorld.ismastersim 主机分支创建权威管理器；需要客户端表现时声明最小网络字段。
3. 用 WatchWorldState 订阅 isday、season、israining 等变量，并在初始化时主动应用当前值。
4. 周期事件使用可保存计时或世界设置计时器，明确暂停、长更新、回滚和配置覆盖。
5. 生成实体前检查世界、地形、玩家距离、密度、唯一性和已有实例；结束时清理关联对象。
6. 跨分片共享时选择 Shard RPC 或 shard 组件，并定义主分片决策和分片不可用行为。
7. 测试新世界、旧存档、地表、洞穴、空服务器、多玩家分散、季节跳转和回滚。

## 源码锚点

- prefabs/world.lua、world_network.lua 及世界初始化 Prefab。
- components/seasons.lua、weather.lua、caveweather.lua、worldtemperature.lua。
- entityscript.lua：WatchWorldState 与事件。
- worldsettingsutil.lua、worldsettings_overrides.lua：世界设置。
- components 中各类 manager 与 spawner。

## 不变量

- 不要让每个实体各自执行可由一个世界管理器完成的全局扫描。
- 地表与洞穴的 TheWorld 是不同实例，不能假设共享 Lua 状态。
- 回滚可重复外部动作，世界事件必须幂等。
- 世界设置关闭功能时取消任务并处理已存在实体。

## 验证

- 事件在单人、空服务器和多人分散时符合生成规则。
- 保存重载与回滚不会重复唯一实体或奖励。
- 季节、天气和世界设置变化后所有订阅者能恢复一致状态。

