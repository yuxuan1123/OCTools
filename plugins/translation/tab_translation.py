"""
OCTools/plugins/translation/tab_translation.py
────────────────────────────────────────────
翻译页（板块三：翻译与屏幕 / 语音工具）—— 由 translation_tab.py 拆分而来，
原 class TranslatePage 更名为 class TabTranslation。

功能（与原实现逐字一致，仅把大方法拆进独立文件）：
  - 中英互译：中→英 / 英→中 / 自动检测（hy-mt / opus-mt，可配置并持久化）
  - 五个最终应用（业务与浮窗在 apps/，本页只做 启动/停止 挂载）：
      屏幕OCR         = 截图 + 图像识别           → 纯文本悬浮窗
      屏幕翻译        = 截图 + 图翻译（单次）      → 双语悬浮窗
      屏幕实时翻译     = 自动区域截图 + 图翻译      → 双语悬浮窗（暂停/手动/区域可调）
      屏幕字幕        = 内置语音识别               → 纯文本字幕悬浮窗
      语音翻译        = 实时语音识别 + 文字翻译     → 双语字幕悬浮窗
  - 全局快捷键（Alt+X / Alt+C）与托盘入口在 main_window 装配，共用 toggle_app。
"""

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame

from config.translator_config import TranslatorConfig, \
    ENGINE_LABELS as TR_ENGINE_LABELS, ENGINE_ORDER as TR_ENGINE_ORDER
from config.stt_config import SttConfig
from config.screen_region_config import ScreenRegionConfig
from config import presets
from ui.toast import show_toast
from ui import icon_res
from config.ui_config import CONFIG as C
from core.utils.file_handler import read_text, write_text

from plugins.translation.apps import (
    ScreenOcrApp,
    OneShotScreenTranslateApp,
    RealtimeScreenTranslateApp,
    ScreenSubtitleApp,
    SpeechTranslateApp,
)

from plugins.translation import (
    card_direction, card_screen, card_voice, card_source,
    card_result, card_log, button_translate,
)
from plugins.translation import actions, runner, engine_ctl, app_controller
from ui.tabs.tab_component.page_header import build_page_header


class _LogBridge(QObject):
    """跨线程日志桥：工作线程 → 主线程 追加日志（避免在子线程碰 Qt 控件）"""
    msg = Signal(str)


class TabTranslation(QWidget):
    """翻译页：中→英 / 英→中 / 自动检测（本地模型，参考 mvp/l2l.py、mvp/hy.py）"""

    # 翻译结果回传（发射自后台线程，自动排队到主线程回调）
    translation_finished = Signal(object, bool, str)
    translation_error = Signal(object, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._busy = False
        self.log_text = None
        self.input_edit = None
        self.output_edit = None
        self.direction_combo = None
        self.translate_btn = None
        self.tr_engine_combo = None
        # 三个配置对象（翻译 / 语音识别 / 截图框），加载上次保存，缺省用默认
        self.translator_config = presets.load_last_translator_config() or TranslatorConfig()
        self.stt_config = presets.load_last_stt_config() or SttConfig()
        self.screen_region_config = (presets.load_last_screen_region_config()
                                     or ScreenRegionConfig())
        # 跨线程日志桥（后台线程 → 主线程 UI）
        self._log_bridge = _LogBridge(self)
        self._log_bridge.msg.connect(self._on_log_qt)
        # 最终应用状态（屏幕OCR / 屏幕翻译 / 屏幕实时翻译 / 屏幕字幕 / 语音翻译）
        self._apps = {}          # key → 应用实例（applications/*）
        self._app_btns = {}      # key → 启动/停止 切换按钮
        self._app_status = {}    # key → 状态标签（未启动 / 运行中）

        # 后台线程通过信号回到主线程更新 UI
        self.translation_finished.connect(self.on_translation_finished)
        self.translation_error.connect(self.on_translation_error)

        self._build_ui()
        self._init_apps()

    def showEvent(self, e):
        """进入翻译页：按翻译设置后台预加载 OCR / 翻译模型（幂等，失败静默）"""
        super().showEvent(e)
        try:
            from plugins.translation.preload import start_preload
            start_preload(self.translator_config, timing="tab")
        except Exception:
            pass

    def _on_log_qt(self, msg):
        """主线程日志落盘（UI 控件只能在此线程访问）"""
        app_controller.append_log(self, msg)

    # ──────────────────────────────────────
    #  布局
    # ──────────────────────────────────────

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(C.size("card_spacing"))

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
        lay.addWidget(build_page_header(body, "page_translate_title", "page_translate_sub"))

        # ── 方向卡 → 屏幕卡 → 语音卡 → 原文卡 → 开始翻译 → 译文卡 → 日志卡 ──
        lay.addWidget(card_direction.build_direction_card(body, page=self))
        lay.addWidget(card_screen.build_screen_card(body, page=self))
        lay.addWidget(card_voice.build_voice_card(body, page=self))
        lay.addWidget(card_source.build_source_card(body, page=self))
        lay.addWidget(button_translate.build_translate_button(body, page=self))
        lay.addWidget(card_result.build_result_card(body, page=self))
        lay.addWidget(card_log.build_log_card(body, page=self), 1)

    # ──────────────────────────────────────
    #  工具
    # ──────────────────────────────────────

    def append_log(self, msg):
        """追加一行日志（主线程调用）"""
        app_controller.append_log(self, msg)

    def log(self, msg):
        """线程安全日志：可从工作线程调用，跨线程桥回主线程落盘"""
        self._log_bridge.msg.emit(msg)

    def clear_log(self):
        app_controller.clear_log(self)

    def _init_apps(self):
        """创建最终应用实例；悬浮窗被关闭（stopped）时自动复位行按钮"""
        app_controller.init_apps(self)

    def app(self, key):
        """按 key 获取最终应用实例（main_window 托盘/热键查询用）"""
        return app_controller.app(self, key)

    def is_app_running(self, key) -> bool:
        return app_controller.is_app_running(self, key)

    def toggle_app(self, key):
        """启动 ⇄ 停止：页面按钮 / 热键 / 托盘菜单共用入口"""
        app_controller.toggle_app(self, key)

    def stop_all_apps(self):
        """退出前停止全部最终应用（幂等）"""
        app_controller.stop_all_apps(self)

    # ──────────────────────────────────────
    #  翻译执行（后台线程）
    # ──────────────────────────────────────

    def _run_translation(self):
        runner.run_translation(self)

    def on_translation_finished(self, page, ok, result):
        """完成回调（主线程，由信号/主窗口连接调用）"""
        runner.on_translation_finished(page, ok, result)

    def on_translation_error(self, page, err):
        runner.on_translation_error(page, err)

    # ──────────────────────────────────────
    #  翻译引擎（预选模型 + 参数）
    # ──────────────────────────────────────

    def _refresh_tr_engine_combo(self):
        """刷新「翻译引擎」下拉，显示当前配置的引擎"""
        engine_ctl.refresh_tr_engine_combo(self)

    def _on_tr_engine_selected(self, index):
        """翻译引擎下拉选择 → 更新配置并持久化"""
        engine_ctl.on_tr_engine_selected(self, index)

    # ──────────────────────────────────────
    #  选项与汇总
    # ──────────────────────────────────────

    def open_translator_options(self):
        """打开「翻译引擎参数」对话框（直接修改自持的 translator_config 并持久化）"""
        from plugins.translation.set_translator import SetTranslator
        dlg = SetTranslator(self.translator_config, self)
        if dlg.exec():
            presets.save_last_translator_config(self.translator_config)
            self._refresh_tr_engine_combo()

    def open_stt_options(self, stt_config):
        """打开「语音识别参数」对话框"""
        from plugins._shared.set_stt import SetStt
        dlg = SetStt(stt_config, self)
        dlg.exec()

    def open_screen_region_options(self, region_config):
        """打开「截图区域参数」对话框"""
        from plugins.translation.set_screen_region import SetScreenRegion
        dlg = SetScreenRegion(region_config, self)
        dlg.exec()

    def refresh_settings_summaries(self):
        """切换引擎后刷新汇总（各卡片已实时联动，此空实现供统一调用）"""
        self._refresh_tr_engine_combo()