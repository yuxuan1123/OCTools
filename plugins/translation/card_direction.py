"""
OCTools/ui/tabs/translation/card_direction.py
───────────────────────────────────────────────────────
翻译方向卡片：方向下拉 + 翻译引擎行（下拉 + 「模型参数…」+ 提示）+ 缺模型警告。

对应原文 _build_ui 中「卡片 1：翻译方向」整段。
"""

from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QComboBox, QPushButton,
)

from ui import icon_res
from config.ui_config import CONFIG as C

from plugins.translation.registry import TRANSLATOR, TR_ENGINE_LABELS, TR_ENGINE_ORDER
from ui.tabs.tab_component.card_widgets import make_card, make_title_row
from plugins.translation import engine_ctl


def build_direction_card(parent, **ctx):
    """翻译方向卡片（方向下拉 + 翻译引擎行 + 缺模型警告），返回 QFrame。

    ctx 需含 page（TabTranslation），用于登记 direction_combo / tr_engine_combo 并连接信号。
    """
    page = ctx["page"]

    card, c1 = make_card(parent)
    make_title_row(card, "translate", "翻译方向", c1)

    # 方向行
    dir_row = QWidget(card)
    d_lay = QHBoxLayout(dir_row)
    d_lay.setContentsMargins(0, 0, 0, 0)
    d_lay.setSpacing(C.size("form_row_spacing"))
    d_lab = QLabel("方向:", dir_row)
    d_lab.setObjectName("fieldLabel")
    d_lay.addWidget(d_lab)
    page.direction_combo = QComboBox(dir_row)
    page.direction_combo.addItems(
        [TRANSLATOR.DIRECTION_LABELS[d] for d in TRANSLATOR.DIRECTION_ORDER])
    # 默认「自动检测」
    try:
        page.direction_combo.setCurrentIndex(TRANSLATOR.DIRECTION_ORDER.index("auto"))
    except ValueError:
        page.direction_combo.setCurrentIndex(0)
    page.direction_combo.setMinimumWidth(C.size("combo_min_w"))
    d_lay.addWidget(page.direction_combo)
    d_hint = QLabel("（自动检测：含中文视为中→英，否则英→中）", dir_row)
    d_hint.setObjectName("hint")
    d_lay.addWidget(d_hint, 1)
    c1.addWidget(dir_row)

    # 翻译引擎行（预选模型 + 参数）
    eng_row = QWidget(card)
    eg_lay = QHBoxLayout(eng_row)
    eg_lay.setContentsMargins(0, 0, 0, 0)
    eg_lay.setSpacing(C.size("form_row_spacing"))
    eg_lab = QLabel("翻译引擎:", eng_row)
    eg_lab.setObjectName("fieldLabel")
    eg_lay.addWidget(eg_lab)
    page.tr_engine_combo = QComboBox(eng_row)
    page.tr_engine_combo.addItems([TR_ENGINE_LABELS[e] for e in TR_ENGINE_ORDER])
    page.tr_engine_combo.currentIndexChanged.connect(page._on_tr_engine_selected)
    page.tr_engine_combo.setMinimumWidth(C.size("combo_min_w_240"))
    eg_lay.addWidget(page.tr_engine_combo)
    tr_btn = QPushButton("模型参数…", eng_row)
    tr_btn.setObjectName("primary")
    tr_btn.setIcon(icon_res.colored_icon("globe"))
    tr_btn.setIconSize(QSize(C.size("icon_small"), C.size("icon_small")))
    tr_btn.clicked.connect(page.open_translator_options)
    eg_lay.addWidget(tr_btn)
    tr_hint = QLabel("（默认 Hy-MT2-1.8B 本地大模型）", eng_row)
    tr_hint.setObjectName("hint")
    eg_lay.addWidget(tr_hint, 1)
    c1.addWidget(eng_row)
    engine_ctl.refresh_tr_engine_combo(page)

    # 缺模型警告
    if not TRANSLATOR.models_ready(page.translator_config):
        cfg = page.translator_config
        if cfg.engine == "hy":
            detail = f"Hy-MT 模型文件不存在: {cfg.hy_model_path}（可点「模型参数」配置）"
        else:
            detail = f"Opus-MT 模型目录缺失: {cfg.opusmt_base}（与 mvp/l2l.py 相同）"
        warn = QLabel(f"{detail}，否则翻译会失败。", card)
        warn.setObjectName("hint")
        warn.setWordWrap(True)
        c1.addWidget(warn)

    return card