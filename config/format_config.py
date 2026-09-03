"""
octool/config/format_config.py
───────────────────────────────────────────────
MD → DOCX 完整格式配置（最小功能单元）：FormatConfig

聚合四类子配置（页面布局 / 字体排版 / 内容样式 / 高级特性），
提供预设工厂、验证与 JSON 序列化。

子配置拆分到独立模块：
  - page_layout.py  页面布局（PaperSize/Orientation/边距/装订线）
  - heading.py      单个标题级别样式
  - typography.py   字体与排版
  - content.py      内容样式映射
  - advanced.py     高级特性
"""

from dataclasses import dataclass, field
from typing import List
import json

from config.enums import Alignment, LineSpacingMode, Orientation, PaperSize
from config.page_layout import PageLayout
from config.heading import HeadingStyle
from config.typography import Typography
from config.content import ContentStyles
from config.advanced import AdvancedFeatures


@dataclass
class FormatConfig:
    """MD → DOCX 完整格式配置"""
    # 元数据
    name: str = "默认配置"
    description: str = "内置默认中文排版配置"
    version: str = "1.0"

    # 子配置
    page: PageLayout = field(default_factory=PageLayout)
    typography: Typography = field(default_factory=Typography)
    content: ContentStyles = field(default_factory=ContentStyles)
    advanced: AdvancedFeatures = field(default_factory=AdvancedFeatures)

    # ── 工厂方法 ────────────────────────

    @classmethod
    def default_chinese(cls) -> "FormatConfig":
        """中文排版默认配置（宋体小四，首行缩进2字符，左对齐）"""
        return FormatConfig(
            name="默认配置",
            description="符合中文出版规范的默认配置",
            page=PageLayout(),
            typography=Typography(
                body_font_cn="宋体",
                body_font_en="Times New Roman",
                body_font_size=12.0,
                first_line_indent_chars=2.0,
                alignment=Alignment.LEFT,
                line_spacing_mode=LineSpacingMode.MULTIPLE,
                line_spacing=1.5,
            ),
            content=ContentStyles(),
            advanced=AdvancedFeatures(),
        )

    @classmethod
    def default_western(cls) -> "FormatConfig":
        """西文排版默认配置（无首行缩进，左对齐）"""
        return FormatConfig(
            name="Western Default",
            description="Western typesetting defaults",
            page=PageLayout(margin_left=2.54, margin_right=2.54),
            typography=Typography(
                body_font_cn="Calibri",
                body_font_en="Calibri",
                body_font_size=11.0,
                first_line_indent_chars=0.0,
                alignment=Alignment.LEFT,
                line_spacing_mode=LineSpacingMode.MULTIPLE,
                line_spacing=1.15,
                headings={
                    "h1": HeadingStyle(font_cn="Calibri", font_en="Calibri", font_size=20.0),
                    "h2": HeadingStyle(font_cn="Calibri", font_en="Calibri", font_size=16.0),
                    "h3": HeadingStyle(font_cn="Calibri", font_en="Calibri", font_size=13.0),
                },
            ),
            content=ContentStyles(
                list_bullet_char="•",
                code_font="Consolas",
            ),
            advanced=AdvancedFeatures(),
        )

    @classmethod
    def paper_format(cls) -> "FormatConfig":
        """论文格式预设"""
        return FormatConfig(
            name="论文格式",
            description="适合学术论文的中文排版：宋体小四、首行缩进2字符、标题编号、目录",
            page=PageLayout(
                paper_size=PaperSize.A4,
                margin_top=2.54,
                margin_bottom=2.54,
                margin_left=3.18,
                margin_right=3.18,
            ),
            typography=Typography(
                body_font_cn="宋体",
                body_font_en="Times New Roman",
                body_font_size=12.0,
                first_line_indent_chars=2.0,
                alignment=Alignment.LEFT,
                line_spacing_mode=LineSpacingMode.MULTIPLE,
                line_spacing=1.5,
                headings={
                    "h1": HeadingStyle(font_cn="黑体", font_en="Arial", font_size=22.0, bold=True),
                    "h2": HeadingStyle(font_cn="黑体", font_en="Arial", font_size=18.0, bold=True),
                    "h3": HeadingStyle(font_cn="黑体", font_en="Arial", font_size=14.0, bold=True),
                },
            ),
            content=ContentStyles(),
            advanced=AdvancedFeatures(
                heading_numbering=True,
                auto_toc=True,
                toc_depth=3,
                cover_enabled=False,
            ),
        )

    @classmethod
    def report_format(cls) -> "FormatConfig":
        """周报格式预设"""
        return FormatConfig(
            name="周报格式",
            description="适合职场周报/日报：微软雅黑五号，无缩进，简洁排版",
            page=PageLayout(
                paper_size=PaperSize.A4,
                margin_top=2.0,
                margin_bottom=2.0,
                margin_left=2.5,
                margin_right=2.5,
            ),
            typography=Typography(
                body_font_cn="微软雅黑",
                body_font_en="Calibri",
                body_font_size=10.5,
                first_line_indent_chars=0.0,
                alignment=Alignment.LEFT,
                line_spacing_mode=LineSpacingMode.MULTIPLE,
                line_spacing=1.25,
                headings={
                    "h1": HeadingStyle(font_cn="微软雅黑", font_en="Calibri", font_size=16.0, bold=True),
                    "h2": HeadingStyle(font_cn="微软雅黑", font_en="Calibri", font_size=14.0, bold=True),
                    "h3": HeadingStyle(font_cn="微软雅黑", font_en="Calibri", font_size=12.0, bold=True),
                },
            ),
            content=ContentStyles(),
            advanced=AdvancedFeatures(
                heading_numbering=False,
                auto_toc=False,
                header_text="",
                footer_text="",
            ),
        )

    # ── 验证 ────────────────────────────

    def validate(self) -> List[str]:
        """验证所有配置，返回错误列表（空列表表示全部通过）"""
        errors = []
        errors.extend(self.page.validate())
        errors.extend(self.typography.validate())
        errors.extend(self.content.validate())
        errors.extend(self.advanced.validate())
        return errors

    # ── 序列化 ──────────────────────────

    def to_dict(self) -> dict:
        """转为纯字典（用于 JSON 序列化）"""
        result = {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "page": {
                "paper_size": self.page.paper_size.value,
                "orientation": self.page.orientation.value,
                "margin_top": self.page.margin_top,
                "margin_bottom": self.page.margin_bottom,
                "margin_left": self.page.margin_left,
                "margin_right": self.page.margin_right,
                "gutter": self.page.gutter,
            },
            "typography": {
                "body_font_cn": self.typography.body_font_cn,
                "body_font_en": self.typography.body_font_en,
                "body_font_size": self.typography.body_font_size,
                "body_color": self.typography.body_color,
                "headings": {},
                "line_spacing_mode": self.typography.line_spacing_mode.value,
                "line_spacing": self.typography.line_spacing,
                "line_spacing_fixed": self.typography.line_spacing_fixed,
                "para_space_before": self.typography.para_space_before,
                "para_space_after": self.typography.para_space_after,
                "first_line_indent_chars": self.typography.first_line_indent_chars,
                "alignment": self.typography.alignment.value,
            },
            "content": {
                "list_bullet_char": self.content.list_bullet_char,
                "list_indent": self.content.list_indent,
                "blockquote_bar_color": self.content.blockquote_bar_color,
                "blockquote_bg_color": self.content.blockquote_bg_color,
                "blockquote_left_indent": self.content.blockquote_left_indent,
                "code_font": self.content.code_font,
                "code_font_size": self.content.code_font_size,
                "code_bg_color": self.content.code_bg_color,
                "code_border": self.content.code_border,
                "table_header_bg": self.content.table_header_bg,
                "table_border": self.content.table_border,
                "table_border_color": self.content.table_border_color,
                "image_max_width_pct": self.content.image_max_width_pct,
                "image_center": self.content.image_center,
                "link_color": self.content.link_color,
                "link_underline": self.content.link_underline,
            },
            "advanced": {
                "heading_numbering": self.advanced.heading_numbering,
                "heading_numbering_format": self.advanced.heading_numbering_format,
                "auto_toc": self.advanced.auto_toc,
                "toc_depth": self.advanced.toc_depth,
                "header_text": self.advanced.header_text,
                "footer_text": self.advanced.footer_text,
                "cover_enabled": self.advanced.cover_enabled,
                "cover_title": self.advanced.cover_title,
                "cover_author": self.advanced.cover_author,
                "cover_date": self.advanced.cover_date,
                "watermark_text": self.advanced.watermark_text,
                "watermark_font_size": self.advanced.watermark_font_size,
                "watermark_opacity": self.advanced.watermark_opacity,
            },
        }
        # 序列化 headings
        for level, hs in self.typography.headings.items():
            result["typography"]["headings"][level] = {
                "font_cn": hs.font_cn,
                "font_en": hs.font_en,
                "font_size": hs.font_size,
                "bold": hs.bold,
                "color": hs.color,
                "alignment": hs.alignment.value,
            }
        return result

    def to_json(self, indent: int = 2) -> str:
        """转为 JSON 字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    @classmethod
    def from_dict(cls, d: dict) -> "FormatConfig":
        """从字典恢复配置"""
        page_d = d.get("page", {})
        page = PageLayout(
            paper_size=PaperSize(page_d.get("paper_size", "A4")),
            orientation=Orientation(page_d.get("orientation", "portrait")),
            margin_top=page_d.get("margin_top", 2.54),
            margin_bottom=page_d.get("margin_bottom", 2.54),
            margin_left=page_d.get("margin_left", 3.18),
            margin_right=page_d.get("margin_right", 3.18),
            gutter=page_d.get("gutter", 0.0),
        )

        typo_d = d.get("typography", {})
        headings = {}
        for level in ("h1", "h2", "h3"):
            hd = typo_d.get("headings", {}).get(level, {})
            headings[level] = HeadingStyle(
                font_cn=hd.get("font_cn", "黑体"),
                font_en=hd.get("font_en", "Arial"),
                font_size=hd.get("font_size", 22.0 if level == "h1" else 18.0 if level == "h2" else 14.0),
                bold=hd.get("bold", True),
                color=hd.get("color", "#000000"),
                alignment=Alignment(hd.get("alignment", "left")),
            )
        typography = Typography(
            body_font_cn=typo_d.get("body_font_cn", "宋体"),
            body_font_en=typo_d.get("body_font_en", "Times New Roman"),
            body_font_size=typo_d.get("body_font_size", 12.0),
            body_color=typo_d.get("body_color", "#000000"),
            headings=headings,
            line_spacing_mode=LineSpacingMode(typo_d.get("line_spacing_mode", "multiple")),
            line_spacing=typo_d.get("line_spacing", 1.5),
            line_spacing_fixed=typo_d.get("line_spacing_fixed", 20.0),
            para_space_before=typo_d.get("para_space_before", 0.0),
            para_space_after=typo_d.get("para_space_after", 0.0),
            first_line_indent_chars=typo_d.get("first_line_indent_chars", 0.0),
            alignment=Alignment(typo_d.get("alignment", "left")),
        )

        content_d = d.get("content", {})
        content = ContentStyles(
            list_bullet_char=content_d.get("list_bullet_char", "●"),
            list_indent=content_d.get("list_indent", 0.63),
            blockquote_bar_color=content_d.get("blockquote_bar_color", "#CCCCCC"),
            blockquote_bg_color=content_d.get("blockquote_bg_color", "#F5F5F5"),
            blockquote_left_indent=content_d.get("blockquote_left_indent", 1.27),
            code_font=content_d.get("code_font", "Consolas"),
            code_font_size=content_d.get("code_font_size", 9.0),
            code_bg_color=content_d.get("code_bg_color", "#F4F4F4"),
            code_border=content_d.get("code_border", True),
            table_header_bg=content_d.get("table_header_bg", "#D9E2F3"),
            table_border=content_d.get("table_border", True),
            table_border_color=content_d.get("table_border_color", "#000000"),
            image_max_width_pct=content_d.get("image_max_width_pct", 80.0),
            image_center=content_d.get("image_center", True),
            link_color=content_d.get("link_color", "#0563C1"),
            link_underline=content_d.get("link_underline", True),
        )

        adv_d = d.get("advanced", {})
        advanced = AdvancedFeatures(
            heading_numbering=adv_d.get("heading_numbering", False),
            heading_numbering_format=adv_d.get("heading_numbering_format", "1."),
            auto_toc=adv_d.get("auto_toc", False),
            toc_depth=adv_d.get("toc_depth", 3),
            header_text=adv_d.get("header_text", ""),
            footer_text=adv_d.get("footer_text", ""),
            cover_enabled=adv_d.get("cover_enabled", False),
            cover_title=adv_d.get("cover_title", ""),
            cover_author=adv_d.get("cover_author", ""),
            cover_date=adv_d.get("cover_date", ""),
            watermark_text=adv_d.get("watermark_text", ""),
            watermark_font_size=adv_d.get("watermark_font_size", 72.0),
            watermark_opacity=adv_d.get("watermark_opacity", 0.1),
        )

        return FormatConfig(
            name=d.get("name", "未命名配置"),
            description=d.get("description", ""),
            version=d.get("version", "1.0"),
            page=page,
            typography=typography,
            content=content,
            advanced=advanced,
        )

    @classmethod
    def from_json(cls, json_str: str) -> "FormatConfig":
        """从 JSON 字符串恢复配置"""
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def from_file(cls, path: str) -> "FormatConfig":
        """从 JSON 文件加载配置"""
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_json(f.read())

    def save_to_file(self, path: str):
        """保存配置到 JSON 文件"""
        import os
        os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_json())
