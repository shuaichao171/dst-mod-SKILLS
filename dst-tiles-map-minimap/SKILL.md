---
name: dst-tiles-map-minimap
description: Create Don't Starve Together ground tiles, turf, map and minimap assets, map icons, render ordering, and map discovery behavior. Use when calling RegisterTileRange or AddTile, defining tile and minimap properties, adding turf items, registering atlases, or integrating custom entities with the map and minimap.
---

# DST 地皮、地图与小地图

同时维护地皮 ID、世界渲染、Minimap 渲染、Turf 物品和世界生成引用的一致性。

## 工作流

1. 确定需求是地面 Tile、可铺 Turf、地图图标、Minimap Tile 还是 MapExplorer/MapReveal 行为。
2. 为自定义 Tile 注册唯一范围；RegisterTileRange 要求 range_end - range_start 至少为 256，再用 AddTile 提供 tile_data、ground_tile_def、minimap_tile_def 和 turf_def。
3. 把自定义 Tile 的 RegisterTileRange 与 AddTile 注册放入 modworldgenmain.lua。mods.lua 在普通运行时会先加载该入口再加载 modmain.lua，而世界生成会跳过 modmain.lua；不要在两个入口无条件重复注册，否则普通运行时会触发重复 range 或 Tile 断言。
4. 声明 ground、noise、minimap、inventory atlas 等资源，并核对纹理尺寸、格式和路径。
5. 按需要设置 Tile、Minimap 和 Falloff 属性或渲染顺序；只调整自定义内容相关项。
6. 世界生成 Room 与布局引用稳定 Tile 常量，不硬编码可能冲突的数字 ID。
7. 实体地图图标使用 MiniMapEntity 和注册 Atlas，明确可见范围、图标和移除行为。
8. 用新世界、存档重载、铺地/铲地、地图缩放和多个地皮模组组合测试。

## 源码锚点

- tilemanager.lua、tiledefs.lua、worldtiledefs.lua、tilegroups.lua。
- modutil.lua：RegisterTileRange、AddTile、SetTileProperty 与 Minimap API。
- map/terrain.lua、map/rooms.lua、map/static_layouts/。
- prefabs/turfs.lua、MiniMapEntity 使用范例。

## 不变量

- 不要硬编码占用原版或其他模组的 Tile ID。
- Tile range 名称必须唯一，且 range_end - range_start 不得小于 256。
- 世界 Tile、Minimap Tile 与 Turf 定义缺一时要明确限制。
- 客户端资源路径必须与 Asset 声明完全一致。
- 改变渲染顺序前检查对其他地皮的全局影响。

## 验证

- 新世界能生成地皮，旧存档能重载而不改变已有 ID。
- 铺设、挖起、地图显示和 Minimap 显示一致。
- 与另一个自定义地皮模组同时启用时无 ID 冲突。
