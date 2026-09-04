"""
OCTools/ui/widgets/no_wheel_filter.py
───────────────────────────────────────
全局滚轮阻断：通过 monkey-patch 覆盖 wheelEvent，
阻止 QComboBox/QRadioButton/QCheckBox/QSpinBox/QDoubleSpinBox/QSlider
在鼠标悬浮时误改值。

原理：事件过滤器无法拦截子控件的 Wheel 事件，
而直接覆盖类的 wheelEvent 在 C++ virtual dispatch 层面生效，
对所有实例（已创建和后续创建）有效。

调用 install() 一次即可全局生效。
"""

from PySide6.QtWidgets import (
    QComboBox, QRadioButton, QCheckBox,
    QSpinBox, QDoubleSpinBox, QSlider,
)

_installed = False


def _block_wheel(self, event):
    """忽略滚轮事件"""
    event.ignore()


def install():
    """全局安装滚轮阻断（幂等，重复调用安全）"""
    global _installed
    if _installed:
        return
    _installed = True

    for cls in (QComboBox, QRadioButton, QCheckBox,
                QSpinBox, QDoubleSpinBox, QSlider):
        cls.wheelEvent = _block_wheel