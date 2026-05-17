#!/usr/bin/env python3
"""
Apple-style WeChat publishing asset builder.

Reads a Markdown file with YAML-ish frontmatter and produces:
  - WeChat-compatible inline HTML (for draft body)
  - Standalone preview HTML (for local browser preview)
  - Cover image JPG (white Apple-style cover + black title + muted metadata)

Style: Apple-inspired minimalism.
  - Paper white page, ink text, muted gray secondary
  - Single accent color: Apple blue (#0071E3)
  - Typography-driven hierarchy, no color blocks or cards
  - Thin dividers between sections
  - Author bio footer fixed inside this file (edit AUTHOR_BIO to change)

Environment variables (all optional; defaults suit single-article dev loop):
  WECHAT_MD       source markdown path
  WECHAT_HTML     output WeChat HTML body path
  WECHAT_PREVIEW  output standalone preview HTML path
  WECHAT_COVER    output cover JPG path
"""
from __future__ import annotations

import html
import os
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
SOURCE = Path(os.environ.get("WECHAT_MD", ROOT / "AI输出Markdown格式.md"))
HTML_OUT = Path(os.environ.get("WECHAT_HTML", SOURCE.with_suffix(".wechat.html")))
PREVIEW_OUT = Path(os.environ.get("WECHAT_PREVIEW", SOURCE.with_suffix(".preview.html")))
COVER_OUT = Path(os.environ.get("WECHAT_COVER", SOURCE.with_suffix(".cover.jpg")))


# Apple-inspired palette. Accent uses 墨蓝 (Ink Blue) — same brand color as the cover.
C = {
    "ink": "#1D1D1F",        # primary text
    "sub": "#6E6E73",        # secondary text
    "muted": "#86868B",      # tertiary / meta text
    "line": "#D2D2D7",       # dividers
    "bg": "#FBFBFD",         # page background
    "card": "#F5F5F7",       # inline code background
    "accent": "#243A56",     # 墨蓝 (Ink Blue, light end) — eyebrow / blockquote border
    "accent_dark": "#15263D",  # 墨蓝 (Ink Blue, dark end)
}

FONT_STACK = (
    "-apple-system,BlinkMacSystemFont,'SF Pro Text','SF Pro Display',"
    "'PingFang SC','Helvetica Neue','Microsoft YaHei',Arial,sans-serif"
)

# 标题专用字体栈：宋体优先，正文继续用 PingFang sans。
# 灵感来自 nexu-io/html-anything 的 doc-kami-parchment skill。
# 设计逻辑：中文 serif 标题 + sans 正文 = "刊物感"，避免全 sans 的"博客感"。
# macOS/iOS 读者会看到 Songti SC（最常见），其他系统降级到 Noto Serif / 系统 serif。
FONT_STACK_HEADING = (
    "'Songti SC','Source Han Serif SC','Noto Serif CJK SC',"
    "'Noto Serif SC','STSong',Georgia,"
    "'PingFang SC','Microsoft YaHei',serif"
)


# GFM Alert labels — 把 GitHub `> [!XXX]` 转成中文铭牌。
# 参考 doocs/md (12.6k★) 的 GFM Alert 实现，简化为饶秋风格的
# 单一墨蓝边框 + 铭牌标签，符合视觉禁区"no colored boxes"硬规则。
ALERT_LABELS: dict[str, str] = {
    "NOTE": "注",
    "TIP": "小贴士",
    "IMPORTANT": "重点",
    "WARNING": "注意",
    "CAUTION": "警示",
}


# 微信公众号草稿 API 硬限制：单篇 content 字段 < 20,000 字符。
# 参考 geekjourneyx/md2wechat-skill (2.2k★) 项目踩坑记录。
# 超过会发不出去，所以在 19,000 字预警。
WECHAT_DRAFT_CHAR_LIMIT = 20000
WECHAT_DRAFT_WARN_AT = 19000


AUTHOR_BIO_HTML = (
    f'<section style="margin:44px 0 8px 0;padding-top:24px;'
    f'border-top:1px solid {C["line"]};">'
    f'<p style="margin:0 0 10px 0;color:{C["muted"]};font-size:11.5px;'
    f'letter-spacing:2px;font-weight:600;">关 于 饶 秋</p>'
    f'<p style="margin:0 0 8px 0;color:{C["ink"]};font-size:15px;'
    f'line-height:1.75;font-weight:500;">一个用 AI 干活的人。</p>'
    f'<p style="margin:0 0 8px 0;color:{C["sub"]};font-size:14px;'
    f'line-height:1.8;">上市公司运营总监，业余给企业和高校讲 AI 课。</p>'
    f'<p style="margin:0;color:{C["sub"]};font-size:14px;line-height:1.8;">'
    f'这里写真实工作里的 AI 判断与方法。</p>'
    f'</section>'
)


# -----------------------------
# Frontmatter parsing
# -----------------------------
def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end]
    body = text[end + 5:]
    meta: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        meta[key.strip()] = value
    return meta, body


# -----------------------------
# Markdown → Apple-style HTML
# -----------------------------
def inline(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(
        r"`([^`]+)`",
        rf'<code style="background:{C["card"]};color:{C["ink"]};padding:1px 5px;'
        rf'border-radius:3px;font-size:13px;font-family:Menlo,Consolas,\'SF Mono\','
        rf"monospace;\">\1</code>",
        escaped,
    )
    escaped = re.sub(
        r"\*\*([^*]+)\*\*",
        rf'<strong style="color:{C["ink"]};font-weight:600;">\1</strong>',
        escaped,
    )
    return escaped


def p(text: str) -> str:
    return (
        f'<p style="margin:14px 0;color:{C["ink"]};font-size:15.5px;'
        f'line-height:1.9;font-weight:400;">{inline(text)}</p>'
    )


def flush_paragraph(parts: list[str], out: list[str]) -> None:
    if not parts:
        return
    text = " ".join(s.strip() for s in parts if s.strip())
    if text:
        out.append(p(text))
    parts.clear()


def flush_list(items: list[str], out: list[str]) -> None:
    if not items:
        return
    lis = "".join(
        f'<li style="margin:8px 0;color:{C["ink"]};font-size:15.5px;'
        f'line-height:1.85;padding-left:4px;">{inline(item)}</li>'
        for item in items
    )
    out.append(
        f'<ul style="margin:14px 0;padding-left:20px;list-style:disc;'
        f'color:{C["muted"]};">{lis}</ul>'
    )
    items.clear()


def flush_numbered(items: list[str], out: list[str]) -> None:
    if not items:
        return
    lis = "".join(
        f'<li style="margin:8px 0;color:{C["ink"]};font-size:15.5px;'
        f'line-height:1.85;padding-left:4px;">{inline(item)}</li>'
        for item in items
    )
    out.append(
        f'<ol style="margin:14px 0;padding-left:22px;color:{C["muted"]};">{lis}</ol>'
    )
    items.clear()


def render_table(headers: list[str], rows: list[list[str]]) -> str:
    th_cells = "".join(
        f'<th style="padding:10px 12px;border-bottom:2px solid {C["ink"]};'
        f'text-align:left;color:{C["ink"]};font-weight:600;font-size:13.5px;'
        f'background:{C["card"]};">{inline(cell)}</th>'
        for cell in headers
    )
    body_rows: list[str] = []
    for row in rows:
        cells = list(row) + [""] * (len(headers) - len(row))
        cells = cells[: len(headers)]
        td_cells = "".join(
            f'<td style="padding:10px 12px;border-bottom:1px solid {C["line"]};'
            f'color:{C["ink"]};font-size:14px;line-height:1.7;'
            f'vertical-align:top;">{inline(cell)}</td>'
            for cell in cells
        )
        body_rows.append(f"<tr>{td_cells}</tr>")
    return (
        f'<table style="margin:18px 0;border-collapse:collapse;width:100%;'
        f'font-family:{FONT_STACK};">'
        f'<thead><tr>{th_cells}</tr></thead>'
        f'<tbody>{"".join(body_rows)}</tbody></table>'
    )


_TABLE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")
_TABLE_DELIM_RE = re.compile(r"^\s*\|[\s\-:|]+\|\s*$")


def _split_table_row(line: str) -> list[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [cell.strip() for cell in stripped.split("|")]


def render_body(body: str) -> str:
    out: list[str] = []
    paragraph: list[str] = []
    bullets: list[str] = []
    numbered: list[str] = []
    in_code = False
    code_lines: list[str] = []

    def flush_all() -> None:
        flush_paragraph(paragraph, out)
        flush_list(bullets, out)
        flush_numbered(numbered, out)

    lines = body.splitlines()
    i = 0
    while i < len(lines):
        raw_line = lines[i]
        line = raw_line.rstrip()

        if line.startswith("```"):
            if in_code:
                code_html = html.escape("\n".join(code_lines))
                out.append(
                    f'<pre style="margin:18px 0;padding:14px 16px;'
                    f'background:{C["card"]};border-radius:6px;'
                    f'white-space:pre-wrap;word-break:break-word;'
                    f'color:{C["ink"]};font-size:13px;line-height:1.7;'
                    f"font-family:Menlo,Consolas,'SF Mono',monospace;\">"
                    f'{code_html}</pre>'
                )
                code_lines.clear()
                in_code = False
            else:
                flush_all()
                in_code = True
            i += 1
            continue

        if in_code:
            code_lines.append(line)
            i += 1
            continue

        if not line.strip():
            flush_all()
            i += 1
            continue

        if line.strip() == "---":
            flush_all()
            # Ornamental section divider — three centered dots in serif,
            # replaces the plain <hr>. Reads as "出版物分章" instead of
            # "网页分割"。
            out.append(
                f'<div style="margin:36px 0;text-align:center;'
                f'color:{C["muted"]};font-family:{FONT_STACK_HEADING};'
                f'font-size:14px;letter-spacing:14px;">·  ·  ·</div>'
            )
            i += 1
            continue

        if (
            i + 1 < len(lines)
            and _TABLE_ROW_RE.match(line)
            and _TABLE_DELIM_RE.match(lines[i + 1].rstrip())
        ):
            flush_all()
            headers = _split_table_row(line)
            j = i + 2
            data_rows: list[list[str]] = []
            while j < len(lines) and _TABLE_ROW_RE.match(lines[j].rstrip()):
                data_rows.append(_split_table_row(lines[j].rstrip()))
                j += 1
            out.append(render_table(headers, data_rows))
            i = j
            continue

        h = re.match(r"^(#{2,4})\s+(.+)$", line)
        if h:
            flush_all()
            level = len(h.group(1))
            text = h.group(2)
            if level == 2:
                out.append(
                    f'<h2 style="margin:38px 0 12px 0;color:{C["ink"]};'
                    f'font-family:{FONT_STACK_HEADING};'
                    f'font-size:20px;line-height:1.4;font-weight:600;'
                    f'letter-spacing:0.5px;">{inline(text)}</h2>'
                )
            elif level == 3:
                out.append(
                    f'<h3 style="margin:24px 0 8px 0;color:{C["ink"]};'
                    f'font-family:{FONT_STACK_HEADING};'
                    f'font-size:17px;line-height:1.45;font-weight:600;'
                    f'letter-spacing:0.3px;">'
                    f'{inline(text)}</h3>'
                )
            else:
                out.append(
                    f'<h4 style="margin:18px 0 6px 0;color:{C["ink"]};'
                    f'font-family:{FONT_STACK_HEADING};'
                    f'font-size:15.5px;line-height:1.5;font-weight:600;'
                    f'letter-spacing:0.2px;">{inline(text)}</h4>'
                )
            i += 1
            continue

        if line.startswith(">"):
            flush_all()
            # Collect ALL consecutive '>' lines into one quote block.
            # Supports GFM Alert syntax: `> [!NOTE]` / `> [!TIP]` / etc.
            quote_lines: list[str] = []
            while i < len(lines):
                ql = lines[i].rstrip()
                if not ql.startswith(">"):
                    break
                # Strip leading '> ' or '>'
                if ql.startswith("> "):
                    quote_lines.append(ql[2:])
                elif ql == ">":
                    quote_lines.append("")
                else:
                    quote_lines.append(ql[1:])
                i += 1

            # GFM Alert detection: first line is exactly `[!TYPE]`
            alert_match = (
                re.match(r"^\[!(\w+)\]\s*$", quote_lines[0])
                if quote_lines else None
            )

            if alert_match:
                alert_type = alert_match.group(1).upper()
                label = ALERT_LABELS.get(alert_type, alert_type)
                # Join body lines (skip the first [!TYPE] line); preserve
                # paragraph breaks by joining empty lines with double-space.
                body_text = " ".join(
                    l.strip() for l in quote_lines[1:] if l.strip()
                )
                out.append(
                    f'<section style="margin:22px 0;padding:8px 0 8px 18px;'
                    f'border-left:3px solid {C["accent"]};">'
                    f'<p style="margin:0 0 6px 0;color:{C["accent"]};'
                    f'font-size:11.5px;font-weight:700;letter-spacing:3px;">'
                    f'{label}</p>'
                    f'<p style="margin:0;color:{C["ink"]};font-size:15px;'
                    f'line-height:1.85;">{inline(body_text)}</p>'
                    f'</section>'
                )
            else:
                # Regular blockquote: join all lines with a space
                full_text = " ".join(
                    l.strip() for l in quote_lines if l.strip()
                )
                out.append(
                    f'<blockquote style="margin:18px 0;padding:4px 0 4px 16px;'
                    f'border-left:3px solid {C["accent"]};color:{C["sub"]};'
                    f'font-size:15.5px;line-height:1.9;font-style:normal;">'
                    f'{inline(full_text)}</blockquote>'
                )
            continue

        b = re.match(r"^[-*]\s+(.+)$", line)
        if b:
            flush_paragraph(paragraph, out)
            flush_numbered(numbered, out)
            bullets.append(b.group(1))
            i += 1
            continue

        n = re.match(r"^\d+\.\s+(.+)$", line)
        if n:
            flush_paragraph(paragraph, out)
            flush_list(bullets, out)
            numbered.append(n.group(1))
            i += 1
            continue

        flush_list(bullets, out)
        flush_numbered(numbered, out)
        paragraph.append(line)
        i += 1

    flush_all()
    return "".join(out)


def render_article(meta: dict[str, str], body: str) -> str:
    title = meta.get("title", "未命名文章")
    digest = meta.get("digest", "")
    eyebrow = meta.get("eyebrow", "").strip()

    header_parts: list[str] = []
    if eyebrow:
        header_parts.append(
            f'<p style="margin:0 0 16px 0;color:{C["accent"]};font-size:11.5px;'
            f'letter-spacing:3px;font-weight:600;text-transform:uppercase;">'
            f'{inline(eyebrow)}</p>'
        )
    header_parts.append(
        f'<h1 style="margin:0 0 16px 0;color:{C["ink"]};'
        f'font-family:{FONT_STACK_HEADING};'
        f'font-size:26px;line-height:1.35;font-weight:700;'
        f'letter-spacing:1px;">'
        f'{inline(title)}</h1>'
    )
    if digest:
        header_parts.append(
            f'<p style="margin:0 0 20px 0;color:{C["sub"]};font-size:14.5px;'
            f'line-height:1.8;font-weight:400;">{inline(digest)}</p>'
        )
    header_parts.append(
        f'<div style="width:28px;height:2px;background:{C["accent"]};'
        f'margin:4px 0 0 0;border-radius:1px;"></div>'
    )
    header_html = (
        f'<section style="margin:0 0 32px 0;">{"".join(header_parts)}</section>'
    )

    return (
        f'<section style="max-width:677px;margin:0 auto;padding:28px 16px;'
        f'background:{C["bg"]};font-family:{FONT_STACK};color:{C["ink"]};">'
        + header_html
        + render_body(body)
        + AUTHOR_BIO_HTML
        + '</section>'
    )


# -----------------------------
# Cover image — Keynote 双行节奏 (kicker + main title)
# -----------------------------
# 饶秋公众号封面品牌色：墨蓝 / Ink Blue（仅用作装饰短线点缀）
# 来源：中国传统墨色干在纸上的蓝调，"写字人的颜色"
INK_BLUE_DARK = (21, 38, 61)    # #15263D
INK_BLUE_LIGHT = (36, 58, 86)   # #243A56 — used as accent rule color


def _add_radial_gradient(base: Image.Image,
                         center_pct: tuple[float, float],
                         radius_pct: float,
                         color: tuple[int, int, int],
                         max_alpha: float = 0.65) -> Image.Image:
    """
    Blend a soft radial gradient overlay onto a base image.
    Generated at 1/4 resolution for speed, then bilinearly upscaled —
    looks identical to the full-res version but ~16× faster.
    """
    width, height = base.size

    scale = 4
    sw, sh = width // scale, height // scale
    cx = sw * center_pct[0]
    cy = sh * center_pct[1]
    radius = min(sw, sh) * radius_pct

    mask = Image.new("L", (sw, sh), 0)
    mask_pixels = mask.load()
    for y in range(sh):
        for x in range(sw):
            dx = x - cx
            dy = y - cy
            dist = (dx * dx + dy * dy) ** 0.5
            if dist >= radius:
                continue
            t = 1.0 - dist / radius
            t = t * t * (3 - 2 * t)  # smoothstep falloff
            mask_pixels[x, y] = int(t * 255 * max_alpha)

    mask = mask.resize((width, height), Image.BILINEAR)
    overlay = Image.new("RGB", (width, height), color)
    return Image.composite(overlay, base, mask)


def _make_diagonal_gradient(w: int, h: int,
                            c_top_left: tuple[int, int, int],
                            c_bottom_right: tuple[int, int, int]) -> Image.Image:
    """Linear diagonal gradient (135°). Kept for legacy reference; current
    cover uses radial gradients via `_add_radial_gradient` instead."""
    img = Image.new("RGB", (w, h))
    pixels = img.load()
    denom = max(w + h - 2, 1)
    for y in range(h):
        for x in range(w):
            t = (x + y) / denom
            pixels[x, y] = (
                int(c_top_left[0] * (1 - t) + c_bottom_right[0] * t),
                int(c_top_left[1] * (1 - t) + c_bottom_right[1] * t),
                int(c_top_left[2] * (1 - t) + c_bottom_right[2] * t),
            )
    return img


def _load_font(size: int, weight: str = "regular"):
    """Load PingFang at given size with weight preference (regular|semibold|bold)."""
    if weight == "bold":
        indices = [5, 4, 3, 2]
    elif weight == "semibold":
        indices = [4, 3, 2]
    else:
        indices = [2, 3]

    candidates: list[tuple[str, int | None]] = []
    for idx in indices:
        candidates.append(("/System/Library/Fonts/PingFang.ttc", idx))
    candidates.append(("/System/Library/Fonts/PingFang.ttc", None))
    candidates.append(("/System/Library/Fonts/STHeiti Medium.ttc", None))
    candidates.append(("/System/Library/Fonts/Hiragino Sans GB.ttc", None))
    candidates.append(("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", None))

    for path, idx in candidates:
        if not Path(path).exists():
            continue
        try:
            if idx is None:
                return ImageFont.truetype(path, size)
            return ImageFont.truetype(path, size, index=idx)
        except Exception:
            continue
    return ImageFont.load_default()


def _wrap_by_width(text: str, font, max_width: int, draw: ImageDraw.ImageDraw) -> list[str]:
    lines: list[str] = []
    current = ""
    for ch in text:
        test = current + ch
        bbox = draw.textbbox((0, 0), test, font=font)
        if (bbox[2] - bbox[0]) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = ch
    if current:
        lines.append(current)
    return lines


def make_cover(cover_title: str, digest: str, eyebrow: str, *,
               issue: str = "", year: str = "",
               topic: str = "", category: str = "",
               cover_kicker: str = "") -> None:
    """
    饶秋公众号封面（Keynote 双行节奏版 / v10-D）：
      - 纸白底 + 微渐变光影 (右上暖米光 + 左下浅蓝光) ──── Apple keynote 极简空气感
      - 顶部：栏目标 (左) + N°XX 期号 (右)
      - 中部：引语 cover_kicker (22px sub gray) + 主标题 cover_title (auto-fit 44–60px) + 墨蓝装饰短线
      - 没有 footnote / 没有 metadata stack ── 所有元素 ≥ 14px, 缩略图也读得清

    重要：`cover_title` 和 `cover_kicker` 是封面专用文字，不一定等于文章标题。
    它们应当与 frontmatter 的 `title` 不同，避免封面/标题重复。
    详见 CLAUDE.md「封面 vs 文章标题」段。
    """
    width, height = 900, 383

    # Base paper white + subtle radial gradient atmosphere
    img = Image.new("RGB", (width, height), (251, 251, 253))
    img = _add_radial_gradient(img, (0.9, 0.2), 0.65,
                               (244, 236, 221), max_alpha=0.65)  # warm beige top-right
    img = _add_radial_gradient(img, (0.1, 0.9), 0.55,
                               (226, 232, 240), max_alpha=0.6)   # cool gray bottom-left

    draw = ImageDraw.Draw(img)

    # Fonts
    tag_font = _load_font(14, weight="semibold")
    num_font = _load_font(14, weight="semibold")
    kicker_font = _load_font(22, weight="regular")

    # Colors
    ink = (29, 29, 31)
    sub = (110, 110, 115)
    accent = INK_BLUE_LIGHT  # 墨蓝 #243A56

    # Padding
    pad_left = 72
    pad_right = 72
    pad_top = 50

    # ===== TOP: Tag (left) + N°XX (right) =====
    if eyebrow:
        tag_text = " ".join(list(eyebrow.replace(" ", "")))
        draw.text((pad_left, pad_top), tag_text, font=tag_font, fill=sub)

    if issue:
        num_text = f"N°{issue}"
        bbox = draw.textbbox((0, 0), num_text, font=num_font)
        tw = bbox[2] - bbox[0]
        draw.text(
            (width - pad_right - tw, pad_top),
            num_text, font=num_font, fill=sub,
        )

    # ===== MIDDLE: Kicker + Title + Rule =====
    title_max_width = width - pad_left - pad_right

    # Auto-fit title size: try larger first, find largest that fits 1 line.
    title_size = 56
    for candidate in (60, 58, 56, 54, 52, 50, 48, 46, 44):
        f = _load_font(candidate, weight="bold")
        if len(_wrap_by_width(cover_title, f, title_max_width, draw)) == 1:
            title_size = candidate
            break
    else:
        title_size = 44

    title_font = _load_font(title_size, weight="bold")
    title_lines = _wrap_by_width(cover_title, title_font, title_max_width, draw)[:2]

    # Wrap kicker if needed (max 2 lines)
    kicker_lines: list[str] = []
    if cover_kicker:
        kicker_lines = _wrap_by_width(cover_kicker, kicker_font, title_max_width, draw)[:2]

    # Line heights and explicit gaps
    kicker_lh = int(22 * 1.5)             # ~33
    title_lh = int(title_size * 1.18)      # ~66 for 56, ~70 for 60
    gap_kicker_title = 6                   # extra gap between kicker block and title block
    gap_title_rule = 8                     # extra gap between title block and rule
    rule_h = 3
    rule_w = 36

    # Total title-block height for vertical centering
    block_h = 0
    if kicker_lines:
        block_h += len(kicker_lines) * kicker_lh + gap_kicker_title
    block_h += len(title_lines) * title_lh + gap_title_rule + rule_h

    y = (height - block_h) // 2

    # Draw kicker block
    if kicker_lines:
        for line in kicker_lines:
            draw.text((pad_left, y), line, font=kicker_font, fill=sub)
            y += kicker_lh
        y += gap_kicker_title

    # Draw title block
    for line in title_lines:
        draw.text((pad_left, y), line, font=title_font, fill=ink)
        y += title_lh
    y += gap_title_rule

    # Draw 墨蓝 accent rule
    draw.rectangle(
        [pad_left, y, pad_left + rule_w, y + rule_h],
        fill=accent,
    )

    img.save(COVER_OUT, quality=94, optimize=True)


# -----------------------------
# Entrypoint
# -----------------------------
def main() -> None:
    raw = SOURCE.read_text(encoding="utf-8")
    meta, body = split_frontmatter(raw)
    title = meta.get("title", SOURCE.stem)
    digest = meta.get("digest", "")
    eyebrow = meta.get("eyebrow", "AI 工作心得")

    # Issue: from frontmatter `issue`, fallback to leading digits of filename.
    issue = meta.get("issue", "")
    if not issue:
        m = re.match(r"^(\d{2,3})", SOURCE.stem)
        if m:
            issue = m.group(1)

    # Year: first 4 chars of frontmatter `date`.
    year = ""
    date_str = meta.get("date", "")
    if len(date_str) >= 4 and date_str[:4].isdigit():
        year = date_str[:4]

    # Optional editorial fields used in the right-side metadata stack.
    topic = meta.get("topic", "")
    category = meta.get("category", "")

    # ===== Cover-specific text overrides =====
    # CRITICAL design principle: cover text MUST differ from article title.
    # If `cover_title` / `cover_kicker` are set explicitly, the cover uses them.
    # Otherwise it falls back to article-level `title` / `kicker` (for backward
    # compat — but this fallback creates the duplication problem; new articles
    # should always set `cover_*` explicitly).
    # See CLAUDE.md「封面 vs 文章标题」for the 3 patterns + decision tree.
    cover_title_text = meta.get("cover_title", title)
    cover_kicker_text = meta.get("cover_kicker", meta.get("kicker", ""))

    html_body = render_article(meta, body)
    HTML_OUT.write_text(html_body, encoding="utf-8")

    # WeChat 草稿 API 硬限制：单篇 content 字段 < 20,000 字符。
    # 超过会发不出去。19,000 字预警，让作者有空间调整。
    import sys
    html_chars = len(html_body)
    if html_chars >= WECHAT_DRAFT_CHAR_LIMIT:
        print(
            f"❌ HTML 长度 {html_chars} 字符，已超过 WeChat 草稿 API 上限 "
            f"{WECHAT_DRAFT_CHAR_LIMIT}。草稿创建会失败，请精简内容或拆分文章。",
            file=sys.stderr,
        )
    elif html_chars >= WECHAT_DRAFT_WARN_AT:
        print(
            f"⚠️  HTML 长度 {html_chars} 字符，接近 WeChat 草稿 API 上限 "
            f"{WECHAT_DRAFT_CHAR_LIMIT}。建议精简内容，或减少 inline style 占用。",
            file=sys.stderr,
        )

    # Preview body bg matches the article section bg, so the preview no longer
    # looks like a "card on a gray page" — it mimics how WeChat actually renders
    # the article: continuous paper-white background, no visible card frame.
    preview = (
        "<!doctype html><html lang=\"zh\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        f"<title>{html.escape(title)}</title></head>"
        f'<body style="margin:0;padding:24px 0;background:{C["bg"]};">'
        + html_body
        + "</body></html>"
    )
    PREVIEW_OUT.write_text(preview, encoding="utf-8")

    make_cover(cover_title_text, digest, eyebrow,
               issue=issue, year=year, topic=topic, category=category,
               cover_kicker=cover_kicker_text)

    print(HTML_OUT)
    print(PREVIEW_OUT)
    print(COVER_OUT)


if __name__ == "__main__":
    main()
