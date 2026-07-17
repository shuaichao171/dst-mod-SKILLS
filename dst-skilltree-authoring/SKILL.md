---
name: dst-skilltree-authoring
description: Design and integrate Don't Starve Together character skill trees. Use when writing skilltree prefab data, defining skill nodes and prerequisites, activation and deactivation callbacks, locks and affinities, skilltreeupdater behavior, skill selection persistence, custom icons and backgrounds, or debugging skill-tree UI and networking.
---

# DST 技能树编写

把节点图、解锁规则、激活副作用、UI 资源和角色生命周期作为一个可逆系统设计。

## 工作流

1. 定义稳定节点 ID、root、connects、locks、tags、互斥、点数成本和每个节点的可观察效果。
2. 对照 prefabs/skilltree_defs.lua 与相近角色的 prefabs/skilltree_*.lua，复用当前字段契约，不从旧教程猜结构。
3. 调用 CreateSkillTreeFor 注册节点，再显式写入该角色的 SKILLTREE_ORDERS、BACKGROUND_SETTINGS，并按需写入 CUSTOM_FUNCTIONS。
4. 让 onactivate 与 ondeactivate 幂等且对称；这些回调由服务器 skilltreeupdater 执行。客户端表现监听 onactivateskill_client 与 ondeactivateskill_client，不在 UI 中授予权威能力。
5. 注册技能树图标和背景 Atlas，补齐名称、描述、锁定提示，并指定恰好一个 defaultfocus 供控制器初始聚焦。
6. 处理角色初始化、重选技能、重生、换洞穴、存档载入和版本删除节点的迁移。
7. 检查 CreateSkillTreeFor 的 FIXME 输出，再测试零点数、满点、非法组合、旧存档技能、多人同步和不同分辨率 UI。

## 注册契约

在普通运行时入口中先加载公共定义，再按当前源码公开的表完成注册：

    local defs = require('prefabs/skilltree_defs')
    defs.CreateSkillTreeFor(characterprefab, skills)
    defs.SKILLTREE_ORDERS[characterprefab] = orders
    defs.SKILLTREE_METAINFO[characterprefab].BACKGROUND_SETTINGS = background_settings
    if custom_functions ~= nil then
        defs.CUSTOM_FUNCTIONS[characterprefab] = custom_functions
    end

CreateSkillTreeFor 为非 lock_open、非 infographic 节点从 rpc_id 0 开始编号。当前代码在计数达到 32 时就打印 TOO MANY，且引擎目前只使用第一个 32-bit 槽处理初次选择与其他玩家检查数据；把需要联网的技能节点控制在 32 个以下作为安全目标。

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
- 恰好一个节点设置 defaultfocus；每个普通节点必须是 root，或可由 connects、locks 关系接入，避免浮空节点和无效锁关系。

## 验证

- 合法图可从根节点遍历，且不存在意外孤立或循环依赖。
- 激活、停用和重新载入产生相同最终状态。
- 非法客户端选择不会改变服务器角色。
- 联网节点数低于当前警告阈值，且 CreateSkillTreeFor 不输出 defaultfocus、FLOATING、connects 或 locks 诊断。
