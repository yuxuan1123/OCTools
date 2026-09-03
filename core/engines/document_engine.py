"""
OCTools/core/engines/document_engine.py
───────────────────────────────────────────────
文档引擎（核心引擎层）：文本类文档处理（md / docx / pdf / txt / 图片→文档）

覆盖：
  - Markdown：→ docx / pdf / txt / images / html(演示类见 presentation_engine)
  - DOCX：→ md / pdf / txt / images
  - PDF：→ md / docx / txt / images
  - TXT：→ md / docx / pdf / images
  - 图片 → 文档：pdf / docx / md / txt / txt-ocr(OCR)
  - OCR 兜底：pdf → txt-ocr（扫描版逐页识别）

设计原则（与旧 src/converters.py 一致）：
  - 每个转换函数签名统一为 (input_path, output_path, log) -> bool
  - log 是 callable(msg)，线程安全由调用方保证
  - 优先 pandoc（格式覆盖广），其余走专用库（python-docx / pypdf / pdfplumber /
    reportlab / PIL / img2pdf / PaddleOCR）

"""

import os
import glob
import base64
import shutil
import tempfile
import subprocess

import pypandoc
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ROW_HEIGHT_RULE
from docx.oxml.ns import qn
from docx.oxml.shared import OxmlElement
import markdown as md_lib
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw
import img2pdf
from pypdf import PdfWriter, PdfReader
import pdfplumber
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from config.image_docx_config import ImageDocxConfig
from core.utils.file_handler import file_exists, read_text, write_text, safe_name


# ════════════════════════════════════════════
#  公共工具
# ════════════════════════════════════════════

def _ensure_pandoc(log):
    """确保 pandoc 可用，返回其路径"""
    try:
        return pypandoc.get_pandoc_path()
    except OSError:
        log("⏳ 未检测到 pandoc，正在下载（约 50MB）…")
        pypandoc.download_pandoc()
        return pypandoc.get_pandoc_path()


# ── CJK 字体注册（解决 PDF 中文乱码） ──────
_CJK_FONT_NAME = None  # 缓存已注册的 CJK 字体名


def _register_cjk_font():
    """Windows 专用：强制使用系统自带中文字体"""
    global _CJK_FONT_NAME
    if _CJK_FONT_NAME is not None:
        return _CJK_FONT_NAME

    # Windows 字体目录
    win_fonts = os.environ.get("WINDIR", r"C:\Windows") + r"\Fonts"

    font_map = {
        "simsun": os.path.join(win_fonts, "simsun.ttc"),      # 宋体 ✅
        "msyh": os.path.join(win_fonts, "msyh.ttc"),          # 微软雅黑 ✅
        "simhei": os.path.join(win_fonts, "simhei.ttf"),      # 黑体
        "simkai": os.path.join(win_fonts, "simkai.ttf"),      # 楷体
    }

    for name, path in font_map.items():
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(name, path))
                _CJK_FONT_NAME = name
                return name
            except Exception as e:
                # 不吞异常，方便调试
                print(f"[WARN] 注册字体失败 {path}: {e}")

    # 实在不行，直接报错，避免生成乱码 PDF
    raise RuntimeError(
        "❌ 未找到 Windows 中文字体，无法生成 PDF。"
        "请确认 C:\\Windows\\Fonts 下有 simsun.ttc 或 msyh.ttc"
    )


def _make_cjk_styles(font_name):
    """基于 CJK 字体创建 reportlab 样式表"""
    from reportlab.lib.styles import ParagraphStyle as _PS
    styles = getSampleStyleSheet()
    for key in list(styles.byName.keys()):
        base = styles.byName[key]
        # 只处理 ParagraphStyle，跳过 ListStyle、TableStyle 等
        if isinstance(base, _PS):
            # 拷贝关键属性，避免 ListStyle 缺少 leading 等问题
            style_kwargs = dict(
                name=f"{key}_CJK",
                parent=base,
                fontName=font_name,
            )
            try:
                if hasattr(base, 'leading') and base.leading:
                    style_kwargs['leading'] = base.leading * 1.3
                if hasattr(base, 'fontSize') and base.fontSize:
                    style_kwargs['fontSize'] = base.fontSize
            except Exception:
                pass
            styles.add(ParagraphStyle(**style_kwargs))
    return styles


# ════════════════════════════════════════════
#  A. Markdown 相关
# ════════════════════════════════════════════

def md_to_docx(input_path, output_path, log, config=None):
    """MD → DOCX（支持高级格式控制）

    参数:
      config: FormatConfig 或 None。为 None 时使用 pandoc 快速转换；
              传入 FormatConfig 时使用高级引擎，支持完整的格式控制。
    """
    if not file_exists(input_path, log): return False
    try:
        # 如果提供了配置，使用高级引擎
        if config is not None:
            from core.engines.md_docx_engine import MdToDocxEngine
            engine = MdToDocxEngine(config)
            return engine.convert(input_path, output_path, log)

        # 否则走原有 pandoc 快速通道
        _ensure_pandoc(log)
        log(f"🔄 MD → DOCX: {input_path}")
        pypandoc.convert_file(input_path, "docx", outputfile=output_path,
                              extra_args=["--standalone"])
        log(f"✅ 完成 → {output_path}")
        return True
    except Exception as e:
        log(f"❌ {e}"); return False


def md_to_pdf(input_path, output_path, log):
    """MD → PDF（优先 pandoc 直出，无 PDF 引擎时走 HTML+reportlab + CJK 字体）"""
    if not file_exists(input_path, log): return False
    try:
        _ensure_pandoc(log)
        log(f"🔄 MD → PDF: {input_path}")
        # 优先 pandoc 直出 pdf（需要 xelatex / wkhtmltopdf / weasyprint 等 PDF 引擎）
        try:
            pypandoc.convert_file(input_path, "pdf", outputfile=output_path,
                                  extra_args=["--standalone"])
        except RuntimeError:
            # pandoc 缺 pdf 引擎时走 html 中转 → reportlab（已适配 CJK 字体）
            log("⚠ pandoc 无 PDF 引擎（可安装 wkhtmltopdf 或 MiKTeX 获得更好效果），"
                "改用 HTML→PDF 路径")
            cjk_font = _register_cjk_font()
            if cjk_font:
                log(f"   已加载中文字体: {cjk_font}")
            tmp_html = output_path + ".tmp.html"
            pypandoc.convert_file(input_path, "html", outputfile=tmp_html,
                                  extra_args=["--standalone"])
            html_to_pdf_via_reportlab(tmp_html, output_path, log)
            os.remove(tmp_html)
        log(f"✅ 完成 → {output_path}")
        return True
    except Exception as e:
        log(f"❌ {e}"); return False


def md_to_txt(input_path, output_path, log):
    """MD → TXT（剥掉标记，只留纯文本）"""
    if not file_exists(input_path, log): return False
    try:
        log(f"🔄 MD → TXT: {input_path}")
        text = md_lib.markdown(read_text(input_path))
        soup = BeautifulSoup(text, "html.parser")
        write_text(output_path, soup.get_text(separator="\n"))
        log(f"✅ 完成 → {output_path}")
        return True
    except Exception as e:
        log(f"❌ {e}"); return False


def md_to_images(input_path, output_path, log):
    """MD → 图片（先转 HTML，再用浏览器截图；playwright 不可用时退回 reportlab 渲染）"""
    if not file_exists(input_path, log): return False
    try:
        log(f"🔄 MD → 图片: {input_path}")
        # 用 markdown 库渲染为 HTML
        html_body = md_lib.markdown(read_text(input_path), extensions=["extra", "codehilite"])
        styled = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
body{{font-family:Helvetica,Arial,sans-serif;max-width:800px;margin:20px auto;padding:20px;line-height:1.7;color:#222}}
h1,h2,h3{{color:#1a1a1a}}code{{background:#f4f4f4;padding:2px 5px;border-radius:3px}}
pre{{background:#f4f4f4;padding:12px;border-radius:5px;overflow:auto}}img{{max-width:100%}}
</style></head><body>{html_body}</body></html>"""
        tmp_html = output_path + ".tmp.html"
        write_text(tmp_html, styled)
        ok = _html_to_images_playwright(tmp_html, output_path, log)
        if not ok:
            log("⚠ Playwright 不可用，改用 reportlab 渲染单图")
            html_to_pdf_via_reportlab(tmp_html, output_path.replace(".png", ".pdf"), log)
        os.remove(tmp_html)
        log(f"✅ 完成 → {output_path}")
        return True
    except Exception as e:
        log(f"❌ {e}"); return False


# ════════════════════════════════════════════
#  B. DOCX 相关
# ════════════════════════════════════════════

def docx_to_md(input_path, output_path, log):
    """DOCX → MD（pandoc GFM）"""
    if not file_exists(input_path, log): return False
    try:
        _ensure_pandoc(log)
        log(f"🔄 DOCX → MD: {input_path}")
        pypandoc.convert_file(input_path, "gfm", outputfile=output_path,
                              extra_args=["--wrap=none", "--columns=1000"])
        log(f"✅ 完成 → {output_path}")
        return True
    except Exception as e:
        log(f"❌ {e}"); return False


def docx_to_pdf(input_path, output_path, log):
    """DOCX → PDF（优先 docx2pdf/LibreOffice，均失败时退回 reportlab 重建）"""
    if not file_exists(input_path, log): return False
    try:
        log(f"🔄 DOCX → PDF: {input_path}")
        # 方法1: docx2pdf（Windows + MS Word）
        try:
            from docx2pdf import convert as d2p
            d2p(input_path, output_path)
            log(f"✅ 完成(docx2pdf) → {output_path}")
            return True
        except Exception as e1:
            log(f"⚠ docx2pdf 失败({e1})，尝试 LibreOffice…")
        # 方法2: LibreOffice headless
        if _libreoffice_convert(input_path, output_path, "pdf", log):
            return True
        # 方法3: 用 reportlab 重建（丢格式但可保留文字）
        log("⚠ 用 reportlab 重建 PDF（仅保留文本）")
        _docx_to_pdf_reportlab(input_path, output_path, log)
        log(f"✅ 完成(reportlab) → {output_path}")
        return True
    except Exception as e:
        log(f"❌ {e}"); return False


def docx_to_txt(input_path, output_path, log):
    """DOCX → TXT（python-docx 提取段落文本）"""
    if not file_exists(input_path, log): return False
    try:
        log(f"🔄 DOCX → TXT: {input_path}")
        doc = Document(input_path)
        lines = []
        for p in doc.paragraphs:
            lines.append(p.text)
        # 也提取表格
        for table in doc.tables:
            for row in table.rows:
                lines.append("\t".join(cell.text for cell in row.cells))
        write_text(output_path, "\n".join(lines))
        log(f"✅ 完成 → {output_path}")
        return True
    except Exception as e:
        log(f"❌ {e}"); return False


def docx_to_images(input_path, output_path, log):
    """DOCX → 图片（docx → pdf → png）"""
    if not file_exists(input_path, log): return False
    try:
        log(f"🔄 DOCX → 图片: {input_path}")
        tmp_pdf = output_path + ".tmp.pdf"
        if not docx_to_pdf(input_path, tmp_pdf, log):
            return False
        pdf_to_images(tmp_pdf, output_path, log)
        os.remove(tmp_pdf)
        log(f"✅ 完成 → {output_path}")
        return True
    except Exception as e:
        log(f"❌ {e}"); return False


# ════════════════════════════════════════════
#  C. PDF 相关
# ════════════════════════════════════════════

def pdf_to_md(input_path, output_path, log):
    """PDF → MD（pdfplumber 提取文本 + pandoc 结构化）"""
    if not file_exists(input_path, log): return False
    try:
        log(f"🔄 PDF → MD: {input_path}")
        text = _pdf_extract_text(input_path, log)
        # 简单启发式：把缩进段落转成列表/标题
        md_lines = _pdf_text_to_md(text)
        write_text(output_path, "\n".join(md_lines))
        log(f"✅ 完成 → {output_path}")
        return True
    except Exception as e:
        log(f"❌ {e}"); return False


def pdf_to_docx(input_path, output_path, log, config=None):
    """PDF → DOCX。

    转换方式由 config（PdfDocxConfig）决定：
      - method == "text"  ：直接 pdfplumber 提取文本 + python-docx 重建（仅文字）
      - method == "libreoffice"（默认）：LibreOffice headless 直转（保留版式），
        失败自动回退「文本提取 + python-docx 重建」
    config 为 None 时按默认（libreoffice）处理。
    """
    if not file_exists(input_path, log): return False
    try:
        method = getattr(config, "method", "libreoffice") if config else "libreoffice"
        log(f"🔄 PDF → DOCX: {input_path}")

        # ── 方式一：LibreOffice headless 直转（保留更多版式）──
        if method == "libreoffice":
            if _libreoffice_convert(input_path, output_path, "docx", log):
                log(f"✅ 完成(LibreOffice) → {output_path}")
                return True
            log("⚠ LibreOffice 不可用，改用文本提取方式")

        # ── 方式二（或兜底）：pdfplumber 提取文本 → python-docx 重建 ──
        text = _pdf_extract_text(input_path, log)
        if not text.strip():
            log("❌ PDF 未能提取到任何文本（可能为扫描版，请使用 OCR 路径）")
            return False
        os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)
        doc = Document()
        for line in text.splitlines():
            doc.add_paragraph(line)
        doc.save(output_path)
        log(f"✅ 完成(文本提取) → {output_path}")
        return True
    except Exception as e:
        log(f"❌ {e}"); return False


def pdf_to_txt(input_path, output_path, log):
    """PDF → TXT（pdfplumber 高质量提取）"""
    if not file_exists(input_path, log): return False
    try:
        log(f"🔄 PDF → TXT: {input_path}")
        text = _pdf_extract_text(input_path, log)
        write_text(output_path, text)
        log(f"✅ 完成 → {output_path}")
        return True
    except Exception as e:
        log(f"❌ {e}"); return False


def _resolve_image_output(output_path: str, fmt: str):
    """
    解析“文档 → 图片”的输出目标。

    返回 (输出目录, 单文件路径或 None)：
      - output_path 无扩展名 / 以分隔符结尾 / 已是目录 → 视为文件夹，直接使用；
      - output_path 是图片文件（如 xxx.jpg）→ 目录为 <xxx>_图片/，
        单页时直接把图片写到该文件，多页时按页存进目录。
    """
    ext = os.path.splitext(output_path)[1].lower()
    is_folder = (not ext) or output_path.endswith(("/", "\\")) or os.path.isdir(output_path)
    if is_folder:
        return output_path, None
    folder = os.path.splitext(output_path)[0] + "_图片"
    return folder, output_path


def _render_pdf_pages(pdf_path: str, out_dir: str, fmt: str, log, base: str = "page"):
    """把 PDF 每页渲染为图片文件，返回生成的文件列表（fmt: png / jpg）"""
    generated = []
    # 方式1: pypdfium2（纯 Python，无需外部二进制，优先）
    try:
        import pypdfium2 as pdfium
        pdf = pdfium.PdfDocument(pdf_path)
        try:
            n_pages = len(pdf)
            for i in range(n_pages):
                bitmap = pdf[i].render(scale=200 / 72.0)  # 200 DPI
                pil = bitmap.to_pil()
                p = os.path.join(out_dir, f"{base}_{i + 1:03d}.{fmt}")
                if fmt == "jpg":
                    pil.convert("RGB").save(p, "JPEG", quality=90)
                else:
                    pil.save(p, "PNG")
                generated.append(p)
        finally:
            pdf.close()
    except Exception as e:
        log(f"⚠ pypdfium2 渲染失败: {e}")
        generated = []
    if not generated:
        try:
            # 方式2: pdftoppm（生成 base-1.fmt、base-2.fmt …）
            flag = "-jpeg" if fmt == "jpg" else "-png"
            subprocess.run(
                ["pdftoppm", "-r", "200", flag, pdf_path, os.path.join(out_dir, base)],
                check=True, capture_output=True, timeout=180
            )
            generated = sorted(glob.glob(os.path.join(out_dir, base + "-*." + fmt)))
        except Exception:
            generated = []
    if not generated:
        # 方式3: pdf2image 兜底
        try:
            from pdf2image import convert_from_path
            imgs = convert_from_path(pdf_path, dpi=200)
            for i, im in enumerate(imgs, 1):
                p = os.path.join(out_dir, f"{base}_{i:03d}.{fmt}")
                if fmt == "jpg":
                    im.convert("RGB").save(p, "JPEG", quality=90)
                else:
                    im.save(p, "PNG")
                generated.append(p)
        except Exception as e:
            log(f"⚠ 渲染 PDF 页面失败: {e}")
            return []
    return generated


def _pdf_to_images(input_path, output_path, log, fmt: str):
    """PDF → 图片（每页一张，多页时输出到文件夹）"""
    if not file_exists(input_path, log): return False
    try:
        log(f"🔄 PDF → {fmt.upper()}: {input_path}")
        out_dir, single_file = _resolve_image_output(output_path, fmt)
        os.makedirs(out_dir, exist_ok=True)
        generated = _render_pdf_pages(input_path, out_dir, fmt, log)
        if not generated:
            log("❌ 未能渲染任何页面")
            return False
        if single_file and len(generated) == 1:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)
            shutil.move(generated[0], output_path)
            log(f"✅ 完成 → {output_path}")
        else:
            log(f"📁 共 {len(generated)} 页，已按页输出到文件夹: {out_dir}")
        return True
    except Exception as e:
        log(f"❌ {e}"); return False


def pdf_to_images(input_path, output_path, log):
    """PDF → PNG 图片（每页一张；多页 → 文件夹）"""
    return _pdf_to_images(input_path, output_path, log, "png")


def pdf_to_jpgs(input_path, output_path, log):
    """PDF → JPG 图片（每页一张；多页 → 文件夹）"""
    return _pdf_to_images(input_path, output_path, log, "jpg")


def docx_to_jpgs(input_path, output_path, log):
    """DOCX → JPG（先转 PDF，再按页输出到图片文件夹）"""
    if not file_exists(input_path, log): return False
    try:
        log(f"🔄 DOCX → JPG: {input_path}")
        tmp_pdf = output_path + ".tmp.pdf"
        if not docx_to_pdf(input_path, tmp_pdf, log):
            return False
        try:
            return pdf_to_jpgs(tmp_pdf, output_path, log)
        finally:
            if os.path.exists(tmp_pdf):
                os.remove(tmp_pdf)
    except Exception as e:
        log(f"❌ {e}"); return False


# ════════════════════════════════════════════
#  D. TXT 相关
# ════════════════════════════════════════════

def txt_to_md(input_path, output_path, log):
    """TXT → MD（保留段落，空行分段）"""
    if not file_exists(input_path, log): return False
    try:
        log(f"🔄 TXT → MD: {input_path}")
        text = read_text(input_path)
        # 用空行分段，每段包成普通段落
        paras = [p.strip() for p in text.split("\n\n") if p.strip()]
        md = "\n\n".join(paras)
        write_text(output_path, md)
        log(f"✅ 完成 → {output_path}")
        return True
    except Exception as e:
        log(f"❌ {e}"); return False


def txt_to_docx(input_path, output_path, log):
    """TXT → DOCX（reportlab 太重，这里用 python-docx 直接写）"""
    if not file_exists(input_path, log): return False
    try:
        log(f"🔄 TXT → DOCX: {input_path}")
        text = read_text(input_path)
        doc = Document()
        style = doc.styles['Normal']
        style.font.name = 'Arial'
        style.font.size = Pt(11)
        for line in text.splitlines():
            doc.add_paragraph(line)
        doc.save(output_path)
        log(f"✅ 完成 → {output_path}")
        return True
    except Exception as e:
        log(f"❌ {e}"); return False


def txt_to_pdf(input_path, output_path, log):
    """TXT → PDF（reportlab，自动适配 CJK 字体）"""
    if not file_exists(input_path, log): return False
    try:
        log(f"🔄 TXT → PDF: {input_path}")
        text = read_text(input_path)
        doc = SimpleDocTemplate(output_path, pagesize=A4,
                                leftMargin=20*mm, rightMargin=20*mm)
        cjk_font = _register_cjk_font()
        if cjk_font:
            styles = _make_cjk_styles(cjk_font)
            normal_style = styles["Normal_CJK"]
        else:
            styles = getSampleStyleSheet()
            normal_style = styles["Normal"]
        story = []
        for line in text.splitlines():
            story.append(Paragraph(line or "&nbsp;", normal_style))
        doc.build(story)
        log(f"✅ 完成 → {output_path}")
        return True
    except Exception as e:
        log(f"❌ {e}"); return False


def txt_to_images(input_path, output_path, log):
    """TXT → 图片（PIL 渲染文本到 PNG）"""
    if not file_exists(input_path, log): return False
    try:
        log(f"🔄 TXT → 图片: {input_path}")
        from PIL import ImageFont, ImageDraw
        text = read_text(input_path)
        lines = text.splitlines() or [""]
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        except (OSError, IOError):
            font = ImageFont.load_default()
        # 计算尺寸
        max_w = max(font.getbbox(l)[2] - font.getbbox(l)[0] for l in lines) + 40
        line_h = (font.getbbox("Hg")[3] - font.getbbox("Hg")[1]) + 6
        h = line_h * len(lines) + 40
        img = Image.new("RGB", (max(max_w, 400), max(h, 100)), "white")
        draw = ImageDraw.Draw(img)
        y = 20
        for line in lines:
            draw.text((20, y), line, fill="black", font=font)
            y += line_h
        ext = os.path.splitext(output_path)[1].lower()
        if ext in (".jpg", ".jpeg"):
            img.save(output_path, "JPEG", quality=90)
        else:
            img.save(output_path, "PNG")
        log(f"✅ 完成 → {output_path}")
        return True
    except Exception as e:
        log(f"❌ {e}"); return False


# ════════════════════════════════════════════
#  E. 图片相关（→ 文档类）
# ════════════════════════════════════════════

def images_to_pdf(input_path, output_path, log):
    """图片 → PDF（img2pdf，支持单张或多张合并）"""
    if not file_exists(input_path, log): return False
    try:
        log(f"🔄 图片 → PDF: {input_path}")
        # 判断是单文件还是目录
        if os.path.isdir(input_path):
            imgs = sorted(glob.glob(os.path.join(input_path, "*.*")))
            imgs = [f for f in imgs if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".gif", ".webp", ".svg"))]
        else:
            imgs = [input_path]
        if not imgs:
            log("❌ 未找到图片文件"); return False
        # 统一转成 PNG 再合并
        png_list = []
        for im in imgs:
            ext = os.path.splitext(im)[1].lower()
            p = im + ".tmp.png"
            if ext == ".svg":
                from core.engines.image_engine import svg_to_png
                if not svg_to_png(im, p, log):
                    log(f"⚠ 无法渲染 SVG，跳过 {os.path.basename(im)}")
                    continue
            else:
                img = Image.open(im).convert("RGB")
                img.save(p, "PNG")
            png_list.append(p)
        if not png_list:
            log("❌ 没有可用的图片文件"); return False
        with open(output_path, "wb") as f:
            f.write(img2pdf.convert(png_list))
        for p in png_list: os.remove(p)
        log(f"✅ 完成 → {output_path}（{len(imgs)} 张图片）")
        return True
    except Exception as e:
        log(f"❌ {e}"); return False


def images_to_md(input_path, output_path, log):
    """图片 → MD（OCR 不可用，退而求其次：把图片以 base64 嵌入 markdown）"""
    if not file_exists(input_path, log): return False
    try:
        log(f"🔄 图片 → MD: {input_path}")
        if os.path.isdir(input_path):
            files = sorted(glob.glob(os.path.join(input_path, "*.*")))
            files = [f for f in files if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp", ".svg"))]
        else:
            files = [input_path]
        md_parts = []
        for f in files:
            ext = os.path.splitext(f)[1].lower().strip(".")
            if ext == "svg":
                mime = "image/svg+xml"
            else:
                mime = f"image/{'jpeg' if ext in ('jpg','jpeg') else ext}"
            with open(f, "rb") as fh:
                b64 = base64.b64encode(fh.read()).decode()
            md_parts.append(f"![{os.path.basename(f)}](data:{mime};base64,{b64})")
        write_text(output_path, "\n\n".join(md_parts))
        log(f"✅ 完成 → {output_path}（{len(files)} 张图以 base64 嵌入）")
        return True
    except Exception as e:
        log(f"❌ {e}"); return False


def images_to_txt(input_path, output_path, log):
    """图片 → TXT（无 OCR 时输出图片信息清单）"""
    if not file_exists(input_path, log): return False
    try:
        log(f"🔄 图片 → TXT: {input_path}")
        if os.path.isdir(input_path):
            files = sorted(glob.glob(os.path.join(input_path, "*.*")))
            files = [f for f in files if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp", ".svg"))]
        else:
            files = [input_path]
        lines = [f"图片清单（共 {len(files)} 张）", "=" * 40]
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            try:
                if ext == ".svg":
                    from core.engines.image_engine import svg_to_png
                    tmp = f + ".tmp.png"
                    if not svg_to_png(f, tmp, log):
                        continue
                    try:
                        with Image.open(tmp) as img:
                            lines.append(f"{os.path.basename(f)}: {img.size[0]}x{img.size[1]} {img.mode}")
                    finally:
                        if os.path.exists(tmp):
                            os.remove(tmp)
                else:
                    with Image.open(f) as img:
                        lines.append(f"{os.path.basename(f)}: {img.size[0]}x{img.size[1]} {img.mode}")
            except Exception as e:
                log(f"⚠ 无法读取图片，跳过 {os.path.basename(f)}: {e}")
        write_text(output_path, "\n".join(lines))
        log(f"✅ 完成 → {output_path}")
        return True
    except Exception as e:
        log(f"❌ {e}"); return False


def _apply_table_border_color(table, color_hex: str):
    """为 python-docx 表格设置统一边框颜色（#RRGGBB）"""
    tbl = table._tbl
    tblPr = tbl.tblPr
    if tblPr is None:
        tblPr = OxmlElement('w:tblPr')
        tbl.insert(0, tblPr)
    borders = OxmlElement('w:tblBorders')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        e = OxmlElement(f'w:{edge}')
        e.set(qn('w:val'), 'single')
        e.set(qn('w:sz'), '4')
        e.set(qn('w:space'), '0')
        e.set(qn('w:color'), color_hex.lstrip('#'))
        borders.append(e)
    existing = tblPr.find(qn('w:tblBorders'))
    if existing is not None:
        tblPr.replace(existing, borders)
    else:
        tblPr.append(borders)


def images_to_docx(input_path, output_path, log, image_config=None):
    """图片 → DOCX（网格排版：每行/每列图片数、图片长宽、是否显示文件名等可配置）"""
    if not file_exists(input_path, log): return False
    if image_config is None:
        image_config = ImageDocxConfig()
    tmp_pngs = []  # 转 PNG 的临时文件（webp/heic 等 python-docx 不支持的格式）
    try:
        log(f"🔄 图片 → DOCX: {input_path}")
        # 收集图片：单文件或目录
        if os.path.isdir(input_path):
            files = sorted(glob.glob(os.path.join(input_path, "*.*")))
            files = [f for f in files if f.lower().endswith(
                (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp", ".tiff", ".heic", ".svg"))]
        else:
            files = [input_path]
        if not files:
            log("❌ 未找到图片文件"); return False

        # python-docx 不识别 webp / heic / svg 等格式，先统一转为 PNG 临时文件再插入
        _DOCX_SAFE_EXTS = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff", ".tif")
        work_files, labels = [], []
        for f in files:
            labels.append(os.path.basename(f))
            ext = os.path.splitext(f)[1].lower()
            if ext in _DOCX_SAFE_EXTS:
                work_files.append(f)
            elif ext == ".svg":
                tmp = f + ".tmp.png"
                from core.engines.image_engine import svg_to_png
                if svg_to_png(f, tmp, log):
                    work_files.append(tmp)
                    tmp_pngs.append(tmp)
                else:
                    log(f"⚠ 无法渲染 SVG，跳过 {os.path.basename(f)}")
            else:
                tmp = f + ".tmp.png"
                try:
                    with Image.open(f) as im:
                        im.convert("RGB" if im.mode not in ("RGB", "RGBA") else im.mode).save(tmp, "PNG")
                    work_files.append(tmp)
                    tmp_pngs.append(tmp)
                except Exception as e:
                    log(f"⚠ 无法读取图片，跳过 {os.path.basename(f)}: {e}")
        if not work_files:
            log("❌ 没有可用的图片文件"); return False
        files = work_files

        rows = max(1, int(image_config.images_per_column))
        cols = max(1, int(image_config.images_per_row))
        # A4 页面，2cm 边距
        PAGE_W_CM, PAGE_H_CM = 21.0, 29.7
        MARGIN_CM = 2.0
        usable_w_cm = PAGE_W_CM - MARGIN_CM * 2
        usable_h_cm = PAGE_H_CM - MARGIN_CM * 2
        cell_w_cm = usable_w_cm / cols
        cell_h_cm = usable_h_cm / rows
        per_page = rows * cols

        doc = Document()
        section = doc.sections[0]
        section.page_width = Cm(PAGE_W_CM)
        section.page_height = Cm(PAGE_H_CM)
        section.top_margin = Cm(MARGIN_CM)
        section.bottom_margin = Cm(MARGIN_CM)
        section.left_margin = Cm(MARGIN_CM)
        section.right_margin = Cm(MARGIN_CM)

        page_no = 0
        for start in range(0, len(files), per_page):
            page_files = files[start:start + per_page]
            if page_no > 0:
                doc.add_page_break()
            page_no += 1

            table = doc.add_table(rows=rows, cols=cols)
            table.autofit = False
            # 表格边框颜色（""/"透明" = 无边框，即透明）
            border_color = (image_config.table_border_color or "").strip()
            if border_color and border_color.lower() not in ("透明", "transparent"):
                _apply_table_border_color(table, border_color)
            for c in range(cols):
                table.columns[c].width = Cm(cell_w_cm)
            for r in range(rows):
                table.rows[r].height = Cm(cell_h_cm)
                table.rows[r].height_rule = WD_ROW_HEIGHT_RULE.AT_LEAST

            for r in range(rows):
                for c in range(cols):
                    cell = table.cell(r, c)
                    cell.width = Cm(cell_w_cm)
                    i = r * cols + c
                    if i >= len(page_files):
                        continue
                    img_file = page_files[i]
                    with Image.open(img_file) as im:
                        iw, ih = im.size
                    if not iw or not ih:
                        continue

                    # 计算目标尺寸
                    w_cm = image_config.image_width_cm
                    h_cm = image_config.image_height_cm
                    if image_config.keep_aspect:
                        if w_cm > 0 and h_cm > 0:
                            scale = min(w_cm / iw, h_cm / ih)
                            w_cm, h_cm = iw * scale, ih * scale
                        elif w_cm > 0:
                            h_cm = w_cm * ih / iw
                        elif h_cm > 0:
                            w_cm = h_cm * iw / ih
                        else:
                            scale = min(cell_w_cm / iw, cell_h_cm / ih)
                            w_cm, h_cm = iw * scale, ih * scale
                    else:
                        if w_cm <= 0: w_cm = cell_w_cm
                        if h_cm <= 0: h_cm = cell_h_cm

                    # 图片段落
                    p_img = cell.paragraphs[0]
                    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    run = p_img.add_run()
                    run.add_picture(img_file, width=Cm(w_cm), height=Cm(h_cm))

                    # 文件名说明
                    if image_config.show_filename:
                        p_name = cell.add_paragraph()
                        p_name.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        p_name.paragraph_format.space_before = Pt(image_config.cell_spacing_pt)
                        p_name.paragraph_format.space_after = Pt(0)
                        rn = p_name.add_run(labels[start + i])
                        rn.font.size = Pt(9)
                        rn.font.color.rgb = RGBColor(100, 100, 100)

        os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)
        doc.save(output_path)
        log(f"✅ 完成 → {output_path}（{len(files)} 张图片，{rows} 行 × {cols} 列/页）")
        return True
    except Exception as e:
        log(f"❌ {e}"); return False
    finally:
        # 清理 webp/heic → PNG 的临时文件
        for p in tmp_pngs:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except OSError:
                    pass


# ════════════════════════════════════════════
#  OCR：图片 / PDF → TXT(OCR)
# ════════════════════════════════════════════

def images_to_txt_ocr(input_path, output_path, log):
    """图片 → TXT(OCR)：调用 PaddleOCR 识别单张图片或整个文件夹的图片"""
    if not file_exists(input_path, log): return False
    try:
        from core.engines import ocr_engine
        log(f"🔄 图片 → TXT(OCR): {input_path}")
        if os.path.isdir(input_path):
            files = sorted(glob.glob(os.path.join(input_path, "*.*")))
            files = [f for f in files
                     if f.lower().endswith(ocr_engine.IMAGE_EXTS)]
            multi = True
        else:
            files = [input_path]
            multi = False
        if not files:
            log("❌ 未找到可识别的图片文件")
            return False
        parts = []
        for i, f in enumerate(files):
            log(f"   🔍 OCR {i + 1}/{len(files)}: {os.path.basename(f)}")
            text = ocr_engine.ocr_image(f)
            if multi:
                parts.append(f"【{os.path.basename(f)}】\n{text}")
            else:
                parts.append(text)
        write_text(output_path, "\n\n".join(parts).strip())
        log(f"✅ 完成 → {output_path}（{len(files)} 张图片 OCR）")
        return True
    except Exception as e:
        log(f"❌ {e}")
        return False


def pdf_to_txt_ocr(input_path, output_path, log):
    """PDF → TXT(OCR)：每页渲染为图片后逐页 OCR（适合扫描版 PDF）"""
    if not file_exists(input_path, log): return False
    try:
        from core.engines import ocr_engine
        log(f"🔄 PDF → TXT(OCR): {input_path}")
        # 提前初始化 OCR 引擎：失败时给出明确原因（未装 paddleocr 等）
        ocr_engine.get_ocr()
        text = ocr_engine.ocr_pdf(input_path, log)
        if not text:
            log("❌ OCR 未识别到任何文本（请确认 PDF 页面清晰、含可识别文字）")
            return False
        write_text(output_path, text)
        log(f"✅ 完成 → {output_path}")
        return True
    except Exception as e:
        log(f"❌ {e}")
        return False


def _to_txt_ocr(input_path, output_path, log):
    """txt-ocr 统一派发：PDF 走逐页 OCR，其余（单图/文件夹）走图片 OCR"""
    if not os.path.isdir(input_path) and _normalize_ext(input_path) == ".pdf":
        return pdf_to_txt_ocr(input_path, output_path, log)
    return images_to_txt_ocr(input_path, output_path, log)


# ════════════════════════════════════════════
#  TTS：txt / md → 音频
# ════════════════════════════════════════════

def text_to_audio(input_path, output_path, log, config=None):
    """txt / md → 音频（TTS 语音合成，引擎由 TtsConfig 决定，默认 Kokoro）"""
    from core.engines.tts_engine import text_to_audio as _tts
    return _tts(input_path, output_path, log, config)


# ════════════════════════════════════════════
#  内部辅助函数
# ════════════════════════════════════════════

def _pdf_extract_text(path, log):
    """用 pdfplumber 提取全部文本"""
    parts = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            t = page.extract_text()
            if t: parts.append(t)
            log(f"📄 提取第 {i+1}/{len(pdf.pages)} 页")
    return "\n".join(parts)


def _pdf_text_to_md(text):
    """把纯文本启发式转成 markdown"""
    lines = text.splitlines()
    md = []
    for line in lines:
        line = line.strip()
        if not line: continue
        # 全大写/短行 → 标题
        if len(line) < 60 and line.isupper():
            md.append(f"## {line.title()}")
        elif len(line) < 80 and line.endswith(":") and not line.startswith("-"):
            md.append(f"### {line.rstrip(':')}")
        elif line.startswith(("•", "-", "*")):
            md.append(line)
        else:
            md.append(line)
    return md


def _libreoffice_bin() -> str:
    """定位 LibreOffice 可执行文件（Windows: soffice.exe；macOS/Linux: soffice）

    查找顺序：环境变量 → config/ui_config.json 的 paths.libreoffice
              → PATH → 常见安装位置 → 裸命令名
    """
    from config.ui_config import CONFIG as _C

    # 1) 环境变量
    env = os.environ.get("LIBREOFFICE_BIN")
    if env and os.path.exists(env):
        return env
    # 2) 配置显式指定（留空表示自动探测）
    cfg = _C.path("libreoffice")
    if cfg and os.path.exists(cfg):
        return cfg
    # 3) PATH
    p = shutil.which("soffice") or shutil.which("libreoffice")
    if p:
        return p
    # 4) 常见安装位置（跨平台）
    candidates = [
        os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"),
                     "LibreOffice", "program", "soffice.exe"),
        os.path.join(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"),
                     "LibreOffice", "program", "soffice.exe"),
        "/usr/bin/soffice",
        "/usr/local/bin/soffice",
        "/opt/libreoffice/program/soffice",
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return "soffice"   # 最后交给 PATH 尝试


def _libreoffice_convert(input_path, output_path, fmt, log):
    """调用 LibreOffice headless 转换（跨平台定位 soffice / libreoffice）"""
    try:
        out_dir = os.path.dirname(os.path.abspath(output_path)) or "."
        os.makedirs(out_dir, exist_ok=True)
        subprocess.run(
            [_libreoffice_bin(), "--headless", "--convert-to", fmt,
             "--outdir", out_dir, input_path],
            check=True, timeout=180, capture_output=True
        )
        # LibreOffice 输出文件名按原文件名（扩展名=目标格式）
        base = safe_name(input_path)
        generated = os.path.join(out_dir, f"{base}.{fmt}")
        if os.path.exists(generated) and generated != output_path:
            os.rename(generated, output_path)
        return os.path.exists(output_path)
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        log(f"⚠ LibreOffice 不可用: {e}")
        return False


def _html_to_images_playwright(html_path, output_path, log):
    """用 Playwright 把 HTML 截成图片"""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1280, "height": 800})
            page.goto(f"file://{os.path.abspath(html_path).replace(os.sep, '/')}")
            page.wait_for_load_state("networkidle")
            # 整页截图
            img_path = output_path if output_path.endswith(".png") else output_path + ".png"
            page.screenshot(path=img_path, full_page=True)
            browser.close()
        if img_path != output_path and output_path.endswith((".jpg", ".jpeg")):
            Image.open(img_path).convert("RGB").save(output_path, "JPEG", quality=90)
            os.remove(img_path)
        return True
    except Exception as e:
        log(f"⚠ Playwright 截图失败: {e}")
        return False


def html_to_pdf_via_reportlab(html_path, output_path, log):
    """HTML → PDF 的轻量方案：提取文本后用 reportlab 排版（自动适配 CJK 字体）"""
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    html = read_text(html_path)
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator="\n")
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    cjk_font = _register_cjk_font()
    if cjk_font:
        styles = _make_cjk_styles(cjk_font)
        normal_style = styles["Normal_CJK"]
        log(f"   使用字体: {cjk_font}")
    else:
        styles = getSampleStyleSheet()
        normal_style = styles["Normal"]
    story = []
    for line in text.splitlines():
        if line.strip():
            story.append(Paragraph(line.strip(), normal_style))
        else:
            story.append(Spacer(1, 6))
    doc.build(story)


def _docx_to_pdf_reportlab(input_path, output_path, log):
    """DOCX → PDF 的文本重建方案（自动适配 CJK 字体）"""
    docx_doc = Document(input_path)
    pdf_doc = SimpleDocTemplate(output_path, pagesize=A4)
    cjk_font = _register_cjk_font()
    if cjk_font:
        styles = _make_cjk_styles(cjk_font)
        h1_style = styles["Heading1_CJK"]
        h2_style = styles["Heading2_CJK"]
        normal_style = styles["Normal_CJK"]
        log(f"   使用字体: {cjk_font}")
    else:
        styles = getSampleStyleSheet()
        h1_style = styles["Heading1"]
        h2_style = styles["Heading2"]
        normal_style = styles["Normal"]
    story = []
    for p in docx_doc.paragraphs:
        txt = p.text.strip()
        if not txt: continue
        style = h1_style if p.style.name.startswith("Heading 1") else \
                h2_style if p.style.name.startswith("Heading 2") else \
                normal_style
        story.append(Paragraph(txt, style))
    pdf_doc.build(story)


# 格式归一化（供 _to_txt_ocr 等使用）
def _normalize_ext(path):
    ext = os.path.splitext(path)[1].lower()
    return FORMAT_ALIASES.get(ext, ext)


# 便捷别名（旧 src 引用保留）
FORMAT_ALIASES = {
    ".markdown": ".md", ".mdown": ".md", ".mkd": ".md",
    ".htm": ".html",
    ".xls": ".xlsx", ".xlsm": ".xlsx",
    ".jpeg": ".jpg", ".tif": ".tiff",
    ".png": ".png", ".bmp": ".bmp", ".gif": ".gif", ".webp": ".webp",
    # ── 媒体别名 ──
    ".m4v": ".mp4", ".oga": ".ogg", ".mka": ".mkv",
}
