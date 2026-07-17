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

