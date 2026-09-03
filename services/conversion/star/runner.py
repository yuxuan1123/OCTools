"""
OCTools/services/conversion/star/runner.py
───────────────────────────────────────────────
星型路径执行器（保底转换的「手」）—— 业务逻辑层

把 router.find_path 找到的路径 [src, f2, ..., dst] 逐跳执行：
  - 中间跳：输出到临时文件（/ 临时目录），供下一跳读取
  - 最后一跳：直接写到用户指定的 output_path
  - 最后一跳且该边需要配置时，把调用方的 config 传下去（md→docx 的
    FormatConfig、图片→docx 的 ImageDocxConfig 等）；中间跳一律用默认配置

"""

import os
import shutil
import tempfile
from typing import Callable, List, Optional

from services.conversion.registry import Registry, ConversionSpec


def _call_spec(spec: ConversionSpec, input_path: str, output_path: str,
               log: Callable[[str], None], config) -> bool:
    """按 spec 标注的 config 类型调用转换函数"""
    if spec.config_type is None or config is None:
        return spec.func(input_path, output_path, log)
    kwargs = {spec.config_kwarg: config}
    return spec.func(input_path, output_path, log, **kwargs)


def run_path(input_path: str, output_path: str, path: List[str],
             registry: Registry, log: Callable[[str], None],
             config=None) -> bool:
    """执行寻路结果 path（格式 id 序列，path[0]=源格式）

    返回 True/False；中间产物在 finally 中清理。
    """
    if not path or len(path) < 2:
        log(f"❌ 星型路径无效: {path}")
        return False

    tmpdir = tempfile.mkdtemp(prefix="star_route_")
    try:
        cur = input_path
        cur_fmt = path[0]
        for i in range(1, len(path)):
            nxt_fmt = path[i]
            is_last = (i == len(path) - 1)
            out = output_path if is_last else os.path.join(tmpdir, f"hop{i}.{nxt_fmt}")

            spec = registry.get(cur_fmt, nxt_fmt)
            if spec is None:
                log(f"❌ 星型路径断链: {cur_fmt} → {nxt_fmt} 没有直达转换")
                return False
            log(f"   ⭐ 星型跳转 {i}/{len(path) - 1}: {cur_fmt} → {nxt_fmt}")
            ok = _call_spec(spec, cur, out, log,
                            config if is_last else None)
            if not ok or not os.path.exists(out):
                log(f"❌ 星型跳转失败: {cur_fmt} → {nxt_fmt}")
                return False
            cur, cur_fmt = out, nxt_fmt
        log(f"✅ 星型转换完成 → {output_path}")
        return True
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
