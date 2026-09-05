"""
OCTools/ui/tabs/translation/app_hooks.py
──────────────────────────────────────────────────
应用行构建：按注册表 key 生成应用行（启动/停止 切换按钮 + 名称 + 说明 + 状态标签），
登记到 page 的 _app_btns / _app_status。
"""

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel

from ui import icon_res
from config.ui_config import CONFIG as C

from plugins.translation.registry import _APP_ROWS


def build_app_rows(parent, keys, page):
    """按注册表 key 生成应用行，登记到 page._app_btns / page._app_status；
    返回可迭代 (key, row)。"""
    for key in keys:
        _cls, label, icon, hint, _hk = _APP_ROWS[key]
        row = QWidget(parent)
        rl = QHBoxLayout(row)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(C.size("form_row_spacing"))
        btn = QPushButton("启动", row)
        btn.setObjectName("primary")
        btn.setIcon(icon_res.colored_icon(icon))
        btn.setIconSize(QSize(C.size("icon_small"), C.size("icon_small")))
        btn.setMinimumWidth(C.size("combo_min_w"))
        btn.setToolTip(C.text("app_start_minimize_tooltip"))
        btn.clicked.connect(lambda _=False, k=key: page.toggle_app(k))
        rl.addWidget(btn)
        name_lab = QLabel(label, row)
        name_lab.setObjectName("fieldLabel")
        rl.addWidget(name_lab)
        hint_lab = QLabel(hint, row)
        hint_lab.setObjectName("hint")
        rl.addWidget(hint_lab, 1)
        status_lab = QLabel("未启动", row)
        status_lab.setObjectName("hint")
        rl.addWidget(status_lab)
        page._app_btns[key] = btn
        page._app_status[key] = status_lab
        yield key, row