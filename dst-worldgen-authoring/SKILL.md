---
name: dst-worldgen-authoring
description: Create Don't Starve Together world-generation content. Use when writing modworldgenmain.lua, adding or modifying task sets, tasks, rooms, levels, locations, start locations, topology locks and keys, world customization options, or debugging generation failures and disconnected maps.
---

# DST 世界生成图编写

在独立的世界生成环境中组合 Location、Level、TaskSet、Task 与 Room，并用可达性约束验证拓扑。

## 工作流

1. 确认内容属于森林、洞穴或自定义 Location，并确定只影响新世界还是也需要旧世界 Retrofit。
2. 在 modworldgenmain.lua 使用 AddTaskSet、AddTask、AddRoom、AddLevel、AddLocation 或对应 PreInit 钩子。要覆盖所有森林或洞穴世界时用 AddLevelPreInitAny 加 level.location 判断，因为自定义预设的 level.id 不一定等于原版预设 id；AddTaskSetPreInitAny 收到的是当前 TaskSet 的拷贝。
3. 从 map/tasksets、tasks、rooms 和 levels 中选择最接近范例，保持 Room distribution、Task keys/locks 与 TaskSet 顺序一致。
4. 用锁钥图表达拓扑依赖，检查每个关键资源、起点和出口均可从起始区域到达。
5. 世界生成逻辑只使用该环境可用的数据与函数，不依赖 TheWorld、玩家或运行时组件。
6. 配置自定义选项时把 modinfo 选项转换为生成参数，并提供合法默认值和未知值回退。需要在建服的世界设置页面里调节时，用 AddCustomizeGroup、AddCustomizeItem 注册带前缀的选项（GetCustomizeDescription 复用原版描述，RemoveCustomizeItem/Group 隐藏选项）；世界生成阶段读 level.overrides，运行时在服务器读 TheWorld.topology.overrides，两处都要处理 nil。
7. 多次用不同种子生成森林和洞穴，检查生成日志、连通性、资源密度与性能。

## 源码锚点

- worldgen_main.lua、map/levels.lua、map/tasksets.lua、map/tasks.lua、map/rooms.lua。
- map/lockandkey.lua、storygen.lua、graphnode.lua、graphedge.lua。
- map/levels/、tasksets/、tasks/、rooms/。
- modutil.lua：世界生成 Add 与 PreInit API。

## 不变量

- 世界生成入口不能调用依赖运行中世界、网络或 UI 的代码。
- 不要修改共享表后忘记复制，避免影响后续生成或其他模组。
- Room 权重、数量和随机选择必须有上限。
- 影响旧存档的需求不要伪装成新世界生成修改。

## 验证

- 至少多个种子能完成生成且无锁钥不可达。
- 森林、洞穴和禁用相关配置的组合均按预期。
- 世界生成失败时日志能定位到自定义 Task、Room 或布局。

## 按需资源

- 需要层级与锁钥关系时读取 references/worldgen-graph.md。
- 注册世界设置选项或使用 LevelPreInitAny、TaskSetPreInitAny 时读取 references/world-options-preinit.md。

