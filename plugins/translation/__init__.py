"""
OCTools/ui/tabs/translation/
────────────────────────
翻译功能页子包（由 translation_tab.py 拆分而来）：
  - registry.py         应用注册表常量与翻译引擎常量引用
  - card_widgets.py       通用卡片构建小工具
  - card_direction.py     翻译方向卡片
  - card_screen.py        屏幕翻译卡片
  - card_voice.py         语音翻译卡片
  - card_source.py        原文卡片
  - card_result.py        译文卡片
  - card_log.py           日志卡片
  - button_translate.py   开始翻译按钮
  - app_hooks.py          应用行构建
  - actions.py            页面交互动作
  - runner.py             翻译执行（后台线程 + 完成回调）
  - engine_ctl.py         翻译引擎下拉控制
  - app_controller.py     最终应用 启动/停止/状态 控制

注1：窗口显隐（启动前最小化主窗口）用公共组件 ui/ui_component/window_ctl.py，
     不放在本子包 —— 「设置 → 截图区域」的框选按钮同样需要它。

注2：本子包的入口页面类 TabTranslation 统一定义在 plugins/translation/tab_translation.py，
由 OCTools 主程序按 manifests/translation.json 动态加载。
"""