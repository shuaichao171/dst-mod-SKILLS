# Action 完整链路

1. Action 定义描述执行语义。
2. ComponentAction 收集候选动作。
3. 客户端根据 Replica 显示候选。
4. BufferedAction 保存 doer、target、invobject 和 position。
5. SG ActionHandler 选择表演状态。
6. 客户端可执行预览或预测。
7. 服务器重新验证并执行 Action.fn。
8. BufferedAction 成功或失败。
9. SG 退出并清理。

## 收集阶段

SCENE 用于世界目标；USEITEM 用于手持物对目标；POINT 用于地面点；EQUIPPED 与 INVENTORY 用于装备或物品栏。每种回调签名从当前 componentactions.lua 复核。

收集函数只向 actions 插入候选。不要扣除资源、播放权威动画或改变目标。

## 常见故障

| 症状 | 检查 |
| --- | --- |
| 动作不出现 | 组件已注册、类型正确、Replica 条件 |
| 出现但点了没反应 | SG ActionHandler、状态标签、距离 |
| 主机可用客户端不可用 | Replica、netvar、客户端 SG |
| 执行两次 | 预测与服务器均产生副作用 |
| 动作后卡住 | BufferedAction 未完成、SG 无退出 |

## 收集回调签名（componentactions.lua 当前版本）

| 类型 | 回调参数 | 触发场景 |
| --- | --- | --- |
| SCENE | `inst, doer, actions, right` | 鼠标指向世界中带该组件的实体 |
| USEITEM | `inst, doer, target, actions, right` | 拿着带该组件的物品对 target 使用 |
| POINT | `inst, doer, pos, actions, right, target` | 手持物对地面点 |
| EQUIPPED | `inst, doer, target, actions, right` | 装备带该组件的物品时对 target |
| INVENTORY | `inst, doer, actions, right` | 物品栏中带该组件的物品 |
| ISVALID | `inst, action, right` | 校验某个动作当前是否仍然有效 |

- 回调在客户端也会执行，`inst` 上通常只有 replica 和标签可以用，不能访问 `inst.components`。
- 客户端能否收集到某个组件的动作，取决于服务器在 AddComponent 时登记、并同步到客户端的 action component 列表。这个组件只在客户端存在不够，服务器也必须添加它。
- `right` 为 true 表示右键收集，左右键要分别插入对应的动作。

## AddAction 与 Action 字段

- `AddAction(id, str, fn)`，或者传入一个已经构造好的 `Action({...})` 对象并设置 `id`、`str`、`fn`。它会写入 `ACTIONS[id]` 和 `STRINGS.ACTIONS[id]`，并按模组分配 `code` 用于网络传输。**id 不会自动转大写**，按原版习惯写成大写并加前缀。
- 常用构造参数（`Action({ ... })`）：`priority`、`rmb`、`distance`、`mindistance`、`instant`、`mount_valid`、`encumbered_valid`、`ghost_valid`、`ghost_exclusive`、`floating_valid`、`paused_valid`、`canforce`、`rangecheckfn`、`extra_arrive_dist`、`customarrivecheck`、`is_relative_to_platform`、`disable_platform_hopping`、`do_not_locomote`、`silent_fail`。名字和含义以当前 actions.lua 的 `Action` 构造函数为准。
- 动作文字需要随目标变化时，设置 `action.strfn = function(act) return "子键" end`，并把 `STRINGS.ACTIONS[id]` 写成表 `{ GENERIC = ..., 子键 = ... }`。
