"""
OCTools/mvp/tree/set_tts.py
───────────────────────────────────────────────
TTS 语音参数设置窗口（PySide6 版，txt / md → 音频）

包含：
  1. 预设管理（加载 / 保存 / 另存为 / 删除 / 导入 / 导出，参考 MD→DOCX 预设页面）
  2. 语音引擎选择（Kokoro 默认 / Edge-TTS / MOSS-TTS）
  3. 各引擎独立参数（QStackedWidget 切换）

点「确定」写回调用方持有的 TtsConfig 对象。
"""

import os

from PySide6.QtCore import Qt, QSize
from ui import icon_res
from PySide6.QtGui import QGuiApplication, QCursor
from PySide6.QtWidgets import (
    QHBoxLayout, QFormLayout, QLabel, QComboBox,
    QLineEdit, QSpinBox, QCheckBox, QSlider, QPushButton,
    QStackedWidget, QWidget, QFileDialog, QMessageBox,
)

from ui.options._base import OptionsDialogBase

from config.tts_config import ENGINE_LABELS, ENGINE_ORDER, TtsConfig
from core.engines.tts_engine import (
    EDGE_ZH_VOICES, KOKORO_LANGS, list_kokoro_voices, list_moss_models,
)
from config import presets

from ui.theme import THEME as T
from config.ui_config import CONFIG as C


class SetTts(OptionsDialogBase):
    """语音参数窗口"""

    def __init__(self, config: TtsConfig, parent=None):
        super().__init__("语音参数 - TXT / MD → 音频", parent)
        self._config = config
        # 尺寸自适应屏幕：小屏幕不超出屏幕外（内容区可滚动）
        screen = QGuiApplication.screenAt(QCursor.pos()) or QGuiApplication.primaryScreen()
        sgeo = screen.geometry()
        self.resize(min(640, sgeo.width() - 120), min(640, sgeo.height() - 140))
        self.setMinimumSize(min(460, sgeo.width() - 60), min(420, sgeo.height() - 100))

        self.build_header("语音参数（TXT / MD → 音频）")

        # ── 可滚动内容区（窗口过小时滚动查看，不会超出屏幕）──
        body, b_lay = self.build_scroll_body(margins=(20, 16, 20, 12))

        # ── 引擎选择 ──
        eng_row = QWidget(body)
        e_lay = QHBoxLayout(eng_row)
        e_lay.setContentsMargins(0, 0, 0, 0)
        e_lay.setSpacing(C.size("form_row_spacing"))
        lab = QLabel("语音引擎:", eng_row)
        lab.setObjectName("fieldLabel")
        e_lay.addWidget(lab)
        self._engine_combo = QComboBox(eng_row)
        self._engine_combo.addItems([ENGINE_LABELS[e] for e in ENGINE_ORDER])
        try:
            self._engine_combo.setCurrentIndex(ENGINE_ORDER.index(config.engine))
        except ValueError:
            self._engine_combo.setCurrentIndex(0)
        self._engine_combo.setMinimumWidth(200)
        e_lay.addWidget(self._engine_combo)
        hint = QLabel("不同引擎参数不同，请按需设置", eng_row)
        hint.setObjectName("hint")
        e_lay.addWidget(hint)
        e_lay.addStretch(1)
        b_lay.addWidget(eng_row)

        # ── 预设管理（参考 MD→DOCX 预设页面）──
        preset_row = QWidget(body)
        p_lay = QHBoxLayout(preset_row)
        p_lay.setContentsMargins(0, 0, 0, 0)
        p_lay.setSpacing(C.size("header_row_spacing"))
        p_lab = QLabel("预设:", preset_row)
        p_lab.setObjectName("fieldLabel")
        p_lay.addWidget(p_lab)
        self._preset_combo = QComboBox(preset_row)
        self._preset_combo.setMinimumWidth(170)
        p_lay.addWidget(self._preset_combo, 1)
        for text, ic, cmd, obj in (
                ("加载", "file-import", self._load_preset, "primary"),
                ("保存", "file-export", self._save_preset, "primary"),
                ("删除", "trash", self._delete_preset, "danger")):
            b = QPushButton(text, preset_row)
            b.setIcon(icon_res.colored_icon(ic, size=C.size("icon_small")))
            b.setIconSize(QSize(C.size("icon_small"), C.size("icon_small")))
            b.setObjectName(obj)
            b.clicked.connect(cmd)
            p_lay.addWidget(b)
        b_lay.addWidget(preset_row)

        # 另存为 + 导入 / 导出
        tool_row = QWidget(body)
        t_lay = QHBoxLayout(tool_row)
        t_lay.setContentsMargins(0, 0, 0, 0)
        t_lay.setSpacing(C.size("header_row_spacing"))
        import_btn = QPushButton("导入预设", tool_row)
        import_btn.setIcon(icon_res.colored_icon("file-import"))
        import_btn.setIconSize(QSize(C.size("icon_small"), C.size("icon_small")))
        import_btn.setObjectName("ghost")
        import_btn.clicked.connect(self._import_preset)
        t_lay.addWidget(import_btn)
        export_btn = QPushButton("导出当前", tool_row)
        export_btn.setIcon(icon_res.colored_icon("file-export"))
        export_btn.setIconSize(QSize(C.size("icon_small"), C.size("icon_small")))
        export_btn.setObjectName("ghost")
        export_btn.clicked.connect(self._export_preset)
        t_lay.addWidget(export_btn)
        self._preset_name = QLineEdit(tool_row)
        self._preset_name.setPlaceholderText("输入新预设名称…")
        t_lay.addWidget(self._preset_name, 1)
        save_as_btn = QPushButton("另存为", tool_row)
        save_as_btn.setIcon(icon_res.colored_icon("download"))
        save_as_btn.setIconSize(QSize(C.size("icon_small"), C.size("icon_small")))
        save_as_btn.setObjectName("primary")
        save_as_btn.clicked.connect(self._save_preset_as)
        t_lay.addWidget(save_as_btn)
        b_lay.addWidget(tool_row)

        self._refresh_preset_combo()

        # ── 参数区 ──
        self._stack = QStackedWidget(body)

        def make_form(parent):
            form = QFormLayout()
            form.setContentsMargins(4, 8, 4, 8)
            form.setHorizontalSpacing(C.size("form_spacing"))
            form.setVerticalSpacing(C.size("form_row_spacing"))
            form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
            return form

        def hint_label(text):
            lab = QLabel(text)
            lab.setObjectName("hint")
            lab.setWordWrap(True)
            return lab

        # ── Edge-TTS ──
        fr_edge = QWidget()
        edge_form = make_form(fr_edge)
        fr_edge.setLayout(edge_form)
        self._edge_voice = QComboBox(fr_edge)
        self._edge_voice.setEditable(True)
        voices = list(EDGE_ZH_VOICES)
        cur_voice = config.edge_voice or "zh-CN-XiaoxiaoNeural"
        if cur_voice not in voices:
            voices.append(cur_voice)
        self._edge_voice.addItems(voices)
        self._edge_voice.setCurrentText(cur_voice)
        edge_form.addRow("音色 voice:", self._edge_voice)
        self._edge_rate = QLineEdit(config.edge_rate or "+0%", fr_edge)
        edge_form.addRow("语速 rate:", self._edge_rate)
        self._edge_volume = QLineEdit(config.edge_volume or "+0%", fr_edge)
        edge_form.addRow("音量 volume:", self._edge_volume)
        self._edge_pitch = QLineEdit(config.edge_pitch or "+0Hz", fr_edge)
        edge_form.addRow("音调 pitch:", self._edge_pitch)
        edge_form.addRow("", hint_label("格式如 +10% / -20% / +0Hz，在线合成需联网"))
        self._stack.addWidget(fr_edge)

        # ── Kokoro ──
        fr_kokoro = QWidget()
        kokoro_form = make_form(fr_kokoro)
        fr_kokoro.setLayout(kokoro_form)
        self._kokoro_lang = QComboBox(fr_kokoro)
        self._kokoro_lang.addItems([f"{c}（{lbl}）" for c, lbl in KOKORO_LANGS])
        try:
            self._kokoro_lang.setCurrentIndex([c for c, _ in KOKORO_LANGS].index(config.kokoro_lang))
        except ValueError:
            self._kokoro_lang.setCurrentIndex(0)
        kokoro_form.addRow("语言:", self._kokoro_lang)

        self._kokoro_voice = QComboBox(fr_kokoro)
        self._kokoro_voice.setEditable(True)
        kvoices = list(list_kokoro_voices())
        kcur = config.kokoro_voice or "zf_xiaoxiao"
        if kcur not in kvoices:
            kvoices.append(kcur)
        self._kokoro_voice.addItems(kvoices)
        self._kokoro_voice.setCurrentText(kcur)
        kokoro_form.addRow("音色（assets/voices_model）:", self._kokoro_voice)

        speed_row = QWidget(fr_kokoro)
        s_lay = QHBoxLayout(speed_row)
        s_lay.setContentsMargins(0, 0, 0, 0)
        s_lay.setSpacing(C.size("form_row_spacing"))
        self._kokoro_speed_slider = QSlider(Qt.Horizontal, speed_row)
        self._kokoro_speed_slider.setRange(50, 200)
        self._kokoro_speed_slider.setSingleStep(5)
        self._kokoro_speed_label = QLabel(speed_row)
        self._kokoro_speed_label.setFixedWidth(52)
        s_lay.addWidget(self._kokoro_speed_slider, 1)
        s_lay.addWidget(self._kokoro_speed_label)
        kokoro_form.addRow("语速 speed(0.5–2.0):", speed_row)
        self._set_speed(float(config.kokoro_speed))
        self._kokoro_speed_slider.valueChanged.connect(
            lambda v: self._kokoro_speed_label.setText(f"{v / 100:.2f}"))

        self._kokoro_split = QLineEdit(config.kokoro_split_pattern, fr_kokoro)
        self._kokoro_split.setPlaceholderText("留空 = 使用内置自定义分句")
        kokoro_form.addRow("自定义分句 split_pattern:", self._kokoro_split)
        kokoro_form.addRow("", hint_label("留空 = 使用内置自定义分句（逐句合成，保留 mvp 逻辑）"))
        self._stack.addWidget(fr_kokoro)

        # ── MOSS-TTS ──
        fr_moss = QWidget()
        moss_form = make_form(fr_moss)
        fr_moss.setLayout(moss_form)

        self._moss_model = QComboBox(fr_moss)
        self._moss_model.setEditable(True)
        models = list(list_moss_models())
        mcur = config.moss_model_dir or ""
        if mcur and mcur not in models:
            models.append(mcur)
        self._moss_model.addItems(models)
        if mcur:
            self._moss_model.setCurrentText(mcur)
        moss_form.addRow("模型目录（assets/voices_model）:", self._moss_model)

        self._moss_voice = QLineEdit(config.moss_voice, fr_moss)
        moss_form.addRow("内置音色 voice:", self._moss_voice)

        ref_row = QWidget(fr_moss)
        r_lay = QHBoxLayout(ref_row)
        r_lay.setContentsMargins(0, 0, 0, 0)
        r_lay.setSpacing(C.size("widget_row_spacing"))
        self._moss_ref = QLineEdit(config.moss_reference, ref_row)
        browse_btn = QPushButton("浏览…", ref_row)
        browse_btn.setObjectName("ghost")
        browse_btn.clicked.connect(self._browse_ref)
        r_lay.addWidget(self._moss_ref, 1)
        r_lay.addWidget(browse_btn)
        moss_form.addRow("模仿音频:", ref_row)

        self._moss_tokens = QSpinBox(fr_moss)
        self._moss_tokens.setRange(1, 1000)
        self._moss_tokens.setValue(config.moss_voice_clone_max_text_tokens or 75)
        moss_form.addRow("单段最大 token（≈75）:", self._moss_tokens)

        self._moss_frames = QSpinBox(fr_moss)
        self._moss_frames.setRange(0, 100000)
        self._moss_frames.setSingleStep(100)
        self._moss_frames.setValue(config.moss_max_new_frames or 0)
        moss_form.addRow("最大生成帧（0=默认）:", self._moss_frames)

        self._moss_sample = QCheckBox("随机采样（关闭=更稳定）", fr_moss)
        self._moss_sample.setChecked(bool(config.moss_do_sample))
        moss_form.addRow("", self._moss_sample)

        self._moss_seed = QLineEdit(str(config.moss_seed), fr_moss)
        moss_form.addRow("随机种子（-1=随机）:", self._moss_seed)
        self._stack.addWidget(fr_moss)

        b_lay.addWidget(self._stack, 1)
        self._engine_combo.currentIndexChanged.connect(self._on_engine_changed)
        self._on_engine_changed(self._engine_combo.currentIndex())

        # ── 底部按钮（固定在窗口底部，不随内容滚动）──
        self._lay.addWidget(self.build_buttons(
            left_text="恢复默认", left_on_click=self._reset,
            ok_text="确定", ok_icon="check", on_ok=self._ok,
            margins=(20, 4, 20, 12)))

    # ── 工具 ──

    def _set_speed(self, value: float):
        v = max(0.5, min(2.0, float(value)))
        self._kokoro_speed_slider.setValue(int(round(v * 100)))
        self._kokoro_speed_label.setText(f"{v:.2f}")

    def _browse_ref(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择模仿音频（参考音频，声音克隆）",
            os.path.dirname(self._moss_ref.text()) if self._moss_ref.text() else "",
            "音频文件 (*.wav *.mp3 *.flac);;所有文件 (*.*)")
        if path:
            self._moss_ref.setText(path)

    def _on_engine_changed(self, idx: int):
        eng = ENGINE_ORDER[idx] if 0 <= idx < len(ENGINE_ORDER) else "kokoro"
        mapping = {"edge": 0, "kokoro": 1, "moss": 2}
        self._stack.setCurrentIndex(mapping.get(eng, 1))

    def _reset(self):
        self._load_into_form(TtsConfig())

    # ── 表单 ⇄ 配置 ──

    def _collect_config(self) -> TtsConfig:
        """从表单收集当前参数为新的 TtsConfig"""
        cfg = TtsConfig()
        idx = self._engine_combo.currentIndex()
        cfg.engine = ENGINE_ORDER[idx] if 0 <= idx < len(ENGINE_ORDER) else "kokoro"
        cfg.edge_voice = self._edge_voice.currentText().strip() or "zh-CN-XiaoxiaoNeural"
        cfg.edge_rate = self._edge_rate.text().strip() or "+0%"
        cfg.edge_volume = self._edge_volume.text().strip() or "+0%"
        cfg.edge_pitch = self._edge_pitch.text().strip() or "+0Hz"
        li = self._kokoro_lang.currentIndex()
        cfg.kokoro_lang = KOKORO_LANGS[li][0] if 0 <= li < len(KOKORO_LANGS) else "z"
        cfg.kokoro_voice = self._kokoro_voice.currentText().strip() or "zf_xiaoxiao"
        cfg.kokoro_speed = self._kokoro_speed_slider.value() / 100.0
        cfg.kokoro_split_pattern = self._kokoro_split.text().strip()
        cfg.moss_model_dir = self._moss_model.currentText().strip()
        cfg.moss_voice = self._moss_voice.text().strip()
        cfg.moss_reference = self._moss_ref.text().strip()
        cfg.moss_voice_clone_max_text_tokens = int(self._moss_tokens.value() or 75)
        cfg.moss_max_new_frames = int(self._moss_frames.value() or 0)
        cfg.moss_do_sample = bool(self._moss_sample.isChecked())
        try:
            cfg.moss_seed = int(self._moss_seed.text().strip() or "-1")
        except ValueError:
            cfg.moss_seed = -1
        return cfg

    def _load_into_form(self, cfg: TtsConfig):
        """把配置写入表单控件（预设加载 / 恢复默认共用）"""
        self._engine_combo.setCurrentIndex(
            ENGINE_ORDER.index(cfg.engine) if cfg.engine in ENGINE_ORDER else 0)
        self._edge_voice.setCurrentText(cfg.edge_voice or "zh-CN-XiaoxiaoNeural")
        self._edge_rate.setText(cfg.edge_rate or "+0%")
        self._edge_volume.setText(cfg.edge_volume or "+0%")
        self._edge_pitch.setText(cfg.edge_pitch or "+0Hz")
        try:
            self._kokoro_lang.setCurrentIndex(
                [c for c, _ in KOKORO_LANGS].index(cfg.kokoro_lang))
        except ValueError:
            self._kokoro_lang.setCurrentIndex(0)
        self._kokoro_voice.setCurrentText(cfg.kokoro_voice or "zf_xiaoxiao")
        self._set_speed(float(cfg.kokoro_speed))
        self._kokoro_split.setText(cfg.kokoro_split_pattern or "")
        self._moss_model.setCurrentText(cfg.moss_model_dir or "")
        self._moss_voice.setText(cfg.moss_voice or "")
        self._moss_ref.setText(cfg.moss_reference or "")
        self._moss_tokens.setValue(int(cfg.moss_voice_clone_max_text_tokens or 75))
        self._moss_frames.setValue(int(cfg.moss_max_new_frames or 0))
        self._moss_sample.setChecked(bool(cfg.moss_do_sample))
        self._moss_seed.setText(str(cfg.moss_seed))
        self._on_engine_changed(self._engine_combo.currentIndex())

    # ── 预设管理 ──

    def _refresh_preset_combo(self):
        self._preset_combo.blockSignals(True)
        self._preset_combo.clear()
        self._preset_combo.addItems(presets.list_tts_presets())
        self._preset_combo.blockSignals(False)

    def _load_preset(self):
        name = self._preset_combo.currentText().strip()
        if not name:
            QMessageBox.warning(self, "提示", "请先选择一个预设")
            return
        cfg = presets.load_tts_preset(name)
        if cfg is None:
            QMessageBox.critical(self, "失败", f"无法加载预设: {name}")
            return
        self._load_into_form(cfg)
        QMessageBox.information(self, "成功", f"已加载预设: {name}")

    def _save_preset(self):
        """把当前表单参数保存到选中的预设（覆盖同名）"""
        name = self._preset_combo.currentText().strip()
        if not name:
            QMessageBox.warning(self, "提示", "请先选择一个预设")
            return
        presets.save_tts_preset(self._collect_config(), name)
        self._refresh_preset_combo()
        QMessageBox.information(self, "成功", f"已保存预设: {name}")

    def _save_preset_as(self):
        name = self._preset_name.text().strip()
        if not name:
            QMessageBox.warning(self, "提示", "请输入预设名称")
            return
        presets.save_tts_preset(self._collect_config(), name)
        self._refresh_preset_combo()
        self._preset_combo.setCurrentText(name)
        self._preset_name.clear()
        QMessageBox.information(self, "成功", f"已保存为新预设: {name}")

    def _delete_preset(self):
        name = self._preset_combo.currentText().strip()
        if not name:
            QMessageBox.warning(self, "提示", "请先选择一个预设")
            return
        ret = QMessageBox.question(self, "确认", f"确定删除预设「{name}」吗？")
        if ret != QMessageBox.Yes:
            return
        if presets.delete_tts_preset(name):
            self._refresh_preset_combo()
            QMessageBox.information(self, "成功", f"已删除预设: {name}")
        else:
            QMessageBox.critical(self, "失败", f"无法删除预设「{name}」")

    def _import_preset(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "导入语音预设", "", "JSON 文件 (*.json);;所有文件 (*.*)")
        if not path:
            return
        cfg = presets.import_tts_preset(path)
        if cfg is None:
            QMessageBox.critical(self, "失败", "无法读取语音预设文件")
            return
        self._load_into_form(cfg)
        QMessageBox.information(self, "成功", f"已导入语音预设: {os.path.basename(path)}")

    def _export_preset(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "导出语音预设", "", "JSON 文件 (*.json)")
        if not path:
            return
        presets.export_tts_preset(self._collect_config(), path)
        QMessageBox.information(self, "成功", f"已导出语音预设到:\n{path}")

    def _ok(self):
        for k, v in self._collect_config().to_dict().items():
            setattr(self._config, k, v)
        self.accept()


def show_tts_options(parent, config: TtsConfig, on_close=None):
    """打开「语音参数」窗口；点「确定」把表单值写回 config 并关闭。"""
    dlg = SetTts(config, parent)
    dlg.setAttribute(Qt.WA_DeleteOnClose)

    def _finished(_result):
        if on_close:
            on_close()

    dlg.finished.connect(_finished)
    dlg.show()
    dlg.raise_()
    dlg.activateWindow()
    return dlg
