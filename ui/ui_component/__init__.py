"""
OCTools/ui/ui_component/__init__.py
───────────────────────────────────
通用 UI 组件包（原 services/components 已迁入，与既有组件共存）。

既有组件：
  - titlebar_component.py   标题栏（CustomTitleBar）
  - button_component.py     按钮（开关 / 图标按钮 handle）
  - split_window.py         上下/左右分栏（_Pane）
  - split_titlebar.py       分栏标题栏
  - left_sidebar.py         左侧边栏
  - window_resizer.py       无边框窗口边缘/角落缩放（attach_resizer）

由 services/components 迁入的组件：
  - timer.py                定时器（TimerComponent，周期触发）
  - hotkeys.py              热键绑定（parse_hotkey）
  - overlay.py              悬浮显示框（FloatingOverlay，参数化 UI 组件）
  - region_box.py           区域框选（RegionSelectDialog / LiveRegionBox）
  - window_ctl.py           顶层窗口显隐（子控件→主窗口解析 + 最小化 / 恢复 / 泵事件）

组件一律通过 `from ui.ui_component.<module> import <symbol>` 显式导入。
"""