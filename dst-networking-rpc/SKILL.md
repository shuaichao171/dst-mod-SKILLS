---
name: dst-networking-rpc
description: Implement and debug Don't Starve Together multiplayer replication and RPC. Use when separating master simulation from clients, declaring net variables and dirty events, writing component replicas, synchronizing UI, adding server, client, or shard Mod RPC handlers, validating requests, or fixing desync and prediction bugs.
---

# DST 联机复制与 RPC

由服务器保存并验证权威状态；客户端只复制展示或预测所需的最小数据。

## 工作流

1. 为每个字段标注权威所有者、读者、更新频率、初始值和能否由现有 Replica 推导。
2. 在所有端创建网络实体；在 SetPristine 前声明直接挂在实体上的 netvar、对应 dirty 监听、客户端初始视觉和必要标签。
3. SetPristine 后让非主机分支返回，仅在主机添加 Component、保存逻辑和权威状态机。已注册为可复制的 Component 会在 AddComponent 内先触发 ReplicateComponent，其 Replica 构造函数可以在此时创建自己的 netvar。
4. 选择最小 net 类型；状态用 netvar，瞬时通知才使用 net_event，并在 dirty 回调中只更新表现或缓存。
5. 客户端需要组件式接口时创建 Replica，并在相关实体实例化前从 modmain.lua 调用 AddReplicableComponent；保持 Replica 方法对缺失数据返回安全值。
6. 按方向选择 AddModRPCHandler、AddClientModRPCHandler 或 AddShardModRPCHandler；在接收端重新校验玩家、实体、距离、权限、冷却和参数范围。
7. 预测动作必须可由服务器结果纠正；分别测试主机玩家、远端客户端、专服和洞穴分片。

## 源码锚点

- netvars.lua：可用网络变量和 net_event。
- networkclientrpc.lua：Mod RPC 注册、发送、队列和处理。
- entityreplica.lua、components/*_replica.lua：Replica 契约。
- prefabs/ 中含 SetPristine 与 TheWorld.ismastersim 的实体。
- stategraphs/SGwilson.lua 与客户端 SG：动作预测范例。

## 不变量

- 永远不信任客户端传来的实体、坐标、物品、数值或权限声明。
- 不要在 RPC 中传递大型表或高频连续状态。
- 不要依赖 ThePlayer 代表服务器请求者；使用处理器提供的 player 或 sender。
- dirty 回调可能在对象初始化的不同阶段到达，必须允许依赖暂缺。
- 跨分片逻辑明确目标 shard，并处理目标不可用。

## 验证

- 加入中的客户端能获得正确初始状态，而不只收到后续 dirty 更新。
- 恶意或过期 RPC 不改变服务器状态并产生可诊断结果。
- 延迟、重复输入、断线重连、换洞穴和服务器回滚后状态一致。

## 按需资源

- 需要方向、权威与 Replica 选择时读取 references/network-contract.md。
