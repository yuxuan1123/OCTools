"""
OCTools/ui/options/set_image_docx.py
───────────────────────────────────────────────
图片 → DOCX 排版选项窗口（PySide6 版）

配置图片→DOCX 的网格排版参数（每行/每列图片数、长宽、
表格边框颜色、预设保存/加载等），点「确定」写回调用方
持有的 ImageDocxConfig 对象。
"""

from PySide6.QtCore import Qt, QSize
from ui import icon_res
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QComboBox,
    QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox, QPushButton,
    QWidget, QColorDialog, QMessageBox,
)

from ui.options._base import OptionsDialogBase

from config.ui_config import CONFIG as C


class SetImageDocx(OptionsDialogBase):
    """图片 → DOCX 排版选项窗口"""

    def __init__(self, config, parent=None):
        super().__init__("图片排版选项 - 图片 → DOCX", parent)
        from config.image_docx_config import ImageDocxConfig  # 局部导入避免循环依赖
        from config import presets

        self._ImageDocxConfig = ImageDocxConfig
        self._presets = presets
        self._config = config

        self.fit_size(600, 640, min_w=520, min_h=520)

        self.build_header("图片排版选项（仅 图片 → DOCX 生效）")
        body, b_lay = self.build_scroll_body(margins=(20, 16, 20, 12))

        # ── 变量 ──
        self._vars = {
            "images_per_row": config.images_per_row,
            "images_per_column": config.images_per_column,
            "image_width_cm": config.image_width_cm,
            "image_height_cm": config.image_height_cm,
            "keep_aspect": config.keep_aspect,
            "show_filename": config.show_filename,
            "cell_spacing_pt": config.cell_spacing_pt,
            "table_border_color": config.table_border_color or "透明",
        }

        def spin(lo, hi, step=1.0, suffix=""):
            sb = QDoubleSpinBox(body)
            sb.setRange(lo, hi)
            sb.setSingleStep(step)
            sb.setDecimals(max(0, len(str(step).split(".")[1]) if "." in str(step) else 0))
            if suffix:
                sb.setSuffix(suffix)
            return sb

        def int_spin(lo, hi):
            sb = QSpinBox(body)
            sb.setRange(lo, hi)
            return sb

        # ── 预设 ──
        card1, c1 = self.build_section_card("预设", body)
        f1 = self.make_form(c1)
        c1.addLayout(f1)

        preset_row = QWidget(card1)
        p_lay = QHBoxLayout(preset_row)
        p_lay.setContentsMargins(0, 0, 0, 0)
        p_lay.setSpacing(C.size("widget_row_spacing"))
        self._preset_combo = QComboBox(preset_row)
        p_lay.addWidget(self._preset_combo, 1)
        load_btn = QPushButton("加载", preset_row)
        load_btn.setIcon(icon_res.colored_icon("folder"))
        load_btn.setIconSize(QSize(C.size("icon_small"), C.size("icon_small")))
        load_btn.setObjectName("primary")
        load_btn.clicked.connect(self._load_preset)
        p_lay.addWidget(load_btn)
        del_btn = QPushButton("删除", preset_row)
        del_btn.setIcon(icon_res.colored_icon("trash"))
        del_btn.setIconSize(QSize(C.size("icon_small"), C.size("icon_small")))
        del_btn.setObjectName("danger")
        del_btn.clicked.connect(self._delete_preset)
        p_lay.addWidget(del_btn)
        f1.addRow("", preset_row)

        save_row = QWidget(card1)
        s_lay = QHBoxLayout(save_row)
        s_lay.setContentsMargins(0, 0, 0, 0)
        s_lay.setSpacing(C.size("widget_row_spacing"))
        self._name_edit = QLineEdit(save_row)
        self._name_edit.setPlaceholderText("输入预设名称…")
        s_lay.addWidget(self._name_edit, 1)
        save_btn = QPushButton("另存为预设", save_row)
        save_btn.setIcon(icon_res.colored_icon("download"))
        save_btn.setIconSize(QSize(C.size("icon_small"), C.size("icon_small")))
        save_btn.setObjectName("primary")
        save_btn.clicked.connect(self._save_preset)
        s_lay.addWidget(save_btn)
        f1.addRow("", save_row)
        b_lay.addWidget(card1)

        # ── 网格排版 ──
        card2, c2 = self.build_section_card("网格排版", body)
        f2 = self.make_form(c2)
        c2.addLayout(f2)
        self._sp_per_row = int_spin(1, 8)
        self._sp_per_row.setValue(int(self._vars["images_per_row"]))
        f2.addRow("每行图片数 (列数):", self._sp_per_row)
        self._sp_per_col = int_spin(1, 8)
        self._sp_per_col.setValue(int(self._vars["images_per_column"]))
        f2.addRow("每列图片数 (每页行数):", self._sp_per_col)
        b_lay.addWidget(card2)

        # ── 图片尺寸 ──
        card3, c3 = self.build_section_card("图片尺寸", body)
        f3 = self.make_form(c3)
        c3.addLayout(f3)
        self._sp_width = spin(0, 40, 0.5, " cm")
        self._sp_width.setValue(float(self._vars["image_width_cm"]))
        f3.addRow("图片宽度 (cm, 0=自动):", self._sp_width)
        self._sp_height = spin(0, 40, 0.5, " cm")
        self._sp_height.setValue(float(self._vars["image_height_cm"]))
        f3.addRow("图片高度 (cm, 0=自动):", self._sp_height)
        self._ck_aspect = QCheckBox("保持宽高比", card3)
        self._ck_aspect.setChecked(bool(self._vars["keep_aspect"]))
        f3.addRow("", self._ck_aspect)
        b_lay.addWidget(card3)

        # ── 其他 ──
        card4, c4 = self.build_section_card("其他", body)
        f4 = self.make_form(c4)
        c4.addLayout(f4)
        self._ck_filename = QCheckBox("图片下方显示文件名", card4)
        self._ck_filename.setChecked(bool(self._vars["show_filename"]))
        f4.addRow("", self._ck_filename)
        self._sp_spacing = spin(0, 100, 1, " pt")
        self._sp_spacing.setValue(float(self._vars["cell_spacing_pt"]))
        f4.addRow("间距 (pt):", self._sp_spacing)

        # 表格边框颜色
        color_row = QWidget(card4)
        c_lay = QHBoxLayout(color_row)
        c_lay.setContentsMargins(0, 0, 0, 0)
        c_lay.setSpacing(C.size("widget_row_spacing"))
        self._border_edit = QLineEdit(str(self._vars["table_border_color"]), color_row)
        self._border_edit.setFixedWidth(C.size("input_min_w"))
        c_lay.addWidget(self._border_edit)
        pick_btn = QPushButton("选色", color_row)
        pick_btn.setIcon(icon_res.colored_icon("palette"))
        pick_btn.setIconSize(QSize(C.size("icon_small"), C.size("icon_small")))
        pick_btn.setObjectName("ghost")
        pick_btn.clicked.connect(self._pick_border_color)
        c_lay.addWidget(pick_btn)
        clear_btn = QPushButton("透明", color_row)
        clear_btn.setObjectName("ghost")
        clear_btn.clicked.connect(lambda: self._border_edit.setText("透明"))
        c_lay.addWidget(clear_btn)
        c_lay.addStretch(1)
        f4.addRow("表格边框颜色:", color_row)
        b_lay.addWidget(card4)

        b_lay.addWidget(self.hint_label("提示：0 表示自动适配；勾选保持宽高比时不会拉伸变形。", body))
        b_lay.addStretch(1)

        # ── 按钮行（固定在窗口底部）──
        self._lay.addWidget(self.build_buttons(
            left_text="恢复默认", left_icon="refresh", left_on_click=self._reset,
            ok_text="确定", ok_icon="check", on_ok=self._apply,
            margins=(20, 4, 20, 12)))

        self._refresh_preset_combo()

    # ── 工具 ──

    def _refresh_preset_combo(self):
        names = self._presets.list_image_presets()
        self._preset_combo.clear()
        self._preset_combo.addItems(names)

    def _form_config(self):
        border = self._border_edit.text().strip()
        if border.lower() in ("", "透明", "transparent"):
            border = ""
        return self._ImageDocxConfig(
            images_per_row=int(self._sp_per_row.value()),
            images_per_column=int(self._sp_per_col.value()),
            image_width_cm=float(self._sp_width.value()),
            image_height_cm=float(self._sp_height.value()),
            keep_aspect=bool(self._ck_aspect.isChecked()),
            show_filename=bool(self._ck_filename.isChecked()),
            cell_spacing_pt=float(self._sp_spacing.value()),
            table_border_color=border,
        )

    def _load_into_form(self, cfg):
        self._sp_per_row.setValue(int(cfg.images_per_row))
        self._sp_per_col.setValue(int(cfg.images_per_column))
        self._sp_width.setValue(float(cfg.image_width_cm))
        self._sp_height.setValue(float(cfg.image_height_cm))
        self._ck_aspect.setChecked(bool(cfg.keep_aspect))
        self._ck_filename.setChecked(bool(cfg.show_filename))
        self._sp_spacing.setValue(float(cfg.cell_spacing_pt))
        self._border_edit.setText(cfg.table_border_color or "透明")

    def _load_preset(self):
        name = self._preset_combo.currentText().strip()
        if not name:
            QMessageBox.warning(self, "提示", "请先选择一个预设")
            return
        cfg = self._presets.load_image_preset(name)
        if cfg is None:
            QMessageBox.critical(self, "失败", f"无法加载预设: {name}")
            return
        self._load_into_form(cfg)
        QMessageBox.information(self, "成功", f"已加载预设: {name}")

    def _save_preset(self):
        name = self._name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "提示", "请输入预设名称")
            return
        cfg = self._form_config()
        errors = cfg.validate()
        if errors:
            QMessageBox.critical(self, "配置有误", "\n".join(errors))
            return
        self._presets.save_image_preset(cfg, name)
        self._refresh_preset_combo()
        self._name_edit.clear()
        QMessageBox.information(self, "成功", f"已保存预设: {name}")

    def _delete_preset(self):
        name = self._preset_combo.currentText().strip()
        if not name:
            QMessageBox.warning(self, "提示", "请先选择一个预设")
            return
        ret = QMessageBox.question(self, "确认", f"确定删除预设「{name}」吗？")
        if ret != QMessageBox.Yes:
            return
        if self._presets.delete_image_preset(name):
            self._refresh_preset_combo()
            QMessageBox.information(self, "成功", f"已删除预设: {name}")
        else:
            QMessageBox.critical(self, "失败", f"无法删除预设「{name}」")

    def _pick_border_color(self):
        cur = self._border_edit.text().strip()
        initial = QColor(cur) if (cur.startswith("#") and len(cur) == 7
                                  and QColor(cur).isValid()) else QColor(C.color("colorpicker_default"))
        color = QColorDialog.getColor(initial, self, "选择表格边框颜色")
        if color.isValid():
            self._border_edit.setText(color.name().upper())

    def _reset(self):
        d = self._ImageDocxConfig()
        self._load_into_form(d)

    def _apply(self):
        cfg = self._form_config()
        errors = cfg.validate()
        if errors:
            QMessageBox.critical(self, "配置有误", "\n".join(errors))
            return
        # 写回调用方持有的配置对象
        for k, v in cfg.to_dict().items():
            setattr(self._config, k, v)
        self.accept()


def show_image_docx_options(parent, config, on_close=None):
    """打开「图片排版选项」窗口（PySide6 版）。"""
    dlg = SetImageDocx(config, parent)
    dlg.setAttribute(Qt.WA_DeleteOnClose)

    def _finished(_result):
        if on_close:
            on_close()

    dlg.finished.connect(_finished)
    dlg.show()
    dlg.raise_()
    dlg.activateWindow()
    return dlg
