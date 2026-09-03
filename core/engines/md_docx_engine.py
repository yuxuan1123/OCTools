"""
octool/core/engines/md_docx_engine.py
───────────────────────────────────────────────
MD → DOCX 高级格式控制引擎 —— 核心引擎层

基于 python-docx 直接构建 Word 文档，绕过 pandoc，
实现对每一项格式的精确控制。

核心流程:
  1. Markdown → HTML（markdown 库）
  2. BeautifulSoup 遍历 DOM 树
  3. python-docx 构建 Document（逐元素应用 FormatConfig 中的样式）
  4. 后处理（目录、页眉页脚、封面、水印）

旧路径 src/md_to_docx_engine.py 保留为兼容 shim（re-export 本模块）。
"""

import os
import re
import subprocess
import zipfile
import datetime
import base64
import tempfile
import xml.etree.ElementTree as mdxml
from pathlib import Path
from typing import Optional, Callable, List, Tuple, Dict

from docx import Document
from docx.shared import Pt, Cm, Inches, Emu, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml
from docx.oxml.shared import OxmlElement
from lxml import etree

import markdown as md_lib
from markdown import util
from markdown.inlinepatterns import Pattern
from markdown.extensions import Extension
from bs4 import BeautifulSoup, Tag, NavigableString

from config.enums import PaperSize, Orientation, LineSpacingMode, Alignment as CfgAlignment
from config.format_config import FormatConfig
from config.heading import HeadingStyle


# ════════════════════════════════════════════
#  工具函数
# ════════════════════════════════════════════

def _hex_to_rgb(hex_color: str) -> RGBColor:
    """#RRGGBB → RGBColor"""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return RGBColor(r, g, b)


def _pt_to_emu(pt: float) -> int:
    """磅 → EMU (1pt = 12700 EMU)"""
    return int(pt * 12700)


def _cm_to_emu(cm: float) -> int:
    """厘米 → EMU (1cm = 360000 EMU)"""
    return int(cm * 360000)


def _remove_theme_font_attrs(rFonts):
    """
    移除 rFonts 上的主题字体属性（w:asciiTheme / w:hAnsiTheme /
    w:eastAsiaTheme / w:cstheme）。

    重要：在 OOXML 中，只要存在主题属性，Word 就会优先使用主题字体，
    显式设置的 w:ascii / w:eastAsia 等会被忽略——这正是标题字体
    显示为 MS Gothic 等主题字体的原因。设置显式字体前必须先清掉它们。
    """
    for attr in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        key = qn(attr)
        if key in rFonts.attrib:
            del rFonts.attrib[key]


def _set_cjk_font(run, font_cn: str, font_en: str):
    """
    为 run 设置中西文字体。
    python-docx 的 run.font.name 只设置西文字体；
    中文字体需要通过 XML 操作 w:rPr/w:rFonts 的 east-Asia 属性。
    """
    run.font.name = font_en
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.insert(0, rFonts)
    _remove_theme_font_attrs(rFonts)
    rFonts.set(qn('w:ascii'), font_en)
    rFonts.set(qn('w:hAnsi'), font_en)
    rFonts.set(qn('w:eastAsia'), font_cn)
    rFonts.set(qn('w:cs'), font_en)


def _set_paragraph_spacing(paragraph, config_typography):
    """设置段间距和行距"""
    pf = paragraph.paragraph_format
    pf.space_before = Pt(config_typography.para_space_before)
    pf.space_after = Pt(config_typography.para_space_after)

    if config_typography.line_spacing_mode == LineSpacingMode.FIXED:
        pf.line_spacing = Pt(config_typography.line_spacing_fixed)
    else:
        pf.line_spacing = config_typography.line_spacing


def _set_alignment(paragraph, alignment: CfgAlignment):
    """设置段落对齐"""
    mapping = {
        CfgAlignment.LEFT: WD_ALIGN_PARAGRAPH.LEFT,
        CfgAlignment.CENTER: WD_ALIGN_PARAGRAPH.CENTER,
        CfgAlignment.RIGHT: WD_ALIGN_PARAGRAPH.RIGHT,
        CfgAlignment.JUSTIFY: WD_ALIGN_PARAGRAPH.JUSTIFY,
    }
    paragraph.alignment = mapping.get(alignment, WD_ALIGN_PARAGRAPH.LEFT)


def _set_first_line_indent(paragraph, chars: float, font_size_pt: float):
    """设置首行缩进（字符数 → EMU）"""
    if chars > 0:
        # 1 字符 ≈ 当前字号宽度
        indent_emu = _cm_to_emu(chars * font_size_pt * 0.035)  # 近似：1pt ≈ 0.035cm
        paragraph.paragraph_format.first_line_indent = indent_emu


def _add_table_borders(table, color: str = "#000000"):
    """为表格添加边框"""
    tbl = table._tbl
    tblPr = tbl.tblPr if tbl.tblPr is not None else OxmlElement('w:tblPr')
    borders = OxmlElement('w:tblBorders')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        element = OxmlElement(f'w:{edge}')
        element.set(qn('w:val'), 'single')
        element.set(qn('w:sz'), '4')
        element.set(qn('w:space'), '0')
        element.set(qn('w:color'), color.lstrip("#"))
        borders.append(element)
    # 确保 tblPr 在正确位置
    existing_borders = tblPr.find(qn('w:tblBorders'))
    if existing_borders is not None:
        tblPr.replace(existing_borders, borders)
    else:
        tblPr.insert(0, borders)


def _set_cell_shading(cell, color: str):
    """设置单元格背景色"""
    tcPr = cell._tc.get_or_add_tcPr()
    shading = OxmlElement('w:shd')
    shading.set(qn('w:fill'), color.lstrip("#"))
    shading.set(qn('w:val'), 'clear')
    # 移除已有 shading
    existing = tcPr.find(qn('w:shd'))
    if existing is not None:
        tcPr.replace(existing, shading)
    else:
        tcPr.append(shading)


def _add_paragraph_border_left(paragraph, color: str):
    """为段落添加左侧竖线（引用块效果）"""
    pPr = paragraph._element.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    left = OxmlElement('w:left')
    left.set(qn('w:val'), 'single')
    left.set(qn('w:sz'), '12')
    left.set(qn('w:space'), '8')
    left.set(qn('w:color'), color.lstrip("#"))
    pBdr.append(left)
    existing_bdr = pPr.find(qn('w:pBdr'))
    if existing_bdr is not None:
        pPr.replace(existing_bdr, pBdr)
    else:
        pPr.insert(0, pBdr)


def _add_paragraph_shading(paragraph, color: str):
    """为段落添加背景色"""
    pPr = paragraph._element.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), color.lstrip("#"))
    shd.set(qn('w:val'), 'clear')
    existing = pPr.find(qn('w:shd'))
    if existing is not None:
        pPr.replace(existing, shd)
    else:
        pPr.append(shd)


# ════════════════════════════════════════════
#  数学公式支持（LaTeX → OMML）
# ════════════════════════════════════════════

# OOXML 命名空间
_M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
_W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
_R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

# 匹配 $...$ 行内公式 与 $$...$$ 块级公式（\$ 表示转义字面量，不当作公式）
# 注意：整个交替必须用非捕获组包裹。Pattern 基类会把模式包装为
# `^(.*?)<pattern>(.*)$`，若不包裹，行内分支将永远无法带前缀匹配。
_MATH_RE = r"(?:\$\$(?P<display>.+?)\$\$|(?<!\\)\$(?P<inline>[^$\n]+)\$)"


class _MathPattern(Pattern):
    """识别行内 / 块级 LaTeX 公式，输出 <math display="..."> 元素"""

    def handleMatch(self, m):
        latex = m.group("display") or m.group("inline")
        el = mdxml.Element("math")
        el.set("display", "display" if m.group("display") else "inline")
        # AtomicString 保护公式内容：内部 LaTeX（如 \alpha）不再被
        # 后续 inline 处理器（转义 / 强调等）二次修改
        el.text = util.AtomicString(latex)
        return el


class _MathExtension(Extension):
    """markdown 数学扩展：注册到行内处理器（优先级介于反引号代码与转义之间，
    因此 `$x$` 不会被当作公式；`` `$x$` `` 内的 $ 也不会被解析，
    而 $...$ 内部的 \alpha 等 LaTeX 命令不会被转义处理器破坏）"""

    def extendMarkdown(self, md):
        md.inlinePatterns.register(_MathPattern(_MATH_RE, md),
                                   "converter_math", 185)


def _parse_omml(xml_str: str):
    """将 OMML XML 片段解析为 lxml 元素（自动补齐 m/w/r 命名空间声明）"""
    try:
        wrapper = etree.fromstring(
            ('<root xmlns:m="%s" xmlns:w="%s" xmlns:r="%s">%s</root>'
             % (_M_NS, _W_NS, _R_NS, xml_str)).encode("utf-8"))
        return wrapper[0] if len(wrapper) else None
    except Exception:
        return None


def _batch_latex_to_omml(formulas: List[str],
                         log: Callable[[str], None]) -> Dict[str, Tuple[str, str]]:
    """将一批 LaTeX 公式批量转换为 OMML（单次 pandoc 调用，避免逐条开销）。

    返回 {公式: (inline_oMath_xml, display_oMathPara_xml)}；
    pandoc 不可用 / 转换失败时返回空字典（公式回退为纯文本，不丢失内容）。
    """
    seen, unique = set(), []
    for f in formulas:
        f = (f or "").strip()
        if f and f not in seen:
            seen.add(f)
            unique.append(f)
    if not unique:
        return {}

    tmp_path = out_path = None
    try:
        fd, tmp_path = tempfile.mkstemp(suffix=".md")
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            parts = []
            for i, f in enumerate(unique):
                if i:
                    parts.append(f"ZZMATHSEP{i}ZZ")
                parts.append("$$" + f + "$$")
            fh.write("\n\n".join(parts))

        out_path = tmp_path + ".docx"
        result = subprocess.run(["pandoc", tmp_path, "-o", out_path],
                                capture_output=True, text=True, timeout=90)
        if result.returncode != 0:
            log("⚠ 未检测到 pandoc，公式将按纯文本输出")
            return {}

        with zipfile.ZipFile(out_path) as z:
            xml = z.read("word/document.xml").decode("utf-8")
        blocks = re.findall(r"<m:oMathPara>.*?</m:oMathPara>"
                            r"|<m:oMath>.*?</m:oMath>", xml, re.S)

        cache: Dict[str, Tuple[str, str]] = {}
        for i, f in enumerate(unique):
            if i >= len(blocks):
                break
            block = blocks[i]
            inner = re.search(r"<m:oMath>.*?</m:oMath>", block, re.S)
            inline_xml = inner.group(0) if inner else block
            cache[f] = (inline_xml, block)
        return cache
    except Exception as e:
        log(f"⚠ 公式转换失败（将按纯文本输出）: {e}")
        return {}
    finally:
        for p in (tmp_path, out_path):
            if p:
                try:
                    if os.path.exists(p):
                        os.remove(p)
                except Exception:
                    pass


# ════════════════════════════════════════════
#  引擎类
# ════════════════════════════════════════════

class MdToDocxEngine:
    """MD → DOCX 高级格式控制引擎"""

    def __init__(self, config: FormatConfig):
        self.config = config
        self.doc: Optional[Document] = None
        self.heading_counters = {"h1": 0, "h2": 0, "h3": 0}
        self.image_temp_files: List[str] = []
        self._omml_cache: Dict[str, Tuple[str, str]] = {}   # 公式 → (inline, display) OMML

    def convert(self, input_path: str, output_path: str, log: Callable[[str], None] = lambda m: None) -> bool:
        """
        执行转换。
        返回 True/False。
        """
        try:
            if not os.path.exists(input_path):
                log(f"❌ 文件不存在: {input_path}")
                return False

            log(f"🔄 MD → DOCX (高级引擎): {input_path}")

            # 1. 读取 Markdown，转换为 HTML
            log("📖 读取并解析 Markdown…")
            md_text = self._read_file(input_path)
            html_body = md_lib.markdown(
                md_text,
                extensions=["extra", "codehilite", "toc", "tables",
                            "fenced_code", _MathExtension()]
            )

            # 2. 解析 HTML
            soup = BeautifulSoup(html_body, "html.parser")

            # 2.1 收集文档中的数学公式，批量转换为 OMML（Word 原生公式）
            math_els = soup.find_all("math")
            if math_els:
                log(f"∑ 识别到 {len(math_els)} 个数学公式，转换为 Word 公式…")
            self._omml_cache = _batch_latex_to_omml(
                [m.get_text() for m in math_els], log)

            # 3. 创建 Document
            self.doc = Document()

            # 4. 设置页面
            log("📐 设置页面布局…")
            self._setup_page()

            # 5. 设置样式
            log("🔤 配置样式…")
            self._setup_styles()

            # 6. 封面页（如果启用）
            if self.config.advanced.cover_enabled:
                log("📔 生成封面页…")
                self._add_cover_page()

            # 7. 目录（如果启用）
            if self.config.advanced.auto_toc:
                log("📑 插入目录域…")
                self._add_toc()

            # 8. 遍历 DOM 树
            log("📝 转换内容…")
            body = soup.find("body") or soup
            for element in body.children:
                if isinstance(element, Tag):
                    self._process_element(element)

            # 9. 页眉页脚
            log("🏷️ 设置页眉页脚…")
            self._add_headers_footers()

            # 10. 水印
            if self.config.advanced.watermark_text:
                log("💧 添加水印…")
                self._add_watermark()

            # 11. 保存
            log("💾 保存文档…")
            os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)
            self.doc.save(output_path)

            # 12. 清理临时文件
            self._cleanup_temp_files()

            log(f"✅ 完成 → {output_path}")
            return True

        except Exception as e:
            log(f"❌ 转换失败: {e}")
            import traceback
            log(traceback.format_exc())
            self._cleanup_temp_files()
            return False

    # ── 页面设置 ──────────────────────────

    def _setup_page(self):
        """设置页面尺寸、方向、边距"""
        section = self.doc.sections[0]
        cfg = self.config.page

        # 纸张大小
        w_cm, h_cm = cfg.paper_size.dimensions_cm()
        if cfg.orientation == Orientation.LANDSCAPE:
            w_cm, h_cm = h_cm, w_cm

        section.page_width = Cm(w_cm)
        section.page_height = Cm(h_cm)

        # 方向
        if cfg.orientation == Orientation.LANDSCAPE:
            section.orientation = WD_ORIENT.LANDSCAPE
        else:
            section.orientation = WD_ORIENT.PORTRAIT

        # 边距
        section.top_margin = Cm(cfg.margin_top)
        section.bottom_margin = Cm(cfg.margin_bottom)
        section.left_margin = Cm(cfg.margin_left)
        section.right_margin = Cm(cfg.margin_right)

        # 装订线（python-docx 不直接支持，通过增加左边距模拟）
        if cfg.gutter > 0:
            section.left_margin = Cm(cfg.margin_left + cfg.gutter)

    # ── 样式设置 ──────────────────────────

    def _setup_styles(self):
        """配置 Word 样式：Normal, Heading 1-3"""
        cfg = self.config.typography

        # ── Normal 样式（正文） ──
        normal = self.doc.styles['Normal']
        normal.font.size = Pt(cfg.body_font_size)
        normal.font.color.rgb = _hex_to_rgb(cfg.body_color)

        # Normal 段落格式
        npf = normal.paragraph_format
        if cfg.line_spacing_mode == LineSpacingMode.FIXED:
            npf.line_spacing = Pt(cfg.line_spacing_fixed)
        else:
            npf.line_spacing = cfg.line_spacing
        npf.space_before = Pt(cfg.para_space_before)
        npf.space_after = Pt(cfg.para_space_after)
        _set_alignment_obj(npf, cfg.alignment)

        # 中西文字体（通过修改 style XML）
        self._set_style_cjk_font('Normal', cfg.body_font_cn, cfg.body_font_en)

        # ── Heading 1-3 样式 ──
        for level_name, hs in cfg.headings.items():
            self._setup_heading_style(level_name, hs)

    def _setup_heading_style(self, level_name: str, hs: HeadingStyle):
        """设置单个标题样式"""
        style_name = f"Heading {level_name[1]}"  # h1 → Heading 1
        try:
            style = self.doc.styles[style_name]
        except KeyError:
            return  # 样式不存在则跳过

        style.font.size = Pt(hs.font_size)
        style.font.bold = hs.bold
        style.font.color.rgb = _hex_to_rgb(hs.color)
        _set_alignment_obj(style.paragraph_format, hs.alignment)

        # 中西文字体
        self._set_style_cjk_font(style_name, hs.font_cn, hs.font_en)

        # 标题段间距
        style.paragraph_format.space_before = Pt(12)
        style.paragraph_format.space_after = Pt(6)

    def _set_style_cjk_font(self, style_name: str, font_cn: str, font_en: str):
        """通过 XML 操作设置样式中的中西文字体"""
        try:
            style = self.doc.styles[style_name]
            rPr = style.element.get_or_add_rPr()
            rFonts = rPr.find(qn('w:rFonts'))
            if rFonts is None:
                rFonts = OxmlElement('w:rFonts')
                rPr.insert(0, rFonts)
            # 关键：python-docx 默认模板的 Heading 1-3 自带主题字体属性，
            # 主题属性优先级高于显式字体名，不清除则标题仍显示主题字体（如 MS Gothic）
            _remove_theme_font_attrs(rFonts)
            rFonts.set(qn('w:ascii'), font_en)
            rFonts.set(qn('w:hAnsi'), font_en)
            rFonts.set(qn('w:eastAsia'), font_cn)
            rFonts.set(qn('w:cs'), font_en)
        except Exception:
            pass

    # ── DOM 遍历 ──────────────────────────

    def _process_element(self, el: Tag):
        """根据 HTML 标签类型分派处理"""
        tag = el.name.lower() if el.name else ""

        if tag in ("h1", "h2", "h3"):
            self._process_heading(el, tag)
        elif tag == "p":
            self._process_paragraph(el)
        elif tag in ("ul", "ol"):
            self._process_list(el, tag)
        elif tag == "blockquote":
            self._process_blockquote(el)
        elif tag == "pre":
            self._process_code_block(el)
        elif tag == "table":
            self._process_table(el)
        elif tag == "hr":
            self._process_hr()
        elif tag in ("div", "section"):
            for child in el.children:
                if isinstance(child, Tag):
                    self._process_element(child)
        # math 通常在 p 内处理；兜底顶层独立公式
        elif tag == "math":
            p = self.doc.add_paragraph()
            self._process_math(p, el)
        # img 通常在 p 内处理，直接调用
        elif tag == "img":
            self._process_image(el)

    def _process_heading(self, el: Tag, level: str):
        """处理标题"""
        level_num = int(level[1])  # h1 → 1
        text = el.get_text(strip=True)
        if not text:
            return

        # 标题编号
        self._update_heading_counter(level)
        if self.config.advanced.heading_numbering:
            prefix = self._get_heading_number(level)
            text = f"{prefix} {text}"

        p = self.doc.add_paragraph(text, style=f"Heading {level_num}")

    def _process_paragraph(self, el: Tag):
        """处理段落（可能含内联元素: strong, em, code, a, img 等）"""
        cfg = self.config.typography
        text_parts = list(el.children)
        if not text_parts:
            # 空段落
            p = self.doc.add_paragraph()
            self._apply_paragraph_format(p)
            return

        # 检查是否只包含 img
        imgs = el.find_all("img")
        if imgs and len(imgs) == 1 and not el.get_text(strip=True):
            self._process_image(imgs[0])
            return

        p = self.doc.add_paragraph()
        self._apply_paragraph_format(p)
        self._process_inline_elements(p, el)

    def _process_inline_elements(self, p, parent: Tag):
        """处理行内元素（strong, em, code, a, img, br, 纯文本）"""
        cfg = self.config.typography

        for child in parent.children:
            if isinstance(child, NavigableString):
                text = str(child)
                if text.strip():
                    run = p.add_run(text)
                    _set_cjk_font(run, cfg.body_font_cn, cfg.body_font_en)
                    run.font.size = Pt(cfg.body_font_size)
                    run.font.color.rgb = _hex_to_rgb(cfg.body_color)

            elif isinstance(child, Tag):
                tag = child.name.lower() if child.name else ""

                if tag == "strong" or tag == "b":
                    run = p.add_run(child.get_text())
                    _set_cjk_font(run, cfg.body_font_cn, cfg.body_font_en)
                    run.font.size = Pt(cfg.body_font_size)
                    run.bold = True

                elif tag == "em" or tag == "i":
                    run = p.add_run(child.get_text())
                    _set_cjk_font(run, cfg.body_font_cn, cfg.body_font_en)
                    run.font.size = Pt(cfg.body_font_size)
                    run.italic = True

                elif tag == "code":
                    # 行内代码
                    text = child.get_text()
                    run = p.add_run(text)
                    run.font.name = self.config.content.code_font
                    run.font.size = Pt(self.config.content.code_font_size)
                    # 浅灰背景
                    _add_run_shading(run, self.config.content.code_bg_color)

                elif tag == "a":
                    text = child.get_text()
                    href = child.get("href", "")
                    run = p.add_run(text)
                    _set_cjk_font(run, cfg.body_font_cn, cfg.body_font_en)
                    run.font.size = Pt(cfg.body_font_size)
                    run.font.color.rgb = _hex_to_rgb(self.config.content.link_color)
                    if self.config.content.link_underline:
                        run.underline = True
                    # 添加超链接（通过 XML）
                    if href:
                        self._add_hyperlink(run, href)

                elif tag == "math":
                    # 数学公式 → Word 原生公式（OMML）
                    self._process_math(p, child)

                elif tag == "img":
                    self._process_image(child)

                elif tag == "br":
                    run = p.add_run("\n")

                elif tag == "del" or tag == "s":
                    run = p.add_run(child.get_text())
                    _set_cjk_font(run, cfg.body_font_cn, cfg.body_font_en)
                    run.font.size = Pt(cfg.body_font_size)
                    run.font.strike = True

                else:
                    # 其他标签递归处理
                    self._process_inline_elements(p, child)

    def _process_math(self, p, el: Tag):
        """在段落 p 中插入 Word 原生公式（OMML）。

        - 行内公式 $...$：插入 <m:oMath>，与正文同段
        - 块级公式 $$...$$：插入 <m:oMathPara>，段落居中、取消首行缩进
        - pandoc 不可用 / 转换失败：回退为 LaTeX 纯文本，不丢失内容
        """
        latex = (el.get_text() or "").strip()
        if not latex:
            return

        item = self._omml_cache.get(latex)
        if item is None:
            run = p.add_run(latex)
            _set_cjk_font(run, self.config.typography.body_font_cn,
                          self.config.typography.body_font_en)
            run.font.size = Pt(self.config.typography.body_font_size)
            return

        inline_xml, display_xml = item
        is_display = (el.get("display") == "display")
        omml_el = _parse_omml(display_xml if is_display else inline_xml)
        if omml_el is not None:
            # 追加到段落末尾；后续 add_run 仍按顺序追加，保持正文顺序
            p._element.append(omml_el)
            if is_display:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.first_line_indent = 0
        else:
            run = p.add_run(latex)
            _set_cjk_font(run, self.config.typography.body_font_cn,
                          self.config.typography.body_font_en)
            run.font.size = Pt(self.config.typography.body_font_size)

    def _apply_paragraph_format(self, p):
        """对段落应用通用格式（首行缩进、对齐、间距）"""
        cfg = self.config.typography
        _set_paragraph_spacing(p, cfg)
        _set_alignment(p, cfg.alignment)
        _set_first_line_indent(p, cfg.first_line_indent_chars, cfg.body_font_size)

    def _process_list(self, el: Tag, list_type: str):
        """处理列表"""
        cfg_content = self.config.content
        is_ordered = list_type == "ol"
        items = el.find_all("li", recursive=False)

        for i, li in enumerate(items):
            p = self.doc.add_paragraph()
            bullet = f"{i + 1}." if is_ordered else f"{cfg_content.list_bullet_char} "
            run = p.add_run(bullet + " ")
            _set_cjk_font(run, self.config.typography.body_font_cn, self.config.typography.body_font_en)
            run.font.size = Pt(self.config.typography.body_font_size)

            # 列表项内容（可能有内联元素）
            text_content = li.get_text(strip=True)
            run2 = p.add_run(text_content)
            _set_cjk_font(run2, self.config.typography.body_font_cn, self.config.typography.body_font_en)
            run2.font.size = Pt(self.config.typography.body_font_size)

            # 列表缩进
            p.paragraph_format.left_indent = Cm(cfg_content.list_indent)
            p.paragraph_format.first_line_indent = Cm(-0.63)  # 悬挂缩进

    def _process_blockquote(self, el: Tag):
        """处理引用块"""
        cfg = self.config.content
        cfg_typo = self.config.typography

        # 引用块内的段落
        for child in el.children:
            if isinstance(child, Tag) and child.name == "p":
                text = child.get_text(strip=True)
                if not text:
                    continue
                p = self.doc.add_paragraph()
                run = p.add_run(text)
                _set_cjk_font(run, cfg_typo.body_font_cn, cfg_typo.body_font_en)
                run.font.size = Pt(cfg_typo.body_font_size)
                run.font.italic = True

                # 左侧缩进
                p.paragraph_format.left_indent = Cm(cfg.blockquote_left_indent)
                # 左侧竖线
                _add_paragraph_border_left(p, cfg.blockquote_bar_color)
                # 背景色
                _add_paragraph_shading(p, cfg.blockquote_bg_color)

    def _process_code_block(self, el: Tag):
        """处理代码块"""
        cfg = self.config.content

        # 提取代码文本
        code_el = el.find("code") if el.find("code") else el
        code_text = code_el.get_text() if hasattr(code_el, "get_text") else el.get_text()

        p = self.doc.add_paragraph()
        run = p.add_run(code_text)
        run.font.name = cfg.code_font
        run.font.size = Pt(cfg.code_font_size)

        # 背景色
        _add_paragraph_shading(p, cfg.code_bg_color)

        # 边框
        if cfg.code_border:
            pPr = p._element.get_or_add_pPr()
            pBdr = OxmlElement('w:pBdr')
            for edge in ('top', 'left', 'bottom', 'right'):
                e = OxmlElement(f'w:{edge}')
                e.set(qn('w:val'), 'single')
                e.set(qn('w:sz'), '4')
                e.set(qn('w:space'), '4')
                e.set(qn('w:color'), 'CCCCCC')
                pBdr.append(e)
            pPr.insert(0, pBdr)

    def _process_table(self, el: Tag):
        """处理 HTML 表格 → python-docx Table"""
        cfg = self.config.content
        cfg_typo = self.config.typography

        rows = el.find_all("tr")
        if not rows:
            return

        # 判断表头行
        has_thead = bool(el.find("thead"))
        first_is_header = has_thead or bool(rows[0].find("th"))

        num_cols = max(len(r.find_all(["td", "th"])) for r in rows) if rows else 1
        table = self.doc.add_table(rows=len(rows), cols=num_cols)
        table.style = 'Table Grid'

        for i, tr in enumerate(rows):
            cells = tr.find_all(["td", "th"])
            for j, cell_el in enumerate(cells):
                if j >= num_cols:
                    break
                cell = table.cell(i, j)

                # 单元格文本
                text = cell_el.get_text(strip=True)
                cell.text = ""

                p = cell.paragraphs[0]
                run = p.add_run(text)
                _set_cjk_font(run, cfg_typo.body_font_cn, cfg_typo.body_font_en)
                run.font.size = Pt(cfg_typo.body_font_size)

                # 表头行样式
                if first_is_header and i == 0:
                    _set_cell_shading(cell, cfg.table_header_bg)
                    run.bold = True
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # 边框
        if cfg.table_border:
            _add_table_borders(table, cfg.table_border_color)

    def _process_hr(self):
        """处理水平线 → 空段落 + 底边线"""
        p = self.doc.add_paragraph()
        pPr = p._element.get_or_add_pPr()
        pBdr = OxmlElement('w:pBdr')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), '12')
        bottom.set(qn('w:space'), '1')
        bottom.set(qn('w:color'), '999999')
        pBdr.append(bottom)
        pPr.insert(0, pBdr)

    def _process_image(self, el: Tag):
        """处理图片"""
        cfg = self.config.content
        src = el.get("src", "")
        if not src:
            return

        try:
            img_path = None

            if src.startswith("data:"):
                # Base64 嵌入图片
                match = re.match(r"data:image/\w+;base64,(.+)", src)
                if match:
                    img_data = base64.b64decode(match.group(1))
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                    tmp.write(img_data)
                    tmp.close()
                    img_path = tmp.name
                    self.image_temp_files.append(img_path)
            elif src.startswith(("http://", "https://")):
                # 网络图片：跳过（避免网络请求）
                self.doc.add_paragraph(f"[图片: {src}]")
                return
            else:
                # 本地文件路径
                if os.path.isabs(src):
                    if os.path.exists(src):
                        img_path = src
                else:
                    # 相对路径
                    cwd = os.getcwd()
                    candidate = os.path.join(cwd, src)
                    if os.path.exists(candidate):
                        img_path = candidate

            if img_path:
                # SVG 是矢量图，python-docx 无法直接插入 → 先渲染为 PNG
                if os.path.splitext(img_path)[1].lower() == ".svg":
                    try:
                        from core.engines.image_engine import svg_to_png
                        tmp = img_path + ".docx_tmp.png"
                        if svg_to_png(img_path, tmp, lambda m: None):
                            self.image_temp_files.append(tmp)
                            img_path = tmp
                    except Exception:
                        pass

                # 计算最大宽度
                page_w_cm = self.config.page.paper_size.dimensions_cm()[0]
                if self.config.page.orientation == Orientation.LANDSCAPE:
                    page_w_cm = self.config.page.paper_size.dimensions_cm()[1]
                margin_l = self.config.page.margin_left
                margin_r = self.config.page.margin_right
                usable_cm = page_w_cm - margin_l - margin_r
                max_w_cm = usable_cm * (cfg.image_max_width_pct / 100.0)

                p = self.doc.add_paragraph()
                if cfg.image_center:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

                run = p.add_run()
                run.add_picture(img_path, width=Cm(max_w_cm))
            else:
                alt = el.get("alt", "图片")
                self.doc.add_paragraph(f"[{alt}]")

        except Exception:
            alt = el.get("alt", "图片")
            self.doc.add_paragraph(f"[{alt}: 无法加载]")

    # ── 高级特性 ──────────────────────────

    def _update_heading_counter(self, level: str):
        """更新标题编号计数器"""
        self.heading_counters[level] += 1
        # 重置下级计数器
        if level == "h1":
            self.heading_counters["h2"] = 0
            self.heading_counters["h3"] = 0
        elif level == "h2":
            self.heading_counters["h3"] = 0

    def _get_heading_number(self, level: str) -> str:
        """获取当前标题编号字符串"""
        fmt = self.config.advanced.heading_numbering_format
        nums = []
        if self.heading_counters["h1"] > 0:
            nums.append(str(self.heading_counters["h1"]))
        if level in ("h2", "h3") and self.heading_counters["h2"] > 0:
            nums.append(str(self.heading_counters["h2"]))
        if level == "h3" and self.heading_counters["h3"] > 0:
            nums.append(str(self.heading_counters["h3"]))

        number = ".".join(nums)
        if "1." in fmt:
            return f"{number}."
        elif "1)" in fmt:
            return f"{number})"
        elif "第1章" in fmt:
            return f"第{nums[0]}章" if nums else number
        return number

    def _add_toc(self):
        """插入目录域（TOC field）"""
        if not self.config.advanced.auto_toc:
            return

        # 添加"目录"标题
        heading = self.doc.add_paragraph("目录", style="Heading 1")
        # 清除该段落的编号（避免被编号影响）
        self.heading_counters["h1"] = max(0, self.heading_counters["h1"] - 1)

        # 插入 TOC 域代码
        p = self.doc.add_paragraph()
        run = p.add_run()

        # TOC 域：使用 fldChar 构建
        fldChar_begin = OxmlElement('w:fldChar')
        fldChar_begin.set(qn('w:fldCharType'), 'begin')
        run._element.append(fldChar_begin)

        run2 = p.add_run()
        instrText = OxmlElement('w:instrText')
        instrText.set(qn('xml:space'), 'preserve')
        depth = self.config.advanced.toc_depth
        instrText.text = f' TOC \\o "1-{depth}" \\h \\z \\u '
        run2._element.append(instrText)

        run3 = p.add_run()
        fldChar_separate = OxmlElement('w:fldChar')
        fldChar_separate.set(qn('w:fldCharType'), 'separate')
        run3._element.append(fldChar_separate)

        run4 = p.add_run("（请在 Word 中右键此处 → 更新域 以生成目录）")
        run4.font.size = Pt(9)
        run4.font.color.rgb = RGBColor(150, 150, 150)
        run4.font.italic = True

        run5 = p.add_run()
        fldChar_end = OxmlElement('w:fldChar')
        fldChar_end.set(qn('w:fldCharType'), 'end')
        run5._element.append(fldChar_end)

        # 添加分页
        self.doc.add_page_break()

    def _add_cover_page(self):
        """添加封面页"""
        adv = self.config.advanced
        cfg = self.config.typography

        # 空行撑开
        for _ in range(6):
            self.doc.add_paragraph()

        # 标题
        title_text = adv.cover_title or "未命名文档"
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(title_text)
        _set_cjk_font(run, cfg.headings["h1"].font_cn, cfg.headings["h1"].font_en)
        run.font.size = Pt(28)
        run.bold = True

        # 空行
        self.doc.add_paragraph()

        # 作者
        if adv.cover_author:
            p = self.doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(adv.cover_author)
            _set_cjk_font(run, cfg.body_font_cn, cfg.body_font_en)
            run.font.size = Pt(16)

        # 日期
        date_str = adv.cover_date or datetime.date.today().strftime("%Y年%m月%d日")
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(date_str)
        _set_cjk_font(run, cfg.body_font_cn, cfg.body_font_en)
        run.font.size = Pt(14)

        # 分页
        self.doc.add_page_break()

    def _add_headers_footers(self):
        """设置页眉页脚"""
        adv = self.config.advanced
        section = self.doc.sections[0]

        # 页眉
        if adv.header_text:
            header = section.header
            header.is_linked_to_previous = False
            p = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(adv.header_text)
            run.font.size = Pt(9)
            run.font.color.rgb = RGBColor(128, 128, 128)

        # 页脚
        if adv.footer_text:
            footer = section.footer
            footer.is_linked_to_previous = False
            p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(adv.footer_text)
            run.font.size = Pt(9)
            run.font.color.rgb = RGBColor(128, 128, 128)

    def _add_watermark(self):
        """添加文字水印（通过 XML 操作 header 中的水印）"""
        adv = self.config.advanced
        if not adv.watermark_text:
            return

        try:
            section = self.doc.sections[0]
            header = section.header
            header.is_linked_to_previous = False

            # 水印需要放在 header 中
            p = header.paragraphs[0] if header.paragraphs else header.add_paragraph()

            # 创建水印 run
            run = p.add_run(adv.watermark_text)
            run.font.size = Pt(adv.watermark_font_size)
            run.font.color.rgb = RGBColor(200, 200, 200)  # 浅灰色模拟透明度
            run.font.bold = True

            p.alignment = WD_ALIGN_PARAGRAPH.CENTER

            # 设置水印的透明度通过 XML
            rPr = run._element.get_or_add_rPr()
            # 添加字符间距使水印文字更分散
            spacing = OxmlElement('w:spacing')
            spacing.set(qn('w:val'), '200')
            rPr.append(spacing)

        except Exception:
            # 水印失败不阻塞转换
            pass

    def _add_hyperlink(self, run, url: str):
        """为 run 添加超链接关系"""
        try:
            # 获取或创建 hyperlink 元素
            rPr = run._element.get_or_add_rPr()
            rStyle = rPr.find(qn('w:rStyle'))
            if rStyle is not None:
                # 超链接样式
                rStyle.set(qn('w:val'), 'Hyperlink')
        except Exception:
            pass

    # ── 辅助 ──────────────────────────────

    @staticmethod
    def _read_file(path: str) -> str:
        """读取文件内容"""
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    def _cleanup_temp_files(self):
        """清理临时图片文件"""
        for tmp in self.image_temp_files:
            try:
                if os.path.exists(tmp):
                    os.remove(tmp)
            except Exception:
                pass
        self.image_temp_files.clear()


def _add_run_shading(run, color: str):
    """为行内 run 添加背景色（用于行内代码）"""
    rPr = run._element.get_or_add_rPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), color.lstrip("#"))
    shd.set(qn('w:val'), 'clear')
    rPr.append(shd)


def _set_alignment_obj(para_format, alignment: CfgAlignment):
    """直接在 paragraph_format 对象上设置对齐"""
    mapping = {
        CfgAlignment.LEFT: WD_ALIGN_PARAGRAPH.LEFT,
        CfgAlignment.CENTER: WD_ALIGN_PARAGRAPH.CENTER,
        CfgAlignment.RIGHT: WD_ALIGN_PARAGRAPH.RIGHT,
        CfgAlignment.JUSTIFY: WD_ALIGN_PARAGRAPH.JUSTIFY,
    }
    para_format.alignment = mapping.get(alignment, WD_ALIGN_PARAGRAPH.LEFT)


# ════════════════════════════════════════════
#  便捷函数（供 converters.py 调用）
# ════════════════════════════════════════════

def convert_md_to_docx(
    input_path: str,
    output_path: str,
    config: FormatConfig = None,
    log: Callable[[str], None] = lambda m: None
) -> bool:
    """
    MD → DOCX 高级转换入口。
    如果未提供 config，使用默认中文配置。
    """
    if config is None:
        config = FormatConfig.default_chinese()
    engine = MdToDocxEngine(config)
    return engine.convert(input_path, output_path, log)
