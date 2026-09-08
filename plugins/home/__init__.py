"""首页包：路径引导 + 统一导出。

顶层包名是 home（不是 mvp.home），因此需要把 home 的**父目录**
（即 .../OCTools/mvp）放进 sys.path，否则 `from home.xxx import` 会失败。

用法：
    sys.path.append("<项目根>/mvp")     # 主程序里加一次即可
    from home import TabHome
    python -m home                       # 独立预览
"""

import sys
from pathlib import Path

# ── 路径引导 ──────────────────────────────
_HERE = Path(__file__).resolve().parent          # .../OCTools/mvp/home
_MVP_ROOT = _HERE.parent                         # .../OCTools/mvp  ← home 包的父目录
_PROJECT_ROOT = _MVP_ROOT.parent                 # .../OCTools      ← config / ui 所在

for _p in (str(_PROJECT_ROOT), str(_MVP_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from home.tab_home import TabHome  # noqa: E402

__all__ = ["TabHome"]
