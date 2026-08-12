---
name: dst-source-research
description: Research and trace Don't Starve Together Lua source. Use when locating vanilla implementations, mapping prefab, component, brain, stategraph, action, UI, or world-generation relationships, finding native API call sites, or verifying a mod design against the installed data/scripts tree.
---

# DST 源码研究与调用链追踪

以当前安装的 Lua 源码为事实基础，先建立可复查的证据链，再提出实现或修改方案。

## 工作流

1. 确认源码根目录。默认使用 D:\steam\steamapps\common\Don't Starve Together\data\scripts；先验证 main.lua、modutil.lua 与目标子目录存在。
2. 把问题归入 Prefab、Component、Brain、Behaviour、StateGraph、Action、Network、UI、Worldgen 或引擎原生绑定，再缩小搜索范围。
3. 先用 rg --files 找候选文件，再用 rg -n 搜符号定义、require、构造调用、标签、事件和组件名；避免直接倾倒整个大文件。
4. 从入口沿 require、Class、Prefab、AddComponent、ListenForEvent、SetBrain、SetStateGraph 和 ActionHandler 追踪到实际执行点。
5. 至少比较一个最接近的原版实现；高风险机制比较两个以上，并说明选择该范例的理由。
6. 找不到 Lua 定义时，将方法视为引擎绑定；搜索所有调用点、参数形态和前后生命周期，不虚构 C++ 契约。
7. 输出精确文件与行号、已验证事实、基于调用点的推断，以及仍未解决的问题。

## 源码锚点

- modutil.lua、mods.lua、modindex.lua：模组环境、入口和公开扩展钩子。
- entityscript.lua、prefabutil.lua、standardcomponents.lua、prefabs/、components/：实体与组件。
- brain.lua、behaviourtree.lua、brains/、behaviours/、stategraph.lua、stategraphs/：AI 与 SG。
- actions.lua、componentactions.lua、bufferedaction.lua、netvars.lua、networkclientrpc.lua：动作与联机。
- map/、widgets/、screens/：世界生成和 UI。

## 不变量

- 只读扫描 data/scripts；所有实现改动都落在用户指定的 Mod 或 Skill 工作区。
- 以当前安装版本为准，不把旧教程或记忆当作最终 API 契约。
- 区分定义、调用、推断和未知项；不要把一次调用样例表述成通用保证。
- 搜索结果过多时按目录、文件类型和符号组合继续收窄。

## 验证

- 每个关键结论都能回到源码文件或可重复的搜索命令。
- 已检查主机、客机、分片或前端上下文是否改变结论。
- 已记录当前源码根目录和研究日期，便于游戏更新后复查。

## 按需资源

- 运行 `powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/scan-dst-source.ps1 -Mode Summary` 生成结构清单；文件检索传 `-Mode Files -Glob <glob>`，符号检索传 `-Mode Symbol -Pattern <pattern>`。Files 或 Symbol 无匹配时脚本会给出明确消息并成功退出。显式的进程级 Bypass 只作用于本次命令，可兼容禁止直接执行本地 `.ps1` 的 Windows 环境。
- 需要搜索策略和原生 API 边界时读取 references/source-research.md。
