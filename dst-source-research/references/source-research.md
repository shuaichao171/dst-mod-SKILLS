# 源码研究方法

## 选择入口

| 问题 | 首选入口 |
| --- | --- |
| 模组钩子或注册 API | modutil.lua、mods.lua |
| 实体构造 | prefabs/、prefabutil.lua、standardcomponents.lua |
| 玩法状态 | components/、entityscript.lua |
| 自定义动作 | actions.lua、componentactions.lua、bufferedaction.lua |
| AI | brain.lua、behaviourtree.lua、brains/、behaviours/ |
| 动画状态 | stategraph.lua、stategraphs/ |
| 联机 | netvars.lua、networkclientrpc.lua、entityreplica.lua |
| 世界生成 | worldgen_main.lua、map/ |
| UI | widgets/、screens/、frontend.lua、input.lua |

## 搜索顺序

1. 先按文件名定位同类原版对象。
2. 搜索公开符号定义。
3. 搜索该符号的所有调用点。
4. 追踪 require、Class、Prefab 和回调注册。
5. 搜索相关组件名、标签、事件名和 SG 状态名。
6. 比较至少一个最接近的完整实现。
7. 将结论分为源码明示、多个调用点推断和未知。

示例：

    powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/scan-dst-source.ps1 -Mode Summary
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/scan-dst-source.ps1 -Mode Symbol -Pattern AddBrainPostInit
    rg -n SetPristine <source-root>/prefabs -g *.lua

## 引擎原生边界

Entity:AddTransform、AnimState、Physics、TheSim 等接口可能由引擎绑定。找不到 Lua 定义时：

1. 搜索所有调用点。
2. 按接收对象类型分组。
3. 比较参数数量、nil 用法和调用前置条件。
4. 检查 SetPristine 前后以及主机、客户端上下文。
5. 检查返回值如何被使用。
6. 将契约标为调用点推断，不声称掌握未公开实现。

## 报告格式

- 源码根目录和研究日期
- 用户问题与目标运行端
- 关键文件和行号
- 调用链
- 已验证事实
- 推断及其证据
- 风险和未解决项
- 推荐原版范例
