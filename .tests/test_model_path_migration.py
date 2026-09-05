"""
OCTools/tests/test_model_path_migration.py
───────────────────────────────────────────────
模型路径外部化与历史配置迁移的回归测试。

覆盖三类场景：
  1. 持久化配置里仍是旧目录名（AI_Modles）→ 自动迁移到当前目录；
  2. 用户自定义且真实存在的路径 → 原样保留，不被改写；
  3. 路径彻底不存在 → 回落到当前默认值（配置回到可用状态）。

同时校验：
  - paths.models 配置结构与路径合成（root + 相对子路径）；
  - 源码中不再残留个人机器的盘符路径。

用法：
  python tests/test_model_path_migration.py
退出码 0 = 全部通过；非 0 = 有失败。
"""

import json
import os
import re
import sys

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from config.ui_config import (  # noqa: E402
    CONFIG as C, _MODEL_ROOT, _MODEL_ROOT_LEGACY, migrate_model_path,
)
from config.translator_config import (  # noqa: E402
    TranslatorConfig, HY_DEFAULT_MODEL_PATH, OPUS_MT_BASE,
)
from config.stt_config import SttConfig, STT_DEFAULT_MODEL_DIR  # noqa: E402
from config.tts_config import TtsConfig  # noqa: E402

_PASS = 0
_FAIL = 0

# 旧目录名用 os.sep.join 构造，避免源码里出现裸盘符字面量
_STALE_MODEL = os.path.join("D:" + os.sep, _MODEL_ROOT_LEGACY, "hy_mt",
                            "Hy-MT2-1.8B-Q4_K_M.gguf")
_STALE_OPUS = os.path.join("D:" + os.sep, _MODEL_ROOT_LEGACY, "opusMT")


def check(name, fn):
    global _PASS, _FAIL
    try:
        fn()
        _PASS += 1
        print(f"  OK  {name}")
    except AssertionError as e:
        _FAIL += 1
        print(f"FAIL  {name}: {e}")
    except Exception as e:  # noqa: BLE001 - 回归测试需捕获一切异常
        _FAIL += 1
        print(f"FAIL  {name}: {type(e).__name__}: {e}")


# ── 1. 配置结构 ──────────────────────────────
def test_models_config_structure():
    """paths.models 必须含 root，且各条目为相对子路径。"""
    m = C.section("paths").get("models")
    assert isinstance(m, dict), "paths.models 缺失或不是对象"
    assert m.get("root"), "paths.models.root 缺失"
    for key in ("hy_path", "opus_base", "sensevoice",
                "paddle_cache", "moss", "kokoro"):
        assert key in m, f"paths.models.{key} 缺失"
        assert not os.path.isabs(m[key]), \
            f"paths.models.{key} 应为相对路径，实际为 {m[key]}"


def test_model_path_resolves():
    """model_path() 应把相对子路径拼到 root 之下。"""
    root = C.model_root()
    assert root, "model_root() 为空"
    for key in ("paddle_cache", "moss", "kokoro", "opus_base", "sensevoice"):
        p = C.model_path(key)
        assert p, f"model_path({key}) 为空"
        assert p.startswith(root), f"{p} 未拼在 root({root}) 之下"


def test_all_model_paths_exist():
    """本机模型齐备时，各路径应指向真实存在的位置。

    模型未下载也不应判失败——这里只在 root 存在时才断言。
    """
    if not os.path.isdir(C.model_root()):
        print("       （模型根目录不存在，跳过存在性断言）")
        return
    for key in ("hy_path", "opus_base", "sensevoice",
                "paddle_cache", "moss", "kokoro"):
        p = C.model_path(key)
        assert os.path.exists(p), f"模型路径不存在: {p}"


# ── 2. 历史配置迁移 ───────────────────────────
def test_migrate_stale_legacy_path():
    """持久化配置里的旧目录名应自动迁移到当前目录。"""
    cfg = TranslatorConfig.from_dict({
        "hy_model_path": _STALE_MODEL,
        "opusmt_base": _STALE_OPUS,
    })
    assert _MODEL_ROOT_LEGACY not in cfg.hy_model_path, \
        f"未迁移，仍指向旧目录: {cfg.hy_model_path}"
    assert _MODEL_ROOT_LEGACY not in cfg.opusmt_base, \
        f"未迁移，仍指向旧目录: {cfg.opusmt_base}"
    if os.path.isdir(C.model_root()):
        assert os.path.exists(cfg.hy_model_path), \
            f"迁移后路径不存在: {cfg.hy_model_path}"
        assert cfg.validate() == [], f"validate 仍报错: {cfg.validate()}"


def test_migrate_preserves_valid_custom_path():
    """用户自定义且真实存在的路径必须原样保留。"""
    real = C.model_path("hy_path")
    if not os.path.exists(real):
        print("       （模型文件不存在，跳过）")
        return
    cfg = TranslatorConfig.from_dict({"hy_model_path": real})
    assert cfg.hy_model_path == real, \
        f"自定义路径被改写: {real} -> {cfg.hy_model_path}"


def test_migrate_falls_back_when_missing():
    """路径彻底不存在时回落到当前默认值。"""
    bogus = os.path.join("Z:" + os.sep, "no", "such", "model.gguf")
    cfg = TranslatorConfig.from_dict({"hy_model_path": bogus})
    assert cfg.hy_model_path == HY_DEFAULT_MODEL_PATH, \
        f"未回落到默认值: {cfg.hy_model_path}"


def test_migrate_empty_value():
    """空值应回落到默认值而不是返回空串。"""
    assert migrate_model_path("", HY_DEFAULT_MODEL_PATH) == HY_DEFAULT_MODEL_PATH
    assert migrate_model_path(None, OPUS_MT_BASE) == OPUS_MT_BASE


def test_stt_tts_migration():
    """STT / TTS 配置同样具备迁移能力。"""
    stale_sv = os.path.join("D:" + os.sep, _MODEL_ROOT_LEGACY, "SenseVoiceSmall")
    cfg = SttConfig.from_dict({"model_dir": stale_sv})
    assert _MODEL_ROOT_LEGACY not in cfg.model_dir

    stale_moss = os.path.join("D:" + os.sep, _MODEL_ROOT_LEGACY, "moss")
    tts = TtsConfig.from_dict({"moss_model_dir": stale_moss})
    assert _MODEL_ROOT_LEGACY not in tts.moss_model_dir


# ── 3. 源码卫生 ──────────────────────────────
def test_no_hardcoded_abs_paths_in_source():
    """源码中不得出现个人机器的盘符路径字面量。

    允许例外：
      - os.environ.get(...) 的标准兜底（C:\\Windows / Program Files）；
      - config/ui_config.py 中刻意的旧目录兼容常量。
    """
    pattern = re.compile(r"""['"]([A-Za-z]:[\\/][^'"]*)['"]""")
    skip_dirs = {"dist", "build", ".venv", "__pycache__", ".git"}
    offenders = []

    for base in ("config", "core", "services", "ui"):
        for dirpath, dirnames, filenames in os.walk(
                os.path.join(_PROJECT_ROOT, base)):
            dirnames[:] = [d for d in dirnames if d not in skip_dirs]
            for fn in filenames:
                if not fn.endswith(".py"):
                    continue
                full = os.path.join(dirpath, fn)
                rel = os.path.relpath(full, _PROJECT_ROOT)
                if rel == os.path.join("config", "ui_config.py"):
                    continue  # 旧目录兼容常量刻意保留
                try:
                    with open(full, encoding="utf-8") as f:
                        for i, line in enumerate(f, 1):
                            for m in pattern.finditer(line):
                                val = m.group(1)
                                # 标准安装位置的兜底值不算硬编码
                                if "Program Files" in val or val.startswith("C:\\Windows"):
                                    continue
                                offenders.append(f"{rel}:{i}: {val}")
                except OSError:
                    pass

    assert not offenders, "源码中残留盘符路径:\n    " + "\n    ".join(offenders)


def main() -> int:
    print("[1/3] 配置结构")
    check("paths.models 结构（root + 相对子路径）", test_models_config_structure)
    check("model_path 相对路径合成", test_model_path_resolves)
    check("模型路径指向真实位置", test_all_model_paths_exist)

    print("[2/3] 历史配置迁移")
    check("旧目录名自动迁移", test_migrate_stale_legacy_path)
    check("有效自定义路径不被改写", test_migrate_preserves_valid_custom_path)
    check("失效路径回落默认值", test_migrate_falls_back_when_missing)
    check("空值回落默认值", test_migrate_empty_value)
    check("STT / TTS 同样具备迁移", test_stt_tts_migration)

    print("[3/3] 源码卫生")
    check("源码无残留盘符路径", test_no_hardcoded_abs_paths_in_source)

    print(f"\n结果: {_PASS} 通过, {_FAIL} 失败")
    return 1 if _FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
