"""OCTools/tools/fix_header_paths.py — 一次性脚本：把文档头/注释中的旧项目名 OCTools 统一为 OCTools。

用法：
    python tools/fix_header_paths.py            # 预演（只报告，不写盘）
    python tools/fix_header_paths.py --write    # 实际写入

规则：
1. `OCTools/` -> `OCTools/`（文件头相对路径前缀）
2. 其余裸 `OCTools`（窗口标题、注释、临时文件名、包路径）-> `OCTools`
只处理文本类源文件，跳过二进制与 .pyc/.workbuddy-ai/__pycache__。
"""

from __future__ import annotations

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEXT_EXT = {".py", ".md", ".json", ".txt", ".qss", ".toml", ".cfg", ".ini", ".yml", ".yaml"}
SKIP_DIRS = {"__pycache__", ".git", ".workbuddy-ai", "build", "dist", ".idea", ".vscode"}

PAT = re.compile(r"OCTools")


def iter_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if os.path.splitext(fn)[1].lower() in TEXT_EXT:
                yield os.path.join(dirpath, fn)


def main() -> int:
    write = "--write" in sys.argv
    changed_files = 0
    changed_lines = 0

    for path in iter_files():
        try:
            with open(path, "r", encoding="utf-8") as f:
                src = f.read()
        except (UnicodeDecodeError, OSError):
            continue

        new = PAT.sub("OCTools", src)
        if new == src:
            continue

        n = sum(1 for a, b in zip(src.splitlines(), new.splitlines()) if a != b)
        changed_files += 1
        changed_lines += n
        rel = os.path.relpath(path, ROOT).replace("\\", "/")
        print(f"{'[WRITE]' if write else '[DRY]  '} {rel}  ({n} 行)")

        if write:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(new)

    print(f"\n合计：{changed_files} 个文件 / {changed_lines} 行 "
          f"{'已写入' if write else '（预演，未写盘）'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
