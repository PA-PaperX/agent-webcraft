#!/usr/bin/env python3
"""Extract a starting design (fonts, colors, radius) from a reference website the user likes.

Usage:
    python ref_extract.py URL [--out FILE]

Reads the page's HTML and up to 6 stylesheets, then writes a draft DESIGN.md front matter (Google Stitch format)
with the most likely background, text, primary and accent colors, font families and corner radius. It is a
starting point: look at the site (screenshot) and correct the roles before showing options to the user.
Pages that build their styles only in JavaScript may yield little; say so and fall back to a screenshot.
Standard library only.
"""
from __future__ import annotations

import argparse
import collections
import colorsys
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/130 Safari/537.36 agent-webcraft-ref/1"}
GENERIC = {"inherit", "initial", "sans-serif", "serif", "monospace", "system-ui", "-apple-system", "blinkmacsystemfont",
           "segoe ui", "roboto", "helvetica", "arial", "helvetica neue", "ui-sans-serif", "ui-serif", "ui-monospace",
           "apple color emoji", "segoe ui emoji", "noto color emoji", "var", ""}


def get(url: str, limit: int = 2_000_000) -> str:
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
            return r.read(limit).decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        return ""


def to_rgb(v: str):
    v = v.strip().lower()
    m = re.fullmatch(r"#([0-9a-f]{3,8})", v)
    if m:
        h = m.group(1)
        h = "".join(c * 2 for c in h[:3]) if len(h) in (3, 4) else h[:6]
        return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)) if len(h) == 6 else None
    m = re.fullmatch(r"rgba?\(\s*(\d+)[\s,]+(\d+)[\s,]+(\d+)(?:[\s,/]+([\d.]+%?))?\s*\)", v)
    if m:
        if m.group(4) and not m.group(4).endswith("%") and float(m.group(4)) < 0.5:
            return None  # mostly transparent: not a brand color
        return tuple(int(m.group(i)) / 255 for i in (1, 2, 3))
    return None


def hexs(rgb) -> str:
    return "#" + "".join(f"{round(c * 255):02X}" for c in rgb)


def lum(rgb) -> float:
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = map(f, rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b) -> float:
    x, y = sorted((lum(a), lum(b)), reverse=True)
    return (x + 0.05) / (y + 0.05)


def sat(rgb) -> float:
    return colorsys.rgb_to_hls(*rgb)[2]


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Draft design tokens from a reference website")
    ap.add_argument("url")
    ap.add_argument("--out")
    a = ap.parse_args()
    page = get(a.url)
    if not page:
        print(f"could not load {a.url}; ask the user for a screenshot instead", file=sys.stderr)
        return 1
    css_urls = [urllib.parse.urljoin(a.url, h) for h in
                re.findall(r'<link[^>]+rel=["\']?stylesheet["\']?[^>]*href=["\']([^"\']+)', page, re.I)]
    css_urls += [urllib.parse.urljoin(a.url, h) for h in
                 re.findall(r'<link[^>]+href=["\']([^"\']+\.css[^"\']*)["\'][^>]*rel=["\']?stylesheet', page, re.I)]
    css = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", page, re.S | re.I))
    css += "\n" + " ".join(re.findall(r'style="([^"]+)"', page))
    fetched = 0
    for u in dict.fromkeys(css_urls):
        if fetched >= 6:
            break
        if "fonts.googleapis.com" in u:
            continue
        body = get(u, 1_500_000)
        if body:
            css += "\n" + body
            fetched += 1

    google = sorted({urllib.parse.unquote_plus(f).split(":")[0] for href in
                     re.findall(r'fonts\.googleapis\.com/css2?\?([^"\'>]+)', page) for f in
                     re.findall(r"family=([^&]+)", href)})
    fams = collections.Counter()
    for decl in re.findall(r"font-family\s*:\s*([^;}{]+)", css, re.I):
        first = decl.split(",")[0].strip().strip("\"'")
        if first.lower() not in GENERIC and not first.startswith("var("):
            fams[first] += 1
    for name in re.findall(r"@font-face\s*{[^}]*font-family\s*:\s*[\"']?([^;\"'}]+)", css, re.I):
        fams[name.strip()] += 3
    fonts = [f for f, _ in fams.most_common(4)] or google[:2]

    bgs, fgs, allc = collections.Counter(), collections.Counter(), collections.Counter()
    for prop, val in re.findall(r"(background(?:-color)?|color|border(?:-color)?|fill|--[\w-]+)\s*:\s*"
                                r"(#[0-9a-fA-F]{3,8}|rgba?\([^)]*\))", css):
        rgb = to_rgb(val)
        if not rgb:
            continue
        rgb = tuple(round(c, 3) for c in rgb)
        allc[rgb] += 1
        if prop.startswith("background"):
            bgs[rgb] += 1
        elif prop == "color":
            fgs[rgb] += 1
    if not allc:
        print("no colors found in HTML/CSS (styles may be built in JavaScript); use a screenshot instead")
        return 1
    bg = max(bgs or allc, key=lambda c: (bgs[c] if bgs else allc[c]) * (2 if sat(c) < 0.15 else 1))
    text_candidates = [c for c in (fgs or allc) if contrast(c, bg) >= 4.5] or [(0, 0, 0) if lum(bg) > 0.4 else (1, 1, 1)]
    text = max(text_candidates, key=lambda c: fgs[c] if fgs else allc[c])
    colorful = [c for c, n in allc.most_common() if sat(c) > 0.35 and 0.06 < lum(c) < 0.85]
    primary = colorful[0] if colorful else text
    hue = lambda c: colorsys.rgb_to_hls(*c)[0] * 360
    accent = next((c for c in colorful[1:] if min(abs(hue(c) - hue(primary)), 360 - abs(hue(c) - hue(primary))) > 30),
                  primary)
    muted = next((c for c, _ in (fgs or allc).most_common() if c != text and 3 <= contrast(c, bg) < 9), text)
    radii = collections.Counter(re.findall(r"border-radius\s*:\s*([\d.]+(?:px|rem))", css))
    radius = radii.most_common(1)[0][0] if radii else "8px"
    on_primary = max(((1, 1, 1), (0.07, 0.07, 0.07)), key=lambda c: contrast(c, primary))
    host = urllib.parse.urlparse(a.url).netloc
    fm = f'''---
version: alpha
name: "Reference: {host}"
description: "Draft extracted from {a.url}. Roles are guesses from CSS frequency; verify against a screenshot."
colors:
  background: "{hexs(bg)}"
  surface: "{hexs(bg)}"
  text-primary: "{hexs(text)}"
  text-secondary: "{hexs(muted)}"
  primary: "{hexs(primary)}"
  on-primary: "{hexs(on_primary)}"
  accent: "{hexs(accent)}"
  border: "{hexs(muted)}"
typography:
  display-lg:
    fontFamily: "{fonts[0] if fonts else ''}"
  body-md:
    fontFamily: "{fonts[1] if len(fonts) > 1 else (fonts[0] if fonts else '')}"
rounded:
  card: "{radius}"
  control: "{radius}"
x-source: "{a.url}"
---
'''
    out = Path(a.out or f".webcraft/preview/ref-{re.sub(r'[^a-z0-9]+', '-', host.lower()).strip('-')}.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(fm + f"# Reference: {host}\n\nStylesheets read: {fetched}. Fonts seen: "
                        f"{', '.join(fonts) or 'none'}; Google Fonts: {', '.join(google) or 'none'}.\n", encoding="utf-8")
    print(f"{out.as_posix()}")
    print(f"fonts: {', '.join(fonts) or 'none found'}" + (f" (Google Fonts: {', '.join(google)})" if google else ""))
    print(f"background {hexs(bg)} · text {hexs(text)} ({contrast(text, bg):.1f}:1) · primary {hexs(primary)} · "
          f"accent {hexs(accent)} · radius {radius} · stylesheets read {fetched}")
    if not fonts or fetched == 0 or len(allc) < 8:
        print("confidence: LOW (few styles found in HTML/CSS, likely built in JavaScript). Take a screenshot of the "
              "site and set the roles by eye before using this draft.")
    else:
        print("confidence: medium. Roles are frequency guesses; confirm them against a screenshot of the site.")
    print("next: compare with a screenshot, fix the roles, then show it next to the shortlist in the preview")
    return 0


if __name__ == "__main__":
    sys.exit(main())
