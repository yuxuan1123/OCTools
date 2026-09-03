"""
octool/services/converter/cross_category.py
───────────────────────────────────────────────
跨类转换调度（业务逻辑层）

跨类转换 = 源与目标属于不同类别（如 音频→文本、文本→音频、
图片→文档、视频→音频、文档→图片）。自动寻找是否存在可用的跨类路径：

  1) 直达边（CONVERSION_TABLE / REGISTRY）命中 → 直接转换
  2) 否则交给星型寻路（star/router）经枢纽中转

本模块提供跨类路径规划 + 便捷查询，供 converter_factory 与 UI 使用。
"""

from typing import List, Optional

from core import formats as FMT
from services.conversion.registry import REGISTRY
from services.conversion.star.router import router as STAR_ROUTER


def is_cross_category(src: str, dst: str) -> bool:
    """(源, 目标) 是否跨类"""
    sf, df = FMT.family_of(src), FMT.family_of(dst)
    return bool(sf and df and sf != df)


def cross_path(src: str, dst: str) -> List[str]:
    """返回跨类转换路径（直达 [src, dst] 或星型中转序列）；不可达返回 []"""
    src, dst = FMT.resolve(src), FMT.resolve(dst)
    if not is_cross_category(src, dst):
        return []
    if REGISTRY.has(src, dst):
        return [src, dst]
    return STAR_ROUTER.find_path(src, dst) or []


def cross_reachable(src: str, dst: str) -> bool:
    """跨类可达性判断"""
    return bool(cross_path(src, dst))


def cross_targets_from(src: str) -> List[str]:
    """从 src 出发可到达的全部跨类目标格式"""
    src = FMT.resolve(src)
    out = []
    for f in FMT.target_ids():
        if f == src:
            continue
        if is_cross_category(src, f) and cross_reachable(src, f):
            out.append(f)
    return sorted(out)


