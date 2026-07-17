---
name: dst-client-frontend-mods
description: Build Don't Starve Together client-only and frontend mods. Use when writing modfrontendmain.lua, declaring client_only_mod, modifying main menus or frontend screens, adding local HUD helpers, reading client replicas, storing local configuration, or ensuring a mod never requires server-side installation.
---

# DST 纯客户端与前端模组

严格区分 FrontEnd、游戏客户端和服务器环境，只使用本地 UI、公开客户端数据或可选 RPC。

## 工作流

1. 确定功能只影响主菜单、游戏 HUD、输入、地图、提示还是客户端视觉，并证明无需服务器权威状态。
2. 在 modinfo.lua 设置正确的 client_only_mod 与兼容标志；不要同时要求所有客户端安装。
3. 前端逻辑放入 modfrontendmain.lua，只访问 FrontEnd 可用模块；游戏 HUD 逻辑在客户端入口延迟到玩家和 HUD 存在。
4. 读取 Replica、网络变量或客户端已有数据；服务器未安装模组时不发送自定义 RPC。
5. 本地配置与服务器配置分开，默认值在配置缺失或版本变化时仍安全。
6. 通过 ClassPostConstruct 小范围扩展 Screen 或 Widget，并为重建、返回主菜单和重连清理。
7. 分别测试加入无模组服务器、装有同模组服务器、离线前端、重连和禁用模组。

## 源码锚点

- mods.lua、modindex.lua：client_only_mod 和前端环境。
- frontend.lua、screens/mainscreen.lua、screens/modsscreen.lua。
- screens/playerhud.lua、widgets/controls.lua。
- entityreplica.lua 与 components/*_replica.lua。

## 不变量

- 纯客户端模组不能依赖服务器 Component、自定义 Prefab 或服务器 RPC 必然存在。
- 前端阶段通常没有 TheWorld 和 ThePlayer。
- 不要修改影响服务器判定的本地值并宣称改变玩法。
- 加入服务器时客户端缺少数据必须优雅降级。

## 验证

- 服务器未安装该模组时仍能加入并使用允许的客户端功能。
- 返回主菜单和多次重连不残留 Widget 或输入处理器。
- 禁用模组后不要求服务器或存档迁移。

