"""
OCTools/ui/tabs/conversion/card_target.py
────────────────────────────────────────
目标格式卡片：二级格式选择器 + 预设区（md→docx 排版 / 图片→docx 预设 /
TXT·MD→音频 语音引擎 / 音频→TXT 语音识别 / 占位提示）。

对应原 tab_conversion.py 中「卡片 2：目标格式」整段。
"""

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QLabel, QComboBox, QPushButton

from ui import icon_res
from config.ui_config import CONFIG as C

from ui.tabs.tab_component.card_widgets import make_card, make_title_row
from ui.tabs.conversion import target_ctl, engine_ctl
from ui.tabs.conversion.registry import (
    ALL_FORMATS, FormatPicker, _categories_for,
    PRESET_NEW_OPTION, IMG_PRESET_DEFAULT_OPTION,
    TTS_ENGINE_LABELS, TTS_ENGINE_ORDER,
)
from ui.tabs.tab_component.docx_format_card import DocxFormatCard


def build_target_card(parent, **ctx):
    """目标格式卡片，返回 QFrame。

    ctx 需含 page（TabConversion），用于登记 format_picker / docx_card /
    img_preset_combo / tts_engine_combo / _stt_summary / _preset_area 等。
    """
    page = ctx["page"]

    card, c2 = make_card(parent)
    make_title_row(card, "target", "目标格式", c2)

    form2 = QFormLayout()
    form2.setHorizontalSpacing(12)
    form2.setVerticalSpacing(9)
    form2.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

    page.format_picker = FormatPicker(_categories_for(ALL_FORMATS), card)
    page.format_picker.format_selected.connect(page._select_format)
    target_ctl.update_picker_available(page, list(page._format_list))
    form2.addRow("选择目标格式:", page.format_picker)

    # 预设区（md→docx / 图片→docx / tts / stt / 占位）
    page._preset_area = QWidget(card)
    pa_lay = QVBoxLayout(page._preset_area)
    pa_lay.setContentsMargins(0, 4, 0, 0)
    pa_lay.setSpacing(4)

    # md → docx 排版卡片（预设下拉 + 编辑按钮复用「格式选项」弹窗）
    page.docx_card = DocxFormatCard(
        page._preset_area, page.current_config,
        on_edit=page._show_format_panel)
    page.docx_card.config_changed.connect(page._on_docx_card_config_changed)
    pa_lay.addWidget(page.docx_card)
    page.docx_card.setVisible(False)

    # 图片 → docx 预设行
    page._img_row_w = QWidget(page._preset_area)
    ig_lay = QHBoxLayout(page._img_row_w)
    ig_lay.setContentsMargins(0, 0, 0, 0)
    ig_lay.setSpacing(C.size("form_row_spacing"))
    ig_lab = QLabel("图片预设:", page._img_row_w)
    ig_lab.setObjectName("fieldLabel")
    ig_lay.addWidget(ig_lab)
    page.img_preset_combo = QComboBox(page._img_row_w)
    page.img_preset_combo.currentIndexChanged.connect(page._on_img_preset_selected)
    page.img_preset_combo.setMinimumWidth(200)
    ig_lay.addWidget(page.img_preset_combo, 1)
    target_ctl.refresh_img_preset_combo(page)
    pa_lay.addWidget(page._img_row_w)
    page._img_row_w.setVisible(False)

    # txt/md → 音频：语音引擎行
    page._tts_row_w = QWidget(page._preset_area)
    tt_lay = QHBoxLayout(page._tts_row_w)
    tt_lay.setContentsMargins(0, 0, 0, 0)
    tt_lay.setSpacing(C.size("form_row_spacing"))
    tt_lab = QLabel("语音引擎:", page._tts_row_w)
    tt_lab.setObjectName("fieldLabel")
    tt_lay.addWidget(tt_lab)
    page.tts_engine_combo = QComboBox(page._tts_row_w)
    page.tts_engine_combo.addItems([TTS_ENGINE_LABELS[e] for e in TTS_ENGINE_ORDER])
    page.tts_engine_combo.currentIndexChanged.connect(page._on_tts_engine_selected)
    page.tts_engine_combo.setMinimumWidth(180)
    tt_lay.addWidget(page.tts_engine_combo)
    engine_ctl.refresh_tts_engine_combo(page)
    tts_btn = QPushButton("语音参数…", page._tts_row_w)
    tts_btn.setObjectName("primary")
    tts_btn.setIcon(icon_res.colored_icon("microphone"))
    tts_btn.setIconSize(QSize(C.size("icon_small"), C.size("icon_small")))
    tts_btn.clicked.connect(page._open_tts_options)
    tt_lay.addWidget(tts_btn)
    tt_hint = QLabel("（TXT/MD → 音频 的合成方式与音色）", page._tts_row_w)
    tt_hint.setObjectName("hint")
    tt_lay.addWidget(tt_hint, 1)
    pa_lay.addWidget(page._tts_row_w)
    page._tts_row_w.setVisible(False)

    # 音频 → txt：语音识别引擎行
    page._stt_row_w = QWidget(page._preset_area)
    st_lay = QHBoxLayout(page._stt_row_w)
    st_lay.setContentsMargins(0, 0, 0, 0)
    st_lay.setSpacing(C.size("form_row_spacing"))
    st_lab = QLabel("语音识别:", page._stt_row_w)
    st_lab.setObjectName("fieldLabel")
    st_lay.addWidget(st_lab)
    page._stt_summary = QLabel("", page._stt_row_w)
    page._stt_summary.setObjectName("hint")
    st_lay.addWidget(page._stt_summary, 1)
    stt_btn = QPushButton("识别参数…", page._stt_row_w)
    stt_btn.setObjectName("primary")
    stt_btn.setIcon(icon_res.colored_icon("terminal"))
    stt_btn.setIconSize(QSize(C.size("icon_small"), C.size("icon_small")))
    stt_btn.clicked.connect(page._open_stt_options)
    st_lay.addWidget(stt_btn)
    stt_hint = QLabel("（音频 → TXT 的识别引擎与语言）", page._stt_row_w)
    stt_hint.setObjectName("hint")
    st_lay.addWidget(stt_hint)
    pa_lay.addWidget(page._stt_row_w)
    page._stt_row_w.setVisible(False)

    # pdf → docx：转换方式行
    page._pdf_row_w = QWidget(page._preset_area)
    pd_lay = QHBoxLayout(page._pdf_row_w)
    pd_lay.setContentsMargins(0, 0, 0, 0)
    pd_lay.setSpacing(C.size("form_row_spacing"))
    pd_lab = QLabel("转换方式:", page._pdf_row_w)
    pd_lab.setObjectName("fieldLabel")
    pd_lay.addWidget(pd_lab)
    page._pdf_summary = QLabel("", page._pdf_row_w)
    page._pdf_summary.setObjectName("hint")
    pd_lay.addWidget(page._pdf_summary, 1)
    pdf_btn = QPushButton("转换方式…", page._pdf_row_w)
    pdf_btn.setObjectName("primary")
    pdf_btn.setIcon(icon_res.colored_icon("file-text"))
    pdf_btn.setIconSize(QSize(C.size("icon_small"), C.size("icon_small")))
    pdf_btn.clicked.connect(page._open_pdf_docx_options)
    pd_lay.addWidget(pdf_btn)
    pd_hint = QLabel("（PDF → DOCX 的实现方式）", page._pdf_row_w)
    pd_hint.setObjectName("hint")
    pd_lay.addWidget(pd_hint)
    pa_lay.addWidget(page._pdf_row_w)
    page._pdf_row_w.setVisible(False)
    target_ctl.refresh_pdf_docx_summary(page)

    # 占位提示
    page._preset_none_label = QLabel(
        "预设选择：无可用预设（仅 MD→DOCX / 图片→DOCX / TXT·MD→音频 / 音频→TXT 支持预设）",
        page._preset_area)
    page._preset_none_label.setObjectName("hint")
    pa_lay.addWidget(page._preset_none_label)
    page._preset_none_label.setVisible(False)

    form2.addRow("", page._preset_area)
    c2.addLayout(form2)

    return card
