"""
OCTools/ui/tabs/tab_component/docx_format_card.py
───────────────────────────────────────────────
MD → DOCX 排版卡片（紧凑头部栏）

设计：
  顶部栏（始终可见）：
    MD → DOCX 排版  [预设下拉（可编辑）]  [编辑]
  - 预设下拉：列出已保存预设，选中即加载；也可输入新名称后按回车保存。
  - 「编辑」按钮复用设置页的「格式选项」弹窗（SetFormat），
    只把打开入口接到同一代码路径，不新增实现。

信号:
    config_changed: 加载 / 保存预设后发出（携带 FormatConfig）
"""

from ui.ui_component.combo_component import Combo
from PySide6.QtCore import QSize, Signal
from PySide6.QtWidgets import (
    QLabel, QPushButton, QFrame, QHBoxLayout, QVBoxLayout,
)

from config.format_config import FormatConfig
from config import presets

from config.ui_config import CONFIG as C
from ui import icon_res


DEFAULT_PRESET_LABEL = "默认预设"


class DocxFormatCard(QFrame):
    """MD → DOCX 排版头部卡片

    信号:
        config_changed: 加载 / 保存预设后发出（携带 FormatConfig）
    """

    config_changed = Signal(object)   # FormatConfig

    def __init__(self, parent=None, config: FormatConfig = None, on_edit=None):
        super().__init__(parent)
        self.setObjectName("docxFormatCard")
        self._config = config or FormatConfig.default_chinese()
        self._on_edit = on_edit or (lambda: None)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        self._build_header(outer)
        self._sync_state_from_config()

    # ── 顶部栏 ──

    def _build_header(self, outer):
        header = QFrame(self)
        header.setObjectName("dxfHeader")
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(14, 10, 14, 10)
        h_lay.setSpacing(10)

        # 图标 + 标题
        icon_lab = QLabel(header)
        icon_lab.setPixmap(icon_res.colored_pixmap(
            "file-text", C.color("card_icon_blue"), C.size("card_header_icon")))
        icon_lab.setFixedSize(C.size("card_header_icon"), C.size("card_header_icon"))
        h_lay.addWidget(icon_lab)

        title = QLabel("MD → DOCX 排版", header)
        title.setObjectName("dxfTitle")
        h_lay.addWidget(title)

        h_lay.addSpacing(4)

        # 预设下拉（可编辑）：选择预设 / 输入新名称保存
        self._preset_combo = Combo(header)
        self._preset_combo.setObjectName("dxfPresetEdit")
        self._preset_combo.setEditable(True)
        self._preset_combo.setMinimumWidth(160)
        self._preset_combo.setMaxVisibleItems(20)
        self._preset_combo.lineEdit().setPlaceholderText(DEFAULT_PRESET_LABEL)
        self._preset_combo.activated.connect(self._on_preset_selected)
        self._preset_combo.lineEdit().returnPressed.connect(self._on_preset_saved)
        h_lay.addWidget(self._preset_combo, 1)

        # 编辑按钮：复用设置页「格式选项」弹窗
        self._edit_btn = QPushButton("编辑", header)
        self._edit_btn.setObjectName("primary")
        self._edit_btn.setIcon(icon_res.colored_icon(
            "settings", C.color("white"), C.size("icon_small")))
        self._edit_btn.setIconSize(QSize(C.size("icon_small"), C.size("icon_small")))
        self._edit_btn.setFixedHeight(32)
        self._edit_btn.clicked.connect(self._on_edit_clicked)
        h_lay.addWidget(self._edit_btn)

        outer.addWidget(header)

    # ── 预设下拉 ──

    def _refresh_preset_combo(self, keep_text=None):
        """重建下拉列表；keep_text 为 None 时保留当前文本"""
        if keep_text is None:
            keep_text = self._preset_combo.currentText()
        self._preset_combo.blockSignals(True)
        self._preset_combo.clear()
        self._preset_combo.addItems(presets.list_presets())
        if keep_text:
            self._preset_combo.setCurrentText(keep_text)
        else:
            self._preset_combo.setCurrentIndex(-1)
        self._preset_combo.blockSignals(False)

    def _sync_state_from_config(self):
        """根据当前配置同步下拉选中项 / 占位文本"""
        name = getattr(self._config, "name", "") or ""
        self._refresh_preset_combo(name if name else None)
        self._preset_combo.lineEdit().setPlaceholderText(
            name or DEFAULT_PRESET_LABEL)

    def _on_preset_selected(self, index):
        """从下拉选中预设 → 加载并应用"""
        name = self._preset_combo.itemText(index).strip()
        if not name:
            return
        cfg = presets.load_preset(name)
        if cfg is None:
            return
        self._config = cfg
        self._sync_state_from_config()
        self.config_changed.emit(cfg)

    def _on_preset_saved(self):
        """输入新名称并按回车 → 保存为命名预设"""
        name = self._preset_combo.currentText().strip()
        if not name:
            return
        presets.save_preset(self._config, name)
        self._sync_state_from_config()
        self.config_changed.emit(self._config)

    # ── 编辑按钮 ──

    def _on_edit_clicked(self):
        """打开格式选项弹窗（与设置页共用同一实现）"""
        self._on_edit()

    # ── 公开 API ──

    def get_config(self) -> FormatConfig:
        return self._config

    def set_config(self, config: FormatConfig):
        """外部设置配置（不发出信号）"""
        self._config = config
        self._sync_state_from_config()
