# Component 与 Replica 契约

## Component 责任

Component 保存服务器权威状态并提供稳定方法。根据需求实现：

- OnSave 与 OnLoad
- LoadPostPass
- LongUpdate
- OnUpdate
- OnRemoveFromEntity
- GetDebugString

优先事件或低频任务。只有必须连续模拟时才使用 OnUpdate。

## Replica 责任

Replica 只向客户端提供动作发现、UI 或预测所需的最小只读接口。典型流程：

1. 在相关实体实例化前从 modmain.lua 调用 AddReplicableComponent。
2. 创建 scripts/components/name_replica.lua。
3. Prefab 在 SetPristine 后的主机分支调用 AddComponent。
4. AddComponent 先调用 ReplicateComponent；Replica 构造函数可在此时创建 netvar，然后才构造服务器 Component。
5. 服务器 Component 更新 Replica。
6. 客户端收到实体初始复制标签后构造 Replica，并通过 inst.replica.name 读取。

Prefab 直接创建的 inst._foo = net_* 应放在 SetPristine 前；Replica 自己的网络字段遵循上述 ReplicateComponent 生命周期，不要为了满足错误的统一顺序而在 Prefab 中重复创建。

## 保存边界

可保存数字、字符串、布尔值和普通表。不要保存 EntityScript、组件、函数、任务、userdata 或循环表。实体引用通过保存记录和 LoadPostPass 恢复。

## 移除边界

停止组件更新，取消任务，并解除由该组件注册的跨实体事件。Replica 不支持与服务器 Component 完全相同的移除生命周期，设计时要从当前原版实现复核。
