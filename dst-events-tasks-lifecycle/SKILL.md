---
name: dst-events-tasks-lifecycle
description: Manage Don't Starve Together events, world-state watchers, scheduled tasks, updates, sleep and wake transitions, and cleanup. Use when writing ListenForEvent callbacks, DoTaskInTime or DoPeriodicTask logic, component updates, entity sleep behavior, delayed actions, or diagnosing leaked callbacks and removed-entity errors.
---

# DST 事件、任务与生命周期

为每个回调确定所有者、事件源、取消时机和睡眠语义，避免实体移除后继续执行。

## 工作流

1. 记录事件名、事件源、监听者、data 契约和谁负责解除监听；不要只凭字符串相同假设数据结构。
2. 使用同一函数引用配对 ListenForEvent 与 RemoveEventCallback；跨实体监听时明确 source。
3. 监听世界变量时配对 WatchWorldState 与 StopWatchingWorldState，并决定初始化时是否主动同步一次。
4. 一次性延迟使用 DoTaskInTime，稳定低频循环使用 DoPeriodicTask，组件级连续更新仅用于确有需要的状态。
5. 把任务句柄保存到明确字段；重启任务前先 Cancel，并在执行后清空句柄。
6. 决定实体睡眠时任务应暂停、继续、折算 LongUpdate 还是在唤醒时重建。
7. 在 OnRemoveEntity、OnRemoveFromEntity、Widget Kill 或 SG onexit 中执行对应清理。

## 源码锚点

- entityscript.lua：事件、世界状态、任务、睡眠和移除。
- scheduler.lua：调度与线程。
- components/ 与 prefabs/：OnEntitySleep、OnEntityWake、LongUpdate 范例。
- widgets/widget.lua：UI 更新和销毁生命周期。

## 不变量

- 回调先验证 inst、目标与组件仍然有效。
- 不要每帧扫描可用事件或低频任务解决的问题。
- 不要用匿名函数注册后再试图用另一个匿名函数解除。
- 服务器玩法任务与客户端表现任务分开建立。

## 验证

- 移除实体或组件后不再触发回调。
- 睡眠、唤醒、保存重载和世界暂停不会重复创建任务。
- 周期逻辑的频率、初始延迟和长时间跳过行为符合设计。

