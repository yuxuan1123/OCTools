"""统计 ui_config.json 中从未被代码读取的「死键」。

判定方式：把项目内所有 .py 源码拼成语料，逐个检查配置键名是否出现。

排除项（否则会全量假阴性 / 假阳性）：
  - config/ui_config.py —— 其 _FALLBACK 字典含全部键名，不排除则所有键都算「已引用」
  - mvp/ —— 早期原型，不参与主程序运行
  - tools/ —— 本目录的诊断脚本
  - dist/ build/ —— 打包产物（独立代码副本）
  - __pycache__ .git —— 非源码

用法:
  python tools/dead_config_keys.py            # 汇总
  python tools/dead_config_keys.py -v         # 列出全部死键名
"""
import io
import json
import os
import sys

SKIP_DIRS = {".git", "dist", "build", "__pycache__", ".workbuddy-ai",
             ".idea", ".vscode", "node_modules"}
SKIP_PATHS = {
    os.path.join("config", "ui_config.py"),   # 含 _FALLBACK 全键兜底
}
SKIP_TOP_DIRS = {"mvp", "tools"}


def iter_py(root="."):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        rel_dir = os.path.relpath(dirpath, root)
        top = rel_dir.split(os.sep)[0] if rel_dir != "." else ""
        if top in SKIP_TOP_DIRS:
            dirnames[:] = []
            continue
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            rel = os.path.normpath(os.path.join(rel_dir, fn)) if rel_dir != "." else fn
            if rel in SKIP_PATHS:
                continue
            yield os.path.join(dirpath, fn)


def load_corpus():
    parts = []
    for p in iter_py():
        try:
            parts.append(io.open(p, encoding="utf-8", errors="ignore").read())
        except OSError:
            pass
    return "\n".join(parts)


def collect_keys(node, prefix=""):
    """扁平化配置键：返回 [(段, 键名)]，主题 profile 内的键按 colors/sizes 归类。"""
    out = []
    if not isinstance(node, dict):
        return out
    for k, v in node.items():
        if k == "profiles" and prefix.endswith("themes"):
            continue
        if isinstance(v, dict) and k in ("colors", "sizes", "fonts", "text"):
            out.extend(collect_keys(v, k))
        elif not isinstance(v, dict):
            out.append((prefix, k))
    return out


def main():
    verbose = "-v" in sys.argv
    cfg = json.load(io.open("config/ui_config.json", encoding="utf-8"))
    corpus = load_corpus()

    keys = collect_keys(cfg)
    # themes 下的 profile 键单独展开（colors/sizes/fonts 子段）
    themes = cfg.get("themes", {})
    for _pname, prof in themes.get("profiles", {}).items():
        for seg in ("colors", "sizes", "fonts"):
            for k in prof.get(seg, {}):
                keys.append((seg, k))

    by_seg = {}
    dead_all = []
    for seg, k in keys:
        by_seg.setdefault(seg or "(根)", []).append(k)
    for seg, ks in sorted(by_seg.items()):
        ks = sorted(set(ks))
        dead = [k for k in ks if k not in corpus]
        dead_all.extend(dead)
        pct = len(dead) / len(ks) * 100 if ks else 0
        print(f"  {seg:10} {len(dead):3}/{len(ks):3} 死键  ({pct:5.1f}%)")
        if verbose and dead:
            print(f"      {', '.join(dead)}")

    total = len(set((s, k) for s, k in keys))
    print(f"\n  合计 {len(set(dead_all))}/{total} 键未被引用 "
          f"({len(set(dead_all)) / total * 100:.1f}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
