"""
octool/config/pdf_docx_config.py
───────────────────────────────────────────────
PDF → DOCX 转换方式配置（唯一配置层）

提供两种转换模式（可在设置页选择并持久化）：
  - libreoffice : LibreOffice headless 直转（保留更多版式，默认）；
                  失败时自动回退「文本提取 + python-docx 重建」
  - text        : 直接使用 pdfplumber 提取文本 + python-docx 重建
                  （不依赖 LibreOffice，仅保留文字）
"""

import os
import json
from dataclasses import dataclass
from typing import List

# 转换方式常量
MODE_LIBREOFFICE = "libreoffice"
MODE_TEXT = "text"

MODE_LABELS = {
    MODE_LIBREOFFICE: "LibreOffice 直转（推荐，失败自动回退）",
    MODE_TEXT: "文本提取 + python-docx 重建（仅文字）",
}


@dataclass
class PdfDocxConfig:
    """PDF → DOCX 转换方式配置"""
    method: str = MODE_LIBREOFFICE   # libreoffice / text

    def validate(self) -> List[str]:
        errors = []
        if self.method not in (MODE_LIBREOFFICE, MODE_TEXT):
            errors.append(f"未知转换方式: {self.method}")
        return errors

    # ── 序列化（与 TtsConfig / SttConfig 保持一致接口）──

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items()}

    @classmethod
    def from_dict(cls, d):
        cfg = cls()
        for k, v in (d or {}).items():
            if hasattr(cfg, k):
                try:
                    setattr(cfg, k, v)
                except Exception:
                    pass
        return cfg

    def to_json(self, indent=2):
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    @classmethod
    def from_json(cls, s):
        return cls.from_dict(json.loads(s))

    def save_to_file(self, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_json())

    @classmethod
    def from_file(cls, path):
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return cls.from_json(f.read())
        except Exception:
            return None


def default_config() -> PdfDocxConfig:
    return PdfDocxConfig()
