# OCTools 项目长期记忆

## 环境

- venv：`./.venv/Scripts/python.exe`（系统 Python 无 PySide6）。跑 Qt 相关脚本加
  `QT_QPA_PLATFORM=offscreen`。
- `import ui.theme` 在导入时把生成的 QSS 回写 `ui/styles/style.qss`，跑测试会弄脏它，
  跑完 `git checkout -- ui/styles/style.qss`。
- 主窗口：`ui/main_window.py` → `TestWindow`（split_titlebar） + 左侧栏 + 右侧 tab 页。
  tab 页由 manifests 动态加载，`set_right_content` → `_Pane.set_body` 会 `addWidget`
  **重新设置父对象**，所以页面是主窗口的子控件。

## 架构约定

- UI 参数（尺寸/颜色/文本/时间）一律落 `config/ui_config.json`，代码不写魔法值；
  访问器 `config/ui_config.py` → `CONFIG`（`size/color/font/layout/text/timing`）。
- 翻译页拆分为子包 `ui/tabs/translation/`（cards / app_hooks / app_controller /
  apps / window_ctl），页面类本体在 `ui/tabs/tab_translation.py`。
- 最终应用（屏幕OCR / 屏幕翻译 / 屏幕实时翻译 / 屏幕字幕 / 语音翻译）业务逻辑在
  `services/recipes/`，UI 挂载在 `ui/tabs/translation/apps/`。
- **Qt 窗口状态坑**：对页面子控件调 `showMinimized()` 是空操作，必须
  `widget.window()` 取顶层窗口（见 `window_ctl.top_window`）。

## 协作

- 启动任一最终应用前最小化主窗口，且**不自动恢复**（用户从任务栏/托盘恢复）。
- 改完要有可验证的数字/断言：新增回归测试放 `tests/`，风格对齐 `smoke_test.py`
  （`_check` + 退出码）。
