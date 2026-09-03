"""
octool/services/converter/pipeline.py
───────────────────────────────────────────────
统一转换入口（业务逻辑层）：直达 → 星型保底自动寻路

转换策略（按优先级）：
  1. 直达：registry 中存在 (源 → 目标) 的转换函数 → 直接执行（按 spec
     自动装配 config：FormatConfig / ImageDocxConfig / TtsConfig / SttConfig）
  2. 星型保底：无直达路径时，用 star.router 自动寻路（BFS 最短路径，
     经星型枢纽 svg/jpg/md/txt-ocr/json/mp4/wav 中转）→ runner 逐跳执行
  3. 失败：给出明确提示

"""

import os
from typing import Callable, Optional

from core import formats as FMT
from core.engines.media_engine import is_media_format
from services.conversion.direct_table import _infer_source_format, _normalize_ext
from services.conversion.registry import REGISTRY, ConversionSpec
from services.conversion.star.router import router as STAR_ROUTER
from services.conversion.star.runner import run_path


def _call_spec(spec: ConversionSpec, input_path: str, output_path: str,
               log: Callable[[str], None], config) -> bool:
    if spec.config_type is None or config is None:
        return spec.func(input_path, output_path, log)
    return spec.func(input_path, output_path, log, **{spec.config_kwarg: config})


def convert(input_path: str, output_path: str,
            log: Callable[[str], None] = lambda m: print(m),
            config=None, target: Optional[str] = None) -> bool:
    """统一转换入口（直达 → 星型保底自动寻路）"""
    if not os.path.exists(input_path):
        log(f"❌ 文件不存在: {input_path}")
        return False

    # ── 源 / 目标格式判定（兼容旧逻辑：文件夹扫描 / target 伪目标）──
    src_ext = _infer_source_format(input_path)
    if not src_ext:
        log(f"❌ 无法识别源文件/文件夹格式: {input_path}")
        return False
    dst_ext = _normalize_ext(output_path)
    if target and target.lower().replace("-", "_") == "txt_ocr":
        dst_ext = ".txt-ocr"
    elif not dst_ext and target:
        dst_ext = "." + target.lstrip(".")
    src, dst = src_ext.lstrip("."), dst_ext.lstrip(".")

    # ── 1) 直达 ──
    spec = REGISTRY.get(src, dst)
    if spec is not None:
        return _call_spec(spec, input_path, output_path, log, config)

    # ── 2) 星型保底：自动寻路 + 逐跳执行 ──
    path = STAR_ROUTER.find_path(src, dst)
    if path:
        log(f"⭐ 无直达路径 {src} → {dst}，星型自动寻路: {' → '.join(path)}")
        return run_path(input_path, output_path, path, REGISTRY, log, config)

    # ── 3) 失败 ──
    if is_media_format(src) and is_media_format(dst):
        log(f"❌ 不支持的媒体转换: {src} → {dst}")
        return False
    log(f"❌ 不支持的转换: {src} → {dst}（无直达路径，星型寻路也未找到）")
    return False
