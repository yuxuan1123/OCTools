"""
OCTools/ui/tabs/plugins/tree/tab_tree.py
───────────────────────────────────────────────
目录树页：根据所选根目录与过滤选项，生成文件目录树文本。

界面：根目录 + 选项（隐藏项 / 文件过滤模式 / 最大深度 / 排除扩展名 /
排除关键词）→ 生成目录树 → 只读等宽文本输出。

由 mvp/tree/ 子包拆分而来：
  - 核心逻辑在 tree/tree_core.py（无 UI 依赖，纯函数）；
  - 选项卡片在 tree/card_options.py，输出卡片在 tree/card_output.py。

所有视觉/布局参数统一从 config/ui_config.json 读取（CONFIG 单例）。
"""

import os
import sys
from pathlib import Path

# 兼容两种运行方式：
#   1. 插件模式 —— 本文件与引用文件夹（tree/*.py）被复制到 ui/tabs/plugins/<name>/，
#      以 ui.tabs.plugins.<name>.tab_tree 导入，需相对导入；
#   2. mvp 独立运行（python mvp/tab_tree.py）—— 无包上下文，tree 为 mvp 下顶层子包。
try:
    from .card_options import build_options_card
    from .card_output import build_output_card
    from .tree_core import build_tree, parse_exclude_ext, parse_keywords
except ImportError:
    from tree.card_options import build_options_card
    from tree.card_output import build_output_card
    from tree.tree_core import build_tree, parse_exclude_ext, parse_keywords

# 独立运行（python mvp/tab_tree.py）时，保证 OCTools 项目根目录可导入 config/ui
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QScrollArea, QFrame,
    QFileDialog, QMessageBox,
)

from config.ui_config import CONFIG as C

# 过滤下拉索引 → FileFilterMode
_FILTER_MAP = {0: "none", 1: "all", 2: "images"}
_FILTER_LABELS = {0: "", 1: "仅目录", 2: "隐藏图片"}


class TabTree(QWidget):
    """目录树页面：生成可选过滤的文件目录树。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.root_path = ""
        self.root_entry = None
        self.show_hidden_check = None
        self.filter_combo = None
        self.max_depth_spin = None
        self.exclude_ext_entry = None
        self.exclude_kw_entry = None
        self.tree_text = None
        self.stat_label = None
        self.generate_btn = None
        self._build_ui()

    # ──────────────────────────────────────
    #  布局
    # ──────────────────────────────────────
    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(C.size("card_spacing"))

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        body = QWidget()
        body.setObjectName("scrollInner")
        lay = QVBoxLayout(body)
        lay.setContentsMargins(0, 0, C.size("scroll_gutter_right"), 0)
        lay.setSpacing(C.size("card_spacing"))
        lay.setAlignment(Qt.AlignTop)
        scroll.setWidget(body)
        outer.addWidget(scroll, 1)

        lay.addWidget(build_options_card(body, page=self))
        lay.addWidget(build_output_card(body, page=self), 1)

    # ──────────────────────────────────────
    #  动作
    # ──────────────────────────────────────
    def _browse_root(self):
        """选择根目录（只读输入框由 card_options 挂载）。"""
        path = QFileDialog.getExistingDirectory(
            self, "选择根目录", self.root_path or "")
        if path:
            self.root_path = path
            self.root_entry.setText(path)

    def _generate(self):
        """读取选项 → 构建目录树 → 写入输出区。"""
        root_str = self.root_entry.text().strip() if self.root_entry else ""
        if not root_str:
            QMessageBox.warning(self, "目录树", "请先选择根目录（必选）。")
            return
        root = Path(root_str).resolve()
        if not root.is_dir():
            QMessageBox.warning(self, "目录树", f"路径不是有效目录：{root_str}")
            return

        show_hidden = self.show_hidden_check.isChecked()
        file_filter = _FILTER_MAP.get(self.filter_combo.currentIndex(), "none")
        max_depth = self.max_depth_spin.value() or None
        exclude_ext = parse_exclude_ext(self.exclude_ext_entry.text().strip())
        keywords = parse_keywords(self.exclude_kw_entry.text().strip())

        text = build_tree(
            root,
            max_depth=max_depth,
            show_hidden=show_hidden,
            file_filter=file_filter,
            exclude_ext=exclude_ext,
            keywords=keywords,
        )
        self.tree_text.setPlainText(text)
        line_count = text.count("\n") + 1
        self._update_stat(line_count, root)

    def _update_stat(self, line_count: int, root: Path):
        parts = []
        if self.show_hidden_check.isChecked():
            parts.append("含隐藏项")
        parts.append(_FILTER_LABELS.get(self.filter_combo.currentIndex(), ""))
        parts.append("不限深度" if self.max_depth_spin.value() == 0
                     else f"深度≤{self.max_depth_spin.value()}")
        tips = "，".join(p for p in parts if p)
        self.stat_label.setText(
            f"已生成 {line_count} 行（根目录：{root}｜{tips or '默认选项'}）")

    # ──────────────────────────────────────
    #  独立运行
    # ──────────────────────────────────────


if __name__ == "__main__":
    try:
        from ui.theme import APP_STYLESHEET
    except ImportError:
        APP_STYLESHEET = ""

    app = QApplication(sys.argv)
    if APP_STYLESHEET:
        app.setStyleSheet(APP_STYLESHEET)

    window = TabTree()
    window.show()
    sys.exit(app.exec())