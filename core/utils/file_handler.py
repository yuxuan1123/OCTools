"""
octool/core/utils/file_handler.py
───────────────────────────────────────────────
通用文件工具函数（核心引擎层）

被 core/engines 与 services 各层复用：
  - file_exists : 检查文件是否存在（不存在时写入日志）
  - read_text   : 以指定编码读取文本文件
  - write_text  : 写文本文件（自动创建父目录）
  - safe_name   : 去掉目录与扩展名，返回主文件名
  - ensure_outdir : 确保输出文件所在目录存在
"""

import os


def file_exists(path, log):
    """检查文件是否存在，不存在时写入日志并返回 False"""
    if not os.path.exists(path):
        log(f"❌ 文件不存在: {path}")
        return False
    return True


def read_text(path, encoding="utf-8"):
    """以指定编码读取文本文件（忽略无法解码的字符）"""
    with open(path, "r", encoding=encoding, errors="ignore") as f:
        return f.read()


def write_text(path, content, encoding="utf-8"):
    """写文本文件，自动创建父目录"""
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    with open(path, "w", encoding=encoding) as f:
        f.write(content)


def safe_name(path):
    """去掉目录与扩展名，返回主文件名"""
    return os.path.splitext(os.path.basename(path))[0]


def ensure_outdir(output_path):
    """确保输出文件所在目录存在（无操作安全）"""
    d = os.path.dirname(os.path.abspath(output_path))
    if d:
        os.makedirs(d, exist_ok=True)
