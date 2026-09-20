---
name: dst-make-scml-animation
description: Analyze, design, create, modify, and audit Spriter SCML animation assets for Don't Starve Together. Use for DST mod actions, animation naming and timing, directional action sets, frame posing, pivots, layer ordering, symbol swaps, transparent PNG parts, SCML/XML repair, or compatibility checks against unpacked game animation references.
---

# DST SCML 动作制作

把游戏运行时契约、动作可读性和 SCML 数据一致性作为同一项工作处理。先选同类型原版参考，再制作动作，不要从单一通用模板猜测全部规则。

## 工作流

1. 确认运行时契约。
   - 在 Lua、StateGraph 和 prefab 中搜索 `SetBank`、`SetBuild`、`PlayAnimation`、`PushAnimation`、`OverrideSymbol`、`HideSymbol` 及目标动作名。
   - 记录 bank、build、entity、动作名、方向组、是否循环、结束事件和可替换 symbol。
   - 保留代码已经依赖的名称；需要改契约时同时改代码和资源。
2. 选择最近的原版参考。
   - 优先匹配资源类别、镜头方向、动作职责和运行时接法，不要只按外观相似选择。
   - 物品参考物品，建筑参考建筑，角色或生物参考相同方向集，FX 参考同生命周期特效。
3. 读取 [references/scml-production.md](references/scml-production.md)。
   - 制作或修复 XML 时读取“SCML 数据约束”和“验证”部分。
   - 设计动作表时读取“动作组织”和“动作设计”部分。
4. 审计参考与目标。
   - 从技能目录运行：

     ```powershell
     python scripts/analyze_scml.py <target.scml> --mode source
     python scripts/analyze_scml.py <baked-reference.scml> --mode baked
     ```

   - 默认 `source` 检查可编辑的 sprite/bone 源工程：保留骨骼、补间和非采样网格关键帧；`baked` 才要求平铺图片时间轴、即时插值和 interval 网格。不要为了通过烘焙检查删除源骨骼；完整支持范围见参考的“验证”部分。
   - 对大语料先加 `--skip-image-checks`；交付目标必须启用 PNG 存在性和尺寸检查。
   - 已有可编辑的源 SCML 和 PNG 时，只修改源工程并用官方 Mod Tools 重新编译；不得把反编译 SCML 当作二次修改源。反编译仅用于参考，或核对最终包的 bank、build、动作、pivot、贴图和编译一致性。确实没有源工程且任务要求恢复资产时，明确记录重建依据和元数据损失风险。
5. 写动作规格。
   - 列出每个动作的用途、持续时间、关键姿势、方向、循环边界、层级变化和挂点要求。
   - 把连续动作拆成 `*_pre`、`*_loop`、`*_pst`，只有在运行时代码确实如此调用时才采用该命名。
   - 默认以 33ms 节拍设计，再以所选原版参考和代码节奏为准。
6. 先做关键姿势，再补帧。
   - 依次建立静止、预备、发力、命中或接触、过冲、恢复。
   - 在游戏实际显示尺寸检查轮廓、重心、接触点和方向，不以编辑器放大图替代。
   - 循环动作先闭合首尾速度与形状，再增加次级摆动。
7. 制作部件与 pivot。
   - 需要新贴图时使用 `$dst-texture-style`，按关节、遮挡和 symbol 替换边界拆件。
   - 同一视觉部件的换帧保持语义 pivot 稳定；更换裁切框时补偿坐标。
   - 静态地面物、建筑和落地 FX 的世界原点必须位于画面主体与地面的实际接触线；不得按画布底边、alpha 最低像素、投影边缘或视觉中心机械设置 pivot。阴影和透明余量可以延伸到原点下方。
   - 保留参考中必要的负缩放、非中心 pivot 和超界 pivot，不做无依据的“清理”。
8. 组织时间轴。
   - 源工程可使用 bone_ref 和补间；匹配烘焙参考时才使用 `curve_type="instant"`、逐帧 mainline key、object_ref 和 z_index。
   - 通过对象进入或退出 mainline 表达显隐；不要假设 alpha 动画会匹配现有导出链路。
   - 检查 bone_ref/object_ref 的 timeline/key 指向、父骨骼链、图片 folder/file 指向和层级顺序。
9. 验证并进游戏检查。
   - 按源工程或烘焙产物选择分析模式，修复 XML、缺图、尺寸和引用问题；源工程的非网格时间与补间统计不等同于格式错误。
   - 在动作前后状态、四方向、镜像、装备覆盖、骑乘或特殊形态中检查连接。
   - 检查首帧闪烁、末帧跳变、脚底滑动、穿层、pivot 抖动和循环停顿。

## 决策原则

- 把 `anim_unpacked/zip` 当作可验证的兼容参考，不把反编译后的烘焙结构误当作 Klei 原始工程文件。
- 优先复用同 bank/build 的 symbol 与动作族；跨类别借用只参考节奏和姿势逻辑。
- 先保证动作意图在小尺寸下一眼可读，再处理细节和缓动感。
- 让命中、落地、开合终点等游戏事件落在明确帧上，便于代码事件对齐。
- 保留方向间共同的节奏和接触时刻，同时允许轮廓与遮挡顺序不同。
- 不手工批量拼接 XML 字符串；使用 XML API、Spriter 或现有导入导出工具。

## 本项目的 side 朝向约定

- 全部 `*_side` 动作必须原生朝右，包括 SCML、GIF 预览和接触表中的未镜像 side 帧。
- 左朝向由运行时对 `*_side` 做水平镜像得到；不得把左朝向资源标成 side 后再镜像生成右朝向。
- manifest 必须记录 `side` 原生对应 `right`、`mirror_for` 对应 `left`。
- 四方向预览固定按 `left, right, down, up` 排列：第一列使用 side 的水平镜像，第二列使用原生 side。
- 修改 side 的位置、角度或缩放时，应对完整姿势做一致的水平镜像，并检查武器手、盾牌手、肩甲、双脚和非对称标记没有交换错误或穿层。
- 交付前逐项检查 `idle_loop_side`、`walk_loop_side`、`attack_side` 和 `death_side`，防止只有部分动作朝向被修正。

## 交付内容

同时交付或报告：

- SCML 与全部引用 PNG；
- 动作名、方向、时长、循环方式和关键事件表；
- bank/build/runtime 接法；
- 采用的原版参考路径与有意偏离之处；
- 分析器结果和未能执行的游戏内验证。
