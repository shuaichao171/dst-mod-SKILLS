# 饥荒联机版模组开发 Skills

面向 Codex 的《饥荒联机版》（Don't Starve Together，DST）模组开发 Skill 集合。项目将源码研究、模组脚手架、联机同步、玩法系统、世界生成、UI、资源管线、测试和发布等工作拆分为可独立选择的专项 Skill，让代理通过约定按任务范围加载最少且必要的开发规范。

当前收录 **48 个 Skill**。主要分类与职责速查见 [SKILL-CATALOG.md](./SKILL-CATALOG.md)。

## 设计原则

- **按任务选择**：只加载当前任务直接相关的 Skill，避免无关上下文干扰实现。
- **先读后做**：采取行动前完整读取所选目录中的 `SKILL.md`；任务范围变化时重新判断。
- **源码优先**：以本机当前版本的 DST Lua 源码为事实依据，不用旧教程或记忆替代 API 契约。
- **原版只读**：游戏源码仅供检索与验证，所有修改都应写入用户指定的 Mod 或本 Skill 工作区。
- **端别明确**：实现和验证时区分主机、远端客户端、专用服务器、洞穴分片、世界生成与前端环境。
- **证据闭环**：结论应能追溯到源码、日志或可重复的测试，并明确区分已验证事实与推断。

默认源码基线：

```text
D:\steam\steamapps\common\Don't Starve Together\data\scripts
```

## 接入方式：通过约定间接装载

本项目目前**没有直接安装或注册到 Codex 的 Skill 目录**，因此不依赖 Codex 自动发现这些 Skill。实际使用的是一条由 `AGENTS.md` 驱动的约定式装载链：

```text
用户提出 DST 任务
    ↓
Codex 读取全局 AGENTS.md
    ↓
AGENTS.md 要求先读取 DST.md
    ↓
DST.md 指向本项目目录，并要求按任务选择最少数量的 Skill
    ↓
Codex 完整读取所选目录的 SKILL.md 后再执行任务
```

当前机器使用以下两个约定文件：

```text
%USERPROFILE%\.codex\AGENTS.md
%USERPROFILE%\.codex\AGENTS_MD\DST.md
```

其中 `%USERPROFILE%` 表示当前 Windows 用户目录，例如 `C:\Users\<用户名>`。

全局 `AGENTS.md` 中负责转接到 DST 专项规则的内容是：

```markdown
## 专项规则

- 制作《饥荒》相关内容前，必须先阅读并遵循 `%USERPROFILE%\.codex\AGENTS_MD\DST.md`。
```

`DST.md` 再通过以下约定把任务路由到本项目：

```markdown
## 模组开发

- 编写《饥荒》模组前，必须根据具体内容选择并使用对应的技能。
- 《饥荒》模组技能目录：`D:\steam\steamapps\common\Don't Starve Together\饥荒模组SKILLS`
- 根据当前任务从目录中选择最少数量的相关 Skill；采取任务行动前，完整读取每个选中 Skill 的 `SKILL.md`。
- 不要读取与当前任务无关的其他 Skill。后续任务的内容发生变化时，重新判断需要使用的 Skill。
```

这样配置后，用户只需正常描述 DST 开发需求，无需写 `$dst-...`：

```text
帮我给这个武器增加一个有冷却时间的远程攻击，并检查联机同步。
```

代理应根据约定自行判断并读取最少数量的相关 Skill，例如战斗、动作或网络专项，然后再研究源码和实施修改。这里的“最少数量”并非固定一个；任务确实跨系统时可以组合，但不能预先加载整个目录。

如果项目移动到了其他位置，只需更新 `DST.md` 中的技能目录路径。若用于其他用户或机器，还应同步调整 `AGENTS.md` 中 `DST.md` 的绝对路径。

## 可选的显式指定

约定式间接装载是本项目的主要使用方式。需要锁定某个专项、复现固定流程或避免选择歧义时，也可以在请求中写出 `$技能名`；这里的名称用于指导代理定位本项目中的对应目录，并不表示该 Skill 已直接安装。

```text
使用 $dst-source-research 查找原版容器 Replica 的实现契约，并给出文件与行号。

使用 $dst-mod-scaffolding 创建一个所有客户端必装的服务器模组骨架。

使用 $dst-stategraph-authoring 为生物添加可安全中断的攻击状态。

使用 $dst-mod-review-refactoring 审查这个模组，先报告问题，不要直接修改。
```

也可以用英文指定：

```text
Use $dst-debugging-testing to diagnose the first relevant error in this DST mod log.
```

### 组合调用

跨系统需求应显式列出边界，避免代理自行扩大范围。例如新增一个带网络同步攻击动作的武器：

```text
使用 $dst-combat-weapons-projectiles、$dst-action-authoring 和 $dst-networking-rpc
实现该武器；先从原版查找最接近的范例，再修改我的 Mod，并列出仍需进游戏验证的项目。
```

不要为了“可能有用”一次加载大量 Skill。编排型 Skill（如 `dst-creature-boss-authoring`、`dst-character-authoring`）负责组织跨系统工作，但不会取代 Brain、StateGraph、网络、保存等底层专项 Skill。

## 选择指南

| 需求 | 优先选择 |
| --- | --- |
| 查 API、原版范例或调用链 | `dst-source-research` |
| 新建模组、入口文件或配置项 | `dst-mod-scaffolding` |
| Prefab、组件与生命周期 | `dst-prefab-authoring`、`dst-component-authoring`、`dst-events-tasks-lifecycle` |
| 动作、状态图与 AI | `dst-action-authoring`、`dst-stategraph-authoring`、`dst-brain-authoring` |
| netvar、Replica 或 RPC | `dst-networking-rpc` |
| 保存、加载与旧档迁移 | `dst-persistence-migration` |
| 报错、不同步或回归测试 | `dst-debugging-testing` |
| 审查现有模组 | `dst-mod-review-refactoring` |
| 游戏更新后的兼容性评估 | `dst-api-update-diff` |
| Steam 创意工坊发布 | `dst-workshop-release` |
| 绘制或审计人物 SCML 部件 | `dst-character-parts`、`dst-make-scml-animation` |
| 分析或统一贴图风格 | `dst-texture-style` |

玩法、世界、UI、资源等细分领域请查阅 [Skill 总目录](./SKILL-CATALOG.md)。

## 目录结构

```text
饥荒模组SKILLS/
├── README.md
├── SKILL-CATALOG.md
└── dst-<领域>/
    ├── SKILL.md              # 触发描述、工作流、不变量与验证标准
    ├── agents/openai.yaml    # 展示信息与默认调用提示（可选）
    ├── references/           # 需要时读取的详细契约（可选）
    ├── assets/               # 可复用模板和资源（可选）
    └── scripts/              # 确定性检查或生成脚本（可选）
```

每个 `SKILL.md` 保持短而可执行；较长的技术说明放在 `references/`，可复用起点放在 `assets/`，适合自动检查的流程放在 `scripts/`。这些按需资源只有在当前任务需要时才应读取或运行。

## 推荐入门顺序

1. 用 `dst-source-research` 学会从当前游戏源码确认事实。
2. 用 `dst-mod-scaffolding` 建立正确的入口和元数据。
3. 依次理解 Prefab、Component、事件生命周期与 Lua 运行环境。
4. 再学习网络、保存、Action、StateGraph 和 Brain。
5. 最后按模组类型选择玩法、世界、UI 或资源专项 Skill。
6. 用 `dst-debugging-testing` 建立可重复的验证流程。

## 使用约束

- 不直接修改 `data/scripts` 下的游戏文件。
- 访问全局对象时先确认字段存在；直接读取 `GLOBAL.XXXX` 可能触发 `__STRICT` 检查。
- 不把静态检查表述为游戏内测试通过。
- 涉及日志时优先保留第一条有效错误和完整堆栈，不用后续连锁报错替代根因。
- 涉及发布、存档变更或其他不可逆操作时，先确认目标与风险。

## 维护约定

新增或调整 Skill 时，应同步检查：

1. `SKILL.md` 的 `name` 与目录名一致，`description` 能覆盖真实触发场景。
2. 工作流、不变量和验证标准具体且可执行。
3. `references/`、`assets/`、`scripts/` 只承载按需内容，并在 `SKILL.md` 中提供入口。
4. `agents/openai.yaml` 的展示名称、简述和默认提示与 Skill 职责一致。
5. [SKILL-CATALOG.md](./SKILL-CATALOG.md) 中的分类、数量和职责说明已同步更新。
