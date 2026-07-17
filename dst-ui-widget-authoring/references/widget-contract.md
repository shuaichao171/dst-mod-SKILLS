# Widget 契约

## 坐标与布局

SetPosition 使用父节点局部坐标。Anchor 决定相对屏幕边缘的位置，region point 决定控件自身的对齐点。ScaleMode 和 UI scale 会改变最终显示；不要用固定屏幕像素推断所有分辨率。

## 所有权

AddChild 建立 Widget 树所有权。父节点 Kill 会清理子节点，但不会自动解除子节点向世界实体、输入系统或其他对象注册的外部回调。

## 更新

优先显式 Refresh 或事件驱动。只有动画和连续跟随需要 OnUpdate。隐藏或暂停时决定是否继续更新，并在 Kill 前 StopUpdating。

## 输入

OnControl 先允许父类处理。处理成功返回 true。为手柄设置默认焦点与 FocusChangeDir，确保取消键和返回路径存在。不要让隐藏 Widget 继续吞输入。

## 生命周期检查

- 构造
- AddChild
- Show 与 Hide
- GainFocus 与 LoseFocus
- 屏幕 Push 与 Pop
- HUD 重建
- 玩家替换
- Kill

