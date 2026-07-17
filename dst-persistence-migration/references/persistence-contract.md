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
