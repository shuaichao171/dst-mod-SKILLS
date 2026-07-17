---
name: dst-lua-runtime
description: Work safely with the Don't Starve Together Lua runtime and mod environment. Use when handling Class inheritance, GLOBAL access, require or modimport, closures and upvalues, scheduler tasks, environment boundaries, monkey patches, or Lua errors caused by scope and lifecycle assumptions.
---

# DST Lua 运行时与模组环境

先确定代码运行环境和对象生命周期，再选择作用域、加载方式与补丁策略。

## 工作流

1. 识别代码运行于 modinfo、前端、世界生成、服务器、客户端还是分片上下文。
2. 沿 class.lua、metaclass.lua 和目标类的 Class 构造追踪继承与方法查找。
3. 优先使用局部变量；仅通过明确的 GLOBAL 引用访问游戏全局，不向全局表泄漏临时符号。
4. 用 require 加载游戏模块，用 modimport 加载模组内文件；确认缓存语义和返回值。
5. 修改闭包或 upvalue 前先证明公开钩子不足，并准备版本变化后的失败检测。
6. 创建任务、线程或回调时记录所有者，并在实体移除、Widget 销毁或状态退出时取消。
7. 用实际堆栈和最小复现验证 nil、环境、递归 require、闭包捕获及返回值问题。

## 源码锚点

- class.lua、metaclass.lua、strict.lua：类和全局访问。
- mods.lua、modutil.lua、main.lua：模组环境与加载。
- scheduler.lua、entityscript.lua：任务、线程和实体生命周期。

## 不变量

- 不要假设所有入口拥有相同全局表或 TheWorld、ThePlayer。
- 不要无条件覆盖原函数；包装时保留可变参数、多返回值和 self。
- 不要依赖未验证的 upvalue 名称或索引。
- 不要在模块加载阶段执行依赖已生成世界或玩家的逻辑。

## 验证

- 在目标入口中确认模块只加载一次或符合预期缓存行为。
- 补丁在原函数缺失、签名变化和重复加载时可安全失败。
- 任务和事件回调没有在所有者销毁后继续运行。

