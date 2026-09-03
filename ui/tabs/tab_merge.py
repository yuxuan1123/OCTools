"""
octool/ui/tabs/tab_merge.py
───────────────────────────────────────────────
拼接页（板块二：文件拼接）—— 仅「拼接」模块：单文件 / 多文件合并为单个文件。

界面：输入（源文件 / 源文件夹）→ 目标格式（二级选择器）→ 输出（单个文件）→
预设区（md→docx / 图片→docx / TTS / STT）→ 开始拼接 → 实时日志。

由 ui/tabs/merge/ 子包细分化而来（卡片在 card_*.py，动作在 actions.py，
目标格式/预设联动在 target_ctl.py，语音引擎在 engine_ctl.py，拼接执行在 runner.py）。
"""

import sys


from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame

from config.ui_config import CONFIG as C
from config import presets
from config.format_config import FormatConfig
from config.image_docx_config import ImageDocxConfig
from config.tts_config import TtsConfig
from config.stt_config import SttConfig

from ui.tabs.merge import (
    card_input, card_target, card_output, button_merge, card_log,
)
from ui.tabs.merge import actions, target_ctl, engine_ctl, runner
from ui.tabs.merge.registry import build_format_list
from ui.tabs.tab_component.page_header import build_page_header


class _LogBridge(QObject):
    """跨线程日志桥：工作线程 → 主线程 追加日志（避免在子线程碰 Qt 控件）"""
    msg = Signal(str)


class TabMerge(QWidget):
    """拼接页面（仅支持「拼接」模式：合并为单个文件）"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # ── 独立运行所需的状态和配置 ──
        self.current_config = presets.load_last_config() or FormatConfig.default_chinese()
        self.image_docx_config = presets.load_last_image_config() or ImageDocxConfig()
        self.tts_config = presets.load_last_tts_config() or TtsConfig()
        self.stt_config = presets.load_last_stt_config() or SttConfig()

        # ── 状态 ──
        self.input_path = ""
        self.output_path = ""
        self.folder_path = ""
        self.src_format = ""
        self.selected_format = ""
        self.available_formats = []
        self._format_list = build_format_list()
        self._available_list = list(self._format_list)
        self._preset_names = []
        self._img_preset_names = []
        self._busy = False

        self.log_text = None
        self.format_picker = None
        self.source_picker = None
        self.input_entry = None
        self.folder_entry = None
        self.output_entry = None
        self.output_browse_btn = None
        self.docx_card = None
        self.img_preset_combo = None
        self.tts_engine_combo = None
        self.convert_btn = None
        self._preset_area = None
        self._img_row_w = None
        self._tts_row_w = None
        self._stt_row_w = None
        self._stt_summary = None
        self._preset_none_label = None
        self._src_fmt_widget = None

        # 跨线程日志桥（后台线程 → 主线程 UI）
        self._log_bridge = _LogBridge(self)
        self._log_bridge.msg.connect(self._on_log_qt)

        self._build_ui()

    # ──────────────────────────────────────
    #  布局
    # ──────────────────────────────────────

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(C.size("card_spacing"))

        # 让页面可滚动（窗口较小时）
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        body = QWidget()
        body.setObjectName("scrollInner")
        lay = QVBoxLayout(body)
        lay.setContentsMargins(0, 0, C.size("scroll_gutter_right"), 0)
        lay.setSpacing(C.size("card_spacing"))
        scroll.setWidget(body)
        outer.addWidget(scroll, 1)

        # ── 页头 ──
        lay.addWidget(build_page_header(body, "page_merge_title", "page_merge_sub"))

        # ── 输入卡 → 目标格式卡 → 输出卡 → 开始拼接 → 日志卡 ──
        lay.addWidget(card_input.build_input_card(body, page=self))
        lay.addWidget(card_target.build_target_card(body, page=self))
        lay.addWidget(card_output.build_output_card(body, page=self))
        lay.addWidget(button_merge.build_merge_button(body, page=self))
        lay.addWidget(card_log.build_log_card(body, page=self), 1)

        # 初始状态
        actions.update_output_state(self)
        target_ctl.update_preset_area(self, "", "")
        target_ctl.refresh_target_combo(self)

        # 手动编辑源路径时联动
        self.input_entry.textChanged.connect(lambda _t: self._on_source_edited())
        self.folder_entry.textChanged.connect(lambda _t: self._on_source_edited())

    # ──────────────────────────────────────
    #  日志
    # ──────────────────────────────────────

    def _on_log_qt(self, msg):
        """主线程日志落盘（UI 控件只能在此线程访问）"""
        self.append_log(msg)
        print(msg)

    def append_log(self, msg):
        """追加一行日志（主线程调用）"""
        if self.log_text is not None:
            self.log_text.append(msg)
            sb = self.log_text.verticalScrollBar()
            if sb is not None:
                sb.setValue(sb.maximum())

    def clear_log(self):
        if self.log_text is not None:
            self.log_text.clear()

    def log(self, msg):
        """线程安全日志：可从工作线程调用，跨线程桥回主线程落盘并打印"""
        self._log_bridge.msg.emit(msg)

    def refresh_settings_summaries(self):
        """独立运行时不需要额外刷新，保留为空"""
        pass

    # ──────────────────────────────────────
    #  源选择（浏览 / 手动编辑）
    # ──────────────────────────────────────

    def _browse_input(self):
        actions.browse_input(self)

    def _browse_folder(self):
        actions.browse_folder(self)

    def _browse_output_file(self):
        actions.browse_output_file(self)

    def _on_folder_fmt_selected(self, fmt):
        actions.on_folder_fmt_selected(self, fmt)

    def _on_source_edited(self):
        actions.on_source_edited(self)

    def _effective_source(self):
        return actions.effective_source(self)

    def _infer_folder_format(self, folder):
        return actions.infer_folder_format(self, folder)

    def _update_output_state(self):
        actions.update_output_state(self)

    def _auto_fill_output(self):
        actions.auto_fill_output(self)

    # ──────────────────────────────────────
    #  目标格式（二级选择器）与预设区
    # ──────────────────────────────────────

    def _reachable_targets(self, src_fmt):
        return target_ctl.reachable_targets(self, src_fmt)

    def _update_picker_available(self, formats):
        target_ctl.update_picker_available(self, formats)

    def _select_format(self, fmt):
        target_ctl.select_format(self, fmt)

    def _refresh_target_combo(self):
        target_ctl.refresh_target_combo(self)

    def _update_preset_area(self, src_fmt, dst_fmt):
        target_ctl.update_preset_area(self, src_fmt, dst_fmt)

    def _refresh_stt_summary(self):
        target_ctl.refresh_stt_summary(self)

    def _refresh_preset_combo(self):
        target_ctl.refresh_preset_combo(self)

    def _on_docx_card_config_changed(self, config):
        target_ctl.on_docx_card_config_changed(self, config)

    def _refresh_img_preset_combo(self):
        target_ctl.refresh_img_preset_combo(self)

    def _on_img_preset_selected(self, index):
        target_ctl.on_img_preset_selected(self, index)

    def _reset_img_preset_combo(self):
        target_ctl.reset_img_preset_combo(self)

    # ──────────────────────────────────────
    #  语音引擎（txt/md → 音频）
    # ──────────────────────────────────────

    def _refresh_tts_engine_combo(self):
        engine_ctl.refresh_tts_engine_combo(self)

    def _on_tts_engine_selected(self, index):
        engine_ctl.on_tts_engine_selected(self, index)

    # ──────────────────────────────────────
    #  选项弹窗
    # ──────────────────────────────────────

    def _show_format_panel(self):
        """打开格式选项对话框"""
        actions.show_format_panel(self)

    def _on_format_panel_finished(self, dlg):
        actions.on_format_panel_finished(self, dlg)

    def _open_tts_options(self):
        actions.open_tts_options(self)

    def _tts_options_closed(self):
        actions.tts_options_closed(self)

    def _open_stt_options(self):
        actions.open_stt_options(self)

    def _stt_options_closed(self):
        actions.stt_options_closed(self)

    def _open_image_docx_options(self):
        actions.open_image_docx_options(self)

    def _image_options_closed(self):
        actions.image_options_closed(self)

    # ──────────────────────────────────────
    #  拼接执行
    # ──────────────────────────────────────

    def _run_concat(self):
        runner.run_concat(self)


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    from ui.theme import APP_STYLESHEET 

    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLESHEET) 

    window = TabMerge()
    window.show()
    sys.exit(app.exec())
