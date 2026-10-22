# 用户命令与投票（AddUserCommand）

以下结论来自 `modutil.lua`、`usercommands.lua`、`builtinusercommands.lua`、`networking.lua`、`mods.lua` 和 `constants.lua`，游戏更新后先重新核对。

> 示例里的 modmain 代码假设已经按 dst-mod-scaffolding 在文件顶部设置了 `__index → GLOBAL` 环境继承。没有设置时，入口环境里未注入的全局变量（如 COMMAND_PERMISSION）要从 `GLOBAL` 读取。`VoteUtil` 不是全局变量，任何情况下都要 `local VoteUtil = require("voteutil")`。

## AddUserCommand

```lua
-- modmain.lua
AddUserCommand("mymod_home", {
    aliases = { "home" },
    prettyname = "回家",                 -- 不写时查 STRINGS.UI.BUILTINCOMMANDS.<NAME>.PRETTYNAME，模组命令通常没有这条字符串
    desc = "传送回出生点。",
    permission = COMMAND_PERMISSION.USER, -- USER / MODERATOR / ADMIN
    slash = true,                         -- 允许在聊天框输入 /mymod_home
    usermenu = false,                     -- true 时出现在玩家列表里对某人的菜单中，并自动提供 params.user
    servermenu = true,                    -- 出现在玩家状态界面的服务器菜单中
    menusort = 10,
    params = {},
    vote = false,
    serverfn = function(params, caller)
        -- caller 可能不是实体：玩家不在世界中时是客户端信息表
        if caller == nil or caller.IsValid == nil or not caller:IsValid() then
            return
        end
        -- 在这里重新校验状态、冷却和目标
    end,
})
```

### 执行流程

1. 客户端在聊天框输入 `/命令`（`screens/chatinputscreen.lua`），或在菜单里点击，进入 `RunTextUserCommand(..., ThePlayer, false)` 或 `RunUserCommand`。
2. `getexectype` 依次检查 `hasaccessfn`、`permission`、`canstartfn`、投票状态等，得到 ALLOW、VOTE、DENY、DISABLED 或 INVALID。
3. ALLOW 时，客户端执行 `localfn`；有 `serverfn` 的话，通过 `TheNet:SendSlashCmdToServer` 把命令文本发给服务器。
4. 服务器由 `Networking_SlashCmd` 再解析一次命令，**再检查一次权限**，然后执行 `serverfn(params, caller)`。这时 `caller` 是 `Ents[guid]`，如果实体不存在，则是 `TheNet:GetClientTableForUser(userid)` 返回的表。
5. 有 `confirm = true` 时，客户端会先弹出确认框。

### 要点

- `localfn` 只在发起者的客户端执行，适合本地 UI 或表现；会改变世界的逻辑一律放进 `serverfn`。
- 参数都是字符串：`params` 按顺序命名，`paramsoptional` 标记可省略的参数，多出来的词拼成 `params.rest`。`params.user` 会被当作目标玩家解析（名字、userid 或玩家编号），解析不了时命令会失败。
- 命令名和别名用 `smallhash` 存放，并按模组分别保存，仍然要加前缀，以免和原版或其他模组的命令冲突。
- 客户端必须能找到命令定义才会解析并发送。只装在服务器上的模组（`all_clients_require_mod = false`），客户端输入的 `/命令` 很可能根本发不到服务器。这是从代码路径推断的，需要用未安装模组的客户端实测确认。
- `hasaccessfn(command, caller, targetid)` 控制谁能看到和使用命令；`canstartfn` 返回 `false, reason` 时命令显示为禁用。

## 投票命令

带投票的命令仍然用 `AddUserCommand` 定义，原版 `kick` 就是这样：

```lua
vote = true,
votetimeout = 30,
voteminstartage = 20,        -- 发起者的最小游戏时长（天）
voteminpasscount = 3,        -- 最少参与人数
votecountvisible = true,
voteallownotvoted = true,
voteoptions = nil,           -- 默认 { "Yes", "No" }
votecanstartfn = VoteUtil.DefaultCanStartVote,   -- local VoteUtil = require("voteutil")
voteresultfn = VoteUtil.YesNoMajorityVote,
localfn = function(params, caller)
    -- 投票通过后执行时 caller 可能是 nil
end,
```

- 投票需要 `TheWorld.net.components.worldvoter` 已启用，发起者也要有 `playervoter`。条件不满足时结果为 INVALID 或 DENY。
- **`AddVoteCommand` 实际上已经没有作用**：它只把数据写入模组环境的 `vote_commands`。读取它的 `ModWrangler:GetVoteCommands()` 在当前脚本里没有任何调用者。新代码不要用它；审查时如果看到它，说明该投票功能实际不会生效。
