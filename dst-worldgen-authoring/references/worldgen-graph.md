# 世界生成层级

## 层级

Location 选择森林、洞穴或其他生成环境。Level 选择 TaskSet 和覆盖参数。TaskSet 组合 Task。Task 通过锁钥图连接 Room。Room 决定地皮、内容分布和可选布局。

## 常用扩展点

- AddLocation
- AddLevel
- AddTaskSet
- AddTask
- AddRoom
- AddStartLocation
- AddTaskSetPreInit
- AddTaskPreInit
- AddRoomPreInit
- AddLevelPreInit

使用前从当前 modutil.lua 核对签名。

## 锁钥检查

每个 Task 的 keys_given 与 locks 必须形成从起始 Task 可达的图。新增锁时确认此前一定存在授予钥匙的路径。关键资源和出口不要只存在于可能被随机裁掉的分支。

## 随机与密度

Room contents 的 countstaticlayouts、distributepercent、distributeprefabs 和 countprefabs 都要有合理上限。多次使用不同种子检查稀有资源既不会缺失，也不会指数生成。

## 环境限制

modworldgenmain 运行时没有正常游戏世界、玩家和服务器 Component。只加载世界生成安全模块，避免依赖 TheWorld、ThePlayer、网络或 UI。

