"""
OCTools/core/engines/image_engine.py
───────────────────────────────────────────────
图像引擎（核心引擎层）：图像格式互转（Pillow / cairosvg / vtracer）

覆盖：
  - 图像 → 图像（Pillow 转码；SVG 走 cairosvg 渲染 / 矢量追踪）
  - SVG → PNG 位图（供 图片→文档 等路径复用）
  - 位图 → SVG（优先 vtracer 真矢量追踪，退化 PNG 嵌入）

设计原则：
  - 每个转换函数签名统一为 (input_path, output_path, log) -> bool
"""

import os

from PIL import Image

from core.engines.ffmpeg_utils import (
    PIL_FORMATS,
    _log_done,
    _norm_ext,
    ensure_cairosvg,
    ensure_heif,
    ensure_outdir,
)
from core.utils.file_handler import file_exists


# ════════════════════════════════════════════
#  图像 → 图像
# ════════════════════════════════════════════

def _save_image(img, output_path, dst, log):
    """把 Pillow Image 按目标格式保存（处理透明通道、格式参数）"""
    save_kwargs = {}
    # 调色板（P）模式（如 GIF）→ 先按透明度转 RGBA / RGB，
    # 否则 PPM 等格式报 "cannot write mode P as PPM"
    if img.mode == "P" and dst != "gif":
        img = img.convert("RGBA" if img.info.get("transparency") is not None else "RGB")
    if dst == "pgm":
        # Pillow 12 起不再支持保存 PGM，这里手写 P5 二进制 PGM
        gray = img.convert("L")
        with open(output_path, "wb") as f:
            f.write(f"P5\n{gray.width} {gray.height}\n255\n".encode("ascii"))
            f.write(gray.tobytes())
        return
    if dst == "jpg":
        # JPEG 不支持透明通道：透明背景合成到白色
        if img.mode in ("RGBA", "LA"):
            bg = Image.new("RGB", img.size, "white")
            bg.paste(img, mask=img.split()[-1])
            img = bg
        elif img.mode != "RGB":
            img = img.convert("RGB")
        save_kwargs["quality"] = 92
    elif dst == "webp":
        save_kwargs["quality"] = 90
    elif dst == "gif":
        # 静态 gif；多帧源（如动图）时保留动画
        save_kwargs["save_all"] = True
        save_kwargs["loop"] = 0
    elif dst == "heic":
        save_kwargs["quality"] = 90
    fmt = PIL_FORMATS.get(dst, dst.upper())
    img.save(output_path, fmt, **save_kwargs)


def image_to_image(input_path, output_path, log):
    """图像 → 图像（Pillow 转码；SVG 走 cairosvg 渲染 / 矢量追踪）"""
    if not file_exists(input_path, log): return False
    src = _norm_ext(input_path)
    dst = _norm_ext(output_path)
    if dst == "svg":
        return _to_svg(input_path, output_path, log)
    if dst not in PIL_FORMATS:
        log(f"❌ 不支持的目标图像格式: {dst}")
        return False
    log(f"🖼️ 图像转换: {os.path.basename(input_path)} → {os.path.basename(output_path)}")
    ensure_outdir(output_path)

    # SVG 作为输入：用 cairosvg 渲染成位图
    if src == "svg":
        return _svg_to_bitmap(input_path, output_path, log, dst)

    # HEIC 输入/输出：需要 pillow-heif
    if src == "heic" or dst == "heic":
        if not ensure_heif():
            log("❌ HEIC 需要 pillow-heif，请执行: pip install pillow-heif")
            return False

    try:
        img = Image.open(input_path)
        img.load()
        _save_image(img, output_path, dst, log)
        _log_done(output_path, log, kind="图像")
        return True
    except Exception as e:
        log(f"❌ {e}")
        return False


def _svg_to_bitmap(input_path, output_path, log, dst):
    """SVG → 位图：cairosvg 渲染 PNG 后转目标格式"""
    cairosvg = ensure_cairosvg()
    if cairosvg is None:
        log("❌ SVG 转换需要 cairosvg，请执行: pip install cairosvg")
        return False
    try:
        if dst == "png":
            cairosvg.svg2png(url=input_path, write_to=output_path)
            _log_done(output_path, log, kind="图像")
            return True
        # 其他格式：先渲染 PNG，再用 Pillow 转换
        tmp = output_path + ".tmp.png"
        try:
            cairosvg.svg2png(url=input_path, write_to=tmp)
            img = Image.open(tmp)
            img.load()
            _save_image(img, output_path, dst, log)
            _log_done(output_path, log, kind="图像")
            return True
        finally:
            if os.path.exists(tmp):
                try: os.remove(tmp)
                except OSError: pass
    except Exception as e:
        log(f"❌ SVG 渲染失败: {e}")
        return False


def svg_to_png(input_path, output_path, log):
    """SVG → PNG 位图（cairosvg 渲染；供 图片→文档 等路径复用）"""
    cairosvg = ensure_cairosvg()
    if cairosvg is None:
        log("❌ SVG 转换需要 cairosvg，请执行: pip install cairosvg")
        return False
    try:
        cairosvg.svg2png(url=input_path, write_to=output_path)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return True
        return False
    except Exception as e:
        log(f"❌ SVG 渲染失败: {e}")
        return False


def _to_svg(input_path, output_path, log):
    """位图 → SVG：优先 vtracer 矢量追踪；不可用时退化为 PNG 嵌入 SVG（无损）"""
    if not file_exists(input_path, log): return False
    ensure_outdir(output_path)
    log(f"🖼️ 图像转换: {os.path.basename(input_path)} → {os.path.basename(output_path)}")
    src = _norm_ext(input_path)
    if src == "svg":
        log("❌ 无法把 SVG 再转换为 SVG")
        return False
    tmp = output_path + ".tmp.png"
    try:
        # 先归一化为 PNG（HEIC 需要 pillow-heif）
        if src == "heic" and not ensure_heif():
            log("❌ HEIC 需要 pillow-heif，请执行: pip install pillow-heif")
            return False
        img = Image.open(input_path)
        img.load()
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA" if img.mode == "P" and img.info.get("transparency") is not None
                              else "RGB")
        img.save(tmp, "PNG")

        # 1) 首选 vtracer 真矢量追踪
        try:
            import vtracer
            vtracer.convert_image_to_svg_py(
                tmp, output_path,
                colormode="color", mode="spline",
                filter_speckle=4, corner_threshold=60,
                length_threshold=4.0, splice_threshold=45,
                path_precision=3, max_iterations=10)
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                _log_done(output_path, log, kind="SVG")
                return True
            raise RuntimeError("vtracer 未生成有效输出")
        except ImportError:
            pass
        except Exception as e:
            log(f"⚠ vtracer 追踪失败，改用 PNG 嵌入方式: {e}")

        # 2) 退化：PNG 以 base64 嵌入 SVG（任意环境可用，无损）
        import base64
        with open(tmp, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        svg_text = (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{img.width}" height="{img.height}" viewBox="0 0 {img.width} {img.height}">'
            f'<image width="{img.width}" height="{img.height}" '
            f'xlink:href="data:image/png;base64,{b64}"/></svg>'
        )
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(svg_text)
        _log_done(output_path, log, kind="SVG")
        return True
    except Exception as e:
        log(f"❌ 导出 SVG 失败: {e}")
        return False
    finally:
        if os.path.exists(tmp):
            try: os.remove(tmp)
            except OSError: pass
