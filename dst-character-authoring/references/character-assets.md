# 模组角色 UI 资源与角色注册辅助 API

各界面按**固定的路径与名称规则**查找模组角色图片。以下结论来自 `characterutil.lua`、`recipes_filter.lua`、`widgets/targetindicator.lua`、`widgets/inventorybar.lua`、`screens/morguescreen.lua`、`prefabs/player_common.lua`、`components/skinner.lua`、`networking.lua` 和 `modutil.lua`，游戏更新后先重新核对。下文 `<c>` 代表角色 Prefab 名。

> 示例里的 modmain 代码假设已经按 dst-mod-scaffolding 在文件顶部设置了 `__index → GLOBAL` 环境继承。没有设置时，入口环境里未注入的全局变量（MOD_AVATAR_LOCATIONS、MOD_CRAFTING_AVATAR_LOCATIONS 等）要从 `GLOBAL` 读取。

## 资源清单

| 用途 | Atlas 路径 | 元素名 | 查找位置 | 缺失时 |
| --- | --- | --- | --- | --- |
| 选人大立绘（未做皮肤） | `bigportraits/<c>.xml` | `<c>.tex` | `SetOvalPortraitTexture` 等 | 选人界面空白或报错 |
| 选人大立绘（有皮肤，`PREFAB_SKINS[<c>]` 存在） | `bigportraits/<c>_none.xml` | `<c>_none_oval.tex`，回退 `<c>_none.tex` | `SetSkinnedOvalPortraitTexture` | 日志打印 `is not a valid portrait file` |
| 名字图（灰） | `images/names_<c>.xml` | `<c>.tex` | `SetHeroNameTexture_Grey` | 不显示名字图 |
| 名字图（金，可选） | `images/names_gold_<c>.xml`；简体/繁体中文客户端查找 `images/names_gold_cn_<c>.xml` | `<c>.tex` | `SetHeroNameTexture_Gold` | 自动回退到灰色名字图 |
| 头像 | `images/avatars/avatar_<c>.xml` | `avatar_<c>.tex` | `GetCharacterAvatarTextureLocation`、封禁列表、目标指示器 | 显示 `avatar_mod.tex` |
| 鬼魂与状态头像（目标指示器） | `images/avatars/avatar_ghost_<c>.xml`，以及 `_1`/`_2`/`_3` 状态后缀版本 | 与文件同名 `.tex` | `TargetIndicator:GetAvatarAtlas` | 指示器图标缺失 |
| 制作栏角色过滤器图标 | `images/crafting_menu_avatars/avatar_<c>.xml` | `avatar_<c>.tex` | `recipes_filter.lua` | 回退到 `images/avatars/avatar_<c>.xml` |
| 自检按钮 | `images/avatars/self_inspect_<c>.xml` | `self_inspect_<c>.tex` | `widgets/inventorybar.lua` | 回退到 HUD 图集里的 `self_inspect_mod.tex` |
| 讣告（Morgue）图标 | `images/saveslot_portraits/<c>.xml` | `<c>.tex` | `screens/morguescreen.lua` | 图标缺失 |
| 小地图图标 | 自己的 Atlas，通过 `AddMinimapAtlas` 注册 | **`<c>.png`** | `player_common.lua` 中 `MiniMapEntity:SetIcon(name..".png")` | 地图上不显示 |

- 头像目录可以通过 `MOD_AVATAR_LOCATIONS[<c>] = "images/mymod/"` 修改，制作栏头像用 `MOD_CRAFTING_AVATAR_LOCATIONS`（默认值在 `mods.lua`）。
- 每张图都要在 modmain 的 `Assets` 里声明 `Asset("ATLAS", xml)` 和 `Asset("IMAGE", tex)`。前端选人界面用到的立绘和名字图，还要确认在前端阶段能被加载（见 dst-client-frontend-mods 的 FrontEndAssets）。
- 地图图标的名字由 player_common 固定为 `<c>.png`。要么在 XML 里把元素命名为 `<c>.png`，要么在 `common_postinit` 里改调 `inst.MiniMapEntity:SetIcon(...)`。
- `images/selectscreen_portraits/` 在当前脚本里没有任何引用，属于旧教程遗留，不要再要求提供。
- 库存、Minimap 等 Atlas 的注册方式见 dst-assets-animation-atlas 的 references/ui-atlas-registration.md。

## ExcludeClothingSymbolForModCharacter

```lua
ExcludeClothingSymbolForModCharacter("mychar", "torso")
ExcludeClothingSymbolForModCharacter("mychar", "arm_upper")
```

- 作用：`components/skinner.lua` 应用衣物时，跳过该角色被排除的 symbol，让衣物不覆盖角色自己的身体部件（例如特殊体型、不想被衣服遮住的躯干）。
- 只影响衣物（CLOTHING）的 symbol 覆盖，不影响角色皮肤 build 和装备的 `OverrideSymbol`。
- 每个 symbol 单独调用一次；查询时会遍历所有已启用模组的排除表。

## RemoveDefaultCharacter

```lua
RemoveDefaultCharacter("wilson")
```

- 把原版角色加入 `MODCHARACTEREXCEPTIONS_DST`。选人界面、大厅、衣柜面板会把它过滤掉；服务器上的 `ValidateSpawnPrefabRequest` 也用同一张表校验，所以服务器加载了模组时，客户端无法绕过限制生成被移除的角色。
- 只接受 `DST_CHARACTERLIST` 中的原版角色名，其他名字只会打印警告。
- 这会影响所有玩家的可选角色，属于服务器玩法配置，通常应做成 modinfo 选项，并说明对已有存档中使用该角色的玩家有什么影响。
