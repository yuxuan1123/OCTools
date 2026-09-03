"""
octool/ui/tabs/tab_settings.py
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

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QScrollArea, QFrame, QMessageBox,
)

from config import presets
from config.ui_config import CONFIG as C
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
        self.log_dir_edit.setPlaceholderText("例如：D:/logs/octool")
        browse_btn = QPushButton("浏览…")
        browse_btn.setObjectName("ghost")
        browse_btn.clicked.connect(self._pick_log_dir)
        dir_row = QHBoxLayout()
        dir_row.setSpacing(C.size("form_row_spacing"))
        dir_row.addWidget(self.log_dir_edit, 1)
        dir_row.addWidget(browse_btn)
        general.body.addLayout(dir_row)

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
    #  自动渲染 Helpers
    # ──────────────────────────────────────
    def _add_manifest_section(self, lay: QVBoxLayout, manifest: dict):
        """为单个标签页清单渲染一个设置分组（名称 + 按钮）。"""
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