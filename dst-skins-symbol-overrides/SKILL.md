---
name: dst-skins-symbol-overrides
description: Implement mod-owned appearance variants, animation build swaps, clothing and symbol overrides in Don't Starve Together. Use when changing AnimState builds, overriding symbols for equipment or forms, managing skin-like local variants, registering related atlases, or avoiding conflicts with official skin, entitlement, and trading systems.
---

# DST 外观变体与 Symbol Override

把模组自有外观变体与 Klei 官方皮肤经济分开，只实现可由模组资源和 Lua 合法控制的 Build 与 Symbol。

## 工作流

1. 定义变体影响完整 Build、单个 Symbol、装备 swap、UI 图标还是角色形态，并列出恢复目标。
2. 从原版装备和形态切换查 SetBuild、OverrideSymbol、OverrideItemSkinSymbol 与 ClearOverrideSymbol 的契约。
3. 所有外观切换使用稳定 source 或状态，进入与退出、装备与卸下、加载与重生完全对称。
4. 需要客户端看到的变体通过网络字段或已有 skin/build 数据同步，不读取服务器临时表。
5. 库存、配方、头像和世界动画分别提供正确 Atlas 或 Build 资源。
6. 如果需求涉及官方 entitlement、交易、掉落或受控皮肤发布，明确说明普通模组无法仿造该服务端体系。
7. 测试多个装备覆盖同一 Symbol、皮肤 Build 切换、变身、死亡、重连和资源缺失。

## 源码锚点

- prefabskin.lua、prefabskins.lua、prefabswaps.lua、skinsutils.lua。
- clothing.lua、beefalo_clothing.lua 与装备 Prefab。
- AnimState OverrideSymbol、ClearOverrideSymbol、SetBuild 调用点。
- skins_defs_data.lua 等只作为官方体系行为参考。

## 不变量

- 不要伪造 entitlement、交易、稀有度或官方拥有状态。
- 清除覆盖时只撤销本模组拥有的层，避免破坏其他装备或模组。
- Build 与 Symbol 名必须来自实际编译资源。
- 视觉变体不能绕过服务器玩法权限。

## 验证

- 装备、卸下、换皮肤和形态切换后符号恢复正确。
- 远端客户端看到相同变体。
- 缺少可选资源时回退基础 Build，不导致 invisible 或崩溃。

