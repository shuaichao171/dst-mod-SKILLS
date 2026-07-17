---
name: dst-tiles-map-minimap
description: Create Don't Starve Together ground tiles, turf, map and minimap assets, map icons, render ordering, and map discovery behavior. Use when calling RegisterTileRange or AddTile, defining tile and minimap properties, adding turf items, registering atlases, or integrating custom entities with the map and minimap.
---

# DST 地皮、地图与小地图

同时维护地皮 ID、世界渲染、Minimap 渲染、Turf 物品和世界生成引用的一致性。

## 工作流

1. 确定需求是地面 Tile、可铺 Turf、地图图标、Minimap Tile 还是 MapExplorer/MapReveal 行为。
2. 为自定义 Tile 注册独立范围，再用 AddTile 提供 tile_data、ground_tile_def、minimap_tile_def 和 turf_def。
3. 声明 ground、noise、minimap、inventory atlas 等资源，并核对纹理尺寸、格式和路径。
4. 按需要设置 Tile、Minimap 和 Falloff 属性或渲染顺序；只调整自定义内容相关项。
5. 世界生成 Room 与布局引用稳定 Tile 常量，不硬编码可能冲突的数字 ID。
6. 实体地图图标使用 MiniMapEntity 和注册 Atlas，明确可见范围、图标和移除行为。
7. 用新世界、存档重载、铺地/铲地、地图缩放和多个地皮模组组合测试。

## 源码锚点

- tilemanager.lua、tiledefs.lua、worldtiledefs.lua、tilegroups.lua。
- modutil.lua：RegisterTileRange、AddTile、SetTileProperty 与 Minimap API。
- map/terrain.lua、map/rooms.lua、map/static_layouts/。
- prefabs/turfs.lua、MiniMapEntity 使用范例。

## 不变量

- 不要硬编码占用原版或其他模组的 Tile ID。
- 世界 Tile、Minimap Tile 与 Turf 定义缺一时要明确限制。
- 客户端资源路径必须与 Asset 声明完全一致。
- 改变渲染顺序前检查对其他地皮的全局影响。

## 验证

- 新世界能生成地皮，旧存档能重载而不改变已有 ID。
- 铺设、挖起、地图显示和 Minimap 显示一致。
- 与另一个自定义地皮模组同时启用时无 ID 冲突。
