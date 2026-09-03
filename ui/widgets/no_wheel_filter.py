"""
octool/ui/widgets/no_wheel_filter.py
───────────────────────────────────────────────
全局滚轮阻断：通过 monkey-patch 直接覆盖 wheelEvent，
阻止 QComboBox / QRadioButton / QCheckBox / QSpinBox / QDoubleSpinBox / QSlider
在鼠标悬浮滚动时误改值。

原理：QComboBox 等控件有内部子控件（QListView / QLineEdit），应用级
事件过滤器拦截不到发给子控件的 Wheel 事件。直接覆盖类的 wheelEvent
方法是在 C++ virtual dispatch 层面生效，能拦截所有情况。

调用 install() 一次即可全局生效，对已创建和后续创建的实例都有效。
"""

from PySide6.QtWidgets import (
    QComboBox, QRadioButton, QCheckBox,
    QSpinBox, QDoubleSpinBox, QSlider,
)

_installed = False


def _block_wheel(self, event):
    """直接忽略滚轮事件（用于不需要滚轮的控件）"""
    event.ignore()


def install():
    """全局安装滚轮阻断（幂等，重复调用安全）"""
    global _installed
    if _installed:
        return
    _installed = True

    # 所有控件一律忽略滚轮，避免鼠标悬浮滚动误改数值 / 切换选项
    for cls in (QComboBox, QRadioButton, QCheckBox,
                QSpinBox, QDoubleSpinBox, QSlider):
        cls.wheelEvent = _block_wheel
