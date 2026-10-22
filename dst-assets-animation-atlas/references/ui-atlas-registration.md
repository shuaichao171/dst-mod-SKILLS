# UI 图集注册 API

游戏按「图片名 → Atlas」查找库存、配方、Minimap、图鉴和技能树图标。原版图标在内置 Atlas 里查找，模组图标必须先注册自己的 Atlas。以下结论来自 `modutil.lua` 与 `simutil.lua`，游戏更新后先重新核对。

## 速查

| modmain API | 底层查找函数 | 键名 | 消费位置 |
| --- | --- | --- | --- |
| `RegisterInventoryItemAtlas(atlas, "<img>.tex")` | `GetInventoryItemAtlas` | 带 `.tex` 的图片名 | 物品栏格子、配方产物、Ingredient、小木牌/画框 |
| `AddMinimapAtlas(atlas)` | `MiniMap:AddAtlas` | 无（整本 Atlas 加入） | `MiniMapEntity:SetIcon` |
| `RegisterScrapbookIconAtlas(atlas, "<img>.tex")` | `GetScrapbookIconAtlas` | 带 `.tex` 的图片名 | 图鉴（Scrapbook）界面 |
| `RegisterSkilltreeIconsAtlas(atlas, "<icon>.tex")` | `GetSkilltreeIconAtlas` | 技能定义 `icon` 加 `.tex` | 技能树按钮 |
| `RegisterSkilltreeBGForCharacter(atlas, charname)` | `GetSkilltreeBG` | 自动拼成 `<charname>_background.tex` | 技能树背景 |

每个 Atlas 都要在 modmain 的 `Assets` 里同时声明 `Asset("ATLAS", xml)` 和 `Asset("IMAGE", tex)`，XML 里 `<Element name=...>` 必须与上表的键名一致，大小写也要一致。

## RegisterInventoryItemAtlas

```lua
-- modmain.lua
Assets = {
    Asset("ATLAS", "images/inventoryimages/mymod_item.xml"),
    Asset("IMAGE", "images/inventoryimages/mymod_item.tex"),
}

RegisterInventoryItemAtlas("images/inventoryimages/mymod_item.xml", "mymod_item.tex")
```

### 契约

- 第二个参数是**带 `.tex` 的图片名**，不是 Prefab 名。modutil.lua 里的参数名叫 `prefabname`，注释的意思是：图片名最好等于 `<prefab>.tex`，这样不用生成实体也能查到。replica 的 `GetImage()` 默认返回 `inst.prefab..".tex"`，原版 `deck_of_cards.lua` 的调用也带 `.tex`。
- 注册只是一张本地查找表，不走网络。modmain 在主机和所有客户端都会执行，所以每端各自注册，不需要 netvar。
- **先注册的生效**：同一个图片名重复注册到不同 Atlas 时，只打印 `already registered`，不会覆盖。
- **查找结果会被缓存，包括回退值**：`GetInventoryItemAtlas(img)` 在未注册又没找到时，默认回退到 `images/inventoryimages4.xml` 并写入缓存，之后再注册也不会生效。因此要在 modmain 顶层注册，不要放进 PostInit、延迟任务或 UI 构造里。
- 存的是原始路径。`Image:SetTexture`、`Recipe:GetAtlas`、`Ingredient:GetAtlas` 会自己 `resolvefilepath`；`AnimState:OverrideSymbol` 这种直接使用路径的地方不会（见下文小木牌）。

### 生效范围

| 场景 | 只注册即可 | 不注册时的替代写法 |
| --- | --- | --- |
| 物品栏/容器格子 | 是（`GetAtlas` 回落到 `GetInventoryItemAtlas(GetImage())`） | 服务器设置 `inventoryitem.atlasname`，通过 classified netvar 下发 |
| 配方产物图标 | 是（`Recipe:GetAtlas` 惰性查找） | `AddRecipe2` 的 `config.atlas` / `config.image` |
| 作为材料的图标 | 是（`Ingredient:GetAtlas`） | `Ingredient(type, amount, atlas)` |
| 制作菜单中尚未生成过的物品 | 是 | 每个配方都要写 atlas |
| 小木牌/画框绘制模组物品 | 还需要 `Asset("ATLAS_BUILD", xml, 256)` | 无，需进游戏验证 |

所以多个系统共用同一张图标时，优先用 `RegisterInventoryItemAtlas`，不用在每个 Recipe、Ingredient 和 Prefab 里重复写 `atlasname`。

### 改名与换图

- `inventoryitem.imagename = "mymod_item_alt"`（不带 `.tex`，replica 会补）或 `inventoryitem:ChangeImageName(name)` 会切换图片名，新图片名同样要注册。
- 同一个 Atlas 可以装多张图，每张分别注册：

```lua
for _, name in ipairs({ "mymod_item", "mymod_item_alt" }) do
    RegisterInventoryItemAtlas("images/inventoryimages/mymod_items.xml", name..".tex")
end
```

### 小木牌 / 画框

`prefabs/minisign.lua` 会执行 `AnimState:OverrideSymbol("SWAP_SIGN", atlas or GetInventoryItemAtlas(img), img)`，把 Atlas 当作 Build 使用；原版为此声明了 `Asset("ATLAS_BUILD", "images/inventoryimages1.xml", 256)`。模组物品要被画上去，需要为自己的 Atlas 声明 `ATLAS_BUILD`。另外，`OverrideSymbol` 使用的路径是原样传入、没有经过 resolve 的，模组路径能否命中要进游戏验证，不能凭静态检查认定已支持。

## AddMinimapAtlas

```lua
Assets = {
    Asset("ATLAS", "images/map_icons/mymod_thing.xml"),
    Asset("IMAGE", "images/map_icons/mymod_thing.tex"),
}
AddMinimapAtlas("images/map_icons/mymod_thing.xml")

-- Prefab 公共部分（所有端）
inst.entity:AddMiniMapEntity()
inst.MiniMapEntity:SetIcon("mymod_thing.tex")
```

- `prefabs/minimap.lua` 在创建小地图时 `resolvefilepath` 并 `AddAtlas` 每个注册路径，所以必须在 modmain 加载时注册，进入世界后再注册不会生效。
- `SetIcon` 的参数是 XML 里的元素名。原版 Minimap Atlas 元素用 `.png` 后缀（如 `chester.png`），模组工具链通常生成 `.tex` 后缀，以自己 XML 的实际名字为准。
- 角色地图图标同样走这条路径（`<charname>.tex` 或对应元素名）。

## RegisterScrapbookIconAtlas

```lua
RegisterScrapbookIconAtlas("images/scrapbook/mymod_item.xml", "mymod_item.tex")
```

只负责图标查找。图鉴里能不能出现某个条目由图鉴数据决定，需要另外查 `screens/redux/scrapbookscreen.lua` 与 scrapbook 数据文件。查找不到时界面会改用 `unknown.tex`。

## 技能树图集

```lua
RegisterSkilltreeBGForCharacter("images/mymod_skilltree_bg.xml", "mychar")  -- 查找 mychar_background.tex
RegisterSkilltreeIconsAtlas("images/mymod_skilltree_icons.xml", "mychar_skill_1.tex")
```

- 背景键名固定为 `<prefab>_background.tex`，缺失时日志打印 `FIXME: Skill tree background ... is missing!`，并显示黑色占位。
- 图标键名是技能定义的 `icon` 字段加 `.tex`；未注册的图标会默认查 `images/skilltree_icons.xml`，界面显示错误图标但不一定报错。每个图标都要单独注册。
- 技能数据与同步流程见 dst-skilltree-authoring。

## 其他带 Atlas 参数的 API

这些 API 直接接收 atlas 参数，不经过上面的查找表：

- `AddRecipeFilter({ name, atlas, image })`、`AddRecipe2(..., { atlas, image })`：见 dst-crafting-tech-prototypers。
- `AddCustomizeGroup(category, name, text, desc, atlas, order)`、`AddCustomizeItem(..., { atlas, image })`：世界设置图标。
- `SetLoadingTipCategoryIcon(category, atlas, icon)`：加载提示分类图标。

## 排查

1. 物品栏显示问号或空白：确认图片名是否带 `.tex`、XML 元素名是否与之一致、是否在 modmain 顶层注册。
2. 日志出现 `RegisterInventoryItemAtlas: Image '...' is already registered`：图片名和其他模组或原版冲突，或者注册前已经查询过。给图片名加模组前缀。
3. 只有远端客户端缺图：检查注册是否被 `TheNet:GetIsServer()`、`TheWorld.ismastersim` 等条件包住了。
4. Minimap 不显示：确认 `AddMinimapAtlas` 已调用，并且 `SetIcon` 的名字和 XML 元素名完全一致。
