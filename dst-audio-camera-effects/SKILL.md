---
name: dst-audio-camera-effects
description: Integrate Don't Starve Together sound events, looping audio, sound remapping, camera shake, camera control, and local presentation effects. Use when working with SoundEmitter, PlaySound or KillSound, RemapSoundEvent, CameraShake, screen emphasis, listener-local feedback, or diagnosing audio and camera effects that duplicate in multiplayer.
---

# DST 音频与相机效果

声音和相机属于客户端表现；服务器只发送必要事件，不直接假设每个玩家的监听与镜头状态。

## 工作流

1. 定义声音事件、是否循环、句柄名、3D 发声实体、可听玩家、停止条件和相机影响范围。
2. 从相同发声对象查找 PlaySound、KillSound 与 SetParameter 范例，确认事件路径和参数存在。
3. 循环声音使用稳定句柄，启动前避免重复播放，所有退出路径 KillSound。
4. 全局 RemapSoundEvent 只用于明确的模组级替换，并提供 RemoveRemapSoundEvent 或禁用恢复。
5. 镜头震动按距离、强度和持续时间在目标客户端执行；多人事件不要只作用于主机 ThePlayer。
6. 接管相机或全屏表现前保存原状态，在跳过、死亡、断线和 Screen 关闭时恢复。
7. 测试本地玩家、远端玩家、多个同类实体、暂停、静音设置和快速进出听觉范围。

## 源码锚点

- camerashake.lua、cameras/、frontend.lua。
- prefabs/ 与 stategraphs/ 中 SoundEmitter:PlaySound、KillSound 调用。
- modutil.lua：RemapSoundEvent 与 RemoveRemapSoundEvent。
- mixes.lua、mixer.lua：混音使用范例。

## 不变量

- 不要把本地声音播放当作服务器事件已发生的证明。
- 循环音句柄不可由多个无关效果共享。
- 相机和全屏效果只作用目标客户端，并允许用户设置降低影响。
- 没有实际音频工具链和资源时不要承诺自定义事件已可加载。

## 验证

- 效果不会因客户端预测与服务器同步重复播放。
- 实体移除、状态中断和返回主菜单后无循环音或相机残留。
- 屏幕外和超出距离的玩家不收到不必要表现。

