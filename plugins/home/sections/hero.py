"""Hero：超大排版时钟 + 问候 + 状态徽章。

只吃数据（HeroModel），不关心时间怎么算、打卡状态怎么判定。
"""

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel

from config.ui_config import CONFIG as C

from home.constants import (
    INK, GRAPHITE, MUTED, FAINT, WARN, DANGER, SUCCESS, BORDER, SOFT_BG,
)
from home.styles import hero_card_qss, hero_shadow


@dataclass
class HeroModel:
    """一帧 Hero 所需的全部展示数据。"""
    date_text: str = ""        # 2026 年 09 月 08 日 星期一
    tip: str = ""              # 主文案：请打卡 / 距离吃饭还剩 …
    clock: str = ""            # 倒计时或当前时间
    color: str = INK           # 主色（INK / WARN / DANGER）
    badge: str = ""            # 右上角徽章
    hint: str = ""             # 副行说明
    hint_color: str = MUTED
    is_countdown: bool = False  # True 表示 clock 是倒计时（字号小一档）


class HeroSection(QFrame):
    """首页顶部大卡。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Hero")
        self.setStyleSheet(hero_card_qss())
        hero_shadow(self)
        self._build_ui()

    # ──────────────────────────────────────
    #  UI
    # ──────────────────────────────────────
    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(30, 26, 30, 26)
        lay.setSpacing(14)

        # 顶部标签行
        tag_row = QHBoxLayout()
        tag_row.setSpacing(8)
        dot = QLabel(self)
        dot.setFixedSize(7, 7)
        dot.setStyleSheet(f"background: {SUCCESS}; border-radius: 4px;")
        tag_row.addWidget(dot)
        brand = QLabel("OCTOOLS · 工作台", self)
        brand.setStyleSheet(
            f"color: {FAINT}; font-size: 10px; font-weight: 700;"
            f" letter-spacing: 2px; background: transparent;"
        )
        tag_row.addWidget(brand)
        tag_row.addStretch(1)
        lay.addLayout(tag_row)

        # 主体：左问候 / 右时钟
        mid = QHBoxLayout()
        mid.setSpacing(16)

        left = QVBoxLayout()
        left.setSpacing(8)
        self.greeting = QLabel("早上好", self)
        self.greeting.setStyleSheet(
            f"color: {INK}; font-size: 34px; font-weight: 800;"
            f" background: transparent; letter-spacing: 1px;"
        )
        left.addWidget(self.greeting)
        self.date_label = QLabel("", self)
        self.date_label.setStyleSheet(
            f"color: {MUTED}; font-size: 13px; background: transparent;"
        )
        left.addWidget(self.date_label)
        self.hint_label = QLabel("", self)
        self.hint_label.setStyleSheet(
            f"color: {GRAPHITE}; font-size: 13px; font-weight: 600;"
            f" background: transparent;"
        )
        left.addWidget(self.hint_label)
        left.addStretch(1)
        mid.addLayout(left, 1)

        right = QVBoxLayout()
        right.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        right.setSpacing(10)
        self.clock_label = QLabel("--:--:--", self)
        self.clock_label.setStyleSheet(
            f"color: {INK}; font-family: '{self._mono()}'; font-size: 46px;"
            f" font-weight: 700; background: transparent; letter-spacing: 2px;"
        )
        self.clock_label.setAlignment(Qt.AlignRight)
        right.addWidget(self.clock_label)
        self.badge = QLabel("待打卡", self)
        self.badge.setMinimumHeight(28)
        self.badge.setAlignment(Qt.AlignCenter)
        right.addWidget(self.badge, 0, Qt.AlignRight)
        mid.addLayout(right)

        lay.addLayout(mid)

    @staticmethod
    def _mono() -> str:
        return C.raw("fonts", "mono_family") or "Consolas"

    # ──────────────────────────────────────
    #  刷新
    # ──────────────────────────────────────
    def apply_model(self, model: HeroModel):
        self.date_label.setText(model.date_text)

        # 提示：长文案自动降一档字号，避免撑破卡片
        self.greeting.setText(model.tip)
        self.greeting.setStyleSheet(
            f"color: {model.color}; font-size: {30 if len(model.tip) > 7 else 34}px;"
            f" font-weight: 800; background: transparent; letter-spacing: 1px;"
        )

        # 时钟：倒计时用 40px（比 HH:MM:SS 短），当前时间用 46px
        self.clock_label.setText(model.clock)
        self.clock_label.setStyleSheet(
            f"color: {model.color}; font-family: '{self._mono()}';"
            f" font-size: {40 if model.is_countdown else 46}px;"
            f" font-weight: 700; background: transparent; letter-spacing: 2px;"
        )

        # 副行说明
        self.hint_label.setText(model.hint)
        self.hint_label.setStyleSheet(
            f"color: {model.hint_color}; font-size: 13px; font-weight: 600;"
            f" background: transparent;"
        )

        # 徽章：黄/红实心，黑则浅底
        self.badge.setText(model.badge)
        self.badge.setStyleSheet(
            self._badge_qss(model.color) +
            " font-size: 11px; font-weight: 700;"
            " padding: 0 14px; border-radius: 14px;"
        )

    @staticmethod
    def _badge_qss(color: str) -> str:
        if color == DANGER:
            return f"color: #FFFFFF; background: {DANGER}; border: none;"
        if color == WARN:
            return f"color: #FFFFFF; background: {WARN}; border: none;"
        return f"color: {MUTED}; background: {SOFT_BG}; border: 1px solid {BORDER};"
