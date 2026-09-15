# 模组入口与标志

## 入口

| 文件 | 环境 | 典型职责 |
| --- | --- | --- |
| modinfo.lua | 元数据沙箱 | 名称、版本、兼容、配置、依赖 |
| modmain.lua | 游戏运行时 | Prefab、Asset、Hook、RPC、配方 |
| modworldgenmain.lua | 世界生成；建服前端也会部分加载 | TaskSet、Task、Room、Level、Tile、预设与世界选项 |
| modservercreationmain.lua | 建服前端部分加载 | 建服界面与服务器创建相关注册 |

当前 mods.lua 不加载 modfrontendmain.lua。普通客户端运行时逻辑仍放在 modmain.lua。只创建实际需要的入口；modworldgenmain.lua 不能依赖 TheWorld 或玩家，modservercreationmain.lua 通常也没有运行中的世界。

## modinfo 环境限制

modinfo.lua 由 `ModIndex:InitializeModInfo`（modindex.lua，搜索 `InitializeModInfo`）用 `kleiloadlua` + `setfenv` 执行，环境是**没有任何元表的裸表**，只提供三个成员：

- `folder_name`：模组文件夹名
- `locale`：当前语言代码（如 zh/zhr/en）
- `ChooseTranslationTable(tbl)`：按 locale 取翻译表

因此标准库全部不可用：`ipairs`、`pairs`、`next`、`table.*`、`string.*`（作为全局库）、`math.*`、`tostring`、`tonumber`、`print`、`setmetatable`、`type`、`os.*`、`require` 等一律是 nil。调用会报 `attempt to call global 'ipairs' (a nil value)`。

modinfo 里安全的构造（工作坊流行模组实际在用）：

```lua
-- 数值 for + # + 直接下标赋值（不用 ipairs/table.insert）
for i = 1, #options do
    configuration_options[#configuration_options + 1] = options[i]
end

-- 字符串值自带元表：方法调用和库函数都能用
local s = "abc"
local u = s:upper()          -- 可用
local f = ("x%s"):format(1) -- 可用

-- GP 的遮蔽技巧：让 string.char 这类库名也可用
local string = ""
local ch = string.char(65)  -- A：解析到局部字符串值，再走元表取库
```

注意事项：

- modmain 的环境在设置 `__index → GLOBAL` 继承后标准库可用，该限制仅针对 modinfo；从 modmain 复制代码到 modinfo 时要改写。
- 工作坊模组 modinfo 里的 `env.pairs`、`env.require` 等调用（如 Epic Healthbar 的 `SetLocaleMod(env)`）位于需要外部传入运行时环境的函数内，modinfo 加载时从不执行；不能当作 modinfo 沙箱可用的证据直接照抄。同理 `DoInit(locale, env)` 在文件尾部只传 locale，env 为 nil，其 `env.MergeMapsDeep` 分支同样不会走。
- 需要按 locale 生成选项时（如 Epic Healthbar 的 DoInit(locale)），只能用上述安全构造实现。
- 语言无关的辅助函数（拼接 description/data 表）是允许的；限制针对的是标准库，不是函数定义本身。

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
