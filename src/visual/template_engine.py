"""
Template editorial fixo: gradiente, hero com blur de fundo, overlay, título, selo, @marca.
"""

from __future__ import annotations

import logging
import os
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

import config
from visual.brand_style import get_style, topic_to_label

logger = logging.getLogger(__name__)


def _vertical_gradient(size: tuple[int, int], top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    w, h = size
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        for x in range(w):
            px[x, y] = (r, g, b)
    return img


def _load_font(size: int):
    from PIL import ImageFont

    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf",
    ]
    for path in candidates:
        if os.path.isfile(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def _rounded_alpha_mask(size: tuple[int, int], radius: int) -> Image.Image:
    m = Image.new("L", size, 0)
    draw = ImageDraw.Draw(m)
    draw.rounded_rectangle((0, 0, size[0], size[1]), radius=radius, fill=255)
    return m


def _contain_resize(im: Image.Image, max_w: int, max_h: int) -> Image.Image:
    im = im.copy()
    im.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
    return im


def _apply_rounded_hero(im: Image.Image, radius: int) -> Image.Image:
    im = im.convert("RGBA")
    mask = _rounded_alpha_mask(im.size, radius)
    out = Image.new("RGBA", im.size)
    out.paste(im, (0, 0))
    out.putalpha(mask)
    return out


def _title_lines(title: str, max_lines: int) -> list[str]:
    t = " ".join(title.split())
    if len(t) > 240:
        t = t[:237] + "…"
    lines = textwrap.wrap(t, width=34) or [t[:40]]
    return lines[:max_lines]


def render_template(
    base_image: Path,
    title: str,
    category: str,
    subtitle: str | None = None,
) -> Path:
    W, H = config.VISUAL_CANVAS_W, config.VISUAL_CANVAS_H
    style = get_style(category)
    label = topic_to_label(category)

    base = Image.open(base_image).convert("RGBA")
    hero = _contain_resize(base, 960, 760)
    hero_rounded = _apply_rounded_hero(hero, radius=22)

    canvas = _vertical_gradient((W, H), style["gradient_top"], style["gradient_bottom"]).convert("RGBA")

    # Blur de fundo a partir do hero (camada editorial)
    blur_src = hero.convert("RGB").resize((min(W, 1200), int(H * 0.5)), Image.Resampling.LANCZOS)
    blur_src = blur_src.filter(ImageFilter.GaussianBlur(radius=16))
    bx = (W - blur_src.width) // 2
    canvas.paste(blur_src, (bx, 100))

    hx = (W - hero_rounded.width) // 2
    hy = 130
    canvas.alpha_composite(hero_rounded, (hx, hy))

    # Faixa escura inferior para contraste do texto
    overlay_dark = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay_dark)
    od.rectangle((0, int(H * 0.54), W, H), fill=(0, 0, 0, 175))
    canvas = Image.alpha_composite(canvas, overlay_dark)

    img = canvas.convert("RGB")
    draw = ImageDraw.Draw(img)

    font_title = _load_font(36)
    font_sub = _load_font(21)
    font_badge = _load_font(19)
    font_handle = _load_font(22)

    # Selo
    pad = 14
    bbox = draw.textbbox((0, 0), label, font=font_badge)
    bw = bbox[2] - bbox[0] + pad * 2
    bh = bbox[3] - bbox[1] + pad
    draw.rounded_rectangle((36, 36, 36 + bw, 36 + bh), radius=8, fill=style["badge_bg"])
    draw.text((36 + pad, 36 + pad // 2), label, fill=(255, 255, 255), font=font_badge)

    y0 = int(H * 0.58)
    lines = _title_lines(title, 4)
    lh = 44
    for i, line in enumerate(lines):
        draw.text((44, y0 + i * lh), line, fill=(255, 255, 255), font=font_title)

    if subtitle:
        sub = " ".join(subtitle.split())[:160]
        if len(sub) > 140:
            sub = sub[:137] + "…"
        draw.text((44, y0 + len(lines) * lh + 10), sub, fill=(200, 205, 215), font=font_sub)

    handle = f"@{config.BRAND_HANDLE.lstrip('@')}"
    hb = draw.textbbox((0, 0), handle, font=font_handle)
    draw.text((W - (hb[2] - hb[0]) - 44, H - 64), handle, fill=style["accent"], font=font_handle)

    config.VISUAL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out = config.VISUAL_OUTPUT_DIR / f"post_{abs(hash(title)) % 10_000_000}_final.jpg"
    img.save(out, format="JPEG", quality=94, optimize=True)
    logger.info("Template renderizado: %s", out.name)
    return out
