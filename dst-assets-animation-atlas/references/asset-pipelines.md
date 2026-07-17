# 资源管线对照

| 目标 | 资源 | Lua 消费 |
| --- | --- | --- |
| 世界动画 | 编译后的 anim zip | Asset ANIM、AnimState |
| UI 动画 | anim zip | UIAnim 的 AnimState |
| UI 图片 | atlas xml 与 tex | Asset ATLAS、Asset IMAGE、Image |
| 库存图标 | inventory atlas | inventoryitem、Recipe、注册 Atlas |
| Minimap 图标 | minimap atlas | MiniMapEntity |
| Shader | ksh | dst-shader-authoring |

## 名称层级

bank、build、animation 与 symbol 是不同名称。SetBank 选择动画银行，SetBuild 选择图像资源，PlayAnimation 选择时间线，OverrideSymbol 替换单个 symbol。

## 检查顺序

1. 源文件存在。
2. Mod Tools 实际编译成功。
3. 编译产物位于模组相对路径。
4. Asset 类型与路径正确。
5. XML 与 TEX 名称匹配。
6. Lua 中 bank、build、animation、symbol 存在。
7. 干净客户端能加载资源。

不要手工制造 anim zip、tex 或其他二进制容器，也不要把未运行的编译步骤写成已通过。

