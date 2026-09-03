"""
OCTools/ui/tabs/plugins/style_lab/tab_style_lab.py
───────────────────────────────────────────────
全局 QSS 样式实验室页面。按类别展示 theme.py 里所有已定义的
objectName / selector，并直接渲染对应控件给出真实预览。

区块：
  1. 按钮    primary / ghost / danger / secondary / convertBtn / catBtn / chip
  2. 导航    navBtn
  3. 标签    pageTitle / pageSubtitle / cardTitle / sectionTitle / hint / formLabel / ...
  4. 徽章/轻提示  badge / toast
  5. 卡片    SettingsSection / card / header / docxFormatCard / dxf*
  6. 输入控件  QLineEdit / QComboBox / QSpinBox — normal / focus / disabled
  7. 勾选/单选  QCheckBox / QRadioButton — unchecked / checked
  8. 滑块    QSlider
  9. 折叠面板  QToolButton#sectionHeader
  10. 日志    QTextEdit#log

每个样式同时给出 objectName / selector、用途说明、可复制的 setObjectName 代码。
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QComboBox, QSpinBox, QCheckBox, QRadioButton, QSlider, QToolButton,
    QTextEdit, QFrame, QScrollArea, QSizePolicy,
)

from config.ui_config import CONFIG as C
from ui.tabs.tab_component.page_header import build_page_header


def _section_card(parent, title: str, hint: str = ""):
    """生成一张 SettingsSection 卡片 + 标题 + 可选副标题，返回 (card, lay)。"""
    card = QFrame(parent)
    card.setObjectName("SettingsSection")
    lay = QVBoxLayout(card)
    lay.setContentsMargins(
        C.size("group_padding_h"), C.size("group_padding_v"),
        C.size("group_padding_h"), C.size("group_padding_v"))
    lay.setSpacing(C.size("form_row_spacing"))
    t = QLabel(title, card)
    t.setObjectName("cardTitle")
    lay.addWidget(t)
    if hint:
        h = QLabel(hint, card)
        h.setObjectName("hint")
        h.setWordWrap(True)
        lay.addWidget(h)
    return card, lay


def _meta_row(lay, obj_name: str, selector: str, purpose: str, usage: str):
    """在样式卡片里追加一行样式元信息（objectName / 选择器 / 用途 / 代码）。"""
    row = QHBoxLayout()
    row.setSpacing(C.size("form_row_spacing"))
    lab = QLabel(obj_name or "(base)", lay.parentWidget())
    lab.setObjectName("formLabel")
    lab.setFixedWidth(110)
    row.addWidget(lab)
    code = QLineEdit(selector, lay.parentWidget())
    code.setReadOnly(True)
    code.setFixedWidth(260)
    row.addWidget(code)
    lay.addLayout(row)
    if purpose:
        p = QLabel(purpose, lay.parentWidget())
        p.setObjectName("hint")
        p.setWordWrap(True)
        lay.addWidget(p)
    if usage:
        u = QLabel(usage, lay.parentWidget())
        u.setWordWrap(True)
        u.setStyleSheet(
            f"font-family: Consolas, Courier New, monospace; "
            f"font-size: {C.font('log')}px; "
            f"color: {C.color('primary_dark')}; "
            f"background: {C.color('primary_light')}; "
            f"border-radius: {C.size('radius_btn')}px; "
            f"padding: 4px 8px;")
        lay.addWidget(u)


# ──────────────────────────────────────────────────────────


class TabStyleLab(QWidget):
    """QSS 样式实验室：按类别列出所有 objectName，并给出真实控件预览。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(C.size("card_spacing"))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("bareScroll")
        outer.addWidget(scroll)

        content = QWidget()
        content.setObjectName("bareSurface")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(C.size("card_spacing"))
        cl.setAlignment(Qt.AlignTop)

        cl.addWidget(build_page_header(content, "page_plugin_title", "page_plugin_sub"))

        # ── 1. 按钮 ──
        cl.addWidget(self._buttons_section(content))

        # ── 2. 导航按钮 ──
        cl.addWidget(self._nav_section(content))

        # ── 3. 标签 ──
        cl.addWidget(self._labels_section(content))

        # ── 4. 徽章 / 轻提示 ──
        cl.addWidget(self._badge_toast_section(content))

        # ── 5. 卡片容器 ──
        cl.addWidget(self._frames_section(content))

        # ── 6. 输入控件 ──
        cl.addWidget(self._inputs_section(content))

        # ── 7. 勾选 / 单选 ──
        cl.addWidget(self._check_section(content))

        # ── 8. 滑块 ──
        cl.addWidget(self._slider_section(content))

        # ── 9. 折叠面板 ──
        cl.addWidget(self._section_header(content))

        # ── 10. 日志区 ──
        cl.addWidget(self._log_section(content))

        scroll.setWidget(content)

    # ────────────── 每个区块都是一张 SettingsSection 卡片 ──────────────

    def _buttons_section(self, parent):
        card, lay = _section_card(parent, "按钮", "所有 QPushButton 子类样式（含 hover / checked / disabled）")
        items = [
            ("primary",      "QPushButton#primary",       "主操作（实心品牌蓝底白字）",       "btn.setObjectName('primary')"),
            ("ghost",        "QPushButton#ghost",          "次操作（浅灰底 + 深字 + 细边框）", "btn.setObjectName('ghost')"),
            ("danger",       "QPushButton#danger",         "危险操作（红色实心）",             "btn.setObjectName('danger')"),
            ("secondary",    "QPushButton#secondary",       "次级强调（绿色实心）",             "btn.setObjectName('secondary')"),
            ("convertBtn",   "QPushButton#convertBtn",     "大号 CTA 转换按钮（大圆角 + 大字）", "btn.setObjectName('convertBtn')"),
            ("catBtn",       "QPushButton#catBtn",         "格式二级选择器（透明底、checked 浅蓝）", "btn.setObjectName('catBtn')"),
            ("chip",         "QPushButton#chip",           "标签/筛选 chip（描边、checked 主色）", "btn.setObjectName('chip')"),
            ("(base)",       "QPushButton",                "普通按钮（未命名时的默认样式）",    "QPushButton(parent)  # 不传 setObjectName"),
        ]
        for obj, sel, purpose, usage in items:
            _meta_row(lay, obj, sel, purpose, usage)
            row = QHBoxLayout()
            row.setSpacing(C.size("form_row_spacing"))
            row.setContentsMargins(20, 0, 0, 0)
            for state_name, make in self._button_state_makers(obj):
                b = make(card)
                b.setMinimumWidth(110)
                if obj == "(base)":
                    pass  # 保持普通按钮
                row.addWidget(b)
            row.addStretch(1)
            lay.addLayout(row)
        return card

    def _button_state_makers(self, obj: str):
        """返回 [(标签, lambda(parent) -> QPushButton), ...] 覆盖 normal / hover / checked / disabled。"""
        base = lambda parent: QPushButton("示例", parent)
        if obj == "(base)":
            return [
                ("normal",  lambda p: QPushButton("普通按钮", p)),
                ("disabled", self._make_lambda_disabled("普通按钮")),
            ]

        def mk(text, obj_name, checked=False, disabled=False):
            def fn(parent):
                b = QPushButton(text, parent)
                b.setObjectName(obj_name)
                if obj_name in ("catBtn", "chip"):
                    b.setCheckable(True)
                    b.setChecked(checked)
                if obj_name in ("navBtn", "convertBtn", "primary", "ghost", "danger", "secondary"):
                    b.setCheckable(checked)
                    if checked:
                        b.setChecked(True)
                if disabled:
                    b.setEnabled(False)
                return b
            return fn

        states = [("normal", mk("normal", obj))]
        if obj in ("catBtn", "chip"):
            states.append(("checked", mk("checked", obj, checked=True)))
        if obj in ("primary", "ghost", "danger", "secondary", "convertBtn"):
            states.append(("disabled", mk("disabled", obj, disabled=True)))
        states.append(("disabled", mk("disabled", obj, disabled=True)))
        # 去重，disabled 只保留一次
        seen = set(); dedup = []
        for s in states:
            if s[0] not in seen:
                seen.add(s[0]); dedup.append(s)
        return dedup

    @staticmethod
    def _make_lambda_disabled(text):
        def fn(parent):
            b = QPushButton(text, parent)
            b.setEnabled(False)
            return b
        return fn

    # ── 导航 ──
    def _nav_section(self, parent):
        card, lay = _section_card(parent, "侧栏导航", "导航入口按钮样式")
        _meta_row(lay, "navBtn", "QPushButton#navBtn",
                  "透明底 + 选中主色高亮；支持 hover / checked / pressed",
                  "btn.setObjectName('navBtn')  # 需 setCheckable(True)")
        row = QHBoxLayout()
        row.setContentsMargins(20, 0, 0, 0)
        b1 = QPushButton("未选中", card); b1.setObjectName("navBtn"); b1.setCheckable(True)
        b2 = QPushButton("hover",   card); b2.setObjectName("navBtn"); b2.setCheckable(True)
        b3 = QPushButton("已选中",   card); b3.setObjectName("navBtn"); b3.setCheckable(True); b3.setChecked(True)
        for b in (b1, b2, b3):
            b.setMinimumWidth(130); row.addWidget(b)
        row.addStretch(1); lay.addLayout(row)
        return card

    # ── 标签 ──
    def _labels_section(self, parent):
        card, lay = _section_card(parent, "标签（QLabel objectName）",
                                 "统一颜色 / 字号 / 粗细的文本层级系统")
        items = [
            ("pageTitle",    "QLabel#pageTitle",    "页面主标题（大号粗体）",
             "lab = QLabel('标题'); lab.setObjectName('pageTitle')",
             "页面主标题"),
            ("pageSubtitle", "QLabel#pageSubtitle", "页面副标题（浅灰、小字号）",
             "lab.setObjectName('pageSubtitle')",
             "页面副标题，补充说明一下正文要表达什么。"),
            ("cardTitle",    "QLabel#cardTitle",    "卡片内标题（中等粗体）",
             "lab.setObjectName('cardTitle')",
             "卡片标题 14px Bold"),
            ("sectionTitle", "QLabel#sectionTitle", "分节标题（主色 / 强调）",
             "lab.setObjectName('sectionTitle')",
             "分节标题（主色）"),
            ("hint",         "QLabel#hint",         "提示/辅助说明（浅灰、小字号）",
             "lab.setObjectName('hint')",
             "辅助说明文字，灰色小字。"),
            ("formLabel",    "QLabel#formLabel",    "表单字段左侧标签（浅灰、定宽）",
             "lab.setObjectName('formLabel')",
             "字段标签"),
            ("fieldLabel",   "QLabel#fieldLabel",   "表单加粗字段（深色、粗体）",
             "lab.setObjectName('fieldLabel')",
             "加粗字段值"),
            ("summary",      "QLabel#summary",      "摘要/统计（浅灰小字）",
             "lab.setObjectName('summary')",
             "共 12 个文件 · 3 分钟前"),
            ("(base)",       "QLabel",              "普通标签（未命名时的默认样式）",
             "QLabel(parent)",
             "普通文本，未指定 objectName 时走全局 QWidget color。"),
        ]
        for obj, sel, purpose, usage, text in items:
            _meta_row(lay, obj, sel, purpose, usage)
            r = QLabel(text, card)
            if obj != "(base)":
                r.setObjectName(obj)
            r.setWordWrap(True)
            r.setStyleSheet("margin-left: 20px;")
            lay.addWidget(r)
        return card

    # ── 徽章 / Toast ──
    def _badge_toast_section(self, parent):
        card, lay = _section_card(parent, "徽章 & 轻提示",
                                  "QLabel 通过动态 property 切换状态")
        _meta_row(lay, "badge", "QLabel#badge[ok=\"1\"|\"0\"]",
                  "插件加载状态徽章（ok=1 绿色成功 / ok=0 红色失败）",
                  "lab.setObjectName('badge'); lab.setProperty('ok', '1')\nlab.style().polish(lab)")
        row = QHBoxLayout(); row.setContentsMargins(20, 0, 0, 0); row.setSpacing(C.size("form_row_spacing"))
        b1 = QLabel("已加载", card); b1.setObjectName("badge"); b1.setProperty("ok", "1"); b1.style().polish(b1)
        b2 = QLabel("加载失败", card); b2.setObjectName("badge"); b2.setProperty("ok", "0"); b2.style().polish(b2)
        row.addWidget(b1); row.addWidget(b2); row.addStretch(1); lay.addLayout(row)

        _meta_row(lay, "toast", "QLabel#toast[kind=\"success\"|\"info\"|\"warn\"]",
                  "轻提示（右上角飞出气泡）",
                  "lab.setObjectName('toast'); lab.setProperty('kind', 'success'); lab.style().polish(lab)")
        row2 = QHBoxLayout(); row2.setContentsMargins(20, 0, 0, 0); row2.setSpacing(C.size("form_row_spacing"))
        for kind, txt in (("success", "✔ 保存成功"), ("info", "ⓘ 已暂停"), ("warn", "⚠ 请选择文件")):
            t = QLabel(txt, card); t.setObjectName("toast"); t.setProperty("kind", kind); t.style().polish(t)
            row2.addWidget(t)
        row2.addStretch(1); lay.addLayout(row2)
        return card

    # ── 卡片 ──
    def _frames_section(self, parent):
        card, lay = _section_card(parent, "卡片容器",
                                  "QFrame 的不同 objectName 决定了整个容器的外观")
        items = [
            ("SettingsSection", "QFrame#SettingsSection", "设置分组卡片（白底 + 边框 + 圆角）",
             "f = QFrame(); f.setObjectName('SettingsSection')"),
            ("card",            "QFrame#card",             "通用卡片（白底 + 边框 + 圆角）",
             "f.setObjectName('card')"),
            ("header",          "QFrame#header",           "弹窗顶栏（底部边框 + 顶部圆角）",
             "f.setObjectName('header')"),
            ("docxFormatCard",  "QFrame#docxFormatCard",   "MD→DOCX 排版卡片（白底 + 边框 + 圆角）",
             "f.setObjectName('docxFormatCard')"),
            ("dxfHeader",       "QFrame#dxfHeader",        "docxFormatCard 的顶部带区（subtle_bg）",
             "f.setObjectName('dxfHeader')"),
            ("dxfBtnBar",       "QFrame#dxfBtnBar",        "docxFormatCard 的底部按钮带（subtle_bg）",
             "f.setObjectName('dxfBtnBar')"),
        ]
        for obj, sel, purpose, usage in items:
            _meta_row(lay, obj, sel, purpose, usage)
            f = QFrame(card); f.setObjectName(obj)
            f.setMinimumHeight(48)
            fl = QVBoxLayout(f); fl.setContentsMargins(12, 8, 12, 8)
            fl.addWidget(QLabel(obj + " 示例", f))
            lay.addWidget(f)

        # headerTitle
        _meta_row(lay, "headerTitle", "QLabel#headerTitle",
                  "弹窗顶栏标题文字",
                  "lab.setObjectName('headerTitle')")
        ht = QLabel("弹窗顶栏标题", card); ht.setObjectName("headerTitle"); ht.setStyleSheet("margin-left:20px")
        lay.addWidget(ht)
        return card

    # ── 输入 ──
    def _inputs_section(self, parent):
        card, lay = _section_card(parent, "输入控件",
                                  "QLineEdit / QComboBox / QSpinBox 的 normal / focus / disabled")
        _meta_row(lay, "(base)", "QLineEdit / QComboBox / QSpinBox",
                  "白底 + 浅灰边框 + 圆角；focus 时主色边框",
                  "e = QLineEdit(parent)")

        for cls_name, cls in (("QLineEdit", QLineEdit),
                              ("QComboBox", QComboBox),
                              ("QSpinBox", QSpinBox)):
            row = QHBoxLayout(); row.setContentsMargins(20, 0, 0, 0); row.setSpacing(C.size("form_row_spacing"))
            for state in ("normal", "focus", "disabled"):
                e = cls(card)
                if cls == QLineEdit:
                    e.setPlaceholderText(f"{cls_name} · {state}")
                elif cls == QComboBox:
                    e.addItems([f"{cls_name} · {state}"])
                elif cls == QSpinBox:
                    e.setRange(0, 99); e.setValue(42)
                if state == "disabled":
                    e.setEnabled(False)
                e.setMinimumWidth(180)
                row.addWidget(QLabel(state, card))
                row.addWidget(e, 1)
            row.addStretch(1); lay.addLayout(row)
        return card

    # ── 勾选 / 单选 ──
    def _check_section(self, parent):
        card, lay = _section_card(parent, "勾选 & 单选",
                                  "QCheckBox / QRadioButton：白底圆形/方形 + 主色 checked")
        row1 = QHBoxLayout(); row1.setContentsMargins(20, 0, 0, 0); row1.setSpacing(24)
        row1.addWidget(QLabel("QCheckBox", card))
        cb1 = QCheckBox("未选中", card)
        cb2 = QCheckBox("已选中", card); cb2.setChecked(True)
        row1.addWidget(cb1); row1.addWidget(cb2); row1.addStretch(1); lay.addLayout(row1)

        row2 = QHBoxLayout(); row2.setContentsMargins(20, 0, 0, 0); row2.setSpacing(24)
        row2.addWidget(QLabel("QRadioButton", card))
        rb1 = QRadioButton("未选中", card)
        rb2 = QRadioButton("已选中", card); rb2.setChecked(True)
        row2.addWidget(rb1); row2.addWidget(rb2); row2.addStretch(1); lay.addLayout(row2)
        return card

    # ── 滑块 ──
    def _slider_section(self, parent):
        card, lay = _section_card(parent, "滑块",
                                  "QSlider::groove / sub-page / handle — 全局缩放等场景")
        row = QHBoxLayout(); row.setContentsMargins(20, 0, 0, 0); row.setSpacing(16)
        row.addWidget(QLabel("QSlider", card))
        s1 = QSlider(Qt.Horizontal, card); s1.setRange(0, 100); s1.setValue(60); s1.setMinimumWidth(280)
        row.addWidget(s1, 1)
        lay.addLayout(row)
        return card

    # ── 折叠面板 ──
    def _section_header(self, parent):
        card, lay = _section_card(parent, "折叠面板",
                                  "QToolButton#sectionHeader — 浅色 header 背景，点击折叠子面板")
        _meta_row(lay, "sectionHeader", "QToolButton#sectionHeader",
                  "浅灰 header 底 + 圆角 + 左边距对齐；hover 加深",
                  "tb = QToolButton(); tb.setObjectName('sectionHeader')")
        row = QHBoxLayout(); row.setContentsMargins(20, 0, 0, 0); row.setSpacing(C.size("form_row_spacing"))
        tb1 = QToolButton(card); tb1.setObjectName("sectionHeader"); tb1.setText("导入清单预览 ▾")
        tb2 = QToolButton(card); tb2.setObjectName("sectionHeader"); tb2.setText("高级设置 ▾")
        row.addWidget(tb1); row.addWidget(tb2); row.addStretch(1); lay.addLayout(row)
        return card

    # ── 日志 ──
    def _log_section(self, parent):
        card, lay = _section_card(parent, "日志区",
                                  "QTextEdit#log — 等宽字体 + 深色底 + 浅色文字")
        _meta_row(lay, "log", "QTextEdit#log",
                  "深色底 (#0C0F15) + 浅色 mono 字体，用于运行日志输出",
                  "te = QTextEdit(); te.setObjectName('log')")
        te = QTextEdit(card); te.setObjectName("log"); te.setReadOnly(True)
        te.setPlainText(
            "[12:03:41] INFO   开始加载 Hy-MT2 模型...\n"
            "[12:03:42] DEBUG  初始化 KV cache (batch=1, ctx=2048)\n"
            "[12:03:43] WARNING 检测到 GPU 不可用，回退 CPU\n"
            "[12:03:45] INFO   模型加载完成，耗时 3.2s\n"
            "[12:03:46] ERROR  第 3 行 OCR 识别失败：timeout"
        )
        te.setMinimumHeight(150)
        lay.addWidget(te)
        return card
