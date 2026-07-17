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
2. 创建 netvar 或让 Replica 创建 netvar。
3. 添加客户端所需标签和视觉初值。
4. SetPristine。
5. 非主机返回。
6. 主机添加 Component 和权威逻辑。

## RPC 校验

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

