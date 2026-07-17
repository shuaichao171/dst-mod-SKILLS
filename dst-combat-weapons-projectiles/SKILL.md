---
name: dst-combat-weapons-projectiles
description: Implement Don't Starve Together combat, targeting, weapons, armor, damage types, planar damage, projectiles, area attacks, and hit effects. Use when modifying combat or health components, attack periods and ranges, damage calculation, hostility, friendly fire, ranged attacks, complexprojectile behavior, or combat stategraphs.
---

# DST 战斗、武器与弹道

由服务器计算命中与伤害，由 SG 控制攻击时序，客户端只表现可复制结果。

## 工作流

1. 定义攻击者、合法目标、阵营、射程、攻击周期、基础伤害、伤害类型、位面数值和友伤规则。
2. 配置 combat、health、weapon、armor、planardamage、planardefense、damagetypebonus 或 damagetyperesist。
3. 让 Brain 选择目标，SG 在正确帧调用攻击，Component 负责数值；避免三处重复实现命中规则。
4. 投射物明确发射者、目标或落点、速度、命中/错过/移除回调、平台坐标和重新瞄准规则。
5. 范围伤害用带标签过滤的有限半径查询，排除攻击者、盟友、无效和不可交互实体。
6. 把声音、FX、震屏与服务器伤害分离，确保预测或 dirty 回调不重复造成伤害。
7. 测试无甲/有甲、位面防御、骑乘、睡眠、冰冻、平台、目标死亡和多个攻击者。

## 源码锚点

- components/combat.lua、health.lua、weapon.lua、armor.lua。
- components/planardamage.lua、planardefense.lua、damagetypebonus.lua、damagetyperesist.lua。
- components/projectile.lua、complexprojectile.lua 及投射物 Prefab。
- brains/ 与 stategraphs/ 中同类攻击者范例。

## 不变量

- 客户端不得决定命中、伤害、掉落或耐久消耗。
- DoAttack、GetAttacked 和直接 DoDelta 路径不可无意叠加。
- 范围查询必须限制半径、标签与触发频率。
- 投射物所有退出路径都必须清理任务、拖尾和命中状态。

## 验证

- 不同防御、伤害类型和 PvP 设置下结果符合公式。
- 高延迟和目标快速移动时不会双重命中。
- 投射物命中、落空、被移除和跨平台路径均结束干净。

