# 前端资源、预加载资源与加载提示

以下结论来自 `modutil.lua`、`mods.lua`、`mainfunctions.lua`、`main.lua`、`loadingtipsdata.lua` 和 `constants.lua`，游戏更新后先重新核对。

> 示例里的 modmain 代码假设已经按 dst-mod-scaffolding 在文件顶部设置了 `__index → GLOBAL` 环境继承。没有设置时，入口环境里未注入的全局变量（STRINGS、LOADING_SCREEN_TIP_CATEGORY_WEIGHTS_START、CONTROL_PRIMARY 等）要从 `GLOBAL` 读取。

## FrontEndAssets / ReloadFrontEndAssets

```lua
-- modservercreationmain.lua
FrontEndAssets = {
    Asset("ATLAS", "images/mymod_customization.xml"),
    Asset("IMAGE", "images/mymod_customization.tex"),
}
ReloadFrontEndAssets()
```

- `ReloadFrontEndAssets` 只在前端环境里定义（`CreateEnvironment(..., isfrontend=true)`），也就是 **modservercreationmain.lua**。modmain 和 modworldgenmain 里调用会因为是 nil 而报错。
- 它用 `FrontEndAssets` 的浅拷贝注册一个名为 `MODFRONTEND_<modname>` 的 Prefab 并立即加载。资源路径相对于模组目录解析。
- 用于建服界面需要的图：世界设置选项图标（`AddCustomizeItem` 的 atlas）、模组设置页的自定义图片等。模组在前端被禁用时，`mods.lua` 会调用 `ModUnloadFrontEndAssets` 卸载这些资源。
- 每次调用都会先卸载本模组上一次加载的前端资源，再重新加载，所以可以重复调用。

## PreloadAssets / ReloadPreloadAssets

```lua
-- modmain.lua 或 modservercreationmain.lua
PreloadAssets = {
    Asset("ATLAS", "images/mymod_tipicon.xml"),
    Asset("IMAGE", "images/mymod_tipicon.tex"),
}
ReloadPreloadAssets()
```

- 除世界生成环境外都有定义。它注册并加载一个名为 `MODPRELOAD_<modname>` 的 Prefab，让资源在常规 Prefab 加载之前就可用。
- modutil.lua 的注释说明它主要用于加载提示图标：加载界面显示时，世界的 Prefab 资源还没有加载。
- 只放加载界面这类早期 UI 确实需要的少量图片。世界内资源仍然放在 `Assets` 或 Prefab 的 assets 里。

## 加载提示

```lua
-- modmain.lua 顶层
AddLoadingTip(STRINGS.UI.LOADING_SCREEN_SURVIVAL_TIPS, "MYMOD_TIP_BEAST", "某种生物害怕火光。")

-- 带按键占位的提示：只有 CONTROLS 和 OTHER 分类会替换占位符
AddLoadingTip(STRINGS.UI.LOADING_SCREEN_OTHER_TIPS, "MYMOD_TIP_CAST",
    "按 {primary} 施放法术。", { primary = CONTROL_PRIMARY })

-- OTHER 分类的默认权重为 0，不设置就永远不会被抽到
SetLoadingTipCategoryWeights(LOADING_SCREEN_TIP_CATEGORY_WEIGHTS_START, { OTHER = 2 })
SetLoadingTipCategoryWeights(LOADING_SCREEN_TIP_CATEGORY_WEIGHTS_END, { OTHER = 2 })

-- 修改分类图标：需要先通过 PreloadAssets 加载图集
SetLoadingTipCategoryIcon("OTHER", "images/mymod_tipicon.xml", "mymod_tipicon.tex")
```

| API | 作用 |
| --- | --- |
| `AddLoadingTip(stringtable, id, text, controltipdata)` | 写入 `stringtable[id] = text`；有 `controltipdata` 时登记到 `LOADING_SCREEN_CONTROL_TIP_KEYS[id]` |
| `RemoveLoadingTip(stringtable, id)` | 删除上面两处登记，也可以用来移除原版提示 |
| `SetLoadingTipCategoryWeights(weighttable, weightdata)` | 把 weightdata 的值合并进 `LOADING_SCREEN_TIP_CATEGORY_WEIGHTS_START` 或 `_END` |
| `SetLoadingTipCategoryIcon(category, atlas, icon)` | 替换 `LOADING_SCREEN_TIP_ICONS[category]`，影响该分类下的所有提示 |

- 可用的字符串表：`STRINGS.UI.LOADING_SCREEN_SURVIVAL_TIPS`、`LOADING_SCREEN_LORE_TIPS`、`LOADING_SCREEN_CONTROL_TIPS`、`LOADING_SCREEN_OTHER_TIPS`。分类键为 `CONTROLS`、`SURVIVAL`、`LORE`、`LOADING_SCREEN`、`OTHER`。
- 默认权重：START 为 CONTROLS 4 / SURVIVAL 3 / LORE 1 / LOADING_SCREEN 2 / **OTHER 0**；END 为 0.5 / 2 / 4 / 3.5 / **0**。系统会按游玩次数在 START 和 END 之间插值。修改权重会影响所有原版提示被抽中的比例，只改自己要用的分类。
- id 是全局键，加模组前缀。已显示次数按 id 保存在 `loadingtips` 持久化文件里，显示次数越多，被抽中的权重越低。
- `TheLoadingTips` 在 `main.lua` 的 `ModManager:LoadMods()` 之后创建，并在构造时一次性计算提示列表和分类权重。所以注册必须写在 modmain 顶层；之后再动态添加，要等下一次 Lua 环境重建才会生效。具体在哪个加载界面开始出现需要进游戏验证。
- 提示文本属于本地化内容，翻译处理见 dst-localization-speech。
