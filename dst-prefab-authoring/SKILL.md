---
name: dst-prefab-authoring
description: Create and modify Don't Starve Together prefab entities. Use when writing scripts/prefabs files, adding Entity subsystems, AnimState, Physics, Network, tags, components, placers, inventory items, structures, creatures, FX, or fixing SetPristine and master-simulation ordering.
---

# DST Prefab 编写

按实体构造、网络可见部分、SetPristine、主机逻辑和持久化的固定顺序编写 Prefab。

## 工作流

1. 在 prefabs/ 中寻找同类别原版实体，比较至少一个简单范例和一个拥有相同网络或持久化需求的范例。
2. 声明 Asset、PrefabFiles 依赖和局部回调；创建 Entity，并按需求添加 Transform、AnimState、SoundEmitter、Physics、Network、Light、Follower 或 VFXEffect。
3. 在 SetPristine 前完成客户端必须立即看到的标签、AnimState 初值、直接挂在实体上的网络变量和原生 Entity 子系统。
4. 调用 inst.entity:SetPristine()，随后在 not TheWorld.ismastersim 分支立即返回客户端实例。
5. 仅在主机分支添加普通 Component、Brain、服务器 SG、掉落、计时、保存和权威事件逻辑。
6. 为 inst.OnSave、inst.OnLoad、inst.OnLoadPostPass、inst.OnLongUpdate、inst.OnRemoveEntity、inst.OnEntitySleep 和 inst.OnEntityWake 明确生命周期责任；不要把 Component 的 LoadPostPass 或 LongUpdate 方法名直接用作 Prefab 回调字段。
7. 返回 Prefab；需要放置时同时创建 Placer，并在 modmain.lua 注册 PrefabFiles 与 Assets。

## 源码锚点

- prefabutil.lua、standardcomponents.lua、physics.lua：Placer、常用物理和标准装配函数。
- entityscript.lua：AddComponent、事件、任务、Brain、SG、保存与移除。
- prefabs/：按 inventory item、structure、creature、fx 等同类实体搜索。
- entityreplica.lua、components/*_replica.lua：客户端可见接口。

## 不变量

- Network、Prefab 直接创建的 netvar 和客户端所需初始标签必须在 SetPristine 前建立；可复制 Component 的 Replica 可由主机分支中的 AddComponent 触发构造。
- 普通服务器 Component 不要在客户端分支访问；客户端读取 Replica 或网络变量。
- 不要仅凭方法名猜引擎原生参数；从多个 Prefab 调用点验证。
- 所有周期任务、事件监听和子实体都要有明确清理路径。
- 客户端视觉回调不得修改权威玩法状态。

## 验证

- 主机、专服客户端和洞穴分片都能生成实体且无 nil。
- 远端客户端能看到初始状态与后续 dirty 更新。
- 保存重载、离开加载范围、堆叠/装备/燃烧等目标生命周期保持正确。

## 按需资源

- 复制 assets/prefab-template.lua 作为网络 Prefab 起点。
- 需要构造顺序、范例选择，或 standardcomponents 装配函数应放在 SetPristine 前还是主机分支时读取 references/prefab-contract.md。
