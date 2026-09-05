"""
OCTools/ui/options/set_screen_region.py
───────────────────────────────────────────────
截图框（OCR 识别区域）选项窗口

配置项（ScreenRegionConfig）：
  - 截图框边框颜色（预设色 / 自定义）
  - 是否固定截图框（固定后热键直接使用该区域，不再弹框选）
  - 框选并设为固定区域 / 清除固定区域
  - 命名预设：保存 / 加载 / 删除 / 导出 / 导入（方便多套区域配置间切换）
"""

import os

from PySide6.QtWidgets import (
    QHBoxLayout, QFormLayout, QLabel, QComboBox,
    QCheckBox, QPushButton, QWidget, QColorDialog, QMessageBox, QInputDialog,
    QFileDialog,
)
from PySide6.QtCore import Qt, QSize
from ui import icon_res
from PySide6.QtGui import QColor

from ui.options._base import OptionsDialogBase

from config.screen_region_config import ScreenRegionConfig, BORDER_COLOR_PRESETS
from config import presets
from ui.theme import THEME as T
from config.ui_config import CONFIG as C


class SetScreenRegion(OptionsDialogBase):
    """截图框（OCR 识别区域）选项窗口"""

    def __init__(self, config: ScreenRegionConfig, parent=None):
        super().__init__("截图框设置（OCR 识别区域）", parent)
        self._config = config
        self.fit_size(580, 540)

        self.build_header("截图框设置（OCR 识别区域）")
        body, b_lay = self.build_scroll_body(margins=(20, 16, 20, 12))

        # ── 识别区域 ──
        card1, c1 = self.build_section_card("识别区域", body)
        form = self.make_form(c1)
        c1.addLayout(form)

        # 边框颜色
        self._color_combo = QComboBox(card1)
        cur = str(config.border_color or "#3B82F6")
        idx = 0
        for i, (label, val) in enumerate(BORDER_COLOR_PRESETS):
            self._color_combo.addItem(label, val)
            if val.lower() == cur.lower():
                idx = i
        self._color_combo.addItem(f"自定义（当前 #{cur.lstrip('#')}）", cur)
        self._color_combo.setCurrentIndex(idx)
        self._color_combo.currentIndexChanged.connect(self._on_color_changed)
        form.addRow("截图框边框颜色:", self._color_combo)

        # 固定开关
        self._fixed_chk = QCheckBox("固定截图框（按热键直接使用该区域，不再弹框选）", card1)
        self._fixed_chk.setChecked(bool(config.fixed))
        form.addRow("", self._fixed_chk)

        # 当前区域
        self._region_summary = QLabel("", card1)
        self._region_summary.setObjectName("summary")
        form.addRow(self._region_summary)

        # 区域操作行
        region_row = QWidget(card1)
        rr_lay = QHBoxLayout(region_row)
        rr_lay.setContentsMargins(0, 0, 0, 0)
        rr_lay.setSpacing(C.size("header_row_spacing"))
        select_btn = QPushButton("框选并设为固定区域", region_row)
        select_btn.setIcon(icon_res.colored_icon("mouse"))
        select_btn.setIconSize(QSize(C.size("icon_small"), C.size("icon_small")))
        select_btn.setObjectName("primary")
        select_btn.clicked.connect(self._pick_region)
        clear_btn = QPushButton("清除固定区域", region_row)
        clear_btn.setIcon(icon_res.colored_icon("trash"))
        clear_btn.setIconSize(QSize(C.size("icon_small"), C.size("icon_small")))
        clear_btn.setObjectName("ghost")
        clear_btn.clicked.connect(self._clear_region)
        rr_lay.addWidget(select_btn)
        rr_lay.addWidget(clear_btn)
        rr_lay.addStretch(1)
        form.addRow("区域:", region_row)
        b_lay.addWidget(card1)

        # ── 命名预设管理 ──
        card2, c2 = self.build_section_card("区域预设（保存多套截图框配置，方便切换）", body)
        self._build_preset_row(card2, c2)
        b_lay.addWidget(card2)

        b_lay.addStretch(1)

        # ── 底部按钮（固定在窗口底部）──
        self._lay.addWidget(self.build_buttons(
            left_text="取消", left_on_click=self.reject,
            ok_text="保存", ok_icon="check", on_ok=self._ok,
            margins=(20, 4, 20, 12)))

        self._refresh_region_summary()

    # ── 颜色 ──

    def _on_color_changed(self, _idx):
        if self._color_combo.currentData() == "__custom__":
            color = QColorDialog.getColor(QColor(str(self._config.border_color)), self)
            if color.isValid():
                self._color_combo.setItemData(self._color_combo.currentIndex(), color.name())
            else:
                self._color_combo.setCurrentIndex(0)

    # ── 区域 ──

    def _refresh_region_summary(self):
        self._region_summary.setText(
            f"当前区域：{self._config.summary()} | 边框：{self._config.border_color}")

    def _pick_region(self):
        """全屏框选一次，设为固定区域。

        框选期间主窗口必须让开，否则用户选不到被它盖住的区域：
          - 本对话框是顶层窗口 → 直接 hide() 即可；
          - 主窗口要经 window_ctl 解析 —— self.parent() 是 **tab 页子控件**，
            对它 hide() 只会把页面藏掉，主窗口框架（标题栏 / 侧栏）依然挡屏。
        用「最小化」而非 hide：任务栏图标还在，用户不会以为程序崩了；
        框选结束（含取消 / 异常）必须恢复，否则用户以为卡死。
        """
        from ui.ui_component.region_box import RegionSelectDialog
        from ui.ui_component import window_ctl

        self.hide()
        host = self.parent()                 # tab 页（子控件）→ 由 window_ctl 解析主窗口
        minimized = window_ctl.minimize_host(host)
        try:
            dlg = RegionSelectDialog(border_color=self._config.border_color)
            if dlg.exec() == QDialog.Accepted and dlg.selected_rect is not None:
                r = dlg.selected_rect
                self._config.set_rect(r.x(), r.y(), r.width(), r.height())
                self._config.fixed = True
                self._fixed_chk.setChecked(True)
                QMessageBox.information(
                    self, "已设置",
                    f"已把区域 ({r.x()}, {r.y()}) {r.width()}×{r.height()} 设为固定截图框。")
        finally:
            if minimized:
                window_ctl.restore_host(host)
            self.show()
            self.raise_()
        self._refresh_region_summary()

    def _clear_region(self):
        self._config.set_rect(0, 0, 0, 0)
        self._config.fixed = False
        self._fixed_chk.setChecked(False)
        self._refresh_region_summary()

    # ── 命名预设 ──

    def _build_preset_row(self, parent, lay):
        row = QWidget(parent)
        r_lay = QHBoxLayout(row)
        r_lay.setContentsMargins(0, 0, 0, 0)
        r_lay.setSpacing(C.size("header_row_spacing"))
        lab = QLabel("预设:", row)
        lab.setObjectName("fieldLabel")
        r_lay.addWidget(lab)
        self._preset_combo = QComboBox(row)
        self._preset_combo.setMinimumWidth(180)
        r_lay.addWidget(self._preset_combo, 1)

        def refresh():
            try:
                self._preset_combo.blockSignals(True)
                self._preset_combo.clear()
                self._preset_combo.addItems(presets.list_screen_region_presets())
                self._preset_combo.setCurrentIndex(-1)
                self._preset_combo.blockSignals(False)
            except Exception:
                pass

        def do_load():
            name = self._preset_combo.currentText().strip()
            if not name:
                QMessageBox.warning(self, "提示", "请先选择一个预设")
                return
            cfg = presets.load_screen_region_preset(name)
            if cfg is None:
                QMessageBox.critical(self, "失败", f"无法加载预设: {name}")
                return
            # 应用预设
            for k, v in cfg.to_dict().items():
                setattr(self._config, k, v)
            self._fixed_chk.setChecked(bool(cfg.fixed))
            self._refresh_color_combo()
            self._refresh_region_summary()
            self._app_log(f"💾 已加载区域预设: {name}")
            refresh()

        def do_save():
            name, ok = QInputDialog.getText(self, "另存为区域预设", "输入预设名称：")
            if not ok or not name or not name.strip():
                return
            name = name.strip()
            try:
                presets.save_screen_region_preset(self._config, name)
                self._app_log(f"💾 已保存区域预设: {name}")
            except Exception as e:
                QMessageBox.critical(self, "失败", str(e))
            refresh()

        def do_delete():
            name = self._preset_combo.currentText().strip()
            if not name:
                QMessageBox.warning(self, "提示", "请先选择一个预设")
                return
            ret = QMessageBox.question(self, "确认", f"确定删除区域预设「{name}」吗？")
            if ret != QMessageBox.Yes:
                return
            if presets.delete_screen_region_preset(name):
                self._app_log(f"🗑 已删除区域预设: {name}")
            refresh()

        def do_export():
            path, _ = QFileDialog.getSaveFileName(
                self, "导出区域配置", "区域配置.json", "JSON (*.json);;所有文件 (*.*)")
            if not path:
                return
            if not os.path.splitext(path)[1]:
                path += ".json"
            try:
                presets.export_screen_region_preset(self._config, path)
                self._app_log(f"📤 已导出区域配置: {path}")
            except Exception as e:
                QMessageBox.critical(self, "失败", str(e))

        def do_import():
            path, _ = QFileDialog.getOpenFileName(
                self, "导入区域配置", "", "JSON (*.json);;所有文件 (*.*)")
            if not path:
                return
            cfg = presets.import_screen_region_preset(path)
            if cfg is None:
                QMessageBox.critical(self, "失败", "无法导入该文件（格式不正确）")
                return
            for k, v in cfg.to_dict().items():
                setattr(self._config, k, v)
            self._fixed_chk.setChecked(bool(cfg.fixed))
            self._refresh_color_combo()
            self._refresh_region_summary()
            self._app_log(f"📥 已导入区域配置: {os.path.basename(path)}")

        load_btn = QPushButton("加载", row)
        load_btn.setObjectName("primary")
        load_btn.clicked.connect(do_load)
        r_lay.addWidget(load_btn)
        del_btn = QPushButton("删除", row)
        del_btn.setObjectName("danger")
        del_btn.clicked.connect(do_delete)
        r_lay.addWidget(del_btn)
        save_btn = QPushButton("另存为…", row)
        save_btn.setObjectName("primary")
        save_btn.clicked.connect(do_save)
        r_lay.addWidget(save_btn)
        lay.addWidget(row)

        # 导出 / 导入 行
        io_row = QWidget(parent)
        io_lay = QHBoxLayout(io_row)
        io_lay.setContentsMargins(0, 0, 0, 0)
        io_lay.setSpacing(C.size("header_row_spacing"))
        io_lay.addStretch(1)
        export_btn = QPushButton("导出配置…", io_row)
        export_btn.setIcon(icon_res.colored_icon("file-export"))
        export_btn.setIconSize(QSize(C.size("icon_small"), C.size("icon_small")))
        export_btn.setObjectName("ghost")
        export_btn.clicked.connect(do_export)
        io_lay.addWidget(export_btn)
        import_btn = QPushButton("导入配置…", io_row)
        import_btn.setIcon(icon_res.colored_icon("file-import"))
        import_btn.setIconSize(QSize(C.size("icon_small"), C.size("icon_small")))
        import_btn.setObjectName("ghost")
        import_btn.clicked.connect(do_import)
        io_lay.addWidget(import_btn)
        lay.addWidget(io_row)
        refresh()

    def _refresh_color_combo(self):
        """按配置边框颜色刷新颜色下拉"""
        cur = str(self._config.border_color or "#3B82F6")
        for i in range(self._color_combo.count()):
            if str(self._color_combo.itemData(i) or "").lower() == cur.lower():
                self._color_combo.setCurrentIndex(i)
                return
        # 自定义：追加一项
        for i in range(self._color_combo.count()):
            if self._color_combo.itemData(i) == "__custom__":
                self._color_combo.setItemData(i, cur)
                self._color_combo.setItemText(i, f"自定义（当前 #{cur.lstrip('#')}）")
                self._color_combo.setCurrentIndex(i)
                return

    def _app_log(self, msg):
        parent_win = self.parent()
        if parent_win is not None and hasattr(parent_win, "log"):
            try:
                parent_win.log(msg)
            except Exception:
                print(msg)
        else:
            print(msg)

    # ── 保存 ──

    def _ok(self):
        color = str(self._color_combo.currentData() or "#3B82F6")
        if color == "__custom__":
            color = self._config.border_color
        self._config.border_color = color
        self._config.fixed = self._fixed_chk.isChecked()
        self.accept()

    def get_config(self) -> ScreenRegionConfig:
        return self._config


def show_screen_region_options(parent, config: ScreenRegionConfig, on_close=None):
    """打开截图框选项窗口（非模态，关闭时回调）"""
    dlg = SetScreenRegion(config, parent)
    dlg.setAttribute(Qt.WA_DeleteOnClose)
    if on_close is not None:
        dlg.finished.connect(lambda _r: on_close())
    dlg.show()
    dlg.raise_()
    dlg.activateWindow()
    return dlg