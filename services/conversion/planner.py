"""
octool/services/converter/planner.py
───────────────────────────────────────────────
统一可达性规划：判断 (源 → 目标) 是否可转换 / 可批量 / 可拼接 —— 业务逻辑层

全项目唯一一份「可达性判断」：
  - 直达边（registry）命中 → 可用
  - 否则交给星型自动寻路（star.router）→ 经枢纽中转可用
  - UI 的目标格式可选列表、batch 的 can_batch/can_concat、实际转换
    （pipeline）全部共用这里的结论，杜绝两处推导不一致

"""

from typing import List, Set

from core import formats as FMT
from services.conversion.registry import REGISTRY
from services.conversion.star.router import router as STAR_ROUTER


def _norm(fmt: str) -> str:
    return FMT.resolve(fmt)


def is_reachable(src: str, dst: str) -> bool:
    """(源 → 目标) 是否存在可用路径（直达或星型寻路）"""
    src, dst = _norm(src), _norm(dst)
    if not src or not dst:
        return False
    if REGISTRY.has(src, dst):
        return True
    return STAR_ROUTER.is_reachable(src, dst)


def path_of(src: str, dst: str) -> List[str]:
    """返回寻路结果（直达 = [src, dst]；星型 = 中转序列）；不可达返回 []"""
    src, dst = _norm(src), _norm(dst)
    if not src or not dst:
        return []
    if REGISTRY.has(src, dst):
        return [src, dst]
    return STAR_ROUTER.find_path(src, dst) or []


def reachable_from(src: str) -> Set[str]:
    """从 src 出发可达的全部目标格式（不含自身）"""
    src = _norm(src)
    out = set(STAR_ROUTER.reachable_from(src))
    out.update(d for (s, d) in REGISTRY.edges() if s == src)
    out.discard(src)
    return out


# ── 批量「转换」模式 ──

def can_batch(src: str, dst: str) -> bool:
    """多文件逐个转换是否可用。
    例外：图片 → 文档类应合并为单文件（视为拼接），不允许逐个转换。
    """
    src, dst = _norm(src), _norm(dst)
    if src in set(FMT.media_image_ids()) and dst in set(FMT.doc_ids()):
        return False
    return is_reachable(src, dst)


# ── 拼接「合并为单文件」模式 ──

def can_concat(src: str, dst: str) -> bool:
    """多文件合并为单个目标文件是否可用。
    规则：
      1) 图片 → 文档类：恒可用（每个文件一页/一张）
      2) 自我拼接 src == dst：目标格式需支持合并
      3) 格式转换拼接：目标可合并，且存在（直达或星型）转换路径
    """
    src_raw = str(src or "").strip().lower().lstrip(".")
    dst_raw = str(dst or "").strip().lower().lstrip(".")
    if dst_raw == "pptx-img":
        return False                     # 图片版PPT 不支持拼接合并
    src, dst = _norm(src_raw), _norm(dst_raw)
    if src in set(FMT.media_image_ids()) and dst in set(FMT.doc_ids()):
        return True
    if src == dst:
        return dst in set(FMT.mergeable_ids())
    if dst not in set(FMT.mergeable_ids()):
        return False
    return is_reachable(src, dst)


# ── 目标格式列表（供 UI 二级选择器）──

def reachable_targets(src: str, mode: str = "convert") -> List[str]:
    """按模式返回 src 的全部可用目标格式"""
    src = _norm(src)
    check = can_concat if mode == "concat" else can_batch
    return [f for f in FMT.target_ids()
            if f != src and check(src, f)]
