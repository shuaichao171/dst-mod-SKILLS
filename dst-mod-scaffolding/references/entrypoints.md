# 模组入口与标志

## 入口

| 文件 | 环境 | 典型职责 |
| --- | --- | --- |
| modinfo.lua | 元数据沙箱 | 名称、版本、兼容、配置、依赖 |
| modmain.lua | 游戏运行时 | Prefab、Asset、Hook、RPC、配方 |
| modworldgenmain.lua | 世界生成 | TaskSet、Task、Room、Level、Tile |
| modfrontendmain.lua | 前端 | 主菜单与 FrontEnd Screen |

只创建实际需要的入口。世界生成入口不能依赖 TheWorld 或玩家；前端入口通常没有运行中的世界。

## 安装模型

| 模型 | client_only_mod | all_clients_require_mod | server_only_mod |
| --- | --- | --- | --- |
| 纯客户端 UI | true | false | false |
| 所有客户端必装内容 | false | true | false |
| 服务器逻辑且客户端无需资源 | false | false | true |

这些标志不要互相矛盾。实际行为仍需在当前 mods.lua 和 modindex.lua 中复核。

## 配置

configuration_options 的 name 是稳定键。选项 data 类型应与 GetModConfigData 的消费逻辑一致。修改或删除已发布键时，为旧配置值提供回退。

## 最小加载检查

1. modinfo 可解析。
2. 模组列表显示正确版本。
3. 默认配置启动。
4. 每个非默认配置启动。
5. 禁用模组后旧世界仍能进入，或明确说明依赖。
6. 专服与远端客户端符合安装模型。

