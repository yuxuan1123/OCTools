"""
octool/services/merger/picture_in_doc.py
───────────────────────────────────────────────
图片合并进文档（业务逻辑层）：图片以表格形式插入 docx / pdf

跨类合并（要求.md 板块二-2）：
  - 图片 → DOCX：网格表格排版（每行/每列图片数、图片长宽、边框颜色等，
    由 ImageDocxConfig 控制，可保存为命名预设）
  - 图片 → PDF：每张图片一页（img2pdf）

旧逻辑来自 src/_converters_legacy.py（images_to_docx / images_to_pdf），
迁移后保留为兼容 shim。
"""

import os
import tempfile
import shutil

from config.image_docx_config import ImageDocxConfig
from core.engines.document_engine import images_to_docx, images_to_pdf
from services.merge.base_merger import BaseMerger


class PictureInDocMerger(BaseMerger):
    """图片 → 文档（docx / pdf）合并器"""

    supported_formats = ["docx", "pdf"]

    def __init__(self, image_config: ImageDocxConfig = None):
        self.image_config = image_config or ImageDocxConfig()

    def merge(self, files, output, log=lambda m: print(m)):
        dst = os.path.splitext(output)[1].lstrip(".").lower()
        if len(files) == 1:
            if dst == "pdf":
                return images_to_pdf(files[0], output, log)
            if dst == "docx":
                return images_to_docx(files[0], output, log,
                                      image_config=self.image_config)
            log(f"❌ 不支持 图片 → {dst}")
            return False
        # 多文件：合并进一个临时文件夹（图片→文档 天然是「单文件」，一页/一张）
        tmp = tempfile.mkdtemp(prefix="pic_doc_")
        try:
            for f in files:
                shutil.copy2(f, os.path.join(tmp, os.path.basename(f)))
            if dst == "pdf":
                return images_to_pdf(tmp, output, log)
            if dst == "docx":
                return images_to_docx(tmp, output, log,
                                      image_config=self.image_config)
            log(f"❌ 不支持 图片 → {dst}")
            return False
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
