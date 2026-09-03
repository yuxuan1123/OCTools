"""
octool/core/engines/presentation_engine.py
───────────────────────────────────────────────
演示引擎（核心引擎层）：演示文稿处理（md / html / pptx）

覆盖：
  - md → html / pptx
  - html → md / pptx
  - pptx → md / html / pdf / 图片版PPTX（防乱码）
  - pptx → pdf（LibreOffice 中转，失败退回每页渲染拼图）

设计原则：
  - 每个转换函数签名统一为 (input_path, output_path, log) -> bool
  - md→html 优先 pandoc（含目录、代码高亮），失败退回 markdown 库

旧路径 src/_converters_legacy.py 保留为兼容 shim（re-export 本模块）。
"""

import os
import shutil
import tempfile
from pathlib import Path

import markdown as md_lib
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw
from pptx import Presentation
from pptx.util import Inches as PxInches

from core.engines.document_engine import (
    _ensure_pandoc,
    _libreoffice_convert,
    images_to_pdf,
)
from core.utils.file_handler import file_exists, read_text, write_text, safe_name


def md_to_html(input_path, output_path, log):
    """MD → HTML（pandoc，含目录和代码高亮）"""
    if not file_exists(input_path, log): return False
    try:
        _ensure_pandoc(log)
        log(f"🔄 MD → HTML: {input_path}")
        pypandoc = _get_pypandoc()
        pypandoc.convert_file(
            input_path, "html", outputfile=output_path,
            extra_args=["--standalone", "--self-contained",
                        "--toc", "--toc-depth=3",
                        "--highlight-style=tango"]
        )
        log(f"✅ 完成 → {output_path}")
        return True
    except Exception as e:
        # 退回 markdown 库
        try:
            log("⚠ pandoc 失败，改用 markdown 库")
            body = md_lib.markdown(read_text(input_path), extensions=["extra", "codehilite", "toc"])
            html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>{safe_name(input_path)}</title>
<style>body{{font-family:sans-serif;max-width:860px;margin:auto;padding:20px;line-height:1.7}}
h1,h2,h3{{border-bottom:1px solid #eee;padding-bottom:.3em}}code{{background:#f4f4f4;padding:2px 4px;border-radius:3px}}
pre{{background:#f4f4f4;padding:12px;border-radius:5px;overflow:auto}}</style></head><body>{body}</body></html>"""
            write_text(output_path, html)
            log(f"✅ 完成 → {output_path}")
            return True
        except Exception as e2:
            log(f"❌ {e2}"); return False


def md_to_pptx(input_path, output_path, log):
    """MD → PPTX（解析标题/段落/列表/图片，逐段生成幻灯片）"""
    if not file_exists(input_path, log): return False
    try:
        log(f"🔄 MD → PPTX: {input_path}")
        text = read_text(input_path)
        # 用 pandoc 先转 html，再解析
        _ensure_pandoc(log)
        pypandoc = _get_pypandoc()
        html = pypandoc.convert_text(text, "html", format="markdown")
        soup = BeautifulSoup(html, "html.parser")
        prs = Presentation()
        prs.slide_width = PxInches(13.333)
        prs.slide_height = PxInches(7.5)
        blank = prs.slide_layouts[6]
        title_layout = prs.slide_layouts[0]
        # 第一页用标题页
        slide = prs.slides.add_slide(title_layout)
        slide.shapes.title.text = safe_name(input_path)
        if slide.placeholders.__len__() > 1:
            slide.placeholders[1].text = "自动生成 · 由 MD 转换"
        # 按元素生成
        from pptx.util import Pt as PxPt
        for el in soup.body.children if soup.body else soup.children:
            if getattr(el, "name", None) is None: continue
            name = el.name
            if name in ("h1", "h2", "h3"):
                s = prs.slides.add_slide(blank)
                txBox = s.shapes.add_textbox(PxInches(0.5), PxInches(0.5), PxInches(12), PxInches(6))
                tf = txBox.text_frame; tf.word_wrap = True
                p = tf.paragraphs[0]; p.text = el.get_text(strip=True)
                p.font.size = PxPt(28 if name == "h1" else 22 if name == "h2" else 18)
                p.font.bold = True
            elif name == "p":
                s = prs.slides.add_slide(blank)
                txBox = s.shapes.add_textbox(PxInches(0.5), PxInches(0.5), PxInches(12), PxInches(6))
                tf = txBox.text_frame; tf.word_wrap = True
                tf.paragraphs[0].text = el.get_text(strip=True)
            elif name == "ul" or name == "ol":
                s = prs.slides.add_slide(blank)
                txBox = s.shapes.add_textbox(PxInches(0.5), PxInches(0.5), PxInches(12), PxInches(6))
                tf = txBox.text_frame; tf.word_wrap = True
                for i, li in enumerate(el.find_all("li")):
                    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
                    p.text = "• " + li.get_text(strip=True)
        prs.save(output_path)
        log(f"✅ 完成 → {output_path}（{len(prs.slides)} 页）")
        return True
    except Exception as e:
        log(f"❌ {e}"); return False


def html_to_md(input_path, output_path, log):
    """HTML → MD（markdownify，保留基本结构）"""
    if not file_exists(input_path, log): return False
    try:
        log(f"🔄 HTML → MD: {input_path}")
        html = read_text(input_path)
        # 尝试用 pandoc 先拿到更完整的结果
        try:
            _ensure_pandoc(log)
            pypandoc = _get_pypandoc()
            pypandoc.convert_file(input_path, "gfm", outputfile=output_path,
                                  extra_args=["--wrap=none"])
            log(f"✅ 完成(pandoc) → {output_path}")
            return True
        except Exception:
            pass
        import markdownify
        md = markdownify.markdownify(html, heading_style="ATX")
        write_text(output_path, md)
        log(f"✅ 完成(markdownify) → {output_path}")
        return True
    except Exception as e:
        # 最后兜底：html2text
        try:
            import html2text
            h = html2text.HTML2Text(); h.ignore_links = False
            write_text(output_path, h.handle(read_text(input_path)))
            log(f"✅ 完成(html2text) → {output_path}")
            return True
        except Exception as e2:
            log(f"❌ {e2}"); return False


def html_to_pptx(input_path, output_path, log):
    """HTML → PPTX（解析 section.slide 或按 h1 分页，逐页放文本）"""
    if not file_exists(input_path, log): return False
    try:
        log(f"🔄 HTML → PPTX: {input_path}")
        html = read_text(input_path)
        soup = BeautifulSoup(html, "html.parser")
        prs = Presentation()
        prs.slide_width = PxInches(13.333)
        prs.slide_height = PxInches(7.5)
        blank = prs.slide_layouts[6]
        # 优先按 section.slide 分页
        sections = soup.select("section.slide")
        if not sections:
            # 没有 slide 标记就按 h1 切分
            parts = soup.find_all(["h1", "h2", "h3", "p", "ul", "ol"])
            sections = [soup]  # 单页兜底
            if parts:
                sections = []
                cur = []
                for el in parts:
                    if el.name in ("h1",) and cur:
                        sections.append(cur); cur = []
                    cur.append(el)
                if cur: sections.append(cur)
        from pptx.util import Pt as PxPt
        for sec in sections:
            s = prs.slides.add_slide(blank)
            txBox = s.shapes.add_textbox(PxInches(0.5), PxInches(0.5), PxInches(12), PxInches(6))
            tf = txBox.text_frame; tf.word_wrap = True
            items = sec if isinstance(sec, list) else sec.find_all(["h1","h2","h3","p","li"])
            for i, el in enumerate(items):
                txt = el.get_text(strip=True) if hasattr(el, "get_text") else str(el).strip()
                if not txt: continue
                p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
                p.text = txt
                if hasattr(el, "name") and el.name in ("h1","h2","h3"):
                    p.font.bold = True
                    p.font.size = PxPt(24 if el.name == "h1" else 20)
        prs.save(output_path)
        log(f"✅ 完成 → {output_path}（{len(prs.slides)} 页）")
        return True
    except Exception as e:
        log(f"❌ {e}"); return False


def pptx_to_md(input_path, output_path, log):
    """PPTX → MD（提取每页标题+正文）"""
    if not file_exists(input_path, log): return False
    try:
        log(f"🔄 PPTX → MD: {input_path}")
        prs = Presentation(input_path)
        lines = []
        for i, slide in enumerate(prs.slides, 1):
            lines.append(f"## 第 {i} 页")
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for p in shape.text_frame.paragraphs:
                        txt = p.text.strip()
                        if txt: lines.append(txt)
            lines.append("")
        write_text(output_path, "\n".join(lines))
        log(f"✅ 完成 → {output_path}")
        return True
    except Exception as e:
        log(f"❌ {e}"); return False


def pptx_to_html(input_path, output_path, log):
    """PPTX → HTML（每页一个 section.slide 容器）"""
    if not file_exists(input_path, log): return False
    try:
        log(f"🔄 PPTX → HTML: {input_path}")
        prs = Presentation(input_path)
        parts = ["""<!DOCTYPE html><html><head><meta charset="utf-8"><title>PPT</title>
<style>body{font-family:sans-serif;margin:0;padding:0}.slide{border-bottom:2px solid #ccc;padding:40px;min-height:60vh;page-break-after:always}
h2{color:#2c3e50;border-bottom:1px solid #eee;padding-bottom:8px}p{line-height:1.7;font-size:16px}</style></head><body>"""]
        for i, slide in enumerate(prs.slides, 1):
            parts.append(f'<section class="slide"><h2>第 {i} 页</h2>')
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for p in shape.text_frame.paragraphs:
                        txt = p.text.strip()
                        if txt: parts.append(f"<p>{txt}</p>")
            parts.append("</section>")
        parts.append("</body></html>")
        write_text(output_path, "\n".join(parts))
        log(f"✅ 完成 → {output_path}")
        return True
    except Exception as e:
        log(f"❌ {e}"); return False


def pptx_to_pdf(input_path, output_path, log):
    """PPTX → PDF（LibreOffice 中转）"""
    if not file_exists(input_path, log): return False
    try:
        log(f"🔄 PPTX → PDF: {input_path}")
        if _libreoffice_convert(input_path, output_path, "pdf", log):
            return True
        # 退回：把每页渲染成图片再拼 pdf
        log("⚠ LibreOffice 不可用，使用截图方案")
        tmp_dir = output_path + "_slides"
        os.makedirs(tmp_dir, exist_ok=True)
        prs = Presentation(input_path)
        imgs = []
        for i, slide in enumerate(prs.slides):
            # 简单文本渲染
            img = Image.new("RGB", (1280, 720), "white")
            draw = ImageDraw.Draw(img)
            y = 40
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for p in shape.text_frame.paragraphs:
                        draw.text((40, y), p.text, fill="black")
                        y += 24
            p_ = os.path.join(tmp_dir, f"slide_{i}.png")
            img.save(p_)
            imgs.append(p_)
        images_to_pdf(tmp_dir, output_path, log)
        for f in imgs: os.remove(f)
        os.rmdir(tmp_dir)
        log(f"✅ 完成 → {output_path}")
        return True
    except Exception as e:
        log(f"❌ {e}"); return False


def pptx_to_pptx_image(input_path, output_path, log, dpi=300):
    """PPTX → 图片版 PPTX（防乱码 / 防修改）

    使用 PowerPoint COM 将每页导出为高清 PNG，
    再重新组装成图片铺满的 PPTX，确保跨设备显示一致。

    仅支持 Windows + Microsoft PowerPoint。
    """
    if not file_exists(input_path, log): return False
    if not os.name == "nt":
        log("❌ 此功能仅支持 Windows + Microsoft PowerPoint")
        return False

    try:
        import win32com.client
    except ImportError:
        log("❌ 缺少 pywin32 依赖，请执行: pip install pywin32")
        return False

    temp_dir = None
    try:
        log(f"🔄 PPTX → 图片版PPTX: {input_path}")
        log(f"   清晰度: {dpi} DPI")

        # ── 步骤1: 用 PowerPoint 导出每页为 PNG ──
        temp_dir = Path(tempfile.mkdtemp(prefix="pptx2img_"))
        images_dir = temp_dir / "images"
        images_dir.mkdir(exist_ok=True)

        log("   启动 PowerPoint...")
        ppt = win32com.client.Dispatch("PowerPoint.Application")
        ppt.Visible = True
        ppt.DisplayAlerts = False

        try:
            pres = ppt.Presentations.Open(str(Path(input_path).absolute()))
            slide_count = pres.Slides.Count
            log(f"   共检测到 {slide_count} 页")

            # 根据页面尺寸计算像素
            slide_width_inch = pres.PageSetup.SlideWidth / 72
            slide_height_inch = pres.PageSetup.SlideHeight / 72
            img_w = int(slide_width_inch * dpi)
            img_h = int(slide_height_inch * dpi)

            for i in range(1, slide_count + 1):
                img_path = images_dir / f"slide_{i:03d}.png"
                pres.Slides.Item(i).Export(
                    str(img_path.absolute()), "PNG", img_w, img_h
                )
                log(f"   ✅ 导出第 {i}/{slide_count} 页")

            pres.Close()
        finally:
            ppt.Quit()

        image_paths = sorted(images_dir.glob("*.png"))
        log(f"   🎉 全部页面导出完成，共 {len(image_paths)} 张图片")

        # ── 步骤2: 重新组装成图片版 PPTX ──
        log("   开始生成图片版PPTX...")
        prs = Presentation()

        # 读取原PPT尺寸
        src_prs = Presentation(input_path)
        prs.slide_width = src_prs.slide_width
        prs.slide_height = src_prs.slide_height

        # 删除默认空白页
        if len(prs.slides) > 0:
            r_id = prs.slides._sldIdLst[0].rId
            prs.part.drop_rel(r_id)
            del prs.slides._sldIdLst[0]

        for idx, img_path in enumerate(image_paths):
            slide = prs.slides.add_slide(prs.slide_layouts[6])  # 空白版式
            # 图片铺满整页
            slide.shapes.add_picture(
                str(img_path), 0, 0,
                prs.slide_width, prs.slide_height
            )
            log(f"   📄 已插入第 {idx + 1} 页")

        # 确保输出目录存在
        os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)
        prs.save(output_path)

        size_mb = os.path.getsize(output_path) / 1024 / 1024
        log("=" * 50)
        log("✅ PPT图片版转换成功！")
        log(f"📁 文件: {output_path}")
        log(f"📦 大小: {size_mb:.1f} MB")
        log(f"📄 页数: {len(image_paths)}")
        log("🔒 每页均为图片，防乱码 / 防修改")
        log("=" * 50)
        return True

    except Exception as e:
        log(f"❌ 转换失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if temp_dir and temp_dir.exists():
            shutil.rmtree(temp_dir)
            log("🧹 临时文件已清理")


def _get_pypandoc():
    """延迟获取 pypandoc 模块（仅在需要时导入）"""
    import pypandoc
    return pypandoc
