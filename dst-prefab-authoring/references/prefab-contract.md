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

## standardcomponents.lua 常用装配函数的位置

原版 Prefab 的固定写法：物理和带 `Pristine` 后缀的函数放在 SetPristine **之前**（所有端），其余放在主机分支。

| 函数 | 位置 | 说明 |
| --- | --- | --- |
| `MakeInventoryPhysics`、`MakeCharacterPhysics`、`MakeObstaclePhysics`、`MakeSmallObstaclePhysics`、`MakeFlyingCharacterPhysics`、`MakeGhostPhysics` 等 | SetPristine 前 | 物理需要在所有端存在 |
| `MakeInventoryFloatable(inst, size, offset, scale, swap_bank, float_index, swap_data)` | SetPristine 前 | 添加 `floater` 组件，负责水面漂浮表现（参见 axe.lua、log.lua） |
| `MakeSnowCoveredPristine`、`MakeSmallPerishableCreaturePristine`、`MakeFeedableSmallLivestockPristine`、`MakeDeployableFertilizerPristine` | SetPristine 前 | 名字带 `Pristine` 的是公共部分 |
| `MakeSnowCovered`、`MakeSmallPerishableCreature`、`MakeFeedableSmallLivestock` | 主机分支 | 对应 Pristine 版本的主机部分（`MakeSnowCovered` 也会自动补上 Pristine 部分） |
| `MakeSmall/Medium/LargeBurnable`、`MakeSmall/Medium/LargePropagator`、`Make*BurnableCharacter` | 主机分支 | 燃烧与火焰传播 |
| `Make*FreezableCharacter` | 主机分支 | 冰冻 |
| `MakeHauntable`、`MakeHauntableLaunch`、`MakeHauntableLaunchAndIgnite`、`MakeHauntableWork`、`MakeHauntablePerish` 等 | 主机分支 | 鬼魂作祟反应；可作祟物品几乎都会调用其中一个 |

用到时到 standardcomponents.lua 查看具体实现和参数，不要凭名字猜默认值。
