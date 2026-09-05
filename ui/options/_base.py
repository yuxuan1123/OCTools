"""
OCTools/ui/options/_base.py
───────────────────────────────────────────────
设置弹窗公共骨架（OptionsDialogBase）

集中「顶栏(52px) + 内容区 + 底部按钮条」三段布局代码：
  - build_header()    : 52px 顶栏（objectName: header / headerTitle）
  - build_plain_body(): 普通内容区（body + b_lay）
  - build_scroll_body(): 可滚动内容区（窗口过小不溢出屏幕）
  - build_buttons()   : 底部按钮条（可选「左按钮」+ 右「确定」）

子类只需继承并在 __init__ 中按需调用，再填充表单控件。
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QWidget,
    QScrollArea, QPushButton, QFormLayout,
)
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QGuiApplication, QCursor

from ui import icon_res
from config.ui_config import CONFIG as C


class OptionsDialogBase(QDialog):
    """设置弹窗公共骨架：顶栏 + 内容区 + 底部按钮条

    统一视觉语言（所有 set_*.py 共用）：
      - 52px 顶栏（header / headerTitle）
      - 内容区默认用 build_scroll_body()（可滚动，窗口过小不溢出屏幕）
      - 内容按 build_section_card() 分组卡片组织（QFrame#card）
      - 底部 build_buttons() 按钮条（ghost 左按钮 + primary 确定）
      - fit_size() 统一窗口尺寸策略：默认尺寸 + 最小尺寸均按屏幕收缩
    """

    HEADER_MIN_HEIGHT = 52

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        self._lay = lay

        self._body = None          # 最近一次 build_*_body() 的内容控件
        self._body_layout = None   # 对应布局管理器

    # ── 统一尺寸策略 ──

    def fit_size(self, default_w: int, default_h: int,
                 min_w: int = 480, min_h: int = 400):
        """统一窗口尺寸：按屏幕可用区域收缩，小屏不溢出、不小到失控。

        所有 set 页面统一调用，消除各自固定 780/560/380 高的尺寸乱象。
        """
        screen = QGuiApplication.screenAt(QCursor.pos()) \
            or QGuiApplication.primaryScreen()
        avail = screen.availableGeometry()
        self.resize(min(default_w, avail.width() - 80),
                    min(default_h, avail.height() - 120))
        self.setMinimumSize(min(min_w, avail.width() - 40),
                            min(min_h, avail.height() - 80))

    # ── 顶栏 ──

    def build_header(self, text: str) -> QFrame:
        """构建 52px 顶栏（header / headerTitle），返回 header 控件。"""
        header = QFrame(self)
        header.setObjectName("header")
        header.setFixedHeight(self.HEADER_MIN_HEIGHT)
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(16, 0, 16, 0)
        title = QLabel(text, header)
        title.setObjectName("headerTitle")
        h_lay.addWidget(title)
        self._lay.addWidget(header)
        return header

    # ── 内容区 ──

    def build_plain_body(self, margins=(20, 18, 20, 14),
                         spacing_key="card_spacing", stretch=1):
        """普通内容区，返回 (body, b_lay)。"""
        body = QWidget(self)
        b_lay = QVBoxLayout(body)
        b_lay.setContentsMargins(*margins)
        b_lay.setSpacing(C.size(spacing_key))
        self._lay.addWidget(body, stretch)
        self._body, self._body_layout = body, b_lay
        return body, b_lay

    def build_scroll_body(self, margins=(20, 16, 20, 14),
                          spacing_key="form_row_spacing", stretch=1):
        """可滚动内容区（窗口过小时滚动查看，不超出屏幕），返回 (body, b_lay)。"""
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        body = QWidget()
        body.setObjectName("scrollInner")
        b_lay = QVBoxLayout(body)
        b_lay.setContentsMargins(*margins)
        b_lay.setSpacing(C.size(spacing_key))
        scroll.setWidget(body)
        self._lay.addWidget(scroll, stretch)
        self._body, self._body_layout = body, b_lay
        return body, b_lay

    # ── 分组卡片 / 表单工厂 ──

    def build_section_card(self, title: str = "", parent=None):
        """统一分组卡片（QFrame#card + cardTitle），返回 (card, lay)。"""
        card = QFrame(parent or self)
        card.setObjectName("card")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(
            C.size("group_padding_h"), C.size("group_padding_v"),
            C.size("group_padding_h"), C.size("group_padding_v"))
        lay.setSpacing(C.size("form_row_spacing"))
        if title:
            lab = QLabel(title, card)
            lab.setObjectName("cardTitle")
            lay.addWidget(lab)
        return card, lay

    def make_form(self, parent=None) -> QFormLayout:
        """统一表单布局：标签左对齐，字段区自适应。

        注意：QFormLayout 的 parent 只能是 QWidget，分组卡片传入的是
        QVBoxLayout，因此这里一律不设父级，由调用方 addLayout 挂接。
        """
        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setHorizontalSpacing(C.size("form_spacing"))
        form.setVerticalSpacing(C.size("form_row_spacing"))
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        return form

    def hint_label(self, text: str, parent=None) -> QLabel:
        """统一提示文本（#hint，自动换行）"""
        lab = QLabel(text, parent)
        lab.setObjectName("hint")
        lab.setWordWrap(True)
        return lab

    # ── 底部按钮条 ──

    def build_buttons(self, left_text=None, left_icon=None, left_on_click=None,
                      ok_text="确定", ok_icon="check", ok_min_width=120,
                      on_ok=None, margins=(20, 4, 20, 12)) -> QWidget:
        """
        构建底部按钮条：可选「左按钮（ghost，如恢复默认）」+ 右「确定（primary）」。
        返回 btn_bar 控件，由调用方自行 addWidget / form.addRow。
        未传 on_ok 时连接 self._ok。
        """
        btn_bar = QWidget(self)
        bt_lay = QHBoxLayout(btn_bar)
        bt_lay.setContentsMargins(*margins)

        if left_text:
            left_btn = QPushButton(left_text, btn_bar)
            if left_icon:
                left_btn.setIcon(icon_res.colored_icon(left_icon))
                left_btn.setIconSize(QSize(C.size("icon_small"), C.size("icon_small")))
            left_btn.setObjectName("ghost")
            left_btn.clicked.connect(left_on_click)
            bt_lay.addWidget(left_btn)

        bt_lay.addStretch(1)

        ok_btn = QPushButton(ok_text, btn_bar)
        if ok_icon:
            ok_btn.setIcon(icon_res.colored_icon(ok_icon))
            ok_btn.setIconSize(QSize(C.size("icon_small"), C.size("icon_small")))
        ok_btn.setObjectName("primary")
        ok_btn.setMinimumWidth(ok_min_width)
        ok_btn.clicked.connect(on_ok if on_ok is not None else self._ok)
        bt_lay.addWidget(ok_btn)

        return btn_bar