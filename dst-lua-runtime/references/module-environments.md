# 模组入口与模块环境

## 加载契约

| 加载方式 | 执行环境 | 返回值与缓存 | 适合内容 |
| --- | --- | --- | --- |
| modmain.lua、modworldgenmain.lua、modservercreationmain.lua | mods.lua 创建的模组环境；含 GLOBAL 和该入口可用的注册 API | 入口返回值不作为模块接口 | 声明、配置与注册 |
| modimport | 与调用入口相同的模组环境 | 丢弃返回值；不使用 package.loaded 缓存 | 依赖 AddAction、AddComponentAction、PostInit 等模组 API 的注册文件 |
| require | Lua 全局模块环境 | 返回模块值；按模块名写入 package.loaded | Prefab、Component、Replica、Brain、StateGraph、Widget 与普通库 |

mods.lua 为模组入口显式设置环境，并让 modimport 对目标块再次 setfenv。普通 require 仍走全局 package loader；entityscript.lua 也用 require 加载 Component、Replica 与 StateGraph。

## 编写规则

- 在 require 模块中直接使用 Class、TheWorld、net_bool、State、FRAMES 等游戏全局，并用 require 加载依赖。不要假设 GLOBAL 存在。
- 在模组入口和 modimport 注册文件中直接调用该环境注入的 Add、Register、PostInit 等 API；访问未注入的游戏全局时使用 GLOBAL。
- 模组入口只注入有限的 Lua 标准函数；使用 assert、tonumber 等未注入函数时也要从 GLOBAL 局部化。后处理注册同理：AddModShadersInit 会被注入，但 resolvefilepath、hash 和后处理枚举不会；PostProcessor 还会晚于 modmain 创建，必须在 Shader 回调实际执行时从 GLOBAL 读取。
- 入口或 modimport 文件中的 GetModConfigData(optionname, get_local_config) 会自动绑定当前 env.modname。require 模块调用全局 GetModConfigData 时必须传入 modname；更稳妥的做法是在 modmain.lua 读取配置后把纯值传给模块。
- 让 require 模块显式 return 类、表或函数。某些原版 behaviour 文件只注册全局类而不返回值；先单独 require，再使用其全局名。
- 在 modmain.lua 尽早执行 AddReplicableComponent、动作和 SG 钩子等注册，避免相关实体或模块先被实例化。

## 选择示例

- scripts/components/mod_state.lua：由 AddComponent 间接 require，直接使用 Class。
- scripts/stategraphs/SGmod_entity.lua：由 SetStateGraph 间接 require，直接使用 StateGraph 与 ACTIONS。
- scripts/register_mod_action.lua：需要 AddAction，使用 modimport 从 modmain.lua 执行，不依赖 return。
