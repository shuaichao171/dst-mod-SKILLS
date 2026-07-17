---
name: dst-persistence-migration
description: Implement durable Don't Starve Together save and load behavior. Use when writing OnSave, OnLoad, LoadPostPass, GetPersistData, SetPersistData, LongUpdate, versioned component data, entity references, save upgrades, retrofit logic, or fixing state lost after rollback, unload, or world migration.
---

# DST 存档、加载与迁移

只保存恢复玩法状态所需的稳定数据，并让旧版本、缺字段和实体重建顺序都可安全处理。

## 工作流

1. 列出必须跨重启保存的字段、可从当前世界推导的字段、临时缓存和外部实体引用。
2. 为数据添加显式 schema 版本；Component:OnSave 的第一个返回值只放可序列化数据，必要时第二个返回值提供实体 refs。Prefab 的 inst.OnSave(inst, data) 写入传入的 data 表，并可返回 refs。
3. OnLoad 接受 nil、缺字段、旧枚举和非法范围，先迁移再应用默认值。
4. 对每个实体引用，在保存数据中保留稳定 GUID 映射并通过 OnSave 的 refs 让引擎收集对象；在 LoadPostPass(newents, data) 解析，目标缺失时降级，不持有旧 EntityScript。
5. 实现 LongUpdate 时按离线时间推进腐败、计时或生长，但对负值、极大值和暂停规则做限制。
6. 改变世界生成或世界组件时区分新世界配置、旧存档 Retrofit 与 Component 或 Prefab 在 OnLoad 中执行的一次性 schema 迁移。不要假设存在可供模组调用的统一存档升级钩子。
7. 在保存、载入、回滚、关服重启、换分片和删除关联实体场景验证。

## 源码锚点

- entityscript.lua：GetSaveRecord、GetPersistData、SetPersistData、LoadPostPass 和 LongUpdate。
- components/ 与 prefabs/ 中的 OnSave、OnLoad、LoadPostPass 范例。
- savefileupgrades.lua：内置存档格式升级实现，不是模组公开钩子；worldsettings_overrides.lua、map/retrofit_savedata.lua：世界设置与 Retrofit。

## 不变量

- 不要保存函数、userdata、任务句柄、组件对象或 EntityScript。
- 不要假设 OnLoad 时其他实体和世界组件已全部可用。
- 不要因为字段缺失就删除整个旧存档状态。
- 迁移必须幂等；多次加载同一版本不会重复发奖励或重复生成实体。

## 验证

- 新存档和至少一个模拟旧 schema 都能恢复。
- 关联实体存在、缺失和被替换三种情况均安全。
- 回滚后不会因外部副作用或重复迁移产生额外状态。

## 按需资源

- 需要数据边界、引用恢复和迁移顺序时读取 references/persistence-contract.md。
