"""
OCTools/config/paths.py
───────────────────────────────────────────────
配置存储路径（最小功能单元）

集中定义 preset 目录、last 配置、图片预设目录等所有路径常量。

打包兼容（PyInstaller）：
  - 源码运行时：ROOT = 项目根目录（OCTools/），配置写进 config/presets/；
  - 打包后（sys.frozen）：sys._MEIPASS 是临时解压目录，退出即被清空，
    因此 ROOT 指向可执行文件所在目录，用户配置持久化到 exe 同目录
    config/presets/，重打包/升级不会丢配置。
"""

import os
import sys


def _compute_root() -> str:
    """项目根目录：源码用 __file__，打包后改用 exe 所在目录（可写、持久）。"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# 项目根目录（打包后为 exe 所在目录）
ROOT = _compute_root()

# 预设目录（config/presets/ 存放 JSON 配置文件）
PRESETS_DIR = os.path.normpath(os.path.join(ROOT, "config", "presets"))

# 持久化键：启动时加载的上次配置
LAST_CONFIG_FILE = os.path.join(PRESETS_DIR, ".last_config.json")
IMAGE_LAST_CONFIG_FILE = os.path.join(PRESETS_DIR, ".last_image_config.json")
TTS_CONFIG_FILE = os.path.join(PRESETS_DIR, ".tts_config.json")
STT_CONFIG_FILE = os.path.join(PRESETS_DIR, ".stt_config.json")
PDF_DOCX_CONFIG_FILE = os.path.join(PRESETS_DIR, ".pdf_docx_config.json")
TRANSLATOR_CONFIG_FILE = os.path.join(PRESETS_DIR, ".translator_config.json")
SCREEN_REGION_CONFIG_FILE = os.path.join(PRESETS_DIR, ".screen_region_config.json")

# 图片 → DOCX 排版预设目录
PRESETS_IMAGE_DIR = os.path.join(PRESETS_DIR, "image")

# TTS 语音预设目录（命名预设，与 last 配置分开存放）
PRESETS_TTS_DIR = os.path.join(PRESETS_DIR, "tts")

# 翻译 / 截图框命名预设目录（与 last 配置分开存放）
PRESETS_TRANSLATOR_DIR = os.path.join(PRESETS_DIR, "translator")
PRESETS_SCREEN_REGION_DIR = os.path.join(PRESETS_DIR, "screen_region")
