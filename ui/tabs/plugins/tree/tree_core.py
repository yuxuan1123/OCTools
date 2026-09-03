"""
OCTools/ui/tabs/plugins/tree/tree_core.py
───────────────────────────────────────────────
目录树生成核心逻辑（纯函数，无 UI 依赖）。

功能：
  - 隐藏文件夹/文件：名称以 '.' 开头的项默认不显示；
  - 文件过滤模式：none（全部显示）/ all（仅目录）/ images（隐藏图片）；
  - 排除扩展名：逗号分隔，如 ".log,.tmp"（自动补点与小写化）；
  - 排除关键词：逗号分隔，名称包含任一关键词即跳过（含目录）；
  - 最大递归深度：max_depth=None 表示不限（语义与原交互脚本一致）。
"""

from pathlib import Path
from typing import List, Literal, Optional, Set

# 常见图片扩展名
IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".bmp",
    ".webp", ".svg", ".ico", ".tiff", ".tif",
    ".heic", ".heif", ".avif",
}

FileFilterMode = Literal["none", "all", "images"]


def is_hidden(path: Path) -> bool:
    """判断路径是否为隐藏项（名称以 '.' 开头）。"""
    return path.name.startswith(".")


def is_image_file(path: Path) -> bool:
    """判断是否为图片文件（基于扩展名）。"""
    return path.suffix.lower() in IMAGE_EXTENSIONS


def parse_exclude_ext(raw: Optional[str]) -> Set[str]:
    """' .log,.tmp,md ' → {'.log', '.tmp', '.md'}（逗号分隔，自动补点与小写）。"""
    exts: Set[str] = set()
    if not raw:
        return exts
    for item in raw.split(","):
        item = item.strip().lower()
        if not item:
            continue
        exts.add(item if item.startswith(".") else "." + item)
    return exts


def parse_keywords(raw: Optional[str]) -> List[str]:
    """'__pycache__, node_modules' → ['__pycache__', 'node_modules']（小写去空格）。"""
    out: List[str] = []
    if not raw:
        return out
    for item in raw.split(","):
        item = item.strip().lower()
        if item:
            out.append(item)
    return out


def _should_skip(entry: Path, show_hidden: bool,
                 file_filter: FileFilterMode,
                 exclude_ext: Set[str],
                 keywords: List[str]) -> bool:
    """返回 True 表示该条目不参与展示（隐藏、排除扩展名/关键词、文件过滤）。"""
    if not show_hidden and is_hidden(entry):
        return True
    name_lower = entry.name.lower()
    for keyword in keywords:
        if keyword in name_lower:
            return True
    if entry.is_dir():
        return False
    if file_filter == "all":
        return True
    if file_filter == "images" and is_image_file(entry):
        return True
    if entry.suffix.lower() in exclude_ext:
        return True
    return False


def build_tree(
    root: Path,
    max_depth: Optional[int] = None,
    show_hidden: bool = False,
    file_filter: FileFilterMode = "none",
    exclude_ext: Optional[Set[str]] = None,
    keywords: Optional[List[str]] = None,
) -> str:
    """递归构建目录树文本。

    参数：
      root          根目录（必须存在且为目录）
      max_depth     最大递归深度；None 表示不限（1 为仅显示直接子项）
      show_hidden   是否显示隐藏项（名称以 '.' 开头）
      file_filter   文件过滤模式：none / all（仅目录）/ images（隐藏图片）
      exclude_ext   排除的扩展名集合（含点，小写）
      keywords      排除关键词列表（名称包含任一关键词即跳过，含目录）
    """
    exclude_ext = exclude_ext or set()
    keywords = keywords or []
    lines: List[str] = [root.name or str(root)]

    def _walk(current: Path, prefix: str, depth: int):
        try:
            entries = sorted(
                current.iterdir(),
                key=lambda p: (not p.is_dir(), p.name.lower()),
            )
        except (OSError, PermissionError):
            lines.append(f"{prefix}⚠ 无法访问 {current.name}")
            return
        entries = [e for e in entries
                   if not _should_skip(e, show_hidden, file_filter,
                                       exclude_ext, keywords)]

        for index, entry in enumerate(entries):
            is_last = index == len(entries) - 1
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{entry.name}")

            if entry.is_dir():
                if max_depth is not None and depth >= max_depth:
                    continue
                child_prefix = prefix + ("    " if is_last else "│   ")
                _walk(entry, child_prefix, depth + 1)

    _walk(root, "", 1)
    return "\n".join(lines)