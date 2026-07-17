---
name: dst-shader-authoring
description: Create, compile, debug, and integrate shader resources for Don't Starve Together (DST) mods. Use when working with .vs, .ps, or .ksh files; world AnimState bloom-pass effects; UIAnim or ImageWidget effects; VFXEffect particles; PostProcessor filters and multipass chains; ShaderCompiler.exe; shader samplers or uniforms; or AddModShadersInit and AddModShadersSortAndEnable.
---

# DST Shader Authoring

为 DST Mod 编写 shader 时，先识别渲染管线，再使用对应模板；不要将不同管线的顶点输入、uniform 或 sampler 直接混用。

## 执行流程

1. 确认目标是世界 `AnimState` 的 bloom pass、UI `UIAnim`、UI `Image`、`VFXEffect` 还是全屏 `PostProcessor`。
2. 读取 `references/shader-contracts.md` 中该管线的输入契约、标准 uniform 和 Lua 绑定。
3. 从 `assets/templates/` 复制匹配的 `.vs`、`.ps`，仅在 Mod 目录中修改副本。
4. 先让片元阶段原样输出 `SAMPLER[0]`，确认顶点布局、纹理和绑定正确。
5. 逐项加入效果数学、uniform 和额外 sampler；每次只增加一个可验证变量。
6. 使用 Mod Tools 的 `ShaderCompiler.exe` 将 `.vs` 与 `.ps` 编译为 `.ksh`。
7. 使用 `Asset("SHADER", "shaders/name.ksh")` 注册，并用相应 Lua 入口加载。
8. 在游戏中验证；报告编译器、加载、排序或 runtime 的实际错误，不要把未运行的编译说成成功。

## 选择管线

| 目标 | 使用模板 | 绑定 API |
| --- | --- | --- |
| 世界动画实体的 bloom pass | `anim_effect.*` | `AnimState:SetBloomEffectHandle()` |
| UI 中的动画 bank/build | `ui_anim_effect.*` | `UIAnim:GetAnimState():SetDefaultEffectHandle()` |
| HUD、图标、图片、屏幕 UI | `ui_effect.*` | `Image:SetEffect()` + `SetEffectParams()` |
| GPU 粒子 | `vfx_effect.*` | `VFXEffect:SetRenderResources()` |
| 单阶段整屏滤镜 | `postprocess_effect.*` | `AddModShadersInit()` + `PostProcessor` |
| 模糊、合成等多阶段整屏滤镜 | `postprocess_blur*` + `postprocess_multipass_modmain.lua` | `AddSamplerEffect()` + `AddPostProcessEffect()` |

`SetBloomEffectHandle()` 只替换 `RENDERPASS.BLOOM` 使用的 shader，不会替换世界实体的正常主渲染。不要承诺用它实现任意世界 `AnimState` 主 pass shader。`SetDefaultEffectHandle()` 的本地可验证用法属于 UI `UIAnim` 的 `AnimState`。

不要将 `ground.ksh`、`ocean.ksh`、`waves.ksh`、`minimap.ksh` 用于普通 Mod UI 或实体；它们依赖专用 C++ 渲染组件。

## 编写规则

- 使用 DST 自带的旧式 GLSL：`attribute`、`varying`、`texture2D`、`gl_FragColor`；不要添加 `#version`、`layout`、`in/out`、UBO 或现代 GLSL 特性。
- 使顶点和片元阶段的每个 `varying` 名称、类型、维度完全一致。
- 使 `uniform sampler2D SAMPLER[n]` 的大小与实际绑定数一致。
- 保持 UI 和常规 additive VFX 的预乘 alpha；同时缩放透明度时，也要同步缩放已经预乘的 RGB。
- 不要把 `vfx_particle_add` 的预乘契约套到 `vfx_particle_reveal`；先确认目标 blend/shader 家族。
- 仅为实际有来源的 uniform 声明变量。普通后处理 uniform 必须依次 `AddUniformVariable`、`SetEffectUniformVariables`、`SetUniformVariable`。
- 把 sampler effect 的自动 `SAMPLER_PARAMS` 作为特殊内建 uniform 处理，不要手动写入它。
- 后处理注册文件运行在 `modmain.lua` 的受限环境；`Asset`、`AddModShadersInit` 与 `AddModShadersSortAndEnable` 会被注入，`resolvefilepath`、`hash`、后处理枚举及未注入的标准函数必须从 `GLOBAL` 局部化。
- `PostProcessor` 晚于 `modmain.lua` 创建；在 `AddModShadersInit`、`AddModShadersSortAndEnable` 回调或实际调用的辅助函数内读取 `GLOBAL.PostProcessor`，不要在入口加载时缓存 nil。附带模板已处理该时序。
- 使用从 `GLOBAL` 局部化的 `resolvefilepath()` 传递 Mod 自己的运行时 shader 与纹理路径；`Asset` 注册仍使用 Mod 相对路径。

## 编译与部署

默认 Mod Tools 路径为：

```powershell
& "D:\steam\steamapps\common\Don't Starve Together\mod_tools\tools\bin\ShaderCompiler.exe" `
  -little <name> <vertex.vs> <fragment.ps> <name.ksh> -oglsl
```

将结果放到 Mod 的 `shaders/` 目录。若编译器因旧的 Cg/VC90 依赖无法启动，说明实际错误并停止；不要手改 `.ksh` 或将未验证的输出当成可用资源。

## 后处理的特殊顺序

- 在 `AddModShadersInit` 中创建 effect、texture sampler、sampler effect 和 uniform。
- 在 `AddModShadersSortAndEnable` 中调用 `SetPostProcessEffectBefore/After`，然后启用最终 postprocess effect。
- 对普通全屏 effect，`SAMPLER[0]` 是当前屏幕；每次 `AddSampler(effect, ...)` 依次得到 `SAMPLER[1]`、`SAMPLER[2]`。
- sampler effect 的 `SAMPLER[0]` 来源由 `SamplerEffectBase` 决定；以另一个 sampler effect 为输入时，使用 `SamplerEffectBase.Shader` 和前一 pass 的 ID。
- 从 `assets/templates/postprocess_modmain.lua` 开始编写单 pass；多 pass 先读取 `references/postprocess-multipass.md`，再复制对应模板。

## 验证清单

1. `.ksh` 已由 `.vs` 和 `.ps` 编译得到，未手工修改二进制容器。
2. `Assets` 已注册 shader，以及所有自定义纹理。
3. `varying`、矩阵、属性和 sampler 符合目标渲染器的契约。
4. 世界 `AnimState` 自定义 shader 被明确当作 bloom pass；UI 动画才使用 `SetDefaultEffectHandle()`。
5. UI 参数使用 `IMAGE_PARAMS` / `IMAGE_PARAMS2` / `ALPHA_RANGE` 的正确 Lua 写入方法。
6. VFX 的 RGB 与 alpha 符合所选 blend 家族，生命周期淡出没有破坏预乘关系。
7. 后处理最终 effect 已排序并启用；所有中间 sampler effect 都能从最终 effect 的依赖链到达。
8. 使用原样采样和参数可视化先排除黑屏，再优化特效。

## 按需资源

- 读取 `references/shader-contracts.md`：需要精确属性、uniform、sampler、Lua 绑定、调试或性能细节时。
- 读取 `references/postprocess-multipass.md`：需要纹理 sampler、离屏 sampler effect、自动尺寸参数或多 pass 链时。
- 复制 `assets/templates/`：需要新建 bloom、UIAnim、Image、VFX 或后处理 shader 时。
