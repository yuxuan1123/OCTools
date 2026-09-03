"""
octool/services/merger/base_merger.py
───────────────────────────────────────────────
合并抽象接口（业务逻辑层）

所有合并器实现统一接口：
  - merge(files, output, log) -> bool
  - 支持格式声明（supported_formats）
"""

from abc import ABC, abstractmethod
from typing import Callable, List


class BaseMerger(ABC):
    """所有合并器的抽象基类"""

    #: 支持合并的目标格式 id 列表（如 ["pdf", "docx"]）
    supported_formats: List[str] = []

    @abstractmethod
    def merge(self, files: List[str], output: str,
              log: Callable[[str], None] = lambda m: print(m)) -> bool:
        """把 files 合并为单个 output 文件，返回 True/False"""
        raise NotImplementedError

    def supports(self, dst_fmt: str) -> bool:
        return dst_fmt.lstrip(".").lower() in self.supported_formats


class MergeError(Exception):
    """合并失败异常"""
