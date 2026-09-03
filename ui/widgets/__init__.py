"""
octool/ui/widgets/__init__.py
───────────────────────────────────────────────
可复用自定义控件：
  - format_select_widget.py  源/目标格式选择控件（FormatPicker + 格式元数据）
  - batch_options_widget.py  单文件 / 文件夹选项控件
  - merge_order_widget.py    可拖拽排序列表（合并顺序）
  - config_editor_dialog.py  配置编辑弹窗（通用）
  - no_wheel_filter.py       全局滚轮阻断（monkey-patch wheelEvent，阻止悬浮滚动误改值）
"""

from ui.widgets.format_select_widget import FormatPicker  # noqa: F401

__all__ = ["FormatPicker"]
