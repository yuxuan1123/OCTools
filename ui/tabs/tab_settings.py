"""
OCTools/ui/tabs/tab_settings.py
───────────────────────────────────────────────
设置页：聚合各标签页参数设置 + 应用级配置。

自动渲染：
  - 读取所有 manifest 目录（ui/tabs/manifests、旧版 manifests/plugins、用户导入插件
    挂载目录 <插件根>/manifests，由 plugin_registry.iter_manifest_dirs 统一提供）的
    settings 段，为每个标签页生成一个设置分组；
  - 每个设置条目按 button_name 生成按钮，点击后按 module + class_name 自动导入
    弹窗类并弹出（config 由 _CONFIG_LOADERS 提供「上次保存 or 默认」实例）；
  - 全局 UI 风格（主题/字体/颜色/尺寸）由 ui/options/set_ui.py 的 Setui 弹窗承载，
    本页只负责渲染入口按钮。

应用级配置：
  - 日志输出目录：QFileDialog 选择 + 保存到应用设置（config/presets.py）。
  - 应用信息展示（版本 / 数据目录）。

所有视觉/布局参数统一从 config/ui_config.json 读取（CONFIG 单例）。
"""

import importlib
import json
import os

from PySide6.QtCore import Qt, QSize, QRect
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QScrollArea, QFrame, QMessageBox,
    QDialog, QListWidget, QListWidgetItem, QAbstractItemView,
    QStyledItemDelegate, QStyle,
)

from config import presets
from config.ui_config import CONFIG as C
from ui.toast import show_toast
from ui.theme import THEME_BUS
from ui.icon_res import colored_pixmap
from ui.tabs.tab_component.page_header import build_page_header
from config.format_config import FormatConfig
from config.image_docx_config import ImageDocxConfig
from config.pdf_docx_config import PdfDocxConfig
from config.screen_region_config import ScreenRegionConfig
from config.stt_config import SttConfig
from config.translator_config import TranslatorConfig
from config.tts_config import TtsConfig
from ui.tabs.plugin_registry import iter_manifest_dirs, ensure_plugin_dirs

# ─────────────────────────────────────────────
#  manifest → config 解析（按弹窗类名匹配）
# ─────────────────────────────────────────────


def _last_or_default(loader, factory):
    """取「上次保存配置」，无则返回默认实例。"""
    cfg = loader()
    return cfg if cfg is not None else factory()


_CONFIG_LOADERS = {
    "SetTranslator": lambda: _last_or_default(
        presets.load_last_translator_config, TranslatorConfig),
    "SetStt": lambda: _last_or_default(
        presets.load_last_stt_config, SttConfig),
    "SetTts": lambda: _last_or_default(
        presets.load_last_tts_config, TtsConfig),
    "SetImageDocx": lambda: _last_or_default(
        presets.load_last_image_config, ImageDocxConfig),
    "SetPdfDocx": lambda: _last_or_default(
        presets.load_last_pdf_docx_config, PdfDocxConfig),
    "SetScreenRegion": lambda: _last_or_default(
        presets.load_last_screen_region_config, ScreenRegionConfig),
    "SetFormat": lambda: _last_or_default(
        presets.load_last_config, FormatConfig),
}


def _iter_manifests():
    """按 order 依次产出带 settings 段的标签页清单，缺失/损坏文件跳过。

    扫描所有 manifest 目录（内建 manifests + 旧版 plugins 子目录 +
    用户导入插件挂载目录），与左侧导航、插件导入逻辑共用同一份目录清单
    （plugin_registry.iter_manifest_dirs），确保插件自带的设置项必定出现在设置页。
    """
    # 确保插件挂载点已接入 sys.path（点击设置按钮时按 module 导入插件弹窗需要）
    try:
        ensure_plugin_dirs()
    except OSError:
        pass

    seen_paths = set()
    items = []
    for directory in iter_manifest_dirs():
        try:
            names = sorted(os.listdir(directory))
        except OSError:
            continue
        for n in names:
            if not n.endswith(".json"):
                continue
            fpath = os.path.join(directory, n)
            if fpath in seen_paths:
                continue
            seen_paths.add(fpath)
            try:
                with open(fpath, encoding="utf-8") as f:
                    manifest = json.load(f)
            except (OSError, ValueError):
                continue
            if manifest.get("settings"):
                items.append(manifest)
    items.sort(key=lambda m: m.get("order", 999))
    yield from items


def _iter_all_manifests():
    """产出全部导航 manifest（含无 settings 的），携带文件路径，按 (order, name) 排序。

    供「侧栏顺序」卡片使用：左侧栏按此清单生成入口，保存顺序即重写各
    manifest 的 order 字段。
    """
    seen_paths = set()
    items = []
    for directory in iter_manifest_dirs():
        try:
            names = sorted(os.listdir(directory))
        except OSError:
            continue
        for n in names:
            if not n.endswith(".json"):
                continue
            fpath = os.path.join(directory, n)
            if fpath in seen_paths:
                continue
            seen_paths.add(fpath)
            try:
                with open(fpath, encoding="utf-8") as f:
                    manifest = json.load(f)
            except (OSError, ValueError):
                continue
            if not isinstance(manifest, dict) or not manifest.get("class_name"):
                continue
            items.append((manifest, fpath))
    items.sort(key=lambda mf: (mf[0].get("order", 999), mf[0].get("name", "")))
    return items


# ─────────────────────────────────────────────


class _Section(QFrame):
    """设置分组卡片。"""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsSection")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(
            C.size("group_padding_h"), C.size("group_padding_v"),
            C.size("group_padding_h"), C.size("group_padding_v"),
        )
        lay.setSpacing(C.size("form_row_spacing"))
        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        lay.addWidget(title_label)
        self.body = lay

    def add_row(self, label_text: str, widget: QWidget):
        row = QHBoxLayout()
        row.setSpacing(C.size("form_row_spacing"))
        label = QLabel(label_text)
        label.setFixedWidth(C.size("form_width_90"))
        label.setObjectName("formLabel")
        row.addWidget(label)
        row.addWidget(widget, 1)
        self.body.addLayout(row)

    def add_info(self, key: str, value: str):
        row = QHBoxLayout()
        row.setSpacing(C.size("form_row_spacing"))
        label = QLabel(key)
        label.setFixedWidth(C.size("form_width_90"))
        label.setObjectName("formLabel")
        row.addWidget(label)
        value_label = QLabel(value)
        value_label.setWordWrap(True)
        row.addWidget(value_label, 1)
        self.body.addLayout(row)


class TabSettings(QWidget):
    """设置页：各标签页参数设置 + 应用级设置（日志目录等）。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._settings = presets.load_app_settings() or {}
        self._build_ui()

    # ──────────────────────────────────────
    #  布局
    # ──────────────────────────────────────
    def _build_ui(self):
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

        # ---- 页头 ----
        cl.addWidget(build_page_header(content, "page_settings_title", "page_settings_sub"))

        # ---- 应用级设置 ----
        general = _Section("通用")
        self.log_dir_edit = QLineEdit(self._settings.get("log_dir", ""))
        self.log_dir_edit.setPlaceholderText("例如：D:/logs/OCTools")
        browse_btn = QPushButton("浏览…")
        browse_btn.setObjectName("ghost")
        browse_btn.clicked.connect(self._pick_log_dir)
        dir_row = QHBoxLayout()
        dir_row.setSpacing(C.size("form_row_spacing"))
        dir_row.addWidget(self.log_dir_edit, 1)
        dir_row.addWidget(browse_btn)
        general.body.addLayout(dir_row)

        order_row = QHBoxLayout()
        order_row.setSpacing(C.size("form_row_spacing"))
        order_label = QLabel("侧栏顺序")
        order_label.setFixedWidth(C.size("form_width_90"))
        order_label.setObjectName("formLabel")
        order_row.addWidget(order_label)
        order_btn = QPushButton("调整…")
        order_btn.setObjectName("ghost")
        order_btn.clicked.connect(self._open_sidebar_order)
        order_row.addWidget(order_btn)
        order_row.addStretch(1)
        general.body.addLayout(order_row)

        save_btn = QPushButton("保存设置")
        save_btn.setObjectName("primary")
        save_btn.clicked.connect(self._save)
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        btn_row.addWidget(save_btn)
        general.body.addLayout(btn_row)
        cl.addWidget(general)

        # ---- 各标签页参数设置（自动读取 manifests） ----
        for manifest in _iter_manifests():
            self._add_manifest_section(cl, manifest)

        # ---- 应用信息 ----
        info = _Section("应用信息")
        info.add_info("数据目录", presets.PRESETS_DIR)
        info.add_info("版本", "1.0.0")
        cl.addWidget(info)

        cl.addStretch(1)
        scroll.setWidget(content)

    # ──────────────────────────────────────
    #  侧栏顺序（独立窗口内拖拽排序）
    # ──────────────────────────────────────
    def _open_sidebar_order(self):
        """弹出独立排序窗口（拖拽调整左侧栏顺序）。"""
        SidebarOrderDialog(self).exec()

    # ──────────────────────────────────────
    #  自动渲染 Helpers
    # ──────────────────────────────────────
    def _add_manifest_section(self, lay: QVBoxLayout, manifest: dict):
        """为单个标签页清单渲染一个设置分组（名称 + 按钮）。

        仅渲染 direct（主进程直载）插件的设置：desc/window 插件的 set_*.py
        位于隔离子进程内、可能依赖独立库，主进程无法 import，
        其设置入口改由插件自身的 UI（控件树 / 独立窗口）承载。
        """
        if manifest.get("ui_mode", "direct") != "direct":
            return
        name = manifest.get("name", "") or ""
        section = _Section(name if name.endswith("设置") else f"{name}设置")
        for entry in manifest.get("settings", []):
            row = QHBoxLayout()
            row.setSpacing(C.size("form_row_spacing"))
            label = QLabel(entry.get("name", ""))
            btn = QPushButton(entry.get("button_name", "设置"))
            btn.setObjectName("ghost")
            btn.clicked.connect(lambda _=False, e=entry: self._open_dialog(e))
            row.addWidget(label, 1)
            row.addWidget(btn)
            section.body.addLayout(row)
        lay.addWidget(section)

    def _open_dialog(self, entry: dict):
        """按 module.class_name 导入弹窗类并弹出设置窗。"""
        try:
            module = importlib.import_module(entry["module"])
            cls = getattr(module, entry["class_name"])
        except Exception as exc:
            QMessageBox.warning(self, "设置", f"加载「{entry.get('name', '')}」失败：{exc}")
            return
        loader = _CONFIG_LOADERS.get(entry["class_name"])
        config = loader() if loader else None
        try:
            dlg = cls(config, self) if config is not None else cls(parent=self)
        except Exception as exc:
            QMessageBox.warning(self, "设置", f"打开「{entry.get('name', '')}」失败：{exc}")
            return
        dlg.setAttribute(Qt.WA_DeleteOnClose)
        dlg.show()
        dlg.raise_()
        dlg.activateWindow()

    # ──────────────────────────────────────
    #  逻辑
    # ──────────────────────────────────────
    def _pick_log_dir(self):
        current = self.log_dir_edit.text().strip()
        chosen = QFileDialog.getExistingDirectory(self, "选择日志目录", current or "")
        if chosen:
            self.log_dir_edit.setText(chosen)

    def _save(self):
        self._settings["log_dir"] = self.log_dir_edit.text().strip()
        presets.save_app_settings(self._settings)
        QMessageBox.information(self, "设置", "设置已保存。")


class _HandleDelegate(QStyledItemDelegate):
    """侧栏顺序列表行：行首手柄图标（menu-order）+ 序号 + 名称。

    序号实时取行号（拖拽让位时自动正确），无需重写 item 文本。
    """

    HANDLE_W = 30
    SEQ_W = 34

    def paint(self, painter, option, index):
        rect = option.rect
        sel = option.state & QStyle.State_Selected
        hover = option.state & QStyle.State_MouseOver
        if sel:
            painter.fillRect(rect, QColor(C.color("nav_active_bg")))
        elif hover:
            painter.fillRect(rect, QColor("#14000000"))

        # 拖拽手柄
        h = C.size("icon_small")
        pm = colored_pixmap("menu-order", C.color("icon_default"), h)
        if not pm.isNull():
            painter.drawPixmap(rect.left() + 6,
                               rect.center().y() - h // 2, pm)

        # 序号
        f = QFont(painter.font())
        f.setBold(True)
        painter.setFont(f)
        painter.setPen(QColor(C.color("text_light")))
        painter.drawText(
            QRect(rect.left() + self.HANDLE_W, rect.top(),
                  self.SEQ_W - 6, rect.height()),
            Qt.AlignVCenter | Qt.AlignRight, str(index.row() + 1))

        # 名称
        f.setBold(False)
        painter.setFont(f)
        painter.setPen(QColor(C.color("nav_active_fg" if sel else "text")))
        painter.drawText(
            QRect(rect.left() + self.HANDLE_W + self.SEQ_W, rect.top(),
                  rect.width() - self.HANDLE_W - self.SEQ_W, rect.height()),
            Qt.AlignVCenter | Qt.AlignLeft, index.data(Qt.DisplayRole))

    def sizeHint(self, option, index):
        return QSize(0, C.size("btn_h") + 8)


class SidebarOrderDialog(QDialog):
    """侧栏顺序独立窗口：拖拽排序，保存后重写各 manifest 的 order。

    - 行首 menu-order 手柄拖拽，拖拽时其他行自动让位留出空槽；
    - 序号由 delegate 实时取行号绘制，随让位自动更新；
    - 「保存顺序」按列表顺序写 order 并广播 THEME_BUS 重建左侧栏。
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("侧栏顺序")
        self.setMinimumWidth(420)
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setSpacing(C.size("form_row_spacing"))

        hint = QLabel("拖动行首手柄调整顺序（拖动时其他标签自动让位），"
                      "点击「保存顺序」后生效。")
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        lay.addWidget(hint)

        self._list = QListWidget()
        self._list.setDragDropMode(QAbstractItemView.InternalMove)
        self._list.setDefaultDropAction(Qt.MoveAction)
        self._list.setSelectionMode(QAbstractItemView.SingleSelection)
        # 列表模式：拖拽时其他行让位留空，而非覆盖
        self._list.setDragDropOverwriteMode(False)
        self._list.setItemDelegate(_HandleDelegate(self._list))
        self._list.setFixedHeight(340)
        border = C.color("input_border")
        radius = C.size("radius_btn")
        self._list.setStyleSheet(
            f"QListWidget {{ background: transparent; "
            f"border: 1px solid {border}; border-radius: {radius}px; "
            f"padding: 4px; outline: none; }}"
            f"QListWidget::item {{ border: none; }}")
        self._reload()
        lay.addWidget(self._list)

        btns = QHBoxLayout()
        btns.setSpacing(C.size("form_row_spacing"))
        btns.addStretch(1)
        reset_btn = QPushButton("重置")
        reset_btn.setObjectName("ghost")
        reset_btn.clicked.connect(self._reload)
        btns.addWidget(reset_btn)
        save_btn = QPushButton("保存顺序")
        save_btn.setObjectName("primary")
        save_btn.clicked.connect(self._save)
        btns.addWidget(save_btn)
        lay.addLayout(btns)

    def _reload(self):
        """按 manifest 当前 (order, name) 重建列表（丢弃未保存的拖动）。"""
        self._list.clear()
        for manifest, fpath in _iter_all_manifests():
            name = manifest.get("name", "")
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, {"name": name, "path": fpath})
            self._list.addItem(item)

    def _save(self):
        """按列表顺序重写各 manifest 的 order，广播重建左侧栏后关闭。"""
        for i in range(self._list.count()):
            item = self._list.item(i)
            fpath = item.data(Qt.UserRole).get("path", "")
            try:
                with open(fpath, encoding="utf-8") as f:
                    data = json.load(f)
                data["order"] = i
                with open(fpath, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
            except (OSError, ValueError):
                continue
        THEME_BUS.changed.emit(C.theme())
        show_toast(self, "侧栏顺序已更新", kind="success")
        self.accept()