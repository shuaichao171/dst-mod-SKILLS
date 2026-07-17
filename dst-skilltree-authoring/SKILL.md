---
name: dst-skilltree-authoring
description: Design and integrate Don't Starve Together character skill trees. Use when writing skilltree prefab data, defining skill nodes and prerequisites, activation and deactivation callbacks, locks and affinities, skilltreeupdater behavior, skill selection persistence, custom icons and backgrounds, or debugging skill-tree UI and networking.
---

# DST 技能树编写

把节点图、解锁规则、激活副作用、UI 资源和角色生命周期作为一个可逆系统设计。

## 工作流

1. 定义节点 ID、层级、连接、前置、互斥、锁、最大点数和每个节点的可观察效果。
2. 对照 prefabs/skilltree_defs.lua 与相近角色的 skilltree_*.lua，复用当前字段契约，不从旧教程猜结构。
3. 让节点激活与停用回调幂等；所有组件、标签、事件、数值和配方修改都能对称撤销。
4. 通过 skilltreeupdater 读取已激活技能，不在客户端 UI 中直接授予服务器能力。
5. 注册技能树图标和背景 Atlas，补齐名称、描述、锁定提示和控制器焦点。
6. 处理角色初始化、重选技能、重生、换洞穴、存档载入和版本删除节点的迁移。
7. 测试零点数、满点、非法组合、旧存档技能、多人同步和不同分辨率 UI。

## 源码锚点

- skilltreedata.lua、prefabs/skilltree_defs.lua：技能树注册与公共定义。
- prefabs/skilltree_*.lua：角色节点范例。
- components/skilltreeupdater.lua：角色侧更新。
- widgets/redux/skilltreewidget.lua、skilltreebuilder.lua 与 skilltreepanel.lua：UI。
- modutil.lua：RegisterSkilltreeBGForCharacter、RegisterSkilltreeIconsAtlas。

## 不变量

- 节点 ID 一旦进入存档应视为稳定标识。
- 客户端选择必须由服务器校验可用点数、前置和互斥。
- 激活回调不能因重载或重复同步叠加数值。
- 删除或重命名节点前提供旧存档迁移。

## 验证

- 合法图可从根节点遍历，且不存在意外孤立或循环依赖。
- 激活、停用和重新载入产生相同最终状态。
- 非法客户端选择不会改变服务器角色。

