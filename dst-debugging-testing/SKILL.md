---
name: dst-debugging-testing
description: Diagnose and test Don't Starve Together mods. Use when investigating load errors, Lua stack traces, nil access, crashes, desync, missing assets, broken actions, save corruption, dedicated-server differences, cave or shard failures, or when building a repeatable multiplayer regression matrix.
---

# DST 调试与测试

先保留第一条有效错误和最小复现，再按加载阶段、运行端与生命周期定位根因。

## 工作流

1. 记录游戏版本、启用模组、配置、世界类型、主机/客户端/分片、复现步骤和预期行为。
2. 从日志中提取第一条相关错误、完整堆栈和前置警告；后续连锁 nil 通常不是根因。
3. 按 modinfo 加载、入口加载、Prefab 构造、运行时事件、网络、保存、资源或性能分类。
4. 用最小世界和最少模组复现；冲突问题用二分启用或交换加载顺序。
5. 沿堆栈进入模组代码，再用当前 data/scripts 查原版调用契约；不要只在报错行加 nil 判断。
6. 添加带模组前缀、实体 GUID、端类型和状态的临时日志；高频路径做限流。
7. 修复后按受影响行为选择主机、远端客户端、专服、洞穴、保存重载和目标生命周期回归，并移除临时噪声日志。引擎运行逻辑适合自动验证时，使用无头测试流程；图形与网络行为追加对应客户端验证。

## 源码锚点

- stacktrace.lua、debugprint.lua、debughelpers.lua：堆栈与调试输出。
- consolecommands.lua、debugcommands.lua、debugkeys.lua：控制台和诊断入口。
- profiler.lua、perfutil.lua：性能诊断。
- mods.lua、modindex.lua：加载阶段错误。

## 不变量

- 不要把未亲自启动的游戏、专服或图形资源测试描述为已通过。
- 不要用吞错、pcall 包裹整段逻辑或无条件 nil return 掩盖状态损坏。
- 先使用只读控制台检查；会生成、删除、回滚或改存档的命令需明确风险。
- 日志中避免输出用户身份、令牌或大表。

## 验证

- 修复能解释第一条错误为何发生，而非只消除最后一个症状。
- 最小复现和原始复现都不再出现问题。
- 测试结果明确区分已执行、静态检查和仍需用户在游戏中验证。

## 静态检查脚本

`scripts/dst_lua_check.py <模组目录>`（`--json` 输出完整报告，`--with <依赖模组>` 可重复）：

- **Lua 5.1 语法**：优先用 lupa 自带的 Lua 5.1 编译（与游戏同版本，只编译不执行），没有时用 luaparser。默认只扫游戏会加载的范围（根目录 `*.lua`、`scripts/`、`modimport` 引用的文件），`--all` 扫全部；`_ai_work/` 总是排除。
- **组件方法声明**：核对 `components.X:Method(` / `replica.X:Method(` 能否在模组自己的组件、依赖模组或原版源码（默认读 `DST_GAME_HOME` 的 scripts.zip）里找到定义，含别名赋值和 `Class(Base, ...)` 父类。`DECLARED` 只说明方法存在，不检查端别和参数；`NEEDS_REVIEW` 要人工追踪（引擎原生组件、补丁、拼写），不等于 Bug。最有价值的两类提示是“主组件有、replica 没有”和“只有 replica 有”。
- 退出码：有语法错误为 1；`--strict` 时 NEEDS_REVIEW 也为 1。离线测试：`python -m unittest discover -s dst-debugging-testing/tests`。

静态检查通过只说明能编译、调用的方法有定义，不能证明运行行为；报告里与无头测试、客户端验证分开写。

## 按需资源

- 需要系统化覆盖时读取 references/test-matrix.md。
- 需要原生无头复现或自动回归时，完整阅读 [../dst-dedicated-server-testing/SKILL.md](../dst-dedicated-server-testing/SKILL.md)，再使用其通用无头流程。

