"""
OCTools/ui/ui_component/combo_component.py
────────────────────────────────────────────
通用下拉选择组件（QComboBox 封装）。

全局 QSS 已统一处理圆角 / 边框 / 聚焦高亮 / chevron 箭头（收起向下、展开向上），
新建下拉框无需再写任何样式代码。

组件：
  - Combo        普通下拉 / 可手输组合框
  - DescComboBox 每项右侧同行显示淡色说明文字（如终端"子命令"选择框）

用法:
    from ui.ui_component.combo_component import Combo, DescComboBox

    Combo(["浅色", "深色"], default="浅色")
    Combo(editable=True, placeholder="输入或选择")
    DescComboBox({"clone": "克隆仓库", "init": "初始化仓库"})
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QFontMetrics, QPalette, QColor, QStandardItemModel, QStandardItem,
)
from PySide6.QtWidgets import (
    QApplication, QComboBox, QStyledItemDelegate, QStyle, QStyleOptionViewItem, QWidget,
)


class _DescDelegate(QStyledItemDelegate):
    """下拉项：左侧主文本 + 右侧淡色描述同行显示。

    描述存于 Qt.UserRole；选中态描述用高亮文字色半透明，普通态用主题占位灰。
    收起与弹出两种状态均由本委托绘制，风格一致。
    """

    def paint(self, painter, option, index):
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        name = opt.text          # 先保存主文本
        opt.text = ""            # 清空默认文本，避免系统重复绘制造成重影
        style = opt.widget.style() if opt.widget else QApplication.style()
        # 仅绘制背景 / 选中 / 悬停状态
        style.drawControl(QStyle.CE_ItemViewItem, opt, painter, opt.widget)

        desc = index.data(Qt.UserRole) or ""
        painter.save()
        painter.setFont(opt.font)
        rect = opt.rect
        if opt.state & QStyle.State_Selected:
            base_col = opt.palette.color(QPalette.HighlightedText)
            desc_col = QColor(base_col)
            desc_col.setAlpha(170)  # 淡色：选中时用高亮文字色半透明
        else:
            base_col = opt.palette.color(QPalette.Text)
            desc_col = opt.palette.color(QPalette.PlaceholderText)  # 淡灰
        fm = QFontMetrics(opt.font)
        pad_l, pad_r = 8, 8
        if desc:
            # 预留描述宽度，名称在剩余空间内省略
            name_w = rect.width() - pad_l - pad_r - fm.horizontalAdvance(desc) - 12
            text = fm.elidedText(name, Qt.ElideRight, max(name_w, 10))
        else:
            text = fm.elidedText(name, Qt.ElideRight, rect.width() - pad_l - pad_r)
        area = rect.adjusted(pad_l, 0, -pad_r, 0)
        painter.setPen(base_col)
        painter.drawText(area, Qt.AlignVCenter | Qt.AlignLeft, text)
        if desc:
            painter.setPen(desc_col)
            painter.drawText(area, Qt.AlignVCenter | Qt.AlignRight, desc)
        painter.restore()


class Combo(QComboBox):
    """通用下拉选择框（完全兼容原生 QComboBox 的调用方式）。

    兼容写法：
        Combo()                       # 等价 QComboBox()
        Combo(parent)                 # 第一个位置参数为 QWidget 时视为父控件
        Combo(["a", "b"], parent=w)   # 便捷：初始选项

    Args:
        arg1:       父控件（QWidget）或初始选项列表（见兼容写法）
        default:     可选，默认选中文本（须在 items 中，否则忽略）
        editable:    True 时允许手输，手输内容不自动进下拉（组合框）
        placeholder: 提示文字（editable 时可见）
        min_width:   可选，最小宽度（建议用配置 combo_min_w / combo_min_w_small）
        parent:      父控件
    """

    def __init__(self, arg1=None, default=None, editable=False,
                 placeholder="", min_width=None, parent=None):
        if isinstance(arg1, QWidget):
            # 原生写法 QComboBox(parent)：第一个位置参数是父控件
            parent = arg1
            arg1 = None
        super().__init__(parent)
        items = arg1
        if items:
            self.addItems(items)
        if default and self.findText(default) >= 0:
            self.setCurrentText(default)
        if editable:
            self.setEditable(True)
            self.setInsertPolicy(QComboBox.NoInsert)  # 手输内容不自动进下拉
        if placeholder:
            self.setPlaceholderText(placeholder)
        if min_width:
            self.setMinimumWidth(min_width)


class DescComboBox(QComboBox):
    """带右侧淡色描述的下拉框（收起 / 展开均同行显示：名称 + 淡色描述）。

    兼容写法：
        DescComboBox(parent)             # 原生 QComboBox(parent)
        DescComboBox({"a": "描述"}, parent=w)

    切换项后通过 currentTextChanged 读取选中名称。
    """

    def __init__(self, arg1=None, parent=None):
        if isinstance(arg1, QWidget):
            # 原生写法 QComboBox(parent)：第一个位置参数是父控件
            parent = arg1
            arg1 = None
        super().__init__(parent)
        self._model = QStandardItemModel(self)
        self.setModel(self._model)
        self.setItemDelegate(_DescDelegate(self))
        if arg1:
            self.set_desc_items(arg1)

    def set_desc_items(self, items):
        """重置选项：items 为 {名称: 描述} 或 [(名称, 描述), ...]。

        调用后默认选中第一项（会触发 currentTextChanged，可在外部 blockSignals）。
        """
        self._model.clear()
        try:
            pairs = list(items.items())  # dict
        except AttributeError:
            pairs = list(items)
        for name, desc in pairs:
            item = QStandardItem(name)
            item.setData(desc, Qt.UserRole)
            item.setEditable(False)
            self._model.appendRow(item)
        if self._model.rowCount():
            self.setCurrentIndex(0)
