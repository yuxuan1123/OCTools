"""
OCTools/ui/tabs/conversion/
────────────────────
转换功能页子包（由 tab_conversion.py 拆分而来）：
  - registry.py         常量注册表与共享引用（formats / engines / helpers）
  - card_input.py       输入卡片
  - card_target.py      目标格式卡片（格式选择 + 预设区）
  - card_output.py      输出卡片
  - button_convert.py   开始转换按钮
  - card_log.py         日志卡片
  - actions.py          页面交互动作（浏览 / 状态联动 / 选项弹窗）
  - target_ctl.py       目标格式与预设区联动控制
  - engine_ctl.py       TTS 语音引擎下拉控制
  - runner.py           转换执行（后台线程）

注：本子包的入口页面类 TabConversion 统一定义在 ui/tabs/tab_conversion.py，
由 OCTools 主程序按 manifests/conversion.json 动态加载。
"""
