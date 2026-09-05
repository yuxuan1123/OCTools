"""
OCTools/services/ext_plugins/log_store.py
───────────────────────────────────────────────
统一日志：主程序滚动日志 + 安装/崩溃/插件日志文件。

文件布局（logs/ 下）：
  app.log                  主程序滚动日志（10MB × 5）
  install_<plugin_id>.log  依赖安装日志
  crash_<plugin_id>.log    插件崩溃日志
  plugin_<plugin_id>.log   插件自身日志（主进程代写）
"""

import logging
import os
from logging.handlers import RotatingFileHandler

from services.ext_plugins import paths

_app_logger = None


def app_logger() -> logging.Logger:
    """主程序滚动日志器（懒加载单例）。"""
    global _app_logger
    if _app_logger is None:
        paths.ensure_dirs()
        logger = logging.getLogger("octools.ext_plugins")
        logger.setLevel(logging.INFO)
        logger.propagate = False
        if not logger.handlers:
            handler = RotatingFileHandler(
                paths.app_log_file(),
                maxBytes=10 * 1024 * 1024,
                backupCount=5,
                encoding="utf-8",
            )
            handler.setFormatter(logging.Formatter(
                "%(asctime)s [%(levelname)s] %(message)s"))
            logger.addHandler(handler)
        _app_logger = logger
    return _app_logger


def append_line(path: str, text: str):
    """追加一行文本到指定日志文件（UTF-8）。"""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(text.rstrip("\n") + "\n")
    except OSError:
        pass
