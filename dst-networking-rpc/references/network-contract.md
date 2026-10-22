# 联机选择与契约

## 选择机制

| 需求 | 机制 |
| --- | --- |
| 仅服务器使用的状态 | 普通 Component 字段 |
| 客户端持续读取的小状态 | netvar |
| 客户端按组件接口读取 | Replica 加 netvar |
| 客户端请求服务器操作 | Mod RPC to server |
| 服务器通知单个或全部客户端 | Client Mod RPC 或网络状态 |
| 分片间通信 | Shard Mod RPC |
| 可从其他状态推导的视觉 | 客户端本地推导 |

状态不要用 net_event 代替。net_event 适合瞬时信号，加入中的客户端不会获得历史事件。

## 网络 Prefab 顺序

1. AddNetwork。
2. 创建直接挂在实体上的 netvar 及其 dirty 监听。
3. 添加客户端所需标签和视觉初值。
4. SetPristine。
5. 非主机返回。
6. 主机添加 Component 和权威逻辑；对于已注册的可复制 Component，AddComponent 会先调用 ReplicateComponent，再构造服务器 Component。

Replica 的网络字段不等同于 Prefab 直接网络字段。服务器可在 SetPristine 后由 AddComponent 构造 Replica；客户端在实体初始标签反序列化后由 ReplicateEntity 构造对应 Replica。必须在相关实体出现前调用 AddReplicableComponent，使两端都知道该组件可复制。

## netvar 类型（netvars.lua）

| 类型 | 取值 |
| --- | --- |
| `net_bool` | 1 bit |
| `net_tinybyte` / `net_smallbyte` / `net_byte` | 0..7 / 0..63 / 0..255 |
| `net_shortint` / `net_ushortint` | -32767..32767 / 0..65535 |
| `net_int` / `net_uint` | 32 位有符号 / 无符号 |
| `net_float` | 32 位浮点 |
| `net_hash` | 设置时传字符串或 hash，读取时只返回 hash |
| `net_string` | 变长字符串 |
| `net_entity` | 实体引用 |
| `net_bytearray` / `net_smallbytearray` / `net_ushortarray` | 数组，最多 31 个元素，开销大 |

- 构造函数是 `net_xxx(inst.GUID, "唯一名", "dirty事件名")`。**服务器和客户端必须以相同的名字和类型声明同一组 netvar**，否则实体反序列化会失败。所以用了 netvar 的模组，服务器和所有客户端都必须安装。
- `set(x)` 只在值真正改变时同步，并在两端触发 dirty 事件。`set_local(x)` 只改本地值、不同步，下一次服务器 `set` 无论值是否变化都会当作 dirty。dirty 事件在 Lua 更新之前触发。
- 只有一个值会变化时，用 `GetIdealUnsignedNetVarForCount(count)` 选择能容纳它的最小无符号类型。
- `net_event(guid, name)` 是对 net_bool 的封装，用 `:push()` 触发，只适合一次性信号。

## 客户端复制钩子

- 客户端反序列化实体后执行 `EntityScript:ReplicateEntity()`：对每个已注册的可复制组件，如果实体带有 `_<组件名>` 或 `__<组件名>` 标签，就构造对应的 Replica。服务器 AddComponent 时也正是通过这个标签告诉客户端要创建 Replica。所以不要手动移除 `_<组件名>` 标签。
- Replica 构造完后会调用 `inst.OnEntityReplicated(inst)`（只要定义了这个字段）。客户端需要依赖 Replica 的初始化（例如 `inst.replica.container:WidgetSetup(...)`）放在这里，并且在 SetPristine 之后的客户端分支里赋值。

## RPC 注册与获取

```lua
-- modmain.lua 顶层：主机、客户端、各分片都必须执行同样的注册，ID 才能对上
AddModRPCHandler("mymod", "accept", function(player, target) ... end)          -- 客户端 → 服务器，首参 player
AddClientModRPCHandler("mymod", "invite", function(inviter) ... end)            -- 服务器 → 客户端，无 player 参数
AddShardModRPCHandler("mymod", "sync", function(shardid, payload) ... end)      -- 分片 → 分片，首参发送方 shardid

SendModRPCToServer(GetModRPC("mymod", "accept"), target)
SendModRPCToClient(GetClientModRPC("mymod", "invite"), userid_or_list_or_nil, inviter)
SendModRPCToShard(GetShardModRPC("mymod", "sync"), shardid_or_list_or_nil, payload)
```

- `GetModRPC` / `GetClientModRPC` / `GetShardModRPC(namespace, name)` 返回 `{ namespace, id }` 表，是发送接口要求的 `id_table`。modutil.lua 把 `MOD_RPC`、`CLIENT_MOD_RPC`、`SHARD_MOD_RPC` 全局表标为 legacy，新代码用 Get 函数。
- 这三个函数直接索引 `MOD_RPC[namespace][name]`，namespace 未注册时会因为对 nil 取下标而报错。发送方和接收方都要先执行对应的 `Add*ModRPCHandler`。
- `GetModRPCHandler` / `GetClientModRPCHandler` / `GetShardModRPCHandler(namespace, name)` 返回已注册的处理函数本身。用于包装或复用其他模组的处理器（先保存旧函数再转发），不能用来发送。
- 发送目标：Client RPC 的第一个附加参数为 `nil` 时发给所有已连接客户端，也可以是单个 userid 或 userid 列表，只能发给本分片上的玩家；Shard RPC 同理，可以是 `nil`、单个 shardid 或列表。分片处理器收到的 shardid 是整数，需要时用 `tostring` 转回字符串（原版 `ShardTransactionSteps` 就是这样做的）。
- 发送前 `Send*` 会断言处理器已注册。重置世界时 `DisableRPCSending` 会把发送函数替换为空函数，这期间发送不会报错，但也不会送达。
- 服务器收到的 RPC 先进入队列，并按发送者限流：基础额度是 `RPC_QUEUE_RATE_LIMIT`（每个逻辑 tick 20 个），每注册一个 mod RPC 加 5。超出额度的请求会被丢弃，每个发送者只记一次日志。不要用高频 RPC 传输连续状态。

## RPC 校验

### 实体参数

RPC 需要传递接收端可见的网络实体时，直接传 Entity。DST 的 RPC 序列化层会把实体参数映射为接收端对应的实体引用；接收端仍必须处理 `nil`、已移除实体和非法参数。

实体参数只能映射接收端已经复制到的实体。服务端刚 `SpawnPrefab` 后不要在同一帧发送依赖该实体的 Client Mod RPC；先等待实体复制，或在严格流程中让客户端确认实体可见后再发送。否则 RPC 可能先于实体出现，处理器只能得到不可用参数；绑定在该实体上的 Talker、动画等瞬时表现也可能一起丢失。固定延时只适合本地测试辅助，正式玩法优先使用已有实体或显式确认。

```lua
-- 服务端通知指定客户端
SendModRPCToClient(GetClientModRPC("example", "invite"), invitee.userid, inviter)

AddClientModRPCHandler("example", "invite", function(inviter)
    if inviter == nil or not inviter:IsValid() then
        return
    end
    SendModRPCToServer(GetModRPC("example", "accept"), inviter)
end)

-- 客户端请求服务端；处理器首参 player 是实际请求者
AddModRPCHandler("example", "accept", function(player, inviter)
    if type(inviter) ~= "table" or inviter.IsValid == nil or not inviter:IsValid() then
        return
    end
    -- 在服务端继续校验 inviter、player、距离、状态和权限
end)
```

禁止把一端的 `entity.GUID` 当作跨网络身份，并在另一端执行 `Ents[guid]`：

```lua
-- 错误：服务端 GUID 不能交给客户端的 Ents 查找，反向同理
SendModRPCToClient(GetClientModRPC("example", "invite"), invitee.userid, inviter.GUID)
AddClientModRPCHandler("example", "invite", function(inviter_guid)
    local inviter = Ents[inviter_guid]
end)
```

主机客户端与服务端处于同一进程，可能让这种错误在主机测试中偶然可用。因此，任何携带实体参数的双向 RPC 都必须用远端客户端复测；不要用主机通过作为 GUID 方案正确的证据。

### 预测动作 RPC

开启延迟补偿时，`preview_cb` 通常在客户端走到目标并进入预测动作时发送 RPC，但服务端权威坐标可能仍落后。处理器若立即调用带距离校验的最终函数，会被服务端拒绝，而客户端只留下预测动作动画。

让预测与非预测回调汇合到同一服务端动作入口。需要走近目标的交互应在服务端重建 `BufferedAction` 并交给 `locomotor:PushAction`，或使用对应的原版动作 RPC；在服务端动作帧再执行最终状态变更和距离校验。不要让 `preview_cb` 直接调用最终逻辑、`non_preview_cb` 却走服务端 locomotor。

服务器接收客户端请求后重新检查：

- player 或 sender 有效且存活
- 目标 Entity 有效
- 距离与平台坐标
- 物品所有权与容器状态
- 权限、PvP 和世界配置
- 冷却、资源和动作状态
- 数值范围、字符串长度和枚举
- 重复、过期和重放请求

## 测试矩阵

主机玩家、远端客户端、专服、加入中客户端、断线重连、Master、Caves、高延迟、服务器拒绝、回滚。
