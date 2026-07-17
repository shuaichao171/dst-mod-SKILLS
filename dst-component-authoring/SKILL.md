---
name: dst-component-authoring
description: Design and implement Don't Starve Together Lua components and replicas. Use when creating scripts/components files, defining reusable entity state and methods, adding updates, events, save/load behavior, component actions, client replicas, or reviewing a component lifecycle.
---

# DST Component 与 Replica 编写

把权威玩法状态封装在服务器 Component；只有客户端确实需要读取或预测时才增加 Replica。

## 工作流

1. 先写出组件责任、所有者 Prefab、公开方法、事件输入输出和需要持久化的最小状态。
2. 在 scripts/components/name.lua 中使用 Class 构造组件，保存 inst，并让字段默认值可安全重载。
3. 通过 StartUpdatingComponent、任务或事件三者中成本最低的机制驱动更新；静态实体避免每帧 OnUpdate。
4. 实现必要的 OnSave、OnLoad、LoadPostPass、LongUpdate、OnRemoveFromEntity 和 GetDebugString。
5. 在 Prefab 的主机分支 AddComponent；修改原版组件时优先 AddComponentPostInit。
6. 客户端需要状态或方法时创建 name_replica.lua，并在相关实体实例化前从 modmain.lua 调用 AddReplicableComponent。Replica 可在构造函数中创建 netvar；服务器 AddComponent 会先调用 ReplicateComponent，再构造服务器 Component。
7. 若组件参与动作，注册正确类型的 AddComponentAction，并保持客户端收集动作与服务器执行条件一致。

## 源码锚点

- components/：组件实现及生命周期范例。
- entityscript.lua：AddComponent、更新注册、保存和事件。
- entityreplica.lua、components/*_replica.lua：Replica 装载和接口模式。
- componentactions.lua、modutil.lua：组件动作与注册 API。

## 不变量

- Component 默认属于主机；不要让客户端直接依赖 inst.components。
- 保存纯数据，不保存 EntityScript、任务句柄、函数或循环引用。
- OnUpdate、事件和任务必须能在组件移除后停止。
- Replica 只暴露客户端需要的信息，不复制整个服务器对象。
- 变更现有组件字段前先确认字段是实例字段而非共享类状态。

## 验证

- 组件可添加、移除和重复加载，不残留更新或事件监听。
- 保存/读取与 LongUpdate 后状态合法，旧数据缺字段时有默认值。
- 远端客户端读取 Replica 时不会访问未复制的服务器字段。

## 按需资源

- 复制 assets/component-template.lua 和 assets/replica-template.lua。
- 需要生命周期与复制边界时读取 references/component-contract.md。
