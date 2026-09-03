"""
octool/services/converter/converter_factory.py
───────────────────────────────────────────────
转换器工厂（业务逻辑层）：自动选择 直接 or 星型 转换

策略（要求.md 前提-3 / 板块一）：
  1) 直达边（REGISTRY）命中 → 直接用对应的转换函数（含 config 装配）
  2) 否则走星型自动寻路（star/router + runner），经枢纽中转
  3) 仍不可达 → 返回 False 并给出明确日志

本工厂是 pipeline.convert 的面向对象封装：
  - build(src, dst) 返回可执行 callable 或 None
  - convert() 直接执行（等价 services.conversion.pipeline.convert）
"""

from typing import Callable, Optional

from core import formats as FMT
from services.conversion.registry import REGISTRY, ConversionSpec
from services.conversion.star.router import router as STAR_ROUTER


class ConverterFactory:
    """自动选择直接 or 星型转换的工厂"""

    @staticmethod
    def find_spec(src: str, dst: str) -> Optional[ConversionSpec]:
        """返回直达边 spec（无直达返回 None）"""
        return REGISTRY.get(src, dst)

    @staticmethod
    def find_path(src: str, dst: str) -> list:
        """返回完整执行路径：直达 [src, dst]；星型中转序列；不可达 []"""
        src, dst = FMT.resolve(src), FMT.resolve(dst)
        if REGISTRY.has(src, dst):
            return [src, dst]
        return STAR_ROUTER.find_path(src, dst) or []

    @classmethod
    def build(cls, src: str, dst: str) -> Optional[Callable]:
        """返回可执行 callable(input, output, log, config) -> bool；不可达返回 None"""
        path = cls.find_path(src, dst)
        if not path:
            return None
        if len(path) == 2:
            spec = REGISTRY.get(src, dst)
            return _DirectCallable(spec)
        return _StarCallable(path)

    @classmethod
    def convert(cls, input_path, output_path, log=lambda m: print(m),
                config=None, target: Optional[str] = None) -> bool:
        """直接执行（等价 pipeline.convert，供无状态调用）"""
        from services.conversion.pipeline import convert as _convert
        return _convert(input_path, output_path, log, config, target)


class _DirectCallable:
    """直达转换 callable"""

    def __init__(self, spec: ConversionSpec):
        self.spec = spec

    def __call__(self, input_path, output_path, log, config=None):
        if self.spec.config_type is None or config is None:
            return self.spec.func(input_path, output_path, log)
        return self.spec.func(input_path, output_path, log,
                              **{self.spec.config_kwarg: config})


class _StarCallable:
    """星型寻路转换 callable"""

    def __init__(self, path: list):
        self.path = path

    def __call__(self, input_path, output_path, log, config=None):
        from services.conversion.star.runner import run_path
        log(f"⭐ 星型自动寻路: {' → '.join(self.path)}")
        return run_path(input_path, output_path, self.path, REGISTRY, log, config)


# ── 默认单例 ──
factory = ConverterFactory()
