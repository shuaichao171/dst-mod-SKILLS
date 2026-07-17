---
name: dst-character-authoring
description: Create and maintain playable Don't Starve Together characters. Use when adding a mod character, player prefab, stats, starting inventory, character strings and speech, portraits and minimap assets, custom actions, stategraph hooks, skill trees, character-specific UI, save data, or multiplayer spawn behavior.
---

# DST 可玩角色编排

围绕玩家 Prefab 的公共初始化、主机初始化、客户端表现和角色专属系统分层实现。

## 工作流

1. 定义角色规格：基础属性、优势、弱点、初始物品、专属动作、制作、技能树、语音、资源和存档状态。
2. 对照 prefabs/player_common.lua 与至少一个机制相近的原版角色，使用玩家构造助手创建 Prefab。
3. 在所有端初始化 AnimState、标签、网络变量、地图图标和客户端表现；在主机初始化组件数值、物品、监听和保存状态。
4. 只调用一次 AddModCharacter(name, gender, modes) 注册角色；显式传入 FEMALE、MALE、ROBOT、NEUTRAL 或 PLURAL 之一，避免 nil 的警告和默认 NEUTRAL。补齐 STRINGS.CHARACTER_NAMES[name]、STRINGS.CHARACTER_DESCRIPTIONS[name]、STRINGS.CHARACTER_QUOTES[name] 与角色 speech 文件；只有实际提供皮肤时才添加相应 STRINGS.SKIN_NAMES 键。
5. 优先向 SGwilson 和客户端 SG 添加状态、事件或 ActionHandler，不复制整份玩家 SG。
6. 专属制作使用角色过滤器、builder_tag 或 builder_skill；技能树按 skilltree Skill 的数据和同步流程接入。
7. 测试新建角色、重选角色、死亡复活、换洞穴、断线重连、保存重载、不同客户端资源和手柄 UI。

## 源码锚点

- prefabs/player_common.lua、characterutil.lua：玩家 Prefab 与公共行为。
- 各原版角色 Prefab、speech_*.lua 和 skilltree_*.lua。
- stategraphs/SGwilson.lua 与客户端玩家 SG。
- widgets/、screens/redux/：角色选择、HUD 和技能树 UI。
- modutil.lua：AddModCharacter、AddCharacterRecipe 与技能树图集注册。

## 不变量

- 主机属性和客户端视觉初始化分开，不能在客户端访问服务器组件。
- 不要整文件覆盖 SGwilson、字符串表或玩家公共函数。
- 角色资源名、Prefab 名和字符串键保持一致并使用唯一前缀。
- 重生或换角色时清理旧角色拥有的世界监听、子实体和 UI。

## 验证

- 角色在主机、专服客户端和洞穴中均能选择、生成和重连。
- 死亡、复活、换人、保存重载后专属状态不重复或丢失。
- 缺少可选皮肤、技能或配置时仍能使用基础角色。
