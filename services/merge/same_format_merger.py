"""
OCTools/services/merge/same_format_merger.py
───────────────────────────────────────────────
同格式合并器（业务逻辑层）—— 全互通架构「同一格式之间合并」

把 N 个同格式文件合并为单个文件：
  - PDF    → pypdf 逐页追加
  - DOCX   → 深拷贝段落/表格 + 图片关系重映射
  - MD/TXT → 纯文本拼接
  - HTML   → 正文拼进单个页面（带分页样式）
  - XLSX   → 每个文件一个工作表
  - CSV    → 表头只保留一次
  - JSON   → 数组合并
  - PPTX   → 幻灯片深拷贝 + 图片关系重映射

设计原则：
  - 统一入口 merge_files(files, dst_fmt, output, log)
  - 单个文件失败不影响其他文件（跳过并计数）

旧逻辑来自 src/batch.py（merge_files + 各 _merge_*），迁移后 src/batch.py 保留为 shim。
"""

import io
import os
import csv
import json
import copy

from core.utils.file_handler import read_text, write_text
from services.merge.base_merger import BaseMerger, MergeError


class SameFormatMerger(BaseMerger):
    """同格式合并器（pdf / docx / md / txt / html / xlsx / csv / json / pptx）"""

    supported_formats = ["pdf", "docx", "md", "txt", "txt-ocr",
                         "html", "xlsx", "csv", "json", "pptx"]

    def merge(self, files, output, log=lambda m: print(m), src_fmt=None):
        """把同格式文件合并为单个文件（dst 由 output 扩展名决定）"""
        return merge_files(files, _dst_of(output), output, log, src_fmt=src_fmt)


def _dst_of(output: str) -> str:
    return os.path.splitext(output)[1].lstrip(".").lower() or ""


# ════════════════════════════════════════════
#  合并分发
# ════════════════════════════════════════════

def merge_files(files, dst_fmt, output, log=lambda m: print(m), src_fmt=None):
    """把同格式文件合并为单个文件（dst_fmt）。"""
    key = "." + dst_fmt.lstrip(".").lower()
    if not files:
        log("❌ 没有可合并的文件")
        return False

    if key == ".gif":
        from services.merge.image_merger import merge_gif_animated
        return merge_gif_animated(files, output, log)
    if key in _MEDIA_MERGE_EXTS:
        from services.merge.media_merger import merge_media
        return merge_media(files, output, log)
    if key in _IMAGE_CONTACT_EXTS:
        from services.merge.image_merger import merge_images_contact
        return merge_images_contact(files, output, log, dst_fmt)

    fn = {
        ".pdf": _merge_pdf,
        ".docx": _merge_docx,
        ".md": _merge_md,
        ".txt": _merge_txt,
        ".txt-ocr": _merge_txt,   # OCR 文本与普通 txt 同样按文本拼接
        ".html": _merge_html,
        ".xlsx": _merge_xlsx,
        ".csv": _merge_csv,
        ".json": _merge_json,
        ".pptx": _merge_pptx,
    }.get(key)
    if fn is None:
        log(f"❌ 暂不支持合并 {dst_fmt.upper()} 文件")
        return False
    return fn(files, output, log)


# 媒体 / 图像常量（避免顶层循环导入）
def _media_merge_exts():
    from core.engines.ffmpeg_utils import VIDEO_FORMATS, AUDIO_FORMATS
    return {f".{x}" for x in VIDEO_FORMATS + AUDIO_FORMATS}


def _image_contact_exts():
    from core import formats as FMT
    return {f".{x}" for x in FMT.media_image_ids() if x not in ("gif", "svg")}


_MEDIA_MERGE_EXTS = _media_merge_exts()
_IMAGE_CONTACT_EXTS = _image_contact_exts()


# ── PDF 合并（pypdf）──────────────────────

def _merge_pdf(files, output, log):
    from pypdf import PdfWriter, PdfReader
    writer = PdfWriter()
    for f in files:
        try:
            reader = PdfReader(f)
            for page in reader.pages:
                writer.add_page(page)
            log(f"   + {os.path.basename(f)}（{len(reader.pages)} 页）")
        except Exception as e:
            log(f"⚠ 跳过 {os.path.basename(f)}: {e}")
    if len(writer.pages) == 0:
        log("❌ 没有任何 PDF 页可合并")
        return False
    os.makedirs(os.path.dirname(os.path.abspath(output)) or ".", exist_ok=True)
    with open(output, "wb") as fh:
        writer.write(fh)
    log(f"✅ 完成 → {output}（共 {len(writer.pages)} 页）")
    return True


# ── DOCX 合并（深拷贝段落/表格，图片关系重映射）──

_R_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


def _merge_docx(files, output, log):
    from docx import Document
    from docx.oxml.ns import qn
    merged = Document()
    merged_body = merged.element.body

    # 用第一个文件的节属性（页面设置）
    try:
        first = Document(files[0])
        sectPr = first.element.body.find(qn("w:sectPr"))
        if sectPr is not None:
            old = merged_body.find(qn("w:sectPr"))
            if old is not None:
                merged_body.remove(old)
            merged_body.append(copy.deepcopy(sectPr))
    except Exception:
        pass

    for f in files:
        try:
            src = Document(f)
        except Exception as e:
            log(f"⚠ 跳过 {os.path.basename(f)}: {e}")
            continue
        src_part = src.part
        rid_map = {}
        # 第一遍：把每个 r:embed / r:link 图片关系映射到合并文档
        for el in src.element.body.iter():
            for attr in (_R_NS + "embed", _R_NS + "link"):
                rid = el.attrib.get(attr)
                if not rid or rid in rid_map:
                    continue
                try:
                    part = src_part.related_parts[rid]
                except KeyError:
                    continue
                if not part.content_type.startswith("image/"):
                    continue
                try:
                    new_rid, _ = merged.part.get_or_add_image(io.BytesIO(part.blob))
                    rid_map[rid] = new_rid
                except Exception:
                    continue
        # 第二遍：深拷贝元素并重映射关系
        sectPr = merged_body.find(qn("w:sectPr"))
        for el in list(src.element.body):
            if el.tag == qn("w:sectPr"):
                continue
            new_el = copy.deepcopy(el)
            for node in new_el.iter():
                for attr in (_R_NS + "embed", _R_NS + "link"):
                    rid = node.attrib.get(attr)
                    if rid and rid in rid_map:
                        node.set(attr, rid_map[rid])
            if sectPr is not None:
                sectPr.addprevious(new_el)
            else:
                merged_body.append(new_el)
        log(f"   + {os.path.basename(f)}")
    os.makedirs(os.path.dirname(os.path.abspath(output)) or ".", exist_ok=True)
    merged.save(output)
    log(f"✅ 完成 → {output}")
    return True


# ── MD / TXT 合并（纯文本拼接）────────────

def _merge_md(files, output, log):
    parts = []
    for f in files:
        try:
            parts.append(read_text(f).rstrip())
        except Exception as e:
            log(f"⚠ 跳过 {os.path.basename(f)}: {e}")
    if not parts:
        return False
    write_text(output, "\n\n---\n\n".join(parts))
    log(f"✅ 完成 → {output}（{len(parts)} 个文档）")
    return True


def _merge_txt(files, output, log):
    parts = []
    for f in files:
        try:
            parts.append(read_text(f).rstrip())
        except Exception as e:
            log(f"⚠ 跳过 {os.path.basename(f)}: {e}")
    if not parts:
        return False
    write_text(output, "\n\n".join(parts))
    log(f"✅ 完成 → {output}（{len(parts)} 个文档）")
    return True


# ── HTML 合并（正文拼进单个页面，带分页样式）──

def _merge_html(files, output, log):
    from bs4 import BeautifulSoup
    sections = []
    for f in files:
        try:
            soup = BeautifulSoup(read_text(f), "html.parser")
            body = soup.body or soup
            sections.append(str(body))
        except Exception as e:
            log(f"⚠ 跳过 {os.path.basename(f)}: {e}")
    if not sections:
        return False
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>合并文档</title>
<style>body{{font-family:sans-serif;max-width:860px;margin:auto;padding:20px;line-height:1.7}}
section.doc{{page-break-after:always;border-bottom:1px solid #eee;padding-bottom:20px;margin-bottom:20px}}
section.doc:last-child{{page-break-after:auto}}</style></head><body>
{''.join(f'<section class="doc">{s}</section>' for s in sections)}
</body></html>"""
    write_text(output, html)
    log(f"✅ 完成 → {output}（{len(sections)} 个文档）")
    return True


# ── XLSX 合并（每个文件一个工作表，保留值）──

def _merge_xlsx(files, output, log):
    import openpyxl
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    used = set()
    for f in files:
        try:
            src = openpyxl.load_workbook(f, data_only=False)
        except Exception as e:
            log(f"⚠ 跳过 {os.path.basename(f)}: {e}")
            continue
        for ws in src.worksheets:
            name = ws.title
            if name in used:
                i = 2
                while f"{name}_{i}" in used:
                    i += 1
                name = f"{name}_{i}"
            used.add(name)
            dest = wb.create_sheet(title=name[:31])
            for row in ws.iter_rows():
                for cell in row:
                    dest[cell.coordinate] = cell.value
        src.close()
        log(f"   + {os.path.basename(f)}")
    if not wb.worksheets:
        wb.create_sheet("Sheet1")
    os.makedirs(os.path.dirname(os.path.abspath(output)) or ".", exist_ok=True)
    wb.save(output)
    log(f"✅ 完成 → {output}")
    return True


# ── CSV 合并（表头只保留一次）──────────────

def _merge_csv(files, output, log):
    header = None
    rows = []
    for f in files:
        try:
            with open(f, "r", encoding="utf-8-sig", newline="") as fh:
                reader = csv.reader(fh)
                first = True
                for r in reader:
                    if first:
                        first = False
                        if header is None:
                            header = r
                        continue
                    rows.append(r)
        except Exception as e:
            log(f"⚠ 跳过 {os.path.basename(f)}: {e}")
            continue
        log(f"   + {os.path.basename(f)}")
    if header is None and not rows:
        return False
    os.makedirs(os.path.dirname(os.path.abspath(output)) or ".", exist_ok=True)
    with open(output, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        if header:
            w.writerow(header)
        w.writerows(rows)
    log(f"✅ 完成 → {output}（{len(rows)} 行数据）")
    return True


# ── JSON 合并（数组合并）──────────────────

def _merge_json(files, output, log):
    merged = []
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception as e:
            log(f"⚠ 跳过 {os.path.basename(f)}: {e}")
            continue
        if isinstance(data, list):
            merged.extend(data)
        elif isinstance(data, dict):
            merged.append(data)
        log(f"   + {os.path.basename(f)}")
    if not merged:
        return False
    os.makedirs(os.path.dirname(os.path.abspath(output)) or ".", exist_ok=True)
    with open(output, "w", encoding="utf-8") as fh:
        json.dump(merged, fh, ensure_ascii=False, indent=2)
    log(f"✅ 完成 → {output}（{len(merged)} 条记录）")
    return True


# ── PPTX 合并（幻灯片深拷贝 + 图片关系重映射）──

def _merge_pptx(files, output, log):
    from pptx import Presentation
    from pptx.oxml.ns import qn
    merged = Presentation()
    try:
        first = Presentation(files[0])
        merged.slide_width = first.slide_width
        merged.slide_height = first.slide_height
    except Exception:
        pass
    blank = merged.slide_layouts[6]
    total = 0
    for f in files:
        try:
            src_prs = Presentation(f)
        except Exception as e:
            log(f"⚠ 跳过 {os.path.basename(f)}: {e}")
            continue
        for slide in src_prs.slides:
            new_slide = merged.slides.add_slide(blank)
            # 清掉空白版式的占位符
            for shp in list(new_slide.shapes):
                shp._element.getparent().remove(shp._element)
            rid_map = {}
            for shp in slide.shapes:
                el = copy.deepcopy(shp._element)
                for node in el.xpath(".//*[@r:embed]"):
                    old = node.get(qn("r:embed"))
                    if old in rid_map:
                        node.set(qn("r:embed"), rid_map[old])
                        continue
                    try:
                        img_part = slide.part.related_parts[old]
                    except KeyError:
                        continue
                    try:
                        _, new_rid = new_slide.part.get_or_add_image_part(
                            io.BytesIO(img_part.blob))
                        rid_map[old] = new_rid
                        node.set(qn("r:embed"), new_rid)
                    except Exception:
                        continue
                new_slide.shapes._spTree.append(el)
            total += 1
        log(f"   + {os.path.basename(f)}")
    os.makedirs(os.path.dirname(os.path.abspath(output)) or ".", exist_ok=True)
    merged.save(output)
    log(f"✅ 完成 → {output}（共 {total} 页）")
    return True
