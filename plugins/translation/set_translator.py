"""
OCTools/ui/options/set_translator.py
───────────────────────────────────────────────
翻译引擎参数设置窗口（PySide6 版）

包含：
  1. 引擎选择：Hy-MT2-1.8B（默认）/ Opus-MT（轻量）
  2. Hy-MT2 参数：模型路径 / 上下文 / 线程 / GPU 层数 / 采样参数
  3. Opus-MT 参数：模型根目录

点「确定」写回调用方持有的 TranslatorConfig 对象。
"""

import os

from PySide6.QtCore import Qt, QSize
from ui import icon_res
from PySide6.QtWidgets import (
    QHBoxLayout, QFormLayout, QLabel, QComboBox,
    QLineEdit, QSpinBox, QDoubleSpinBox, QPushButton,
    QStackedWidget, QWidget, QFileDialog, QCheckBox,
)

from ui.options._base import OptionsDialogBase

from config.translator_config import (
    ENGINE_LABELS, ENGINE_ORDER, TranslatorConfig, HY_DEFAULT_MODEL_PATH,
)
from ui.theme import THEME as T
from config.ui_config import CONFIG as C

# Opus-MT 模型根目录兜底值（来自 config/ui_config.json 的 paths.models）
OPUS_BASE_FALLBACK = C.model_path("opus_base")
# 模型浏览对话框的起始目录（paths.models.root）
MODEL_ROOT = C.model_root()


class SetTranslator(OptionsDialogBase):
    """翻译引擎参数窗口"""

    def __init__(self, config: TranslatorConfig, parent=None):
        super().__init__("翻译引擎参数 - 中英互译", parent)
        self._config = config
        # 尺寸自适应屏幕：小屏幕不超出屏幕外（内容区可滚动）
        self.fit_size(660, 700, min_w=580, min_h=560)

        self.build_header("翻译引擎参数（中英互译）")

        # ── 可滚动内容区（窗口过小时滚动查看，不会超出屏幕）──
        body, b_lay = self.build_scroll_body(margins=(20, 16, 20, 14))

        # ── 引擎选择 ──
        card1, c1 = self.build_section_card("引擎选择", body)
        f1 = self.make_form(c1)
        c1.addLayout(f1)
        eng_row = QWidget(card1)
        e_lay = QHBoxLayout(eng_row)
        e_lay.setContentsMargins(0, 0, 0, 0)
        e_lay.setSpacing(C.size("form_row_spacing"))
        lab = QLabel("翻译引擎:", eng_row)
        lab.setObjectName("fieldLabel")
        e_lay.addWidget(lab)
        self._engine_combo = QComboBox(eng_row)
        self._engine_combo.addItems([ENGINE_LABELS[e] for e in ENGINE_ORDER])
        try:
            self._engine_combo.setCurrentIndex(ENGINE_ORDER.index(config.engine))
        except ValueError:
            self._engine_combo.setCurrentIndex(0)
        self._engine_combo.setMinimumWidth(240)
        e_lay.addWidget(self._engine_combo)
        hint = QLabel("Hy-MT2 质量更好（本地大模型）；Opus-MT 更轻量", eng_row)
        hint.setObjectName("hint")
        e_lay.addWidget(hint, 1)
        f1.addRow("", eng_row)
        b_lay.addWidget(card1)

        # ── 模型预加载（后台提前加载 OCR + 翻译模型，减少首次使用等待）──
        card2, c2 = self.build_section_card("模型预加载", body)
        f2 = self.make_form(c2)
        c2.addLayout(f2)
        self._preload_chk = QCheckBox("后台预加载 OCR / 翻译模型", card2)
        self._preload_chk.setChecked(bool(getattr(config, "preload_models", True)))
        f2.addRow("", self._preload_chk)
        self._preload_timing = QComboBox(card2)
        self._preload_timing.addItems(["主程序启动后（默认）", "进入翻译页时"])
        timing = getattr(config, "preload_timing", "startup")
        self._preload_timing.setCurrentIndex(0 if timing != "tab" else 1)
        f2.addRow("预加载时机:", self._preload_timing)
        # 取消勾选 → 禁用时机下拉
        self._preload_chk.toggled.connect(self._preload_timing.setEnabled)
        self._preload_timing.setEnabled(self._preload_chk.isChecked())
        f2.addRow("", self.hint_label("后台加载，不阻塞界面；关闭后首次使用需等待模型加载", card2))
        b_lay.addWidget(card2)

        # ── 屏幕翻译悬浮窗（显示相关，通用）──
        card3, c3 = self.build_section_card("屏幕翻译悬浮窗", body)
        f3 = self.make_form(c3)
        c3.addLayout(f3)

        self._overlay_font = QSpinBox(card3)
        self._overlay_font.setRange(8, 24)
        self._overlay_font.setSuffix(" px")
        self._overlay_font.setValue(int(getattr(config, "overlay_font_size", 12) or 12))
        f3.addRow("悬浮窗字号:", self._overlay_font)

        self._overlay_mode = QComboBox(card3)
        self._overlay_mode.addItems(["双语（原文 + 译文）", "仅译文"])
        mode = getattr(config, "overlay_mode", "both")
        self._overlay_mode.setCurrentIndex(0 if mode != "trans" else 1)
        f3.addRow("显示模式:", self._overlay_mode)

        self._bg_combo = QComboBox(card3)
        self._bg_items = [
            ("白色（默认）", "#FFFFFF"),
            ("透明", "transparent"),
            ("深蓝黑（半透明）", "#1F2937"),
            ("浅黄（半透明）", "#FFF7CC"),
            ("自定义颜色…", "__custom__"),
        ]
        self._bg_combo.addItems([t for t, _ in self._bg_items])
        self._custom_bg = ""
        self._sync_bg_combo(getattr(config, "overlay_bg_color", "transparent"))
        self._bg_combo.currentIndexChanged.connect(self._on_bg_changed)
        f3.addRow("背景颜色:", self._bg_combo)
        f3.addRow("", self.hint_label("背景随内容自动扩宽扩高", card3))
        b_lay.addWidget(card3)

        # ── 参数区（按引擎切换）──
        card4, c4 = self.build_section_card("引擎参数", body)
        self._stack = QStackedWidget(card4)
        c4.addWidget(self._stack)
        b_lay.addWidget(card4)

        # ── Hy-MT2-1.8B ──
        fr_hy = QWidget()
        hy_form = self.make_form(fr_hy)
        fr_hy.setLayout(hy_form)

        model_row = QWidget(fr_hy)
        m_lay = QHBoxLayout(model_row)
        m_lay.setContentsMargins(0, 0, 0, 0)
        m_lay.setSpacing(C.size("header_row_spacing"))
        self._hy_model = QLineEdit(config.hy_model_path or HY_DEFAULT_MODEL_PATH, model_row)
        m_lay.addWidget(self._hy_model, 1)
        browse_btn = QPushButton("浏览…", model_row)
        browse_btn.setIcon(icon_res.colored_icon("folder"))
        browse_btn.setIconSize(QSize(C.size("icon_small"), C.size("icon_small")))
        browse_btn.setObjectName("primary")
        browse_btn.clicked.connect(self._browse_model)
        m_lay.addWidget(browse_btn)
        hy_form.addRow("模型文件 (.gguf):", model_row)

        self._hy_ctx = QSpinBox(fr_hy)
        self._hy_ctx.setRange(512, 32768)
        self._hy_ctx.setSingleStep(256)
        self._hy_ctx.setValue(int(config.hy_n_ctx or 2048))
        hy_form.addRow("上下文 n_ctx:", self._hy_ctx)

        self._hy_threads = QSpinBox(fr_hy)
        self._hy_threads.setRange(1, 64)
        self._hy_threads.setValue(int(config.hy_n_threads or 4))
        hy_form.addRow("线程 n_threads:", self._hy_threads)

        self._hy_gpu = QSpinBox(fr_hy)
        self._hy_gpu.setRange(0, 128)
        self._hy_gpu.setValue(int(config.hy_n_gpu_layers or 0))
        hy_form.addRow("GPU 层数(0=纯CPU):", self._hy_gpu)

        self._hy_max_tokens = QSpinBox(fr_hy)
        self._hy_max_tokens.setRange(16, 4096)
        self._hy_max_tokens.setValue(int(config.hy_max_tokens or 256))
        hy_form.addRow("最大生成 max_tokens:", self._hy_max_tokens)

        self._hy_temp = QDoubleSpinBox(fr_hy)
        self._hy_temp.setRange(0.0, 2.0)
        self._hy_temp.setSingleStep(0.1)
        self._hy_temp.setValue(float(config.hy_temperature if config.hy_temperature is not None else 0.7))
        hy_form.addRow("温度 temperature:", self._hy_temp)

        self._hy_top_p = QDoubleSpinBox(fr_hy)
        self._hy_top_p.setRange(0.0, 1.0)
        self._hy_top_p.setSingleStep(0.05)
        self._hy_top_p.setValue(float(config.hy_top_p if config.hy_top_p is not None else 0.6))
        hy_form.addRow("top_p:", self._hy_top_p)

        self._hy_top_k = QSpinBox(fr_hy)
        self._hy_top_k.setRange(1, 100)
        self._hy_top_k.setValue(int(config.hy_top_k or 20))
        hy_form.addRow("top_k:", self._hy_top_k)

        self._hy_penalty = QDoubleSpinBox(fr_hy)
        self._hy_penalty.setRange(0.0, 2.0)
        self._hy_penalty.setSingleStep(0.05)
        self._hy_penalty.setValue(float(config.hy_repeat_penalty if config.hy_repeat_penalty is not None else 1.05))
        hy_form.addRow("重复惩罚 repeat_penalty:", self._hy_penalty)

        hy_form.addRow("", self.hint_label(
            f"默认模型：{HY_DEFAULT_MODEL_PATH}\n"
            "Hy-MT2-1.8B 为本地 GGUF 大模型，中英双向，质量优于 Opus-MT", fr_hy))
        self._stack.addWidget(fr_hy)

        # ── Opus-MT ──
        fr_opus = QWidget()
        opus_form = self.make_form(fr_opus)
        fr_opus.setLayout(opus_form)

        base_row = QWidget(fr_opus)
        b_lay2 = QHBoxLayout(base_row)
        b_lay2.setContentsMargins(0, 0, 0, 0)
        b_lay2.setSpacing(C.size("header_row_spacing"))
        self._opus_base = QLineEdit(config.opusmt_base or "", base_row)
        b_lay2.addWidget(self._opus_base, 1)
        browse2 = QPushButton("浏览…", base_row)
        browse2.setIcon(icon_res.colored_icon("folder"))
        browse2.setIconSize(QSize(C.size("icon_small"), C.size("icon_small")))
        browse2.setObjectName("primary")
        browse2.clicked.connect(self._browse_opus_base)
        b_lay2.addWidget(browse2)
        opus_form.addRow("模型根目录:", base_row)

        opus_form.addRow("", self.hint_label(
            "根目录下需包含 opus-mt-en-zh-ct2 / raw_en-zh 与 opus-mt-zh-en-ct2 / raw_zh-en"
            "（与 mvp/l2l.py 相同）", fr_opus))
        self._stack.addWidget(fr_opus)

        self._engine_combo.currentIndexChanged.connect(self._on_engine_changed)
        self._on_engine_changed(self._engine_combo.currentIndex())

        # ── 底部按钮（固定在窗口底部，不随内容滚动）──
        self._lay.addWidget(self.build_buttons(
            left_text="恢复默认", left_on_click=self._reset,
            ok_text="确定", ok_icon="check", on_ok=self._ok,
            margins=(20, 4, 20, 12)))

    # ── 工具 ──

    def _browse_model(self):
        start = self._hy_model.text().strip() or HY_DEFAULT_MODEL_PATH
        path, _ = QFileDialog.getOpenFileName(
            self, "选择 Hy-MT2 模型文件 (.gguf)", os.path.dirname(start),
            "GGUF 模型 (*.gguf);;所有文件 (*.*)")
        if path:
            self._hy_model.setText(path)

    def _browse_opus_base(self):
        start = self._opus_base.text().strip() or MODEL_ROOT or OPUS_BASE_FALLBACK
        d = QFileDialog.getExistingDirectory(self, "选择 Opus-MT 模型根目录", start)
        if d:
            self._opus_base.setText(d)

    def _on_engine_changed(self, idx: int):
        eng = ENGINE_ORDER[idx] if 0 <= idx < len(ENGINE_ORDER) else "hy"
        self._stack.setCurrentIndex(0 if eng == "hy" else 1)

    # ── 悬浮窗背景色 ──

    def _sync_bg_combo(self, value: str):
        """按配置值设置背景下拉；非预设值落到「自定义…」"""
        value = value or "#FFFFFF"
        for i, (_label, v) in enumerate(self._bg_items):
            if v == value:
                self._bg_combo.setCurrentIndex(i)
                return
        self._custom_bg = value
        self._bg_combo.setCurrentIndex(len(self._bg_items) - 1)

    def _on_bg_changed(self, idx: int):
        if 0 <= idx < len(self._bg_items) and self._bg_items[idx][1] == "__custom__":
            from PySide6.QtWidgets import QColorDialog
            from PySide6.QtGui import QColor
            initial = QColor(self._custom_bg) if QColor(self._custom_bg).isValid() else QColor("#1F2937")
            color = QColorDialog.getColor(initial, self, "选择悬浮窗背景颜色")
            if color.isValid():
                self._custom_bg = color.name().upper()
            else:
                # 取消：回到上一个实际值
                self._sync_bg_combo(self._custom_bg or "#FFFFFF")

    def _bg_value(self) -> str:
        idx = self._bg_combo.currentIndex()
        if 0 <= idx < len(self._bg_items):
            v = self._bg_items[idx][1]
            if v == "__custom__":
                return self._custom_bg or "#FFFFFF"
            return v
        return "#FFFFFF"

    def _reset(self):
        self._load_into_form(TranslatorConfig())

    # ── 表单 ⇄ 配置 ──

    def _collect_config(self) -> TranslatorConfig:
        cfg = TranslatorConfig()
        idx = self._engine_combo.currentIndex()
        cfg.engine = ENGINE_ORDER[idx] if 0 <= idx < len(ENGINE_ORDER) else "hy"
        cfg.hy_model_path = self._hy_model.text().strip() or HY_DEFAULT_MODEL_PATH
        cfg.hy_n_ctx = int(self._hy_ctx.value())
        cfg.hy_n_threads = int(self._hy_threads.value())
        cfg.hy_n_gpu_layers = int(self._hy_gpu.value())
        cfg.hy_max_tokens = int(self._hy_max_tokens.value())
        cfg.hy_temperature = float(self._hy_temp.value())
        cfg.hy_top_p = float(self._hy_top_p.value())
        cfg.hy_top_k = int(self._hy_top_k.value())
        cfg.hy_repeat_penalty = float(self._hy_penalty.value())
        cfg.opusmt_base = self._opus_base.text().strip() or OPUS_BASE_FALLBACK
        cfg.overlay_font_size = int(self._overlay_font.value())
        cfg.overlay_mode = "trans" if self._overlay_mode.currentIndex() == 1 else "both"
        cfg.overlay_bg_color = self._bg_value()
        cfg.preload_models = self._preload_chk.isChecked()
        cfg.preload_timing = "startup" if self._preload_timing.currentIndex() == 0 else "tab"
        return cfg

    def _load_into_form(self, cfg: TranslatorConfig):
        self._engine_combo.setCurrentIndex(
            ENGINE_ORDER.index(cfg.engine) if cfg.engine in ENGINE_ORDER else 0)
        self._hy_model.setText(cfg.hy_model_path or HY_DEFAULT_MODEL_PATH)
        self._hy_ctx.setValue(int(cfg.hy_n_ctx or 2048))
        self._hy_threads.setValue(int(cfg.hy_n_threads or 4))
        self._hy_gpu.setValue(int(cfg.hy_n_gpu_layers or 0))
        self._hy_max_tokens.setValue(int(cfg.hy_max_tokens or 256))
        self._hy_temp.setValue(float(cfg.hy_temperature if cfg.hy_temperature is not None else 0.7))
        self._hy_top_p.setValue(float(cfg.hy_top_p if cfg.hy_top_p is not None else 0.6))
        self._hy_top_k.setValue(int(cfg.hy_top_k or 20))
        self._hy_penalty.setValue(float(cfg.hy_repeat_penalty if cfg.hy_repeat_penalty is not None else 1.05))
        self._opus_base.setText(cfg.opusmt_base or "")
        self._overlay_font.setValue(int(getattr(cfg, "overlay_font_size", 12) or 12))
        self._overlay_mode.setCurrentIndex(0 if getattr(cfg, "overlay_mode", "both") != "trans" else 1)
        self._sync_bg_combo(getattr(cfg, "overlay_bg_color", "#FFFFFF"))
        self._preload_chk.setChecked(bool(getattr(cfg, "preload_models", True)))
        self._preload_timing.setCurrentIndex(
            0 if getattr(cfg, "preload_timing", "startup") != "tab" else 1)
        self._preload_timing.setEnabled(self._preload_chk.isChecked())
        self._on_engine_changed(self._engine_combo.currentIndex())

    def _ok(self):
        for k, v in self._collect_config().to_dict().items():
            setattr(self._config, k, v)
        self.accept()


def show_translator_options(parent, config: TranslatorConfig, on_close=None):
    """打开「翻译引擎参数」窗口；点「确定」把表单值写回 config 并关闭。"""
    dlg = SetTranslator(config, parent)
    dlg.setAttribute(Qt.WA_DeleteOnClose)

    def _finished(_result):
        if on_close:
            on_close()

    dlg.finished.connect(_finished)
    dlg.show()
    dlg.raise_()
    dlg.activateWindow()
    return dlg