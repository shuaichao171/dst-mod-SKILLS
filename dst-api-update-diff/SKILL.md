---
name: dst-api-update-diff
description: Compare Don't Starve Together Lua source across game updates and assess mod compatibility. Use when a new DST build changes data/scripts, when checking removed or changed functions, components, stategraphs, brains, actions, netvars, world-generation data or UI classes, or when generating a source snapshot and migration report.
---

# DST API 更新差异分析

保存轻量源码快照，按公共钩子、签名、调用点和模组依赖分层比较，不修改游戏源码。

## 工作流

1. 确定旧版与新版 data/scripts 根目录，或使用此前由脚本生成的快照；记录游戏构建与日期。
2. 运行 scripts/snapshot-dst-source.ps1 生成文件哈希、声明式与赋值式 Lua 函数、Prefab、组件、Brain、SG 和关键 API 索引，再用 scripts/compare-dst-snapshots.ps1 生成文件级变化表。
3. 比较新增、删除、重命名和内容变化，先检查 modutil.lua、entityscript.lua、networkclientrpc.lua 等公共边界。
4. 针对目标模组搜索其使用的函数、字段、组件、事件、标签和原版 Prefab，建立受影响清单。
5. 对内容变化文件做语义检查：参数、返回值、主客机分支、保存结构、状态名和调用顺序。
6. 按必然破坏、高风险、行为变化、低风险和未影响分类，并给出最小迁移与回归测试。
7. 更新基线前保留旧快照和报告，直到目标模组在新版本完成验证。

## 源码锚点

- modutil.lua、mods.lua、entityscript.lua、stategraph.lua、brain.lua。
- actions.lua、componentactions.lua、netvars.lua、networkclientrpc.lua。
- prefabs/、components/、brains/、stategraphs/、map/、widgets/。
- 目标模组自身的 require、hook、字段和字符串使用点。

## 不变量

- 快照和比较只读访问游戏 data/scripts。
- 文件哈希变化不等于 API 破坏，必须检查目标调用契约。
- 函数索引必须覆盖 function Name(...) 与 Name = function(...) 两种常见定义形式；抽查 modutil.lua 中的 env.Add* 包装器，避免漏掉模组公开边界。
- 不要把内部字段稳定性等同于公开 API 保证。
- 无法获得旧源码时明确基线限制，不伪造差异。

## 验证

- 报告中的每项影响都能链接到差异文件和模组使用点。
- 关键网络、存档、SG 与世界生成变化有专门回归项。
- 脚本在不存在目录、空目录和相同目录时给出明确结果。

## 按需资源

- 运行 scripts/snapshot-dst-source.ps1 生成可比较快照。
- 运行 scripts/compare-dst-snapshots.ps1 比较两个快照。
- 需要影响分级时读取 references/update-assessment.md。
