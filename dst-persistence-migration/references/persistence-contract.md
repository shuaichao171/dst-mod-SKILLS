# 持久化契约

## 数据分类

| 类型 | 处理 |
| --- | --- |
| 可推导缓存 | 不保存，加载后重建 |
| 数值与布尔状态 | OnSave 返回普通数据 |
| 枚举 | 保存稳定字符串或版本化数值 |
| 实体引用 | 在 data 保存 GUID 映射；Component:OnSave 返回第二个 refs 值或 Prefab OnSave 返回 refs；Component:LoadPostPass 或 Prefab OnLoadPostPass 用 newents 恢复 |
| 任务 | 保存剩余时间，不保存任务句柄 |
| 函数与组件 | 不保存 |

## 加载顺序

OnLoad 不能假设关联实体已存在。先恢复本实体纯数据；需要其他实体时在 data 保存 GUID 映射，并从 OnSave 返回 refs 让引擎建立 newents。Component 随后在 LoadPostPass(newents, savedata) 解析；Prefab 则设置 inst.OnLoadPostPass，回调签名为 (inst, newents, savedata)。目标缺失时清空引用或执行明确降级。

## Schema 迁移

保存 schema_version。迁移从旧版本逐步升级，且每一步幂等。未知未来版本不要擅自降级覆盖。

## LongUpdate 与 OnLongUpdate

Component 实现 LongUpdate(dt)；Prefab 设置 inst.OnLongUpdate，回调签名为 (inst, dt)。两者都要明确离线时间是否影响：

- 腐败和燃料
- 生长和再生
- 冷却和 Buff
- 世界事件
- 玩家离线时应暂停的状态

限制极端时间值，并确保在线推进与 LongUpdate 结果兼容。

## 回滚

回滚会再次执行存档内尚未记录完成的动作。奖励、生成和一次性 Retrofit 要先设计幂等标识和原子顺序。

## 引擎调用顺序（entityscript.lua）

保存 `GetPersistData`：

1. 遍历 `self.components`，调用每个组件的 `cmp:OnSave()`，返回 `data, refs`。**只有返回非空表时才会写入 `data[组件名]`**。
2. 调用 `inst.OnSave(inst, data)`，它可以往同一张 data 表里写字段，并返回 refs。
3. data 和 refs 都为空时，这个实体不产生持久化数据。

加载 `SetPersistData(data, newents)`：

1. 处理 `add_component_if_missing`：带这个标记的组件数据会先 `AddComponent`。
2. `inst.OnPreLoad(inst, data, newents)`：在任何组件加载之前执行。
3. 用 `pairs` 遍历 data，对每个组件调用 `cmp:OnLoad(data[组件名], newents)`。**组件之间的加载顺序不确定**，不要依赖另一个组件已经加载完。
4. `inst.OnLoad(inst, data, newents)`。
5. 全部实体都加载完后，`LoadPostPass`：先调用每个组件的 `cmp:LoadPostPass(newents, data[组件名])`，再调用 `inst.OnLoadPostPass(inst, newents, data)`。

由此得到的规则：

- 组件 `OnSave` 返回空表或 `nil` 时，加载时**不会调用这个组件的 `OnLoad`**。默认值必须在构造函数里设置好，不能指望 OnLoad 来补。
- 运行时才动态添加的组件（Prefab 构造函数里没有添加），在 OnSave 返回的表里加上 `add_component_if_missing = true`，加载时就会自动重新添加。原版 `debuffable`、`deathloothandler` 就是这样做的。没有这个标记的话，下次加载时这个组件不存在，它的数据会被静默丢弃。
- **模组自己定义的组件，非必要不要使用 `add_component_if_missing`**。加载时它会调用 `AddComponent`，进而执行 `require("components/<名字>")`（entityscript.lua 的 `LoadComponent`）。玩家关闭模组后，这个文件就不存在了，require 会直接报错，带这条数据的存档将无法加载，相当于存档被损坏。不加这个标记时，缺少的组件数据只会被跳过，存档仍然可以进入。
  - 替代做法：在 Prefab 构造函数或 PostInit 里固定添加组件；或者让 Prefab 的 `inst.OnSave` / `inst.OnLoad` 保存一个标记，加载时由自己的代码判断后再 `AddComponent`。这两种方式在模组关闭后都不会执行，也就不会出错。
  - 给**原版组件**加这个标记是安全的（原版组件文件一直存在），只是要接受：模组关闭后，这个组件仍会随存档被重新添加。
- `inst.persists = false` 的实体不会被世界保存。世界只保存顶层实体：要有 Transform、没有 `entity:GetParent()`，并且 `IsValid()`。用 `SetParent` 挂在别的实体下的子实体、库存里的物品，都要由父实体或对应组件（inventory、container）负责保存和重建。
