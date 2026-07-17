---
name: dst-inventory-equipment-containers
description: Build Don't Starve Together inventory items, equipment, stacks, durability, fuel, perishables, armor, and containers. Use when creating or modifying inventoryitem, equippable, stackable, finiteuses, fueled, perishable, container, container_replica, inventory UI, equip symbols, or item ownership behavior.
---

# DST 物品、装备与容器

围绕物品在地面、物品栏、容器、装备栏和移除阶段的状态转换组织实现。

## 工作流

1. 选择最接近的原版物品，列出地面物理、拾取、堆叠、装备、耐久、燃料、腐败和容器需求。
2. 在 SetPristine 前建立库存图标、标签和客户端所需网络状态；主机分支添加 inventoryitem 等组件。
3. 配置 stackable、finiteuses、fueled、perishable、weapon、armor 或 tool，并明确耗尽、熄灭、腐败和破损回调。
4. equippable 的 onequip 与 onunequip 对称处理 SymbolOverride、速度、伤害、防护、标签和跟随 FX。
5. 容器同时配置 containers.lua 的 widgetsetup、槽位、过滤规则、open/close 回调和 container_replica 可见性。
6. 处理进入库存、掉落、转移容器、角色死亡、堆叠合并、皮肤 Build 和实体移除。
7. 测试鼠标与手柄、远端客户端、满容器、不可接受物品和保存重载。

## 源码锚点

- components/inventoryitem.lua、inventory.lua、stackable.lua、equippable.lua。
- components/finiteuses.lua、fueled.lua、perishable.lua、weapon.lua、armor.lua。
- components/container.lua、container_replica.lua 与 containers.lua。
- widgets/inventorybar.lua、containerwidget.lua、itemtile.lua。

## 不变量

- 装备和卸下必须恢复完全对称的状态。
- 容器过滤在服务器最终校验，客户端 UI 只是预览。
- 不要让堆叠物品保存每个单件不一致的隐藏状态，除非设计明确禁止堆叠。
- 物品进入 Limbo 或容器时停止不应继续的世界任务与物理效果。

## 验证

- 地面、库存、容器、装备、堆叠拆分和角色死亡路径均正确。
- 耐久、燃料和腐败只结算一次。
- 远端客户端的槽位、图标、可用动作和服务器状态一致。

