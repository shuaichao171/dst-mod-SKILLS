---
name: dst-dedicated-server-testing
description: Run isolated native headless tests for Don't Starve Together mods and validate dedicated servers or multi-shard clusters. Use for automated in-engine regressions, runtime behavior, startup and shutdown, saves, Master and Caves, or dedicated-server and remote-client integration.
---

# DST 无头测试、专用服务器与多分片验证

根据要验证的行为选择运行端。无头测试使用原生专服运行游戏逻辑；Master、Caves 和真实客户端分别记录进程、配置与结果。

## 选择测试方式

| 目标 | 方式 |
| --- | --- |
| 组件、动作、AI、状态机、碰撞、世界逻辑、存档的自动回归 | 原生无头专服与测试驱动；先完整读 [references/headless-workflow.md](references/headless-workflow.md) |
| 洞穴、分片通信、迁移与分片持久化 | 按需启动 Master、Caves，分别记录日志；需要自动执行时同时使用通用无头流程 |
| 模组握手、RPC、Replica、预测、重连与多人行为 | 专服加真实客户端，按目标覆盖网络条件 |
| 贴图、UI、音画表现 | 追加有渲染的客户端验证，无头结果只说明相关服务端逻辑 |

只启动覆盖当前改动所需的端与场景；单分片无头用例不要求额外启动 Caves 或图形客户端。

## 无头测试脚本

单分片离线回归直接用 `scripts/dst_headless_run.py`，不要每次重写控制器：

```text
python scripts/dst_headless_run.py --mod <依赖模组> --mod <被测模组> --behavior <用例.lua> --out <目标项目>/_ai_work/headless
```

- 每次生成唯一 run_id；被测模组以 SHA-256 清单校验后复制到 `mods/_altwf_<run_id>_<n>`，另生成测试驱动模组；独立集群、独立 ugc 目录、仅局域网合法端口（10998–11018）。
- 行为脚本用全局 `TEST`：`Check / Equal / Near / Metric / Log / Spawn / After / Invalid / Done`，全部断言之后必须 `TEST.Done()`。
- 判定：passed / failed（断言失败、脚本报错或就绪后日志出现 LUA ERROR）/ invalid（被测模组没加载、标记无效或零断言）/ interrupted（超时或进程提前退出）。结果在 `<out>/<run_id>/results/result.json` 与 `events.jsonl`，原始日志在 `logs/`。
- 结束时发 `c_shutdown(false)`，超时才终止本次启动的进程；默认删除本次复制到 `mods/` 的快照（`--keep-staged` 保留）。`--list-stale` / `--remove-stale` 只处理本工具前缀 `_altwf_` 的遗留目录。
- 用 `--mod-config` 传配置项，`--allow-sandbox-escape` 仅在模组确需读写集群目录外文件时使用。洞穴、多分片和真实客户端仍按下方工作流手工编排。
- 离线测试（假专服）：`python -m unittest discover -s dst-dedicated-server-testing/tests`；真机冒烟样例：`tests/fixtures/sample_mod` + `tests/fixtures/smoke_behavior.lua`（build 761239 实测约 80 秒通过）。

## 工作流

1. 确认游戏版本、模组与依赖、运行端、预期结果和测试范围；本机路径从工作流私有配置读取。
2. 核对 modinfo 的 client_only_mod、all_clients_require_mod、版本和依赖是否符合纯客户端、全客户端必装或客户端可不安装的服务器部署方式；不要依赖当前加载器不识别的 server_only_mod。
3. 新建隔离测试 Cluster、存储目录和端口；复用已有测试世界前备份。按需先启动 Master，再启动 Caves，记录进程身份与启动日志。
4. 按选定方式运行测试驱动或连接真实客户端，观察实际状态与行为。无头自动测试的编排、对照、判定、修复复测和清理遵循通用流程。
5. 按改动选择建世界、保存重载、分片往返、断线重连、回滚、空服运行或版本不一致等用例。
6. 分别检查各端第一条错误；正常关服，确认本次启动的进程退出，再汇总通过、失败、无效和未执行项。
7. 只在用户明确要求时修改实际生产 Cluster 或发布配置。

## 源码锚点

- networking.lua：StartDedicatedServer、客户端连接与重置。
- shardnetworking.lua、shardindex.lua：多分片。
- mods.lua、modindex.lua：服务器模组加载和版本。
- serverpreferences.lua、worldsettingsutil.lua。

## 不变量

- 不要把本地主机测试等同于专服测试。
- 区分语法检查、模拟测试、原生无头执行与真实客户端验证；结论限于实际运行的层级和场景。
- 测试驱动与正式模组分开；调用实际被测代码，保留原生行为，记录所有会影响结果的环境调整。
- 不要在未经确认的生产 Cluster 上回滚、再生世界或改配置。
- 令牌、cluster_token、密码和用户数据不得写入 Skill、日志摘要或提交。
- 每个进程的日志和时间戳分别保存，避免混淆根因。

## 验证

- 选定的运行端和场景完成预设断言；环境或驱动不成立的用例标为无效。
- 涉及存档、分片或网络时，相关重载、迁移或客户端用例达到预期。
- 报告包含版本与源码指纹、配置、实际运行方式、指标、失败和未执行项；分享前脱敏本机路径及敏感日志。
- 已确认本次进程退出，测试配置与临时模组未混入正式发布内容。
