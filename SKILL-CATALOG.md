# DST Mod Skills Catalog

本工作区包含 48 个可独立触发的 Codex Skill。源码基线为 `DST_DATA_DIR` 下的 `scripts/`；本机实际路径以工作流私有路径配置为准。

所有 Skill 都把游戏源码视为只读参考；实际修改应落在用户指定的 Mod 目录。

## 核心基础

| Skill | 职责 |
| --- | --- |
| dst-source-research | 搜索源码、追踪调用链和原版范例 |
| dst-mod-scaffolding | modinfo 与各入口脚手架 |
| dst-lua-runtime | Class、GLOBAL、模块和调度环境 |
| dst-hooking-compatibility | PostInit、包装和模组兼容 |
| dst-prefab-authoring | 网络安全的 Prefab 构造 |
| dst-component-authoring | Component、Replica 与生命周期 |
| dst-events-tasks-lifecycle | 事件、任务、睡眠和清理 |
| dst-networking-rpc | netvar、Replica 与三类 RPC |
| dst-persistence-migration | 保存、加载、引用和迁移 |
| dst-action-authoring | Action、ComponentAction、BufferedAction |
| dst-stategraph-authoring | SG 状态、时间线和预测 |
| dst-brain-authoring | Brain 与 Behaviour Tree |
| dst-debugging-testing | 日志、最小复现和测试矩阵 |

## 常用玩法

| Skill | 职责 |
| --- | --- |
| dst-inventory-equipment-containers | 物品、装备、耐久与容器 |
| dst-combat-weapons-projectiles | 战斗、武器、护甲与弹道 |
| dst-creature-boss-authoring | 生物和 Boss 跨系统编排 |
| dst-character-authoring | 可玩角色跨系统编排 |
| dst-skilltree-authoring | 角色技能树 |
| dst-crafting-tech-prototypers | 配方、科技与制作站 |
| dst-food-cooking | 食物、料理与食谱书 |
| dst-building-deployment-physics | 建筑、部署、Placer 与物理 |
| dst-status-buffs-survival | 生存属性、Buff 与 Debuff |
| dst-followers-mounts-pets | 随从、宠物和坐骑 |
| dst-plants-farming-regrowth | 植物、农作物与再生 |
| dst-world-systems-events-weather | 世界系统、事件和天气 |
| dst-ocean-boats-fishing | 海洋、船和海钓 |

## 世界、UI 与资源

| Skill | 职责 |
| --- | --- |
| dst-worldgen-authoring | TaskSet、Task、Room 与拓扑 |
| dst-worldgen-layouts-retrofit | Static Layout、Setpiece 与旧世界补丁 |
| dst-tiles-map-minimap | 地皮、地图和小地图 |
| dst-shards-caves-portals | 分片、洞穴与迁移 |
| dst-scenarios-setpieces-cutscenes | 场景、布景与演出 |
| dst-ui-widget-authoring | Widget、布局与焦点 |
| dst-hud-screens-input | HUD、Screen 与输入 |
| dst-client-frontend-mods | 纯客户端和建服前端扩展 |
| dst-assets-animation-atlas | 动画、Build、Atlas 与纹理 |
| dst-character-parts | 按 Spriter/SCML 模板制作与审计人物透明 PNG 部件 |
| dst-make-scml-animation | 制作与审计 SCML 动作、时序、引用和编译兼容性 |
| dst-texture-style | 分析原版贴图并制作与参考一致的纹理风格 |
| dst-fx-vfx-authoring | FX 与粒子 |
| dst-audio-camera-effects | 音频与相机表现 |
| dst-localization-speech | 本地化与角色台词 |
| dst-skins-symbol-overrides | 模组外观变体和 Symbol |
| dst-shader-authoring | Shader、VFX 与后处理管线 |

## 工程化

| Skill | 职责 |
| --- | --- |
| dst-performance-profiling | 性能测量与优化 |
| dst-dedicated-server-testing | 通用无头测试、专服与多分片验证；含隔离启动、用例驱动、判定、复测与清理 |
| dst-workshop-release | 候选包和授权发布 |
| dst-api-update-diff | 游戏更新后的源码快照和影响分析 |
| dst-mod-review-refactoring | 证据驱动的审查与重构 |

## 推荐顺序

先掌握 source-research、mod-scaffolding、prefab、component、events、networking、persistence、action、stategraph、brain 和 debugging。再按具体模组加载玩法或世界/UI Skill。

creature-boss-authoring 与 character-authoring 是编排型 Skill；它们依赖多个核心原语，不替代对应的 Brain、SG、网络和保存 Skill。

## 调用

显式调用示例：

    Use $dst-stategraph-authoring to add an interrupt-safe attack state.
    Use $dst-source-research to find the vanilla contract for container replicas.
    Use $dst-mod-review-refactoring to audit this mod before changing it.

每个 Skill 的 SKILL.md 保持短工作流；详细契约、模板和确定性脚本按需放在 references、assets 与 scripts。
