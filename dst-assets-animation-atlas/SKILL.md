---
name: dst-assets-animation-atlas
description: Prepare and integrate Don't Starve Together animation, build, bank, atlas, texture, inventory image, portrait, minimap, and symbol assets. Use when declaring ANIM, ATLAS or IMAGE assets, compiling SCML and textures with Mod Tools, selecting bank and build names, overriding symbols, or diagnosing missing animation and atlas resources.
---

# DST 动画、Build 与图集资源

从资源源文件、编译产物、Asset 声明到 Lua 使用逐层核对名称和路径。

## 工作流

1. 列出每项资源的源文件、编译产物、Asset 类型、相对路径、bank、build、animation、symbol 和消费位置。
2. 从相同用途原版资源调用点确认管线；世界 AnimState、UIAnim、Image、库存图标和 Minimap 使用不同契约。
3. 用 DST Mod Tools 编译 SCML、纹理和图集，保留可再生成的源文件，不手工伪造二进制产物。
4. 在 Prefab 或入口的 Assets 中声明实际使用资源；图集 XML、TEX 和 Lua 路径大小写保持一致。
5. 设置 AnimState bank/build/animation 前确认名称存在；OverrideSymbol 与 ClearOverrideSymbol 成对管理。
6. 库存、配方、角色肖像和 Minimap 图标分别注册正确 Atlas，不用世界动画资源替代 UI 图集：库存图标在 modmain 顶层用 RegisterInventoryItemAtlas(atlas, "<img>.tex")，Minimap 用 AddMinimapAtlas，图鉴与技能树用 RegisterScrapbookIconAtlas、RegisterSkilltreeIconsAtlas、RegisterSkilltreeBGForCharacter。
7. 在干净启动中检查资源加载日志、所有动画状态、皮肤或 Build 切换和远端客户端。

## 源码锚点

- prefabs/ 中 Asset、SetBank、SetBuild、PlayAnimation 和 OverrideSymbol 调用。
- prefabs.lua、prefabutil.lua、modutil.lua 的资源注册 API。
- simutil.lua：RegisterInventoryItemAtlas、GetInventoryItemAtlas 及图鉴、技能树、Minimap 的 Atlas 查找表。
- widgets/image.lua、uianim.lua、itemimage.lua。
- anim 与 atlas 相关 Mod Tools 输出约定。

## 不变量

- Asset 声明路径使用模组相对路径，运行时解析路径按具体 API 契约处理。
- bank、build、animation 和 symbol 是不同命名空间。
- 不要把未实际运行编译器的文件描述为已编译可用。
- 资源替换要清理旧 Override，避免影响后续装备或皮肤。

## 验证

- 启动日志无缺失 Asset、Atlas、Animation 或 Symbol。
- 所有目标动画和 UI 图标在不同客户端可见。
- 源资源可通过记录的工具链重新生成相同类别产物。

## 按需资源

- 需要资源类型与消费 API 对照时读取 references/asset-pipelines.md。
- 注册库存、Minimap、图鉴或技能树图标 Atlas 时读取 references/ui-atlas-registration.md。

