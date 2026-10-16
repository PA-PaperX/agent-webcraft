#!/usr/bin/env python3
"""Design gate: catch the problems that make a site look generic or dishonest, before work is called done.

Usage:
    python design_lint.py [PROJECT_DIR] [--json] [--release]

Checks (ERROR blocks `board.py done` for ui/design/pages/content tasks; WARN is reported):
  tokens   Hard-coded colors (Tailwind arbitrary colors, inline style colors, CSS literals outside token blocks)
           versus token usage. ERROR when hard-coded colors are more than 10 and more than 20% of all color uses.
           Mark a deliberate exception with the comment `webcraft-allow-color` on the same line.
  design   .webcraft/DESIGN.md exists, has token front matter (colors + typography), a "Directions considered"
           table with at least 3 rows and 2+ URLs, a "References" section with 2+ URLs, a "Page blueprint"
           (Based on + 3+ sections), a "Component style" table (5+ groups, components.py choose), and a
           "Searched" entry for every Components row. References include at least one real website like this
           one. An "Existing look: yes" record skips the choice sections.
  quality  Once UI code exists: 3+ visuals (img, svg, video, map, background image, icon set), the icon family
           DESIGN.md names is used, a max-width container, at most 4 placeholder notes ("รอข้อมูล", ...).
  spec     Buttons and images match DESIGN "Component style" (for example B3 sharp buttons, I3 arch images):
           corner radius from Tailwind classes, DESIGN radius tokens or CSS classes. While photos are missing,
           the Images row carries the placeholder spec (components.py choose writes it) and placeholder frames
           (role="img" or aspect-ratio boxes) don't use a dark fill on a light page.
  board    Once UI code exists: the work is on the board and a critique and a benchmark pass are logged; the
           benchmark names a real website (not fonts, GitHub, docs, component libraries or example.com).
  content  Ratings, review counts, phone numbers and LINE IDs pass when BRIEF states them as real (outside the
           Sample and Mockup sections), warn when BRIEF "Mockup content" lists them, and fail otherwise. Stock
           photos need BRIEF Sample or Mockup approval. Stock avatars, placeholder-image services, bare social
           URLs and lorem ipsum always fail. Mockup content needs a visible mockup notice on the page.
  release  With --release (before launch): any mockup item, mockup notice, placeholder note or item still in
           "Content to be supplied" is an error.
  thai     Letter-spacing or tight line-height in files that contain Thai text (WARN).
Standard library only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

SRC_DIRS = ("src", "app", "components", "pages", "lib", "routes", "data", "content", "public")
CODE_EXT = {".tsx", ".jsx", ".ts", ".js", ".mjs", ".svelte", ".vue", ".astro", ".html", ".mdx", ".json", ".md"}
SKIP = {"node_modules", ".next", "dist", "build", ".svelte-kit", ".vercel", ".turbo", "out", ".webcraft", ".git"}
COLOR_LIT = r"(?:#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\)|hsla?\([^)]*\)|oklch\([^)]*\))"
TW_PREFIX = r"(?:bg|text|border(?:-[trblxy])?|from|to|via|fill|stroke|ring|shadow|outline|decoration|placeholder|caret|accent|divide)"
COLOR_IN = r"(?:#[0-9a-fA-F]{3,8}(?![0-9a-fA-F])|rgba?\(|hsla?\(|oklch\()"  # inside [...], "_" may follow a hex
TW_ARBITRARY = re.compile(rf"\b{TW_PREFIX}-\[[^\]\s]*?{COLOR_IN}[^\]\s]*\]")
INLINE = re.compile(rf"(?:color|background(?:Color)?|borderColor|fill|stroke)\s*[:=]\s*['\"`]?{COLOR_LIT}")
TOKEN_CLASS = re.compile(rf"\b{TW_PREFIX}-(?:primary|secondary|accent|muted|background|foreground|card|popover|border|"
                         r"ring|destructive|surface|brand|ink|canvas|[a-z]+-(?:foreground|primary|secondary))\b|var\(--")
TOKEN_BLOCK = re.compile(r"(@theme|:root|\.dark|\[data-theme|html\s*\{|@layer\s+base)")
CONTENT = [
    ("rating", re.compile(r"\b[1-5][.,]\d\s*(?:/\s*5|★|stars?|ดาว|คะแนน)|★{3,}|\"?rating\"?\s*[:=]\s*[0-5]\.\d", re.I)),
    ("review count", re.compile(r"\d[\d,]*\s*\+?\s*(?:reviews?|รีวิว|ratings?)\b", re.I)),
    ("stock photo hotlink", re.compile(r"images\.unsplash\.com|plus\.unsplash\.com|images\.pexels\.com|picsum\.photos|"
                                       r"source\.unsplash\.com", re.I)),
    ("stock avatar", re.compile(r"randomuser\.me|i\.pravatar\.cc|pravatar|uifaces", re.I)),
    ("placeholder image service", re.compile(r"placehold\.co|via\.placeholder\.com|dummyimage\.com", re.I)),
    ("bare social URL", re.compile(r"https?://(?:www\.)?(?:facebook|instagram|tiktok|twitter|x|youtube)\.com/?['\"`\s)]",
                                   re.I)),
    ("phone number", re.compile(r"(?:\+66|\b0)[\s-]?[2-9]\d?[\s-]?\d{3}[\s-]?\d{3,4}\b")),
    ("LINE ID", re.compile(r"line\.me/(?:R/)?(?:ti/p/)?[~@%]?[\w.%-]+|\bLINE\s*(?:ID)?\s*[:：]?\s*@[\w.-]{3,}", re.I)),
    ("lorem ipsum", re.compile(r"lorem ipsum", re.I)),
]
MEDIA = re.compile(r"<(?:img|Image|picture|video|svg|iframe|canvas)\b|background-image\s*:|bg-\[url\(|backgroundImage"
                   r"|url\(['\"]?[^)'\"]+\.(?:jpe?g|png|webp|avif|gif|svg)", re.I)
ICON_IMPORT = re.compile(r"""from\s+['"](?:lucide|@phosphor-icons|phosphor-react|phosphor-svelte|@tabler/icons|@iconify|"""
                         r"""react-icons|@heroicons|@radix-ui/react-icons|~icons/|virtual:icons|unplugin-icons)""")
CONTAINER = re.compile(r"\bmax-w-|max-width\s*:|maxWidth|\bcontainer\b")
PLACEHOLDER_NOTE = re.compile(r"รอข้อมูล|รอรูป|รอเจ้าของ|รอยืนยัน|เร็วๆ\s*นี้|coming soon|to be supplied|\bTBD\b", re.I)
UI_EXT = {".tsx", ".jsx", ".svelte", ".vue", ".astro", ".html"}
MOCK_NOTICE = re.compile(r"mock-?up|ม็อกอัพ|ตัวอย่างดีไซน์|ยังไม่ใช่ของจริง|ข้อมูล(?:ใน)?(?:หน้านี้)?(?:ยัง)?(?:เป็น)?ตัวอย่าง", re.I)
THAI = re.compile(r"[฀-๿]")
THAI_BAD = re.compile(r"\btracking-(?:wide|wider|widest|\[[\d.]+(?:em|px)\])|letter-?[sS]pacing\s*:\s*[0-9.]+(?:em|px)"
                      r"|\bleading-(?:none|tight|snug|\[1(?:\.[0-3])?\])")
URL = re.compile(r"https?://[^\s)|>\"'`]+")
# Hosts that are tools, docs, libraries or design shots, not a live website to compare a page with.
NOT_SITES = re.compile(r"^(?:[\w-]+\.)*(?:fonts\.google\.com|fonts\.googleapis\.com|github\.com|githubusercontent\.com|"
                       r"github\.io|npmjs\.com|unpkg\.com|jsdelivr\.net|21st\.dev|reactbits\.dev|shadcn\.com|"
                       r"tailwindcss\.com|mozilla\.org|lucide\.dev|phosphoricons\.com|iconify\.design|icones\.js\.org|"
                       r"react\.dev|nextjs\.org|vitejs\.dev|vite\.dev|svelte\.dev|figma\.com|dribbble\.com|behance\.net|"
                       r"pinterest\.com|google\.com|goo\.gl|unsplash\.com|pexels\.com|example\.(?:com|org|net)|"
                       r"localhost|127\.0\.0\.1)$", re.I)
TW_RADIUS = {"none": 0, "xs": 2, "sm": 4, "": 4, "md": 6, "lg": 8, "xl": 12, "2xl": 16, "3xl": 24, "4xl": 32,
             "full": 9999}
ELEMENT = re.compile(r"<([A-Za-z][\w.]*)\b([^<]{0,500}?)/?>", re.S)
STRING_LIT = re.compile(r"[\"'`]([^\"'`\n]{10,400})[\"'`]")
CLASS_ATTR = re.compile(r"(?:className|class)=\s*\{?\s*(?:cn\(|clsx\(|twMerge\()?\s*[\"'`]([^\"'`]+)[\"'`]")


def files(root: Path):
    for d in SRC_DIRS:
        base = root / d
        if base.is_dir():
            for p in base.rglob("*"):
                if p.is_file() and (p.suffix in CODE_EXT or p.suffix == ".css") and not SKIP.intersection(p.parts):
                    yield p
    for p in root.glob("*.html"):
        yield p


def css_hardcoded(text: str):
    """Yield (line_no, literal) for color literals outside token-defining blocks."""
    depth, token_depth = 0, None
    for no, line in enumerate(text.splitlines(), 1):
        stripped = line.split("/*")[0]
        if token_depth is None and TOKEN_BLOCK.search(stripped) and "{" in stripped:
            token_depth = depth
        if token_depth is None and "webcraft-allow-color" not in line:
            for m in re.finditer(COLOR_LIT, stripped):
                if not re.match(r"\s*--", stripped):
                    yield no, m.group(0)
        depth += stripped.count("{") - stripped.count("}")
        if token_depth is not None and depth <= token_depth:
            token_depth = None


def section(text: str, title: str) -> str:
    m = re.search(rf"^##\s+{re.escape(title)}[^\n]*\n(.*?)(?=^##\s|\Z)", text, re.M | re.S | re.I)
    return re.sub(r"<!--.*?-->", "", m.group(1), flags=re.S) if m else ""


def without(text: str, *titles: str) -> str:
    for title in titles:
        text = re.sub(rf"^##\s+{re.escape(title)}[^\n]*\n.*?(?=^##\s|\Z)", "", text, flags=re.M | re.S | re.I)
    return text


def bullets(sec: str) -> list[str]:
    return [l.strip()[2:] for l in sec.splitlines() if re.match(r"\s*[-*] \S", l)]


def real_site(url: str) -> bool:
    """A live website to compare against: not a font page, repo, doc site, library or placeholder domain."""
    host = (urlparse(url.rstrip(".,;")).hostname or "").lower()
    return bool(host) and "." in host and not NOT_SITES.match(host) and not host.startswith("docs.")


def luminance(hex_color: str) -> float | None:
    m = re.fullmatch(r"#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6})(?:[0-9a-fA-F]{2})?", hex_color.strip())
    if not m:
        return None
    h = m.group(1) if len(m.group(1)) == 6 else "".join(c * 2 for c in m.group(1))
    ch = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    ch = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in ch]
    return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2]


def px_of(v: str) -> float | None:
    v = str(v).strip().strip("[]").split()[0] if str(v).strip() else ""
    m = re.match(r"(-?[\d.]+)\s*(px|rem|em|%)?", v)
    if not m:
        return None
    n, unit = float(m.group(1)), m.group(2) or "px"
    return 9999.0 if unit == "%" and n >= 50 else n * 16 if unit in ("rem", "em") else n


def radius_px(classes: str, tokens: dict, css: dict) -> float:
    """Corner radius an element gets from its classes; 0 when nothing rounds it."""
    for m in re.finditer(r"(?<![\w-])rounded(?:-([\w\[\].%/-]+))?", classes):
        name = m.group(1) or ""
        if re.match(r"(?:[tblrse]|tl|tr|bl|br|ss|se|es|ee)(?:-|$)", name):
            continue  # one side only (arch shapes are checked separately)
        if name in TW_RADIUS:
            return TW_RADIUS[name]
        if name.startswith("["):
            return px_of(name) or 0.0
        if name in tokens:
            return px_of(tokens[name]) or 0.0
    for c in classes.split():
        if c in css:
            return css[c]
    return 0.0


def table_rows(sec: str) -> list[list[str]]:
    rows = [[c.strip() for c in l.strip().strip("|").split("|")] for l in sec.splitlines() if l.strip().startswith("|")]
    return [r for r in rows[2:] if any(r)] if len(rows) > 2 else []


def lint(root: Path, release: bool = False) -> dict:
    errors, warns, info = [], [], {}
    hard, token_uses = [], 0
    content_hits, thai_hits = [], []
    ui_files, media, icon_imports, inline_svgs, containers, notes = 0, 0, 0, 0, 0, []
    note_names, code_texts, mock_notice = set(), [], 0
    code_files, css_radius, css_colors = [], {}, {}
    for p in files(root):
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = p.relative_to(root).as_posix()
        if p.suffix in UI_EXT and "public" not in p.parts:
            ui_files += 1
        if p.suffix != ".md":
            media += len(MEDIA.findall(text))
            icon_imports += len(ICON_IMPORT.findall(text))
            inline_svgs += text.count("<svg")
            containers += len(CONTAINER.findall(text))
            mock_notice += len(MOCK_NOTICE.findall(text))
            code_texts.append(text)
            code_files.append((rel, text))
            for m in PLACEHOLDER_NOTE.finditer(text):
                notes.append(f"{rel}:{text[:m.start()].count(chr(10)) + 1}")
                # a note stored once (placeholder: '...', const TBD = "...") renders wherever the name is used
                before = text[text.rfind("\n", 0, m.start()) + 1:m.start()]
                d = re.search(r"(\w+)\s*[:=]\s*['\"`][^'\"`]*$", before)
                if d:
                    note_names.add(d.group(1))
        if p.suffix == ".css":
            css_colors.update(re.findall(r"--(?:color-)?([\w-]+)\s*:\s*(#[0-9a-fA-F]{3,8})\b", text))
            for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", text):
                rad = re.search(r"border-radius\s*:\s*([^;]+)", body)
                if rad and px_of(rad.group(1)) is not None:
                    for c in re.findall(r"\.([\w-]+)", sel):
                        css_radius[c] = px_of(rad.group(1))
            hard += [(rel, no, lit) for no, lit in css_hardcoded(text)]
            token_uses += len(re.findall(r"var\(--", text))
        elif p.suffix not in (".md", ".json"):
            for no, line in enumerate(text.splitlines(), 1):
                if "webcraft-allow-color" in line:
                    continue
                hard += [(rel, no, m.group(0)) for m in TW_ARBITRARY.finditer(line)]
                hard += [(rel, no, m.group(0)) for m in INLINE.finditer(line)]
                token_uses += len(TOKEN_CLASS.findall(line))
        if p.suffix != ".css" and "public" not in p.parts:
            for no, line in enumerate(text.splitlines(), 1):
                for kind, rx in CONTENT:
                    m = rx.search(line)
                    if m:
                        content_hits.append((kind, rel, no, m.group(0).strip()[:50]))
        if THAI.search(text):
            for no, line in enumerate(text.splitlines(), 1):
                m = THAI_BAD.search(line)
                if m:
                    thai_hits.append((rel, no, m.group(0)))
    total = len(hard) + token_uses
    info["colors"] = {"hardcoded": len(hard), "token_uses": token_uses}
    if hard:
        by_file: dict[str, int] = {}
        for f, _, _ in hard:
            by_file[f] = by_file.get(f, 0) + 1
        top = ", ".join(f"{f} ({n})" for f, n in sorted(by_file.items(), key=lambda x: -x[1])[:5])
        msg = (f"{len(hard)} hard-coded colors vs {token_uses} token uses. Move them into DESIGN tokens and use "
               f"token classes. Worst files: {top}. Example: {hard[0][0]}:{hard[0][1]} {hard[0][2]}")
        (errors if len(hard) > 10 and len(hard) > 0.2 * total else warns).append(("tokens", msg))

    wc = root / ".webcraft"
    design = wc / "DESIGN.md"
    design_text = design.read_text(encoding="utf-8", errors="replace") if design.is_file() else ""
    if wc.is_dir():
        if not design.is_file():
            errors.append(("design", "no .webcraft/DESIGN.md: choose a direction first (references/design.md)"))
        else:
            t = design_text
            existing = re.search(r"Existing look:\s*yes", t, re.I)
            fm = re.match(r"^---\s*\n(.*?)\n---", t, re.S)
            if not fm or "colors:" not in fm.group(1) or "typography:" not in fm.group(1):
                errors.append(("design", "DESIGN.md has no token front matter (colors + typography); "
                                         "export the chosen style with styles.py export"))
            dirs = section(t, "Directions considered")
            if not existing and (len(table_rows(dirs)) < 3 or len(URL.findall(dirs)) < 2):
                errors.append(("design", "DESIGN.md 'Directions considered' needs 3+ rows and 2+ reference URLs "
                                         "(what the user was shown and chose from)"))
            refs = URL.findall(section(t, "References"))
            if len(refs) < 2:
                errors.append(("design", "DESIGN.md 'References' needs 2+ URLs"))
            if not existing and not any(real_site(u) for u in refs):
                errors.append(("design", "DESIGN.md 'References' has no real website like this one (font pages, GitHub, "
                                         "docs, component libraries and example.com don't count). Add 1-2 live sites "
                                         "the user likes or that do the same job; the benchmark compares against them"))
            bp = section(t, "Page blueprint")
            based = re.search(r"Based on:\s*(\S.*)", bp)
            if not existing and (len(table_rows(bp)) < 3 or not based):
                errors.append(("design", "DESIGN.md 'Page blueprint' needs 'Based on: <reference site, Aura template or "
                                         "recipe>' and 3+ section rows (references/page-blueprints.md)"))
            if not existing and len(table_rows(section(t, "Component style"))) < 5:
                errors.append(("design", "DESIGN.md 'Component style' missing: run components.py preview, let the user "
                                         "choose, then components.py choose B.. C.. N.. I.. S.. (design.md step 6)"))
            rows = table_rows(section(t, "Components"))
            unsearched = [r[0] for r in rows if len(r) < 5 or r[4] in ("", "-", "—")]
            if unsearched:
                errors.append(("design", "Components without a 'Searched' entry (query + source, or why skipped): "
                                         + ", ".join(unsearched[:8])))

    for name in note_names:
        uses = sum(len(re.findall(rf"\.{name}\b|[{{(+,]\s*{name}\b(?!\s*[:=])", x)) for x in code_texts)
        notes += [f"{name} (used)"] * uses
    if ui_files:
        visuals = media + icon_imports
        if visuals < 3:
            errors.append(("quality", f"only {visuals} visual(s) in the UI; the hero and at least 2 sections need one "
                                      f"(photo, designed photo frame with an icon, map, illustration or icon row; "
                                      f"page-blueprints.md, content.md)"))
        fam = re.search(r"^Family:\s*([^·\n]*)", section(design_text, "Icons"), re.M)
        fam = fam.group(1).strip() if fam else ""
        if fam and fam.lower() not in ("none", "-", "—") and icon_imports == 0 and inline_svgs < 3:
            errors.append(("quality", f"DESIGN.md names the icon family '{fam}' but the UI uses no icons "
                                      f"(icons.md: icons.py search, then import or inline them)"))
        if containers == 0:
            errors.append(("quality", "no max-width container: content runs edge to edge on wide screens "
                                      "(quality-bar.md: one max width, about 1120-1280px)"))
        if len(notes) > 4:
            errors.append(("quality", f"{len(notes)} placeholder notes on the page (max 4; e.g. {', '.join(notes[:3])}). "
                                      f"Keep final labels and layout, one short note per section, or use approved "
                                      f"samples (content.md)"))
    picks = {}
    for row in table_rows(section(design_text, "Component style")):
        m = re.match(r"\s*([BI]\d)\b\s*(.*)", row[1] if len(row) > 1 else "")
        if m:
            picks[m.group(1)[0]] = (m.group(1), m.group(2).strip(), row[2] if len(row) > 2 else "")
    if ui_files and picks:
        fm = re.match(r"^---\s*\n(.*?)\n---", design_text, re.S)
        rb = re.search(r"^rounded:\s*\n((?:[ \t]+.*\n?)+)", fm.group(1) + "\n", re.M) if fm else None
        tokens = dict(re.findall(r"^\s+([\w-]+):\s*[\"']?([^\"'\n]+)", rb.group(1), re.M)) if rb else {}
        buttons, images, seen, frames = [], [], set(), []

        def button_like(cls: str) -> bool:  # a class set that styles a button, wherever it is defined
            return (bool(re.search(r"(?<![\w-])inline-flex", cls)) and bool(re.search(r"(?<![\w-])(?:px-|h-\d)", cls))
                    and bool(re.search(r"(?<![\w-])(?:bg-|border(?:-|\b)|rounded)", cls))
                    and not re.search(r"max-w-|mx-auto|(?<![\w-])grid(?![\w-])", cls))

        for rel, text in code_files:
            line_of = lambda pos: f"{rel}:{text[:pos].count(chr(10)) + 1}"
            for m in ELEMENT.finditer(text):
                tag, attrs = m.group(1), m.group(2)
                ca = CLASS_ATTR.search(attrs)
                cls = ca.group(1) if ca else ""
                if ca:
                    seen.add((rel, m.start(2) + ca.start(1)))
                dynamic = not cls.strip() or "${" in cls
                low = tag.lower()
                static = re.sub(r"\$\{[^}]*\}", " ", cls)
                if (re.search(r"role=[\"']img[\"']", attrs) and low not in ("img", "image", "svg", "picture", "video")) \
                        or ("aspect-" in static and re.search(r"(?<![\w-])bg-", static)):
                    frames.append((line_of(m.start()), static))
                if low in ("img", "image", "picture", "video") or (not dynamic and "aspect-" in cls):
                    images.append((line_of(m.start()), "" if dynamic else cls))
                elif dynamic:
                    continue  # resolved below through the class strings it is built from
                elif low == "button" or "button" in low or (
                        (low in ("a", "link") or "link" in low or "cta" in low)
                        and ((re.search(r"(?<![\w-])p[xy]-", cls) and re.search(r"(?<![\w-])(?:bg-|border(?:-|\b))", cls))
                             or any(c in css_radius and re.search(r"btn|button|cta", c) for c in cls.split()))):
                    if "sr-only" not in cls:
                        buttons.append((line_of(m.start()), cls))
            for m in STRING_LIT.finditer(text):
                if (rel, m.start(1)) not in seen and button_like(m.group(1)):
                    buttons.append((line_of(m.start()), m.group(1)))
        rules = {"B2": ("pill", lambda r, c: r >= 999), "B7": ("pill", lambda r, c: r >= 999),
                 "B3": ("radius 0-4px", lambda r, c: r <= 4), "B6": ("radius 0-8px", lambda r, c: r <= 8),
                 "B1": ("not a pill", lambda r, c: r < 999), "B4": ("not a pill", lambda r, c: r < 999),
                 "B5": ("not a pill", lambda r, c: r < 999),
                 "I1": ("rounded corners", lambda r, c: r >= 4), "I2": ("square corners", lambda r, c: r <= 2 and not re.search(r"rounded-(?:[tblrse]|tl|tr|bl|br)-(?!none)", c)),
                 "I3": ("arch: rounded-t-full", lambda r, c: bool(re.search(r"rounded-t-(?:full|\[)|999px 999px", c))),
                 "I4": ("polaroid: rotated frame", lambda r, c: bool(re.search(r"(?<![\w])-?rotate-", c))),
                 "I5": ("organic % radius", lambda r, c: bool(re.search(r"rounded-\[[^\]]*%", c)))}
        for group, items, label in (("B", buttons, "button"), ("I", images, "image or photo frame")):
            if group not in picks or not items or picks[group][0] not in rules:
                continue
            vid, vname, _ = picks[group]
            want, ok = rules[vid]
            off = [(w, c) for w, c in items if not ok(radius_px(c, tokens, css_radius), c)]
            if off:
                ex = ", ".join(f"{w} '{(re.search(r'rounded[^ ]*', c) or [None])[0] or f'radius {radius_px(c, tokens, css_radius):g}px'}'"
                               for w, c in off[:3])
                errors.append(("spec", f"Component style says {vid} {vname} ({want}) but {len(off)} of {len(items)} "
                                       f"{label}(s) differ, e.g. {ex}. Build from the spec in DESIGN.md, or ask the user "
                                       f"and record a new choice with components.py choose"))
        # Placeholder frames: the spec must be recorded, and the fill must follow the page mood.
        brief_text = (wc / "BRIEF.md").read_text(encoding="utf-8", errors="replace") if (wc / "BRIEF.md").is_file() else ""
        photos_missing = bool(frames) or any(
            re.search(r"photo|image|รูป|ภาพ", ln, re.I) and re.search(r"placeholder|frame|none yet|no photos|not yet|"
                                                                     r"to be supplied|รอ|ยังไม่มี", ln, re.I)
            for ln in brief_text.splitlines())
        images_row = next((r for r in table_rows(section(design_text, "Component style")) if r and r[0].lower() == "images"),
                          None)
        if photos_missing and images_row and "placeholder" not in " ".join(images_row).lower():
            errors.append(("spec", "photos are still missing but Component style 'Images' has no placeholder spec. "
                                   "Re-run components.py choose with the same picks; it adds the frame spec "
                                   "(light tint, line icon, muted label)"))
        colors = dict(re.findall(r"^\s+([\w-]+):\s*[\"']?(#[0-9a-fA-F]{3,8})", design_text, re.M))
        colors.update(css_colors)
        page = next((luminance(colors[k]) for k in ("background", "canvas", "bg", "base") if k in colors), None)
        dark_frames = []
        for where, cls in frames:
            fills = [f.split("/")[0] for f in re.findall(r"(?<![\w-])bg-([\w/-]+)", cls)]
            fills += re.findall(r"bg-\[[^\]]*?(#[0-9a-fA-F]{3,8})", cls)
            for f in fills:
                lum = luminance(f) if f.startswith("#") else luminance(colors[f]) if f in colors else (
                    0.0 if re.fullmatch(r"black|[a-z]+-(?:800|900|950)", f) else None)
                if lum is not None and lum < 0.2 and page is not None and page > 0.5:
                    dark_frames.append(f"{where} bg-{f}" if not f.startswith("#") else f"{where} {f}")
                    break
        if dark_frames:
            errors.append(("spec", f"{len(dark_frames)} placeholder photo frame(s) use a dark fill on a light page, "
                                   f"e.g. {', '.join(dark_frames[:2])}. Follow the Images placeholder spec: surface "
                                   f"mixed with 12% primary, a line icon, a muted label"))
        info["spec"] = {"buttons": len(buttons), "images": len(images), "frames": len(frames),
                        "picks": {k: v[0] for k, v in picks.items()}}

    if ui_files and wc.is_dir():
        tasks = list((wc / "tasks").glob("*.md")) + list((wc / "archive").rglob("*.md"))
        logs = "\n".join(x.read_text(encoding="utf-8", errors="replace") for x in tasks)
        if not tasks:
            errors.append(("board", "UI work is not on the board: board.py init, board.py new \"<task>\" --area ui "
                                    "--accept \"...\", then claim and report as you work (board.md)"))
        else:
            if not re.search(r"\bcritique:\s*\S.{30,}", logs, re.I):
                errors.append(("verify", "no critique pass logged yet: screenshots at 390/768/1440, three weakest "
                                         "things each, then board.py report ID --agent NAME --did \"critique: ...\" "
                                         "(verify.md)"))
            bench = re.findall(r"\bbenchmark:(.*)", logs, re.I)
            if not any(len(b) > 40 and any(real_site(u) for u in URL.findall(b)) for b in bench):
                errors.append(("verify", "no benchmark pass against a real website logged yet: open a live reference "
                                         "site from DESIGN.md References at the same width, then board.py report ID "
                                         "--agent NAME --did \"benchmark: compared with https://... - three biggest "
                                         "differences\" (quality-bar.md)"))
    info["quality"] = {"ui_files": ui_files, "media": media, "icon_imports": icon_imports, "inline_svgs": inline_svgs,
                       "containers": containers, "placeholder_notes": len(notes)}

    brief = (wc / "BRIEF.md").read_text(encoding="utf-8", errors="replace") if (wc / "BRIEF.md").is_file() else ""
    sample = section(brief, "Sample content")
    mock = section(brief, "Mockup content")
    supplied = bullets(section(brief, "Content to be supplied"))
    real = without(brief, "Sample content", "Mockup content", "Content to be supplied")
    mock_items = [b for b in bullets(mock) if b.lower() not in ("none", "-", "—")]
    sample_items = [b for b in bullets(sample) if b.lower() not in ("none", "-", "—")]
    photos_ok = bool(re.search(r"photo|image|ภาพ|รูป|unsplash|pexels|stock", sample + mock, re.I))

    def number_in(txt: str, where: str) -> bool:
        num = re.search(r"\d[\d.,]*", txt)
        return bool(num) and bool(re.search(rf"(?<![\d.]){re.escape(num.group(0).rstrip('.,'))}(?!\d)", where))

    def line_id(txt: str) -> str:
        for rx in (r"[@~]([\w.-]{3,})", r"ti/p/([\w.%-]{3,})", r"line\.me/(?:R/)?([\w.%-]{3,})"):
            m = re.search(rx, txt, re.I)
            if m:
                return m.group(1).lower()
        return ""

    def has_id(lid: str, where: str) -> bool:
        return bool(lid) and bool(re.search(rf"(?<![\w.-]){re.escape(lid)}(?![\w-])", where, re.I))

    def dummy(txt: str) -> bool:  # values that can't be a real shop's contact, whatever BRIEF says
        return bool(re.search(r"sample|example|test|demo|yourshop|your-?shop|xxx|ตัวอย่าง|0{5,}|1234567", txt, re.I))

    bad: dict[str, list] = {}
    ok: dict[str, list] = {}
    mocked: dict[str, list] = {}
    for kind, rel, no, txt in content_hits:
        digits = re.sub(r"\D", "", txt)
        if kind in ("rating", "review count"):
            state = "ok" if number_in(txt, real) else "mock" if re.search(r"review|rating|รีวิว|คะแนน|ดาว", mock, re.I) else "bad"
        elif kind == "phone number":
            state = ("ok" if len(digits) >= 9 and digits in re.sub(r"\D", "", real) and not dummy(txt) else
                     "mock" if len(digits) >= 9 and digits in re.sub(r"\D", "", mock) else "bad")
        elif kind == "LINE ID":
            lid = line_id(txt)
            state = ("ok" if has_id(lid, real) and not dummy(lid) else "mock" if has_id(lid, mock) else "bad")
        elif kind == "stock photo hotlink":
            state = "ok" if photos_ok else "bad"
        elif kind == "stock avatar":
            state = "mock" if re.search(r"avatar|รูปโปรไฟล์|profile", mock, re.I) else "bad"
        else:
            state = "bad"
        {"ok": ok, "mock": mocked, "bad": bad}[state].setdefault(kind, []).append(f"{rel}:{no} {txt}")
    summary = lambda d: "; ".join(f"{k} x{len(v)} (e.g. {v[0]})" for k, v in d.items())
    if ok:
        warns.append(("content", "real or approved sample content, keep BRIEF current: "
                                 + "; ".join(f"{k} x{len(v)}" for k, v in ok.items())))
    if mocked:
        (errors if release else warns).append(("content", "mockup content (replace before launch): " + summary(mocked)))
    if bad:
        errors.append(("content", "invented or unapproved content: " + summary(bad)
                                  + ". Facts (ratings, reviews, phones, LINE, social links) must be real in BRIEF, or "
                                    "chosen by the user as mockup and listed in BRIEF 'Mockup content'; never samples "
                                    "(content.md)"))
    if ui_files and mock_items and not mock_notice and not release:
        errors.append(("content", "BRIEF lists mockup content but the page shows no mockup notice "
                                  "('ตัวอย่างดีไซน์ · ข้อมูลยังไม่ใช่ของจริง', content.md)"))
    if release:
        if mock_items:
            errors.append(("release", f"BRIEF 'Mockup content' still lists {len(mock_items)} item(s), e.g. "
                                      f"{mock_items[0][:60]}; replace them with real content"))
        if mock_notice:
            errors.append(("release", "the mockup notice is still on the page; remove it once content is real"))
        if supplied:
            errors.append(("release", f"BRIEF 'Content to be supplied' still lists {len(supplied)} item(s), e.g. "
                                      f"{supplied[0][:60]}"))
        if notes:
            errors.append(("release", f"{len(notes)} placeholder note(s) still on the page, e.g. {notes[0]}"))
        if sample_items:
            warns.append(("release", f"{len(sample_items)} sample item(s) still in use (BRIEF 'Sample content'); "
                                     f"fine if the owner agreed to launch with them"))
    if thai_hits:
        warns.append(("thai", f"letter-spacing or tight line-height in files with Thai text ({len(thai_hits)}), e.g. "
                              f"{thai_hits[0][0]}:{thai_hits[0][1]} {thai_hits[0][2]} (references/thai-web.md)"))
    return {"errors": errors, "warnings": warns, "info": info}


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Design and content gate for web projects")
    ap.add_argument("project", nargs="?", default=".")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--release", action="store_true", help="before launch: mockups and placeholders are errors")
    a = ap.parse_args()
    r = lint(Path(a.project).resolve(), release=a.release)
    if a.json:
        print(json.dumps(r, indent=2, ensure_ascii=False))
    else:
        for kind, msg in r["errors"]:
            print(f"ERROR [{kind}] {msg}")
        for kind, msg in r["warnings"]:
            print(f"warn  [{kind}] {msg}")
        c = r["info"].get("colors", {})
        print(f"{len(r['errors'])} error(s), {len(r['warnings'])} warning(s) · colors: {c.get('hardcoded', 0)} "
              f"hard-coded, {c.get('token_uses', 0)} token uses")
    return 1 if r["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
