"""
ui/tabs/merge/
──────────────
拼接功能页子包（由 tab_merge.py 拆分而来，仅保留「拼接」模块）：
  - registry.py         常量注册表与共享引用（formats / engines / helpers）
  - card_input.py       输入卡片（源文件 / 源文件夹 / 源文件格式）
  - card_target.py      目标格式卡片（格式选择 + 预设区）
  - card_output.py      输出卡片（拼接后的单个文件）
  - button_merge.py     开始拼接按钮
  - card_log.py         日志卡片
  - actions.py          页面交互动作（浏览 / 状态联动 / 选项弹窗）
  - target_ctl.py       目标格式与预设区联动控制
  - engine_ctl.py       TTS 语音引擎下拉控制
  - runner.py           拼接执行（后台线程）

注：本子包的入口页面类 TabMerge 统一定义在 ui/tabs/tab_merge.py，
由 octool 主程序按 manifests/merge.json 动态加载。
"""
