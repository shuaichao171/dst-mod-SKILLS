---
name: dst-mod-scaffolding
description: Create and organize Don't Starve Together mod skeletons. Use when starting a mod, writing modinfo.lua, modmain.lua, modworldgenmain.lua, or modfrontendmain.lua, defining configuration options and compatibility flags, registering assets and prefabs, or correcting a broken mod layout.
---

# DST 模组脚手架

从最小可加载结构开始，根据运行上下文逐步加入入口、配置、资源和依赖。

## 工作流

1. 确认目标是服务器模组、所有客户端必装模组、纯客户端模组、世界生成模组还是前端模组。
2. 从 assets/minimal-mod/ 复制最小模板，只创建任务真正需要的入口和目录。
3. 填写 modinfo.lua 的名称、描述、作者、版本、api_version、dst_compatible、客户端/服务器标志和 configuration_options。
4. 在 modmain.lua 中声明 PrefabFiles、Assets、配置读取与运行时钩子；把世界生成和前端逻辑分别放入对应入口。
5. 使用 modimport 或 require 组织 scripts/ 模块，明确 GLOBAL 访问，避免把大量实现堆在 modmain.lua。
6. 验证资源路径、Prefab 名称、配置数据类型、依赖关系和服务器过滤标记。
7. 以无缓存重启方式分别测试禁用、启用、改配置、建新世界和载入旧世界。

## 源码锚点

- mods.lua、modindex.lua：入口加载、modinfo 校验、优先级和依赖。
- modutil.lua：GetModConfigData、Prefab、Asset 及各类 Add 开头的公开 API。
- frontend.lua、worldgen_main.lua：前端和世界生成上下文。

## 不变量

- 不要同时声明互斥的 client_only_mod 与 all_clients_require_mod。
- 不要在 modinfo.lua 执行游戏运行时逻辑。
- 不要为未使用的资源、Prefab 或入口添加占位声明。
- 保留已有用户文件和配置；扩展现有模组前先读取其结构。

## 验证

- 游戏能读取 modinfo 且模组列表无错误。
- 目标运行上下文只加载需要的入口。
- 所有配置选项在默认值和非默认值下均能启动。

## 按需资源

- 复制 assets/minimal-mod/ 创建新模组。
- 需要入口和兼容标志说明时读取 references/entrypoints.md。

