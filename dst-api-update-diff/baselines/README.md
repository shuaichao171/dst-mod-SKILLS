# DST 源码快照基线

本目录存放 `snapshot-dst-source.ps1` 生成的源码快照，供 `compare-dst-snapshots.ps1` 在游戏更新后做差异比较。

| 快照 | 对应游戏版本 | 说明 |
| --- | --- | --- |
| `dst-scripts-R43-halloween-20261028.json` | R43「咒终对决·下部」+ 万圣夜热修 760178（2026-10-27，本地文件 2026-10-28） | 首个基线，含 Hallowed Nights（760049）与热修 760178 全部脚本 |

## 本基线窗口内已知模组相关变更（2026-10-22 → 10-27）

- R43（官方 Modder Notes 见测试分支 751350 帖；线上 759423/759671）：移除组件 `vault_teleporter`、`vaultroom`、`vault_floor_helper`、`vaultroommanager`，新增 `virtualroommanager`、`virtualroomset` 替代（另有配套组件 `virtualroomteleporter`，vault_teleporter prefab 已改用它）；依赖旧组件的模组需迁移。模组发布 ID：R43_SHADOWYDEPTHS。森林↔洞穴加载提速。
- 万圣夜（760049/760178）：新增小型生物击退标准实现（`CommonHandlers.OnKnockback` + `CommonStates.AddKnockbackStates`，约 50 个原版生物 SG 接入）；新组件 `sweepable`、`sweeper`、`spooked`、`leafpilemanager`、`itemmimic`、`itemmimicconfig` 与 `ACTIONS.SWEEP`；专服新增可选启动参数 `-allow_persistentstorage_read_sandbox_escape` / `-allow_persistentstorage_write_sandbox_escape`（允许模组读写集群目录文件）。
- 相关技能补丁已落在 dst-stategraph-authoring、dst-combat-weapons-projectiles、dst-persistence-migration、dst-dedicated-server-testing（见仓库提交历史）。

## 维护约定

- 每次游戏更新并完成技能库对照审查后，生成新快照替换基线；旧快照先归档（可压缩），直到相关模组在新版本验证完毕。
- 快照只读游戏 `data/scripts`，提交前确认不含游戏源码文本本身（仅哈希与符号索引）。
- 快照约 7 MB；如仓库体积成为问题，可将非当前基线压缩为 `.gz` 归档。
