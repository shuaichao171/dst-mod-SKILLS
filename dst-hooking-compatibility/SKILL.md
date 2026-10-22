---
name: dst-hooking-compatibility
description: Extend Don't Starve Together code through supported hooks and compatibility-safe wrappers. Use when applying prefab, component, brain, stategraph, recipe, player, class, or widget post-inits, wrapping methods, coordinating multiple mods, or replacing fragile direct overrides.
---

# DST 钩子与兼容性补丁

优先使用公开 PostInit 与注册 API，把修改做成可组合、幂等且能检测失效的补丁。

## 工作流

1. 确定修改对象及其创建时机，选择最窄的 AddPrefabPostInit、AddComponentPostInit、AddBrainPostInit、AddStategraphPostInit、AddClassPostConstruct 或 AddGlobalClassPostConstruct；世界级一次性初始化用 AddSimPostInit，启动级用 AddGamePostInit。
2. 玩家初始化优先用 AddComponentPostInit 挂在玩家专属组件上：playervision 用于所有端与 netvar，playerlightningtarget 用于服务器权威组件，playercontroller 用于本机输入。只有这些时机满足不了需求时（例如必须等角色 master_postinit 执行完、并且要在同步阶段拿到完整构造的实例），才用 AddPlayerPostInit 或 AddPrefabPostInitAny。前者只是后者加 HasTag("player")，生成任意实体时都会在所有端执行，使用时要说明为什么需要这个时机。时机和取舍见 references/post-init-hooks.md。
3. 读取 modutil.lua 中对应钩子的调用顺序、参数和作用域，再检查目标原版实现。
4. 只修改所需字段或方法；包装函数时保存旧函数，原样转发 self、可变参数和多返回值。
5. 为重复加载或多个 Prefab 实例添加幂等标记，但不要在共享类表上误用实例标记。
6. 对可选组件、其他模组字段和版本差异做 nil 检查与特性检测。
7. UI、事件和任务钩子记录清理路径；实体或 Widget 移除时解除监听。
8. 使用至少两个加载顺序测试本模组与可能冲突的模组。

## 源码锚点

- modutil.lua：全部官方 Add 开头钩子与注册函数。
- mods.lua：模组初始化、优先级和环境。
- entityscript.lua：组件、事件与移除生命周期。
- widgets/、screens/：ClassPostConstruct 常见目标。

## 不变量

- 不要编辑或复制覆盖 data/scripts 原文件。
- 不要为了一个实例修改所有实例共享的类方法，除非需求明确如此。
- 不要吞掉原函数返回值、错误或副作用。
- 无法安全组合的硬替换必须显式说明冲突范围。
- AddPrefabPostInitAny / AddPlayerPostInit 不作为默认入口：其他钩子能满足需求时就用其他钩子；只有确实需要它们的时机时才使用，回调里先做最便宜的判断再提前返回。审查时，其他钩子就能实现的用法列为性能问题，确实依赖该时机的用法不算问题。

## 验证

- 单独启用、重复初始化和不同加载顺序均不会重复注册。
- 原版行为在未命中新增条件时保持不变。
- 更新后若目标字段或签名改变，补丁能给出明确失败信息。

## 按需资源

- 需要全局 PostInit 时机、玩家初始化挂载点或 GlobalClassPostConstruct 用法时读取 references/post-init-hooks.md。
