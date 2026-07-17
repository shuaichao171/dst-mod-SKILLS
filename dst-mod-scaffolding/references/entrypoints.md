# 模组入口与标志

## 入口

| 文件 | 环境 | 典型职责 |
| --- | --- | --- |
| modinfo.lua | 元数据沙箱 | 名称、版本、兼容、配置、依赖 |
| modmain.lua | 游戏运行时 | Prefab、Asset、Hook、RPC、配方 |
| modworldgenmain.lua | 世界生成；建服前端也会部分加载 | TaskSet、Task、Room、Level、Tile、预设与世界选项 |
| modservercreationmain.lua | 建服前端部分加载 | 建服界面与服务器创建相关注册 |

当前 mods.lua 不加载 modfrontendmain.lua。普通客户端运行时逻辑仍放在 modmain.lua。只创建实际需要的入口；modworldgenmain.lua 不能依赖 TheWorld 或玩家，modservercreationmain.lua 通常也没有运行中的世界。

## 安装模型

| 模型 | client_only_mod | all_clients_require_mod | 客户端安装含义 |
| --- | --- | --- | --- |
| 纯客户端 UI | true | false | 服务器不安装也可使用 |
| 所有客户端必装内容 | false | true | 服务器要求客户端安装并核对版本 |
| 服务器逻辑且客户端无需资源或代码 | false | false | 服务器不强制客户端安装 |

当前 Lua 加载器不识别 server_only_mod。client_only_mod 与 all_clients_require_mod 互斥；两者均为 false 只表示不强制客户端安装，并不能让依赖客户端 Prefab、资源、RPC 或 UI 的内容自动兼容。

## 配置

configuration_options 的 name 是稳定键。选项 data 类型应与 GetModConfigData 的消费逻辑一致。修改或删除已发布键时，为旧配置值提供回退。

## 最小加载检查

1. modinfo 可解析。
2. 模组列表显示正确版本。
3. 默认配置启动。
4. 每个非默认配置启动。
5. 禁用模组后旧世界仍能进入，或明确说明依赖。
6. 专服与远端客户端符合安装模型。
