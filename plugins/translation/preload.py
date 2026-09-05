"""
OCTools/plugins/translation/preload.py
─────────────────────────────────────────
翻译模型后台预加载编排：提前加载 OCR + 翻译模型，减少首次使用等待。

受 TranslatorConfig 控制：
  - preload_models : 是否启用（False = 不预加载，保持惰性加载）
  - preload_timing : 何时预加载（"startup" = 主程序启动后 / "tab" = 进入翻译页时）

调用方在对应时机调用 `start_preload(config, timing=...)`；内部按配置匹配
时机，匹配才启动后台守护线程加载模型。幂等：进程内只启动一次。
加载失败静默（不抛异常、不影响主程序），模型仍会在首次使用时惰性加载。
"""

import threading

from config.translator_config import TranslatorConfig

_PRELOAD_LOCK = threading.Lock()
_PRELOAD_STARTED = False


def _warmup_ocr():
    """后台加载 PaddleOCR 模型（失败静默）"""
    try:
        from core.engines.ocr_engine import warmup_ocr
        warmup_ocr()
    except Exception:
        pass


def _warmup_translate(cfg: TranslatorConfig):
    """后台加载所选翻译引擎模型（失败静默）"""
    try:
        from core.engines import translation_engine
        translation_engine.warmup(direction="auto", config=cfg)
    except Exception:
        pass


def _preload_worker(cfg: TranslatorConfig):
    """OCR 与翻译模型互不依赖，各自独立线程并行加载"""
    threading.Thread(target=_warmup_ocr, daemon=True).start()
    threading.Thread(target=_warmup_translate, args=(cfg,), daemon=True).start()


def start_preload(config=None, timing: str = "startup") -> bool:
    """按配置启动后台预加载；匹配时机才启动，幂等（进程内只执行一次）。

    参数：
      config : TranslatorConfig；None 时用默认配置
      timing : 本次触发时机（"startup" / "tab"），与 config.preload_timing
               相等才真正启动预加载
    返回 True 表示本次已启动（或已由更早调用启动），False 表示未匹配时机
    或配置关闭了预加载。
    """
    global _PRELOAD_STARTED
    with _PRELOAD_LOCK:
        if _PRELOAD_STARTED:
            return True
    cfg = config if config is not None else TranslatorConfig()
    if not getattr(cfg, "preload_models", True):
        return False
    if (getattr(cfg, "preload_timing", "startup") or "startup") != timing:
        return False
    with _PRELOAD_LOCK:
        if _PRELOAD_STARTED:
            return True
        _PRELOAD_STARTED = True
    threading.Thread(target=_preload_worker, args=(cfg,), daemon=True).start()
    return True
