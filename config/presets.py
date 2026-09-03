"""
OCTools/config/presets.py
───────────────────────────────────────────────
预设 / 上次配置管理器（最小功能单元）

本模块管理的配置：
  - FormatConfig   （MD → DOCX 排版）预设 + 上次配置
  - ImageDocxConfig（图片 → DOCX 排版）预设 + 上次配置

配置目录：config/presets/（与旧版一致，保证用户已有配置不丢失）
"""

import os
import sys
from typing import List, Optional

from config.format_config import FormatConfig
from config.image_docx_config import ImageDocxConfig
from config.paths import (
    PRESETS_DIR,
    LAST_CONFIG_FILE,
    IMAGE_LAST_CONFIG_FILE,
    PRESETS_IMAGE_DIR,
    TTS_CONFIG_FILE,
    STT_CONFIG_FILE,
    PDF_DOCX_CONFIG_FILE,
    PRESETS_TTS_DIR,
    TRANSLATOR_CONFIG_FILE,
    SCREEN_REGION_CONFIG_FILE,
    PRESETS_TRANSLATOR_DIR,
    PRESETS_SCREEN_REGION_DIR,
)


def _ensure_dir():
    """确保预设目录存在"""
    os.makedirs(PRESETS_DIR, exist_ok=True)


def _preset_path(name: str) -> str:
    """获取预设文件路径"""
    # 安全文件名：只保留合法字符
    safe = "".join(c for c in name if c.isalnum() or c in "._- ()（）")
    return os.path.join(PRESETS_DIR, f"{safe}.json")


def _preset_name_from_file(filename: str) -> str:
    """从文件名提取预设名称（去掉 .json）"""
    return os.path.splitext(filename)[0]


# ── 内置预设 ────────────────────────────

BUILTIN_PRESETS = {
    "默认配置": FormatConfig.default_chinese(),
    "论文格式": FormatConfig.paper_format(),
    "周报格式": FormatConfig.report_format(),
}


def _ensure_builtin_presets():
    """确保内置预设文件存在（首次运行时创建）"""
    _ensure_dir()
    for name, cfg in BUILTIN_PRESETS.items():
        path = _preset_path(name)
        if not os.path.exists(path):
            cfg.save_to_file(path)


# ── FormatConfig 预设 ───────────────────

def list_presets() -> List[str]:
    """列出所有预设名称（内置 + 用户保存的）"""
    _ensure_builtin_presets()
    names = []
    if os.path.exists(PRESETS_DIR):
        for f in sorted(os.listdir(PRESETS_DIR)):
            if f.endswith(".json") and not f.startswith("."):
                names.append(_preset_name_from_file(f))
    return names


def load_preset(name: str) -> Optional[FormatConfig]:
    """按名称加载预设，失败返回 None"""
    _ensure_builtin_presets()
    path = _preset_path(name)
    if not os.path.exists(path):
        # 尝试在内置预设中查找（可能还没持久化文件）
        if name in BUILTIN_PRESETS:
            return BUILTIN_PRESETS[name]
        return None
    try:
        return FormatConfig.from_file(path)
    except Exception:
        return None


def save_preset(config: FormatConfig, name: str):
    """保存当前配置为预设（会覆盖同名文件）"""
    _ensure_dir()
    config.name = name
    config.save_to_file(_preset_path(name))


def delete_preset(name: str) -> bool:
    """删除用户预设（内置预设不允许删除），返回是否成功"""
    _ensure_builtin_presets()
    if name in BUILTIN_PRESETS:
        return False  # 不允许删除内置预设
    path = _preset_path(name)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False


def export_preset(config: FormatConfig, path: str):
    """导出配置到任意路径"""
    config.save_to_file(path)


def import_preset(path: str) -> Optional[FormatConfig]:
    """从外部 JSON 文件导入配置"""
    if not os.path.exists(path):
        return None
    try:
        return FormatConfig.from_file(path)
    except Exception:
        return None


def reset_to_default() -> FormatConfig:
    """返回默认中文配置"""
    return FormatConfig.default_chinese()


def save_last_config(config: FormatConfig):
    """持久化当前配置，下次启动时自动恢复"""
    _ensure_dir()
    config.save_to_file(LAST_CONFIG_FILE)


def load_last_config() -> Optional[FormatConfig]:
    """加载上次保存的配置"""
    if os.path.exists(LAST_CONFIG_FILE):
        try:
            return FormatConfig.from_file(LAST_CONFIG_FILE)
        except Exception:
            pass
    return None


# ── ImageDocxConfig 预设与上次配置 ──────

def _ensure_image_dir():
    """确保图片预设目录存在"""
    os.makedirs(PRESETS_IMAGE_DIR, exist_ok=True)


def _image_preset_path(name: str) -> str:
    """获取图片预设文件路径"""
    safe = "".join(c for c in name if c.isalnum() or c in "._- ()（）")
    return os.path.join(PRESETS_IMAGE_DIR, f"{safe}.json")


def list_image_presets() -> List[str]:
    """列出所有图片 → DOCX 排版预设名称"""
    _ensure_image_dir()
    names = []
    if os.path.exists(PRESETS_IMAGE_DIR):
        for f in sorted(os.listdir(PRESETS_IMAGE_DIR)):
            if f.endswith(".json") and not f.startswith("."):
                names.append(os.path.splitext(f)[0])
    return names


def save_image_preset(config: ImageDocxConfig, name: str):
    """把当前图片排版配置保存为命名预设"""
    _ensure_image_dir()
    config.save_to_file(_image_preset_path(name))


def load_image_preset(name: str) -> Optional[ImageDocxConfig]:
    """按名称加载图片排版预设，失败返回 None"""
    path = _image_preset_path(name)
    if not os.path.exists(path):
        return None
    try:
        return ImageDocxConfig.from_file(path)
    except Exception:
        return None


def delete_image_preset(name: str) -> bool:
    """删除图片排版预设，返回是否成功"""
    path = _image_preset_path(name)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False


def save_last_image_config(config: ImageDocxConfig):
    """持久化图片 → DOCX 排版配置，下次启动时自动恢复"""
    _ensure_dir()
    config.save_to_file(IMAGE_LAST_CONFIG_FILE)


def load_last_image_config() -> Optional[ImageDocxConfig]:
    """加载上次保存的图片 → DOCX 排版配置"""
    if os.path.exists(IMAGE_LAST_CONFIG_FILE):
        try:
            return ImageDocxConfig.from_file(IMAGE_LAST_CONFIG_FILE)
        except Exception:
            pass
    return None


# ── TTS / STT / PDF→DOCX 上次配置 ────────

def save_last_tts_config(config):
    """持久化 TTS 语音配置（引擎选择 + 各引擎参数），下次启动自动恢复"""
    _ensure_dir()
    config.save_to_file(TTS_CONFIG_FILE)


def load_last_tts_config():
    """加载上次保存的 TTS 语音配置"""
    if os.path.exists(TTS_CONFIG_FILE):
        try:
            from config.tts_config import TtsConfig
            return TtsConfig.from_file(TTS_CONFIG_FILE)
        except Exception:
            pass
    return None


def save_last_stt_config(config):
    """持久化 STT 语音识别配置（模型目录 / 设备 / 语言等），下次启动自动恢复"""
    _ensure_dir()
    config.save_to_file(STT_CONFIG_FILE)


def load_last_stt_config():
    """加载上次保存的 STT 语音识别配置"""
    if os.path.exists(STT_CONFIG_FILE):
        try:
            from config.stt_config import SttConfig
            return SttConfig.from_file(STT_CONFIG_FILE)
        except Exception:
            pass
    return None


def save_last_pdf_docx_config(config):
    """持久化 PDF→DOCX 转换方式配置（LibreOffice / 文本提取），下次启动自动恢复"""
    _ensure_dir()
    config.save_to_file(PDF_DOCX_CONFIG_FILE)


def load_last_pdf_docx_config():
    """加载上次保存的 PDF→DOCX 转换方式配置"""
    if os.path.exists(PDF_DOCX_CONFIG_FILE):
        try:
            from config.pdf_docx_config import PdfDocxConfig
            return PdfDocxConfig.from_file(PDF_DOCX_CONFIG_FILE)
        except Exception:
            pass
    return None


# ── TTS 语音命名预设 ─────────────────────

def _ensure_tts_dir():
    """确保 TTS 预设目录存在"""
    os.makedirs(PRESETS_TTS_DIR, exist_ok=True)


def _tts_preset_path(name: str) -> str:
    """获取 TTS 预设文件路径"""
    safe = "".join(c for c in name if c.isalnum() or c in "._- ()（）")
    return os.path.join(PRESETS_TTS_DIR, f"{safe}.json")


def list_tts_presets() -> List[str]:
    """列出所有 TTS 语音预设名称"""
    _ensure_tts_dir()
    names = []
    if os.path.exists(PRESETS_TTS_DIR):
        for f in sorted(os.listdir(PRESETS_TTS_DIR)):
            if f.endswith(".json") and not f.startswith("."):
                names.append(os.path.splitext(f)[0])
    return names


def save_tts_preset(config, name: str):
    """把当前 TTS 配置保存为命名预设（会覆盖同名文件）"""
    _ensure_tts_dir()
    config.save_to_file(_tts_preset_path(name))


def load_tts_preset(name: str):
    """按名称加载 TTS 预设，失败返回 None"""
    path = _tts_preset_path(name)
    if not os.path.exists(path):
        return None
    try:
        from config.tts_config import TtsConfig
        return TtsConfig.from_file(path)
    except Exception:
        return None


def delete_tts_preset(name: str) -> bool:
    """删除 TTS 预设，返回是否成功"""
    path = _tts_preset_path(name)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False


def export_tts_preset(config, path: str):
    """把当前 TTS 配置导出为 JSON 文件（任意路径）"""
    config.save_to_file(path)


def import_tts_preset(path: str):
    """从外部 JSON 文件导入 TTS 配置，失败返回 None"""
    if not os.path.exists(path):
        return None
    try:
        from config.tts_config import TtsConfig
        return TtsConfig.from_file(path)
    except Exception:
        return None


# ── 应用设置（日志目录等）────────────────────

APP_SETTINGS_FILE = os.path.join(PRESETS_DIR, ".app_settings.json")


def save_app_settings(settings: dict):
    """保存应用级设置（如日志输出目录）"""
    import json
    _ensure_dir()
    with open(APP_SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings or {}, f, ensure_ascii=False, indent=2)


def load_app_settings() -> dict:
    """加载应用级设置，失败返回空字典"""
    import json
    if os.path.exists(APP_SETTINGS_FILE):
        try:
            with open(APP_SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


# ════════════════════════════════════════════
#  翻译配置（翻译页 / 快捷键 / 屏幕翻译显示）
# ════════════════════════════════════════════

def save_last_translator_config(config):
    """持久化翻译配置（引擎选择 + 各引擎参数），下次启动自动恢复"""
    _ensure_dir()
    config.save_to_file(TRANSLATOR_CONFIG_FILE)


def load_last_translator_config():
    """加载上次保存的翻译配置"""
    if os.path.exists(TRANSLATOR_CONFIG_FILE):
        try:
            from config.translator_config import TranslatorConfig
            return TranslatorConfig.from_file(TRANSLATOR_CONFIG_FILE)
        except Exception:
            pass
    return None


# —— 命名预设 ——

def _ensure_translator_dir():
    os.makedirs(PRESETS_TRANSLATOR_DIR, exist_ok=True)


def _translator_preset_path(name: str) -> str:
    safe = "".join(c for c in name if c.isalnum() or c in "._- ()（）")
    return os.path.join(PRESETS_TRANSLATOR_DIR, f"{safe}.json")


def list_translator_presets() -> list:
    _ensure_translator_dir()
    names = []
    if os.path.exists(PRESETS_TRANSLATOR_DIR):
        for f in sorted(os.listdir(PRESETS_TRANSLATOR_DIR)):
            if f.endswith(".json") and not f.startswith("."):
                names.append(os.path.splitext(f)[0])
    return names


def save_translator_preset(config, name: str):
    _ensure_translator_dir()
    config.save_to_file(_translator_preset_path(name))


def load_translator_preset(name: str):
    path = _translator_preset_path(name)
    if not os.path.exists(path):
        return None
    try:
        from config.translator_config import TranslatorConfig
        return TranslatorConfig.from_file(path)
    except Exception:
        return None


def delete_translator_preset(name: str) -> bool:
    path = _translator_preset_path(name)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False


def export_translator_preset(config, path: str):
    config.save_to_file(path)


def import_translator_preset(path: str):
    if not os.path.exists(path):
        return None
    try:
        from config.translator_config import TranslatorConfig
        return TranslatorConfig.from_file(path)
    except Exception:
        return None


# ════════════════════════════════════════════
#  截图框（OCR 识别区域）配置
# ════════════════════════════════════════════

def save_last_screen_region_config(config):
    """持久化截图框（OCR 识别区域）配置，下次启动自动恢复"""
    _ensure_dir()
    config.save_to_file(SCREEN_REGION_CONFIG_FILE)


def load_last_screen_region_config():
    """加载上次保存的截图框配置"""
    if os.path.exists(SCREEN_REGION_CONFIG_FILE):
        try:
            from config.screen_region_config import ScreenRegionConfig
            return ScreenRegionConfig.from_file(SCREEN_REGION_CONFIG_FILE)
        except Exception:
            pass
    return None


# —— 命名预设 ——

def _ensure_screen_region_dir():
    os.makedirs(PRESETS_SCREEN_REGION_DIR, exist_ok=True)


def _screen_region_preset_path(name: str) -> str:
    safe = "".join(c for c in name if c.isalnum() or c in "._- ()（）")
    return os.path.join(PRESETS_SCREEN_REGION_DIR, f"{safe}.json")


def list_screen_region_presets() -> list:
    _ensure_screen_region_dir()
    names = []
    if os.path.exists(PRESETS_SCREEN_REGION_DIR):
        for f in sorted(os.listdir(PRESETS_SCREEN_REGION_DIR)):
            if f.endswith(".json") and not f.startswith("."):
                names.append(os.path.splitext(f)[0])
    return names


def save_screen_region_preset(config, name: str):
    _ensure_screen_region_dir()
    config.save_to_file(_screen_region_preset_path(name))


def load_screen_region_preset(name: str):
    path = _screen_region_preset_path(name)
    if not os.path.exists(path):
        return None
    try:
        from config.screen_region_config import ScreenRegionConfig
        return ScreenRegionConfig.from_file(path)
    except Exception:
        return None


def delete_screen_region_preset(name: str) -> bool:
    path = _screen_region_preset_path(name)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False


def export_screen_region_preset(config, path: str):
    config.save_to_file(path)


def import_screen_region_preset(path: str):
    if not os.path.exists(path):
        return None
    try:
        from config.screen_region_config import ScreenRegionConfig
        return ScreenRegionConfig.from_file(path)
    except Exception:
        return None


# ── 初始化：首次导入时确保内置预设存在 ──
_ensure_builtin_presets()
