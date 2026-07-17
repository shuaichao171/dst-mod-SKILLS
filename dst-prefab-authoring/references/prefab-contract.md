# Prefab 构造契约

## 固定顺序

1. CreateEntity。
2. 添加 Transform、AnimState、Physics、Network 等原生子系统。
3. 设置客户端必须立即知道的动画、标签和 Prefab 直接创建的 netvar。
4. 调用 SetPristine。
5. 非主机立即返回。
6. 主机添加普通 Component、Brain、SG、保存和权威事件；已注册的可复制 Component 会先构造 Replica。
7. 返回 Prefab。

## 判断放置位置

| 内容 | SetPristine 前 | 主机分支 |
| --- | --- | --- |
| Network、Prefab 直接创建的 netvar | 是 | 否 |
| 可复制 Component 的 Replica netvar | 由 ReplicateComponent 创建 | AddComponent 可触发 |
| 客户端动画初值 | 是 | 否 |
| 客户端动作所需标签 | 是 | 否 |
| 普通 Component | 否 | 是 |
| Brain 与服务器 SG | 否 | 是 |
| 掉落、伤害、计时 | 否 | 是 |
| OnSave、OnLoad | 否 | 是 |

## 原生子系统

Entity:AddAnimState、AddPhysics、AddLight、AddFollower、AddVFXEffect 等可能没有 Lua 定义。用同类 Prefab 调用点确认顺序与参数。不要把 Inventory 物理套给建筑或角色。

## 生命周期

检查以下路径是否需要处理：

- OnEntitySleep 与 OnEntityWake
- inst.OnSave、inst.OnLoad、inst.OnLoadPostPass、inst.OnLongUpdate
- OnRemoveEntity
- 进入和离开库存
- 装备和卸下
- 燃烧、冻结、工作和死亡
- 子实体、任务、事件与循环声音清理
