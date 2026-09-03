"""OCTools/tools/check_header_paths.py — 校验/修复文件头声明的 OCTools/<相对路径> 是否与真实路径一致。

用法：
    python tools/check_header_paths.py            # 仅报告
    python tools/check_header_paths.py --fix      # 把不一致的声明路径改写成真实路径

输出不一致清单（声明路径 != 实际路径），以及缺失文件头的清单。
"""

from __future__ import annotations

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {"__pycache__", ".git", ".venv", ".workbuddy-ai", "build", "dist",
             ".idea", ".vscode", "node_modules"}

# 支持两种抬头：OCTools/xxx/yyy.py（文件）与 OCTools/xxx/yyy/（子包目录）
HEAD = re.compile(r"^(OCTools/)([A-Za-z0-9_./\-]+\.(?:py)|[A-Za-z0-9_./\-]+/)(\s*)$", re.M)


def iter_py():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn.endswith(".py"):
                yield os.path.join(dirpath, fn)


def main() -> int:
    fix = "--fix" in sys.argv
    mismatch, missing, ok = [], [], 0

    for path in iter_py():
        rel = os.path.relpath(path, ROOT).replace("\\", "/")
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            src = f.read()

        head = "".join(src.splitlines(keepends=True)[:6])
        m = HEAD.search(head)
        if not m:
            missing.append(rel)
            continue
        # 子包抬头允许写成目录形式（OCTools/pkg/sub/）
        real = rel if not rel.endswith("__init__.py") \
            else os.path.dirname(rel).replace("\\", "/") + "/"
        if m.group(2) in (rel, real):
            ok += 1
            continue

        mismatch.append((rel, m.group(2)))
        if fix:
            # 保持原风格：目录形式抬头仍写目录，文件形式仍写文件名
            target = real if m.group(2).endswith("/") else rel
            new_src = src[:m.start()] + m.group(1) + target + m.group(3) + src[m.end():]
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(new_src)

    print(f"一致：{ok} 个文件")
    print(f"\n=== 声明路径 != 实际路径（{len(mismatch)}）===")
    for real, declared in sorted(mismatch):
        print(f"  {real}\n      声明为 -> {declared}")

    if fix and mismatch:
        print(f"\n已修复 {len(mismatch)} 处声明路径。")

    print(f"\n=== 缺失 OCTools/<path> 文件头（{len(missing)}）===")
    for rel in sorted(missing):
        print(f"  {rel}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
