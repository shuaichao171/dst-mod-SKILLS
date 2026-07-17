# StateGraph 契约

## 状态责任

State 负责短期、可中断的动作与动画时序。持久数值、阶段和冷却放 Component 或 Prefab。

## 状态结构

- name 必须在该 SG 内唯一。
- tags 描述当前能力，不是永久实体标签。
- onenter 设置动画、移动、timeout 和 statemem。
- timeline 在明确帧执行服务器副作用。
- events 处理 animover、timeout、attacked 等。
- onexit 撤销进入时创建的临时状态。

临时数据放 inst.sg.statemem。不要依赖 onexit 只在动画自然结束时调用。

## 玩家预测

自定义玩家动作同时检查：

- SGwilson 的服务器 ActionHandler
- 客户端玩家 SG
- 动作预览和 BufferedAction
- ServerStateMatches
- 服务器拒绝后的复位

伤害、消耗、生成和掉落只在服务器发生。

## 对称清理

进入时改变以下内容，退出时必须恢复：

- locomotor 和 Physics
- 控制锁与 state tag
- 碰撞和无敌
- 颜色、Bloom、Light
- 循环声音与 FX
- 任务和跨实体事件

