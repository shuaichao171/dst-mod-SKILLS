---
name: dst-texture-style
description: Analyze, art-direct, generate, edit, split, and audit transparent PNG textures that must fit the hand-drawn visual language of Don't Starve Together. Use for DST mod items, creatures, buildings, UI symbols, animation parts, effects, style-matching briefs, ImageGen prompts, silhouettes, linework, palettes, alpha edges, pivots, or texture consistency checks against unpacked game references.
---

# DST 贴图风格

以同类原版资源为局部风格基准，制作可在游戏实际尺寸中读取、可被 SCML 正确装配的透明 PNG。不要把“黑色描边加旧颜色”当作完整风格。

## 工作流

1. 定义资产职责。
   - 确认它是世界物体、生物部件、建筑、UI、装备 symbol、阴影还是 FX。
   - 记录游戏显示尺寸、观察角度、动画拆件、pivot、遮挡、状态变体和颜色主题。
2. 选择同类参考。
   - 至少选择 3 个同职责、同尺度、同材质或同动画拓扑的原版 PNG。
   - 优先参考同一 build 或相邻资产族，不从角色脸、UI 图标和水滴特效之间取平均风格。
3. 读取 [references/texture-style.md](references/texture-style.md)。
   - 画世界物体或生物时读取线稿、形体、明度、材质和拆件部分。
   - 画 FX、阴影或 UI 时读取对应例外部分。
4. 测量参考，而不是猜测。
   - 从技能目录运行：

     ```powershell
     python scripts/analyze_textures.py <reference.png-or-directory> --max-files 200 --summary-only
     ```

   - 用数据比较画布、有效边界、透明边、明暗和彩度，但不把全局中位数当成硬阈值。
5. 先解决轮廓和视角。
   - 在目标显示尺寸画黑白剪影，确认主体、朝向、重心和功能一眼可见。
   - 使用略夸张、不完全对称的比例和轮廓转折；保留结构逻辑，避免随意扭曲。
6. 建立手绘线稿。
   - 使用近黑色、粗细变化、轻微抖动和有选择的断线。
   - 在受力、接缝、遮挡和焦点处加重；在亮面和次要边缘减弱。
   - 用少量外伸短线、交叉线和材质刻痕增强触感，不给每条边均匀描边。
7. 铺设颜色与体积。
   - 先用少量大色块组织明暗，再加入有限的第二阶阴影、亮面和叙事焦点色。
   - 降低大面积彩度，让高彩度集中在眼睛、宝石、火焰、魔法或交互部件。
   - 让材质痕迹跟随形体和受力方向，不叠通用噪声滤镜。
8. 生成或编辑位图。
   - 用户要求实际生成或编辑光栅资产时，调用 `$imagegen`，把本 skill 的参考选择、视角、轮廓、线稿、配色、透明背景和拆件要求写进提示。
   - 对生成结果执行人工式清理：修正结构、减少无意义细节、统一线重、重画透明边和接缝。
   - 不用纯文本风格说明代替用户要求的图片产物。
9. 为动画拆件。
   - 按关节、遮挡变化、symbol 替换和独立运动拆分，不按颜色机械切块。
   - 每个部件保留完整描边与少量透明边；被遮挡处留足覆盖，不在动作中露缝。
   - 与 `$dst-make-scml-animation` 协同确定 pivot 和裁切框。
10. 检查并交付。
   - 在浅色、深色和棋盘背景检查透明边与白边。
   - 在 1x 游戏尺寸检查轮廓、焦点、材质和线条密度。
   - 与参考并排但不重叠比较，确认属于同一视觉世界且不是原资源复制品。

## 核心判断

- 轮廓先于内部纹理，功能先于装饰。
- 手绘感来自有控制的不规则，不来自随机噪点、全局扭曲或低分辨率锯齿。
- 近黑色既是外轮廓，也是阴影、接缝和材质信息；不要把黑色只当一圈边框。
- 填色保持图形化和分段明确，避免照片质感、柔滑 3D 渲染和大面积渐变塑料感。
- 资产族内部统一视角、比例、光源和线重；跨资产族只共享上层视觉语言。
- FX 和投影可以软、半透明、少描边；实体物不能因此丢失结构线。
- 空白 100x100 PNG 可能是 symbol 占位，不要把它误判为损坏或风格样本。

## 交付内容

同时交付或报告：

- 透明 RGBA PNG 及必要的分层或拆件版本；
- 目标画布、有效边界、pivot 或装配说明；
- 参考资产路径和取用的具体规律；
- 颜色、材质、状态变体与动画接缝说明；
- 1x 尺寸、浅深背景和分析器检查结果。
