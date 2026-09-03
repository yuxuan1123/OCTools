"""
OCTools/ui/options/set_stt.py
───────────────────────────────────────────────
STT 语音识别参数设置窗口（PySide6 版，音频 → TXT）

包含：
  1. 模型目录（SenseVoiceSmall 本地模型）
  2. 识别设备（CPU / CUDA）
  3. 识别语言（自动 / 中文 / 英文 / 粤语 / 日语 / 韩语）
  4. 数字归一化开关（ITN：1200 而非 一千二百）

点「确定」写回调用方持有的 SttConfig 对象。
"""

import os

from PySide6.QtCore import Qt, QSize
from ui import icon_res
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QComboBox,
    QLineEdit, QCheckBox, QPushButton, QWidget, QFileDialog,
)

from ui.options._base import OptionsDialogBase

from config.stt_config import (
    SttConfig, STT_DEFAULT_MODEL_DIR, STT_LANGUAGE_LABELS, STT_DEVICE_LABELS,
)
from ui.theme import THEME as T
from config.ui_config import CONFIG as C


class SetStt(OptionsDialogBase):
    """语音识别参数窗口"""

    def __init__(self, config: SttConfig, parent=None):
        super().__init__("语音识别参数 - 音频 → TXT", parent)
        self._config = config
        self.resize(600, 380)
        self.setMinimumSize(540, 340)

        self.build_header("语音识别参数（音频 → TXT）")
        body, b_lay = self.build_plain_body(margins=(20, 18, 20, 14))

        form = QFormLayout()
        form.setHorizontalSpacing(C.size("form_spacing"))
        form.setVerticalSpacing(C.size("form_spacing"))
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        # 模型目录
        model_row = QWidget(body)
        m_lay = QHBoxLayout(model_row)
        m_lay.setContentsMargins(0, 0, 0, 0)
        m_lay.setSpacing(C.size("header_row_spacing"))
        self._model_edit = QLineEdit(config.model_dir or STT_DEFAULT_MODEL_DIR, model_row)
        m_lay.addWidget(self._model_edit, 1)
        browse_btn = QPushButton("浏览…", model_row)
        browse_btn.setIcon(icon_res.colored_icon("folder"))
        browse_btn.setIconSize(QSize(C.size("icon_small"), C.size("icon_small")))
        browse_btn.setObjectName("primary")
        browse_btn.clicked.connect(self._browse_model)
        m_lay.addWidget(browse_btn)
        form.addRow("模型目录:", model_row)

        # 识别设备
        self._device_combo = QComboBox(body)
        self._device_combo.addItems([f"{code}（{label}）" for code, label in STT_DEVICE_LABELS])
        try:
            self._device_combo.setCurrentIndex(
                [c for c, _ in STT_DEVICE_LABELS].index(config.device))
        except ValueError:
            self._device_combo.setCurrentIndex(0)
        form.addRow("识别设备:", self._device_combo)

        # 识别语言
        self._lang_combo = QComboBox(body)
        self._lang_combo.addItems([f"{code}（{label}）" for code, label in STT_LANGUAGE_LABELS])
        try:
            self._lang_combo.setCurrentIndex(
                [c for c, _ in STT_LANGUAGE_LABELS].index(config.language))
        except ValueError:
            self._lang_combo.setCurrentIndex(0)
        form.addRow("识别语言:", self._lang_combo)

        # 数字归一化
        self._itn_check = QCheckBox("数字归一化（1200 而非 一千二百）", body)
        self._itn_check.setChecked(bool(config.use_itn))
        form.addRow("", self._itn_check)

        hint = QLabel(
            "SenseVoiceSmall 本地模型，完全离线识别（不联网）。\n"
            f"默认模型目录：{STT_DEFAULT_MODEL_DIR}",
            body)
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        form.addRow("", hint)
        b_lay.addLayout(form)
        b_lay.addStretch(1)

        # 底部按钮
        b_lay.addWidget(self.build_buttons(
            left_text="恢复默认", left_on_click=self._reset,
            ok_text="确定", ok_icon="check", on_ok=self._ok,
            margins=(0, 6, 0, 0)))

    # ── 工具 ──

    def _browse_model(self):
        start = self._model_edit.text().strip() or STT_DEFAULT_MODEL_DIR
        if os.path.isdir(start):
            start = os.path.dirname(start)
        d = QFileDialog.getExistingDirectory(self, "选择 SenseVoice 模型目录", start)
        if d:
            self._model_edit.setText(d)

    def _reset(self):
        self._load_into_form(SttConfig())

    # ── 表单 ⇄ 配置 ──

    def _collect_config(self) -> SttConfig:
        cfg = SttConfig()
        cfg.model_dir = self._model_edit.text().strip() or STT_DEFAULT_MODEL_DIR
        idx = self._device_combo.currentIndex()
        cfg.device = STT_DEVICE_LABELS[idx][0] if 0 <= idx < len(STT_DEVICE_LABELS) else "cpu"
        li = self._lang_combo.currentIndex()
        cfg.language = STT_LANGUAGE_LABELS[li][0] if 0 <= li < len(STT_LANGUAGE_LABELS) else "auto"
        cfg.use_itn = bool(self._itn_check.isChecked())
        return cfg

    def _load_into_form(self, cfg: SttConfig):
        self._model_edit.setText(cfg.model_dir or STT_DEFAULT_MODEL_DIR)
        try:
            self._device_combo.setCurrentIndex(
                [c for c, _ in STT_DEVICE_LABELS].index(cfg.device))
        except ValueError:
            self._device_combo.setCurrentIndex(0)
        try:
            self._lang_combo.setCurrentIndex(
                [c for c, _ in STT_LANGUAGE_LABELS].index(cfg.language))
        except ValueError:
            self._lang_combo.setCurrentIndex(0)
        self._itn_check.setChecked(bool(cfg.use_itn))

    def _ok(self):
        for k, v in self._collect_config().to_dict().items():
            setattr(self._config, k, v)
        self.accept()


def show_stt_options(parent, config: SttConfig, on_close=None):
    """打开「语音识别参数」窗口；点「确定」把表单值写回 config 并关闭。"""
    dlg = SetStt(config, parent)
    dlg.setAttribute(Qt.WA_DeleteOnClose)

    def _finished(_result):
        if on_close:
            on_close()

    dlg.finished.connect(_finished)
    dlg.show()
    dlg.raise_()
    dlg.activateWindow()
    return dlg
