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

1. 在 modmain.lua 调用 AddReplicableComponent。
2. 创建 scripts/components/name_replica.lua。
3. Replica 构造函数创建 netvar。
4. 服务器 Component 更新 Replica。
5. 客户端通过 inst.replica.name 读取。
6. SetPristine 前不得遗漏网络字段的创建。

## 保存边界

可保存数字、字符串、布尔值和普通表。不要保存 EntityScript、组件、函数、任务、userdata 或循环表。实体引用通过保存记录和 LoadPostPass 恢复。

## 移除边界

停止组件更新，取消任务，并解除由该组件注册的跨实体事件。Replica 不支持与服务器 Component 完全相同的移除生命周期，设计时要从当前原版实现复核。

