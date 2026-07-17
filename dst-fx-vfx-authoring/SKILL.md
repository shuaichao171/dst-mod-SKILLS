---
name: dst-fx-vfx-authoring
description: Create Don't Starve Together visual effects and particle systems. Use when building FX prefabs, AnimState effects, follower effects, trails, light and bloom, colour adders, VFXEffect particles, reveal or additive blending, effect lifetimes, or separating local visuals from replicated gameplay state.
---

# DST FX 与 VFX 编写

先选择普通 AnimState FX、跟随特效、Light 或 VFXEffect 管线，再设计生命周期和联机可见性。

## 工作流

1. 定义效果触发、持续时间、空间、跟随对象、可见玩家、混合方式、光照和是否承载玩法判定。
2. 普通序列帧优先使用轻量 FX Prefab；符号跟随使用 Follower；大批粒子才使用 VFXEffect。
3. 纯表现且每个客户端都能从相同事件推导时本地生成；必须同步触发时由服务器复制最小事件或 Prefab。
4. 用 animover、任务或发射器完成条件移除；循环效果绑定拥有者并在其移除、睡眠或状态结束时清理。
5. Bloom、ColourAdder、Light 和声音保存原状态或使用独立子实体，避免污染目标其他效果。
6. 自定义 VFX shader、sampler 或 uniform 时转用 dst-shader-authoring 的管线契约。
7. 测试屏幕外睡眠、快速重复触发、大量实体、暂停、低特效设置和拥有者删除。

## 源码锚点

- fx.lua 与 prefabs/ 中 *_fx、粒子和拖尾 Prefab。
- emitters.lua、components/bloomer.lua、colouradder.lua。
- Entity:AddFollower、AddLight、AddVFXEffect 的原版调用点。
- dst-shader-authoring：自定义 VFXEffect shader。

## 不变量

- 视觉特效不得成为服务器伤害或命中判定的唯一来源。
- 循环 FX 必须有所有者和确定的停止路径。
- 客户端本地 FX 不创建可保存的权威实体。
- 高频效果避免 Network 实体、全局扫描和无限粒子。

## 验证

- 效果正常结束、中断和拥有者移除时无残留。
- 远端客户端看到正确次数，不因预测和服务器事件双重生成。
- 大量同时触发时帧率和实体数量可接受。

