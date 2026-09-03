"""
OCTools/config/ui_config.py
───────────────────────────────────────────────
UI 配置加载器：读取 config/ui_config.json，提供统一访问接口。

设计要点：
  - 所有 UI 参数（颜色 / 字体 / 尺寸 / 布局 / 间距 / 图标引用 / 图片路径）
    都声明在 JSON 文件中，代码不再出现硬编码的魔法值。
  - CONFIG 为模块级单例，启动时一次性加载；theme.py 用它生成全局 QSS。
  - 读取失败时回退一份内置默认值，绝不因配置缺失崩溃。

用法:
  from config.ui_config import CONFIG as C
  C.color("primary")        # -> "#4F6EF7"
  C.size("radius_card")     # -> 12
  C.layout("sidebar_width") # -> 208
  C.spacing("form")         # -> 10
  C.font("body")            # -> 13
  C.path("using_dir")       # 相对项目根的 resources/icons
  C.model_path("hy_path")   # -> 模型路径（paths.models.root + hy_path）
  C.image("logo")           # 图标文件名

模型路径约定（paths.models）：
  - "root" 为模型根目录，其余条目为相对 root 的子路径；
    迁移到别的盘/目录时只改 root 一处即可。
  - 条目若写成绝对路径（含盘符或以 / 开头），则按绝对路径使用、忽略 root。
  - 旧拼写目录（AI_Modles）仍会自动回退，见 _with_legacy_fallback。
"""

import json
import os

# 项目根目录
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(_ROOT, "config", "ui_config.json")

# 模型根目录的旧拼写（历史遗留的错别字）与新拼写。
# 两者互不为子串（AI_Model / AI_Modles 第 7 个字符不同），可安全做字符串替换。
_MODEL_ROOT = "AI_Model"
_MODEL_ROOT_LEGACY = "AI_Modles"

# 已回退过的路径，避免同一路径反复告警
_LEGACY_WARNED = set()


def migrate_model_path(value, fallback: str = "") -> str:
    """把历史配置里保存的旧模型路径修正为当前路径。

    持久化配置是"保存那一刻的默认值快照"：默认值（例如模型目录改名）之后
    再怎么改，已经存下来的配置都不会跟着变，于是老用户一直读到失效路径。
    本函数按下列顺序判定：

      1. value 在磁盘上真实存在 → 原样返回（尊重用户自定义路径）；
      2. value 含旧目录名 → 替换为新目录名，若存在则返回；
      3. 都不存在 → 返回 fallback（当前默认值），让配置回到可用状态。

    Args:
        value:    持久化配置里读到的路径（可能已失效）
        fallback: 修正不了时使用的当前默认值，可为空
    """
    if not isinstance(value, str) or not value:
        return fallback
    if os.path.exists(value):
        return value
    migrated = value.replace(_MODEL_ROOT_LEGACY, _MODEL_ROOT)
    if migrated != value and os.path.exists(migrated):
        return migrated
    return fallback or migrated


def _with_legacy_fallback(path: str) -> str:
    """新路径不存在、但旧拼写目录存在时，回退到旧路径。

    改目录名只影响根目录那一段，因此仅当路径中含 _MODEL_ROOT 时才尝试替换；
    两者互不为子串，替换安全。命中旧目录时提示一次，提醒用户重命名。
    """
    if not path or os.path.exists(path):
        return path
    legacy = path.replace(_MODEL_ROOT, _MODEL_ROOT_LEGACY, 1)
    if legacy == path or not os.path.exists(legacy):
        return path
    if path not in _LEGACY_WARNED:
        _LEGACY_WARNED.add(path)
        # TODO(P0-2): 接入统一 logging 后改为 logger.warning
        print(f"[配置] 模型目录不存在：{path}\n"
              f"       已回退到旧目录：{legacy}\n"
              f"       建议把 {legacy} 重命名为 {_MODEL_ROOT}，之后可移除该兼容回退。")
    return legacy


# ── 内置兜底配置（仅当 JSON 缺失/损坏时使用，保证可启动）─────────
_FALLBACK = {
    "meta": {"name": "converter-ui", "version": 1},
    "paths": {
        "icon_dir": os.path.join("resources", "icons"),
        "using_dir": os.path.join("resources", "icons"),
        "media_dir": os.path.join("resources", "icons"),
        "app_icon": os.path.join("resources", "icons", "logo128.png"),
        "logo32": os.path.join("resources", "icons", "logo32.png"),
        "ffmpeg": "ffmpeg",
        "espeak_data": os.path.join("C:", os.sep, "Program Files",
                                    "eSpeak NG", "share", "espeak-ng-data"),
        "libreoffice": "",
        "models": {
            "root": os.path.join("D:", os.sep, _MODEL_ROOT),
            "hy_path": os.path.join("hy_mt", "Hy-MT2-1.8B-Q4_K_M.gguf"),
            "opus_base": "opusMT",
            "sensevoice": os.path.join(
                "SenseVoiceSmall", "models", "iic--SenseVoiceSmall",
                "snapshots", "master"),
            "paddle_cache": "paddle",
            "moss": "moss",
            "kokoro": "kokoro",
        },
    },
    "fonts": {
        "family": "Microsoft YaHei UI",
        "family_log": "Consolas",
        "body": 13,
        "hint": 11,
        "form_label": 12,
        "field_label_weight": 700,
        "page_title": 22,
        "page_subtitle": 12,
        "card_title": 14,
        "section_title": 12,
        "status": 11,
        "summary": 11,
        "log_title": 12,
        "title_bar_title": 13,
        "brand": 15,
        "brand_sub": 10,
        "brand_badge": 17,
        "nav": 13,
        "btn": 13,
        "win_ctrl": 12,
        "convert": 15,
        "group_header": 14,
        "section_header": 13,
        "log": 11,
        "msgbox": 13,
        "mode_badge": 12,
        "dxf": 12,
        "newline": 0,
    },
    "colors": {
        "bg": "#F3F5F9",
        "card": "#FFFFFF",
        "primary": "#4F6EF7",
        "primary_dark": "#3B5BE0",
        "primary_light": "#EEF2FE",
        "primary_gradient2": "#6B87F9",
        "secondary": "#10B981",
        "secondary_dark": "#0E9F6E",
        "accent": "#F59E0B",
        "danger": "#EF4444",
        "danger_dark": "#DC2626",
        "purple": "#8B5CF6",
        "pink": "#EC4899",
        "text": "#1F2430",
        "text_light": "#64748B",
        "nav_text": "#5A6472",
        "border": "#E6EAF1",
        "input_border": "#D5DBE6",
        "hover": "#F1F4F9",
        "pressed": "#D8DFEA",
        "section_header": "#F8FAFC",
        "group_hover": "#EDF1F7",
        "log_bg": "#101626",
        "log_fg": "#DFE6F2",
        "sidebar_bg": "#FBFCFE",
        "nav_active_bg": "#EEF2FE",
        "nav_active_fg": "#3B5BE0",
        "subtle_bg": "#F8FAFC",
        "disabled_bg": "#F3F4F7",
        "disabled_fg": "#A5ADBB",
        "disabled_border": "#EEF1F5",
        "primary_btn_bg": "#E8F0FE",
        "primary_btn_hover": "#D8E5FD",
        "primary_btn_pressed": "#C9D9FC",
        "primary_btn_disabled_bg": "#F0F4FE",
        "primary_btn_disabled_fg": "#9AA6B8",
        "win_close_hover_bg": "#FEE2E2",
        "indicator_border": "#9AA5B5",
        "chip_text": "#374151",
        "chip_disabled_fg": "#C0C6CF",
        "cat_disabled": "#C6CBD4",
        "field_disabled_fg": "#9AA2B0",
        "scroll_handle": "#C9D2E0",
        "scroll_handle_hover": "#A9B4C6",
        "mode_badge_border": "#D9E2FD",
        "mode_badge_concat_bg": "#ECFDF5",
        "mode_badge_concat_border": "#C8F0DD",
        "icon_default": "#64748B",
        "icon_footer": "#8A94A6",
        "toast_success": "#10B981",
        "toast_info": "#3B82F6",
        "toast_warning": "#F59E0B",
        "toast_text": "#FFFFFF",
        "screen_border": "#3B82F6",
        "screen_mask": "#50000000",
        "screen_hint_bg": "#DC0F172A",
        "screen_hint_fg": "#E2E8F0",
        "screen_bg_default": "#1F2937",
        "voice_sub_bg": "#0C121F",
        "icon_blue": "#2563EB",
        "title_fg": "#1F2937",
        "colorpicker_default": "#000000",
    },
    "sizes": {
        "radius_card": 12,
        "radius_btn": 8,
        "radius_badge": 9,
        "radius_logo": 10,
        "radius_dxf": 7,
        "nav_badge_w": 34,
        "nav_badge_h": 34,
        "nav_padding_v": 10,
        "nav_padding_h": 14,
        "btn_padding_h": 14,
        "btn_h": 34,
        "cta_h": 48,
        "win_padding_v": 4,
        "win_padding_h": 10,
        "win_min_h": 16,
        "convert_padding_h": 32,
        "convert_radius": 12,
        "input_padding_v": 5,
        "input_padding_h": 10,
        "input_min_h": 22,
        "combo_dropdown_w": 24,
        "combo_arrow_l": 5,
        "combo_arrow_t": 6,
        "spin_btn_w": 16,
        "indicator_size": 18,
        "check_radius": 5,
        "radio_radius": 9,
        "group_padding_v": 11,
        "group_padding_h": 14,
        "group_radius": 10,
        "sec_radius": 8,
        "sec_padding_v": 9,
        "sec_padding_h": 12,
        "log_padding": 10,
        "log_radius": 10,
        "scroll_w": 10,
        "scroll_margin": 2,
        "scroll_handle_radius": 4,
        "scroll_handle_min": 30,
        "badge_padding_v": 4,
        "badge_padding_h": 12,
        "badge_radius": 10,
        "cat_padding_v": 6,
        "cat_padding_h": 14,
        "chip_padding_v": 6,
        "chip_padding_h": 14,
        "dxf_padding_v": 4,
        "dxf_padding_h": 10,
        "dxf_btn_padding_h": 12,
        "dxf_btn_radius": 7,
        "title_bar_h": 42,
        "sidebar_w": 208,
        "title_bar_margin_l": 14,
        "title_bar_margin_r": 6,
        "title_bar_margin_v": 0,
        "title_bar_spacing": 8,
        "sidebar_margin_l": 14,
        "sidebar_margin_r": 14,
        "sidebar_margin_t": 18,
        "sidebar_margin_b": 16,
        "sidebar_spacing": 6,
        "page_margin_l": 24,
        "page_margin_r": 24,
        "page_margin_t": 20,
        "page_margin_b": 14,
        "page_spacing": 12,
        "header_spacing": 2,
        "header_row_spacing": 8,
        "sidebar_toggle_btn": 30,
        "icon_nav": 18,
        "icon_card": 18,
        "icon_small": 14,
        "icon_medium": 15,
        "icon_large": 18,
        "icon_btn": 16,
        "icon_footer": 14,
        "toast_padding_v": 10,
        "toast_padding_h": 18,
        "toast_radius": 8,
        "toast_font": 12,
        "form_row_spacing": 10,
        "card_spacing": 12,
        "txn_log_min_h": 160,
        "txn_input_min_h": 120,
        "txn_button_min_h": 48,
        "combo_min_w": 220,
        "combo_min_w_small": 180,
        "combo_min_w_large": 240,
        "min_width_96": 96,
        "min_width_200": 200,
        "delete_btn_w": 40,
        "colorpicker_w": 90,
        "color_btn_w": 52,
        "finish_icon": 18,
        "voice_edge": 8,
        "voice_min_w": 160,
        "voice_min_h": 60,
        "screen_min_size": 24,
        "screen_handle": 10,
        "form_width_90": 90,
    },
    "layout": {
        "title_bar_h": 42,
        "sidebar_w": 208,
        "nav_icon_size": 18,
        "brand_icon_size": 14,
        "toggle_btn_size": 30,
        "page_min_w": 0,
        "page_min_h": 0,
    },
    "icons": {
        "sidebar_toggle": "layout",
        "footer_icon": "bulb",
        "doc": "file",
        "table": "table",
        "presentation": "presentation",
        "image": "photo",
        "video": "video",
        "audio": "music",
        "code": "braces",
    },
    "images": {
        "app_icon": "app_icon.png",
        "logo": "logo128.png",
    },
}


# 全局缩放不介入的硬几何尺寸（命中区域/坐标计算，缩放会破坏交互精度）
_SIZE_NO_SCALE = {
    "resize_margin", "screen_handle", "screen_min_size",
    "overlay_resize_margin", "scrollbar_edge_gutter",
    "overlay_screen_half_div", "overlay_min_w", "overlay_min_h",
    "overlay_max_w_min", "overlay_max_w_max",
}


class _Config:
    """UI 配置访问器：包装 dict，提供按段取值的快捷方法。

    取值优先级（覆盖 > 当前主题 profile > 基座配置）：
      - 基座：ui_config.json 顶层各段（浅色即基座）；
      - 主题：ui_config.json themes.profiles.<主题名> 段（深色覆盖色板）；
      - 覆盖：用户设置页自定义（ui_overrides），优先级最高。
    """

    def __init__(self, data: dict):
        self._data = dict(data)
        self._theme = self.default_theme()
        self._overrides: dict = {}     # {"colors":{}, "sizes":{}, "fonts":{}}
        self._scale: float = 1.0       # 全局缩放系数（fonts/sizes 生效）

    # ── 通用访问 ──────────────────────────
    def _raw_no_override(self, section: str, key: str):
        """忽略用户覆盖层，仅按「主题 profile → 基座」取原始值。"""
        profiles = self._data.get("themes", {}).get("profiles", {})
        theme_sec = (profiles.get(self._theme, {}) or {}).get(section)
        if isinstance(theme_sec, dict) and key in theme_sec:
            return theme_sec[key]
        sec = self._data.get(section, {})
        return sec.get(key) if isinstance(sec, dict) else None

    def raw(self, section: str, key: str):
        ov = self._overrides.get(section, {})
        if isinstance(ov, dict) and key in ov:
            return ov[key]
        return self._raw_no_override(section, key)

    def effective_if_unoverridden(self, section: str, key: str, scale: float):
        """临时计算：假设 key 无覆盖时，在指定 scale 下的生效值（不改状态）。

        供设置页判断「当前控件值是否等于默认」，避免把默认值误写成覆盖。
        """
        base = self._raw_no_override(section, key)
        if not isinstance(base, (int, float)):
            return base
        if scale == 1.0:
            return int(base)
        if section == "fonts" and key.endswith("_weight"):
            return int(base)
        if section == "sizes" and key in _SIZE_NO_SCALE:
            return int(base)
        return int(round(base * scale))

    def section(self, name: str) -> dict:
        merged = {}
        base = self._data.get(name, {})
        if isinstance(base, dict):
            merged.update(base)
        profiles = self._data.get("themes", {}).get("profiles", {})
        theme_sec = (profiles.get(self._theme, {}) or {}).get(name)
        if isinstance(theme_sec, dict):
            merged.update(theme_sec)
        ov = self._overrides.get(name, {})
        if isinstance(ov, dict):
            merged.update(ov)
        return merged

    # ── 主题 / 覆盖 / 缩放 ─────────────────
    def theme(self) -> str:
        return self._theme

    def default_theme(self) -> str:
        return self._data.get("themes", {}).get("default_theme", "light")

    def theme_names(self) -> dict:
        names = self._data.get("themes", {}).get("names", {})
        return names if isinstance(names, dict) else {}

    def set_theme(self, name: str):
        profiles = self._data.get("themes", {}).get("profiles", {})
        if isinstance(profiles, dict) and name in profiles:
            self._theme = name
        else:
            self._theme = self.default_theme()
        return self._theme

    def set_overrides(self, overrides: dict):
        import copy
        self._overrides = copy.deepcopy(overrides) if isinstance(overrides, dict) else {}

    def set_scale(self, scale):
        try:
            self._scale = float(scale)
        except (TypeError, ValueError):
            self._scale = 1.0

    def apply_theme_settings(self, settings: dict):
        """从应用设置（presets/app_settings）一次性应用主题/覆盖/缩放。"""
        settings = settings or {}
        theme = settings.get("ui_theme")
        self.set_theme(theme if isinstance(theme, str) else self.default_theme())
        self.set_scale(settings.get("ui_scale", 1.0))
        self.set_overrides(settings.get("ui_overrides"))

    def theme_settings(self) -> dict:
        """导出当前主题/覆盖/缩放，用于持久化。"""
        import json
        return {
            "ui_theme": self._theme,
            "ui_scale": round(self._scale, 3),
            "ui_overrides": json.loads(
                json.dumps(self._overrides or {}, ensure_ascii=False)),
        }

    # ── 便捷取具体类型 ────────────────────
    def color(self, key: str) -> str:
        v = self.raw("colors", key)
        return v if isinstance(v, str) else ""

    def size(self, key: str) -> int:
        v = self.raw("sizes", key)
        if isinstance(v, (int, float)):
            if self._scale != 1.0 and key not in _SIZE_NO_SCALE \
                    and key not in self._overrides.get("sizes", {}):
                v = round(v * self._scale)
            return int(v)
        return 0

    def font(self, key: str) -> int:
        v = self.raw("fonts", key)
        if isinstance(v, (int, float)):
            # 字重等非字号字段不参与缩放；已单独自定义的字号也保持原值
            if self._scale != 1.0 and not key.endswith("_weight") \
                    and key not in self._overrides.get("fonts", {}):
                v = round(v * self._scale)
            return int(v)
        return 0

    def layout(self, key: str) -> int:
        v = self.raw("layout", key)
        return int(v) if isinstance(v, (int, float)) else 0

    def spacing(self, key: str) -> int:
        return self.size(key)

    def path(self, key: str) -> str:
        v = self.raw("paths", key)
        return v if isinstance(v, str) else ""

    def model_path(self, key: str) -> str:
        """取模型路径（paths.models.<key>）。

        - 条目为绝对路径（含盘符 / 以 / 开头）时直接返回；
        - 否则视为相对路径，拼到 paths.models.root 之下；
        - 拼出的路径不存在时回退旧拼写目录，见 _with_legacy_fallback。
        """
        m = self.raw("paths", "models")
        if not isinstance(m, dict):
            return ""
        v = m.get(key)
        if not isinstance(v, str) or not v:
            return ""
        v = v.replace("/", os.sep) if os.sep != "/" else v
        if os.path.isabs(v):
            return _with_legacy_fallback(os.path.normpath(v))
        root = m.get("root")
        if not isinstance(root, str) or not root:
            return ""
        return _with_legacy_fallback(
            os.path.normpath(os.path.join(root, v)))

    def model_root(self) -> str:
        """模型根目录（paths.models.root），供"浏览"对话框作为起始目录。"""
        m = self.raw("paths", "models")
        root = m.get("root") if isinstance(m, dict) else None
        if not isinstance(root, str) or not root:
            return ""
        root = root.replace("/", os.sep) if os.sep != "/" else root
        return _with_legacy_fallback(os.path.normpath(root))

    def espeak_data(self) -> str:
        """eSpeak NG 数据目录（Kokoro 音素合成依赖）。"""
        v = self.path("espeak_data")
        if not v:
            return ""
        return os.path.normpath(v.replace("/", os.sep) if os.sep != "/" else v)

    def icon(self, key: str) -> str:
        v = self.raw("icons", key)
        return v if isinstance(v, str) else key

    def image(self, key: str) -> str:
        v = self.raw("images", key)
        return v if isinstance(v, str) else key

    def text(self, key: str) -> str:
        v = self.raw("text", key)
        return v if isinstance(v, str) else key

    def text_raw(self, key: str, default: str) -> str:
        v = self.raw("text", key)
        return v if isinstance(v, str) else default

    def icon_dir(self) -> str:
        return os.path.join(_ROOT, self.path("icon_dir"))

    def using_dir(self) -> str:
        return os.path.join(_ROOT, self.path("using_dir"))

    def media_dir(self) -> str:
        return os.path.join(_ROOT, self.path("media_dir"))


def _load() -> _Config:
    """加载 JSON；失败则回退内置默认配置。"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and data:
                return _Config(data)
    except Exception:
        pass
    return _Config(_FALLBACK)


# 模块级单例，供整个 UI 层共用
CONFIG = _load()