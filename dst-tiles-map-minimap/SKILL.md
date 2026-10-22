---
name: dst-tiles-map-minimap
description: Create Don't Starve Together ground tiles, turf, map and minimap assets, map icons, render ordering, and map discovery behavior. Use when calling RegisterTileRange or AddTile, defining tile and minimap properties, adding turf items, registering atlases, or integrating custom entities with the map and minimap.
---

# DST 地皮、地图与小地图

同时维护地皮 ID、世界渲染、Minimap 渲染、Turf 物品和世界生成引用的一致性。

## 工作流

1. 确定需求是地面 Tile、可铺 Turf、地图图标、Minimap Tile 还是 MapExplorer/MapReveal 行为。
2. 为自定义 Tile 注册唯一范围；RegisterTileRange 要求 range_end - range_start 至少为 256，再用 AddTile 提供 tile_data、ground_tile_def、minimap_tile_def 和 turf_def。
3. 把自定义 Tile 的 RegisterTileRange 与 AddTile 注册只放入 modworldgenmain.lua。该入口在普通运行时先于 modmain.lua 加载，世界生成会跳过 modmain.lua；前端启用模组或切换存档时还可能在同一 Lua 进程再次加载它。用带模组前缀的稳定 Tile 常量（如 WORLD_TILES.MYMOD_TILE）或等价的持久全局标记保护整个注册块，只在尚未成功注册时调用 RegisterTileRange 与 AddTile。不要在两个入口无条件注册，也不要假设 FrontendUnloadMod 会清理 TileManager。
4. 声明 ground、noise、minimap、inventory atlas 等资源，并核对纹理尺寸、格式和路径。
5. 按需要设置 Tile、Minimap 和 Falloff 属性或渲染顺序；只调整自定义内容相关项。
6. 世界生成 Room 与布局引用稳定 Tile 常量，不硬编码可能冲突的数字 ID。
7. 实体地图图标使用 MiniMapEntity 和在 modmain 中 AddMinimapAtlas 注册的 Atlas，SetIcon 名称与 XML 元素名一致，明确可见范围、图标和移除行为。
8. 用新世界、存档重载、铺地/铲地、地图缩放和多个地皮模组组合测试。

## 地面纹理合成与变暗排查

- `ground_tile_def.name` 不是分类名。`tilemanager.lua` 会用它解析 `levels/tiles/<name>.tex` 和同名 Atlas；世界初始化时，`MapLayerManager:CreateRenderLayer` 会同时接收该基础图集与 `noise_texture`。因此 `noise_texture` 不是不经处理直接显示在地面上。
- 选择基础图集时先检查其实际 RGB 内容，不能只看透明轮廓。原版 `cobblestone` 图集自带深色石路纹理，适合搭配白色噪声生成道路；若再与彩色自定义 `noise_texture` 合成，会明显压暗并混入石路细节。
- 希望主要保留自定义 `noise_texture` 的颜色和质感时，优先参考原版 `COTL_BRICK` 等地皮使用近白色的 `blocky` 图集。若 `blocky` 的边缘形状不符合设计，再制作包含完整地块组合、同名 XML 元素和近白色 RGB 的专用基础图集。
- 当源 PNG 或反解 TEX 正常、游戏内无角色滤镜时仍显著变暗，先对照解码后的 `levels/tiles/<name>.tex`，再检查环境光、季节 Colour Cube 和自定义后处理。不要在确认基础图集前反复提高源图亮度；压暗来自图集合成时，补偿源图会损失高光和材质层次。
- DXT/RGB 压缩选择主要影响色块、细节和内存，不应造成整张地皮均匀大幅变暗。出现这种现象时优先排查基础图集和环境光。
- 更换 `ground_tile_def.name`、Atlas 或地面 TEX 后完全退出并重启游戏再验证；地面渲染层在世界初始化时创建，前端重载模组不一定清除已有资源状态。

## 源码锚点

- tilemanager.lua：`GroundImage`、`GroundAtlas`、`ValidateGroundTileDef`；tiledefs.lua、worldtiledefs.lua、tilegroups.lua。
- prefabs/world.lua：`MapLayerManager:CreateRenderLayer` 以及地皮颜色参数绑定。
- modutil.lua：RegisterTileRange、AddTile、SetTileProperty 与 Minimap API。
- map/terrain.lua、map/rooms.lua、map/static_layouts/。
- prefabs/turfs.lua、MiniMapEntity 使用范例。

## 不变量

- 不要硬编码占用原版或其他模组的 Tile ID。
- Tile range 名称必须唯一，且 range_end - range_start 不得小于 256。
- Tile 注册必须可重入；同一 Lua 进程重复执行 modworldgenmain.lua 时不得再次注册同一 range 或 Tile。
- 世界 Tile、Minimap Tile 与 Turf 定义缺一时要明确限制。
- 客户端资源路径必须与 Asset 声明完全一致。
- 改变渲染顺序前检查对其他地皮的全局影响。

## 验证

- 新世界能生成地皮，旧存档能重载而不改变已有 ID。
- 铺设、挖起、地图显示和 Minimap 显示一致。
- 与另一个自定义地皮模组同时启用时无 ID 冲突。
- 在模组界面完成启用、禁用、再次启用和切换存档后，不出现重复 range 或 Tile 断言。
