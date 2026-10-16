#!/usr/bin/env python3
"""Style library for choosing a UI direction: built-in presets, popular-brand DESIGN.md files, Aura design systems.

Every source uses the Google Stitch DESIGN.md format (YAML front matter: colors, typography, rounded, spacing),
so one tool can list, score, preview and export any of them. The user makes the final choice.

Usage:
  python styles.py list [--sources builtin,brands,aura] [--query WORD] [--mode light|dark]
  python styles.py shortlist --axes W,P,D,T,E [--query cafe,coffee] [--n 9] [--mode light|dark|any]
  python styles.py preview [ID ...] [--from-shortlist] [--brand NAME] [--title T] [--tagline S] [--out FILE]
  python styles.py export ID [--out .webcraft/DESIGN.md] [--thai-display FONT] [--thai-body FONT]
  python styles.py templates [--query WORD] [--limit 40]
  python styles.py template NAME [--out .webcraft/preview/templates]

Sources (fetched live, cached for 7 days in ~/.cache/agent-webcraft/styles; add --refresh to update):
  builtin  this skill's styles/ folder: 16 presets with axis scores, Thai fonts, icon and motion hints
  brands   github.com/VoltAgent/awesome-design-md (MIT): DESIGN.md files of popular brands' sites
  aura     github.com/PA-PaperX/Aura-Full: Aura design systems (and full-page templates via `templates`)
Axis scores for brands and aura are estimated from their tokens and marked "est.". Standard library only.
"""
from __future__ import annotations

import argparse
import colorsys
import html
import json
import math
import re
import sys
import time
import urllib.error
import unicodedata
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
BUILTIN = SKILL / "styles"
CACHE = Path.home() / ".cache" / "agent-webcraft" / "styles"
TTL = 7 * 86400
UA = {"User-Agent": "agent-webcraft-styles/1"}
REPOS = {
    "brands": ("VoltAgent/awesome-design-md", lambda p: p.startswith("design-md/") and p.endswith("/DESIGN.md")),
    "aura": ("PA-PaperX/Aura-Full", lambda p: p.startswith("Aura_Design_Systems/") and p.endswith("DESIGN.md")),
}
AXES = ("warmth", "playfulness", "density", "trust", "expressiveness")
SERIF_HINTS = ("serif", "playfair", "fraunces", "newsreader", "garamond", "georgia", "times", "instrument serif",
               "trirong", "taviraj", "noto serif", "lora", "merriweather", "dm serif", "cormorant", "tiempos")
DEFAULT_TITLE = "ร้านเล็กๆ ที่อยากให้คุณแวะมา"
DEFAULT_TAGLINE = "บรรยากาศอบอุ่น เมนูทำสดทุกวัน เปิดทุกวัน 08:00–17:00 แวะมานั่งพักได้เสมอ"


# ---------------------------------------------------------------------------
# Fetching and caching
# ---------------------------------------------------------------------------

def http(url: str, timeout: int = 20) -> bytes | None:
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
            return r.read()
    except (urllib.error.URLError, TimeoutError, OSError):
        return None


def repo_tree(repo: str, refresh: bool) -> list[str]:
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / f"{repo.replace('/', '__')}.tree.json"
    if f.is_file() and not refresh and time.time() - f.stat().st_mtime < TTL:
        return json.loads(f.read_text(encoding="utf-8"))
    raw = http(f"https://api.github.com/repos/{repo}/git/trees/HEAD?recursive=1")
    try:
        paths = [e["path"] for e in json.loads(raw)["tree"] if e["type"] == "blob"] if raw else None
    except (ValueError, KeyError):
        paths = None
    if paths is None:
        if f.is_file():
            print(f"note: could not refresh {repo}; using cached list", file=sys.stderr)
            return json.loads(f.read_text(encoding="utf-8"))
        print(f"note: {repo} unreachable and no cache; skipping it", file=sys.stderr)
        return []
    f.write_text(json.dumps(paths), encoding="utf-8")
    return paths


def raw_url(repo: str, path: str) -> str:
    return f"https://raw.githubusercontent.com/{repo}/HEAD/{urllib.parse.quote(path)}"


def cached_file(repo: str, path: str, refresh: bool) -> str | None:
    f = CACHE / repo.replace("/", "__") / path.replace("/", "__")
    if f.is_file() and not refresh and time.time() - f.stat().st_mtime < TTL:
        return f.read_text(encoding="utf-8", errors="replace")
    data = http(raw_url(repo, path))
    if data is None:
        return f.read_text(encoding="utf-8", errors="replace") if f.is_file() else None
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_bytes(data)
    return data.decode("utf-8", errors="replace")


# ---------------------------------------------------------------------------
# DESIGN.md parsing
# ---------------------------------------------------------------------------

def scalar(v: str):
    v = v.strip()
    if v.startswith("[") and v.endswith("]"):
        return [scalar(x) for x in v[1:-1].split(",") if x.strip()]
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    try:
        return int(v)
    except ValueError:
        try:
            return float(v)
        except ValueError:
            return v


def parse_yaml(src: str) -> dict:
    root: dict = {}
    stack = [(-1, root)]
    for line in src.splitlines():
        if not line.strip() or line.lstrip().startswith(("#", "- ")):
            continue
        indent = len(line) - len(line.lstrip(" "))
        m = re.match(r"^([^:]+?):(?:\s+(.*))?$", line.strip())
        if not m:
            continue
        key, val = m.group(1).strip().strip("\"'"), (m.group(2) or "").strip()
        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if val in ("", ">", "|", ">-", "|-"):
            parent[key] = {}
            stack.append((indent, parent[key]))
        else:
            parent[key] = scalar(val)
    return root


def split_doc(text: str) -> tuple[str, str]:
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.S)
    return (m.group(1), m.group(2)) if m else ("", text)


def hex_rgb(v) -> tuple[float, float, float] | None:
    if not isinstance(v, str):
        return None
    m = re.search(r"#([0-9a-fA-F]{3,8})\b", v)
    if not m:
        return None
    h = m.group(1)
    if len(h) in (3, 4):
        h = "".join(c * 2 for c in h[:3])
    h = h[:6]
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)) if len(h) == 6 else None


def to_hex(rgb) -> str:
    return "#" + "".join(f"{round(c * 255):02X}" for c in rgb)


def luminance(rgb) -> float:
    def ch(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def pick(colors: dict, *names, exclude=()) -> tuple | None:
    keys = list(colors)
    for n in names:
        for k in keys:
            if (k == n or k.startswith(n + "-") or k == n.replace("-", "")) and k not in exclude:
                rgb = hex_rgb(colors[k])
                if rgb:
                    return rgb
    return None


def first_family(v) -> str:
    if not isinstance(v, str):
        return ""
    fam = v.split(",")[0].strip().strip("\"'")
    return "" if fam.lower() in ("system-ui", "-apple-system", "sans-serif", "serif", "inherit") else fam


def font_for(typo: dict, *prefixes) -> str:
    for p in prefixes:
        for k, v in typo.items():
            if k.startswith(p) and isinstance(v, dict) and first_family(v.get("fontFamily")):
                return first_family(v.get("fontFamily"))
    return ""


def px(v) -> float:
    m = re.search(r"([\d.]+)", str(v or ""))
    return float(m.group(1)) if m else 0.0


def resolve(meta: dict) -> dict:
    """Map any DESIGN.md's token names onto the roles a preview needs."""
    c = meta.get("colors") or {}
    bg = pick(c, "background", "canvas", "bg", "base", "surface") or (1, 1, 1)
    text = pick(c, "text-primary", "ink", "foreground", "on-background", "body", "text", "on-surface")
    if not text or contrast(text, bg) < 3:
        text = (0.07, 0.07, 0.07) if luminance(bg) > 0.4 else (0.96, 0.96, 0.96)
    muted = pick(c, "text-secondary", "ink-muted", "body-muted", "muted", "ink-subtle", "ink-secondary") or text
    surface = pick(c, "surface", "surface-1", "canvas-soft", "canvas-parchment", "surface-pearl", "card",
                   exclude=("surface-base",)) or bg
    primary = pick(c, "primary", "brand", "accent") or text
    if primary == bg:
        primary = pick(c, "accent", "secondary", "brand", exclude=("primary",)) or text
    on_primary = pick(c, "on-primary")
    if not on_primary or contrast(on_primary, primary) < 3:
        on_primary = max(((1, 1, 1), (0.07, 0.07, 0.07)), key=lambda x: contrast(x, primary))
    accent = pick(c, "accent", "secondary", "brand", exclude=("primary",)) or primary
    if accent in (bg, text):
        accent = primary
    border = pick(c, "border", "hairline", "divider", "outline") or muted
    typo = meta.get("typography") or {}
    rounded = meta.get("rounded") or {}
    thai = meta.get("x-thai") or {}
    display = font_for(typo, "display", "hero", "headline", "heading", "h1", "title")
    body = font_for(typo, "body", "lead", "paragraph", "text") or display
    label = font_for(typo, "label", "mono", "eyebrow", "caption", "button") or body
    serif = any(h in display.lower() for h in SERIF_HINTS)
    return {
        "bg": bg, "surface": surface, "text": text, "muted": muted, "primary": primary, "on_primary": on_primary,
        "accent": accent, "border": border, "display": display, "body": body, "label": label, "serif": serif,
        "radius_card": rounded.get("card") or rounded.get("lg") or rounded.get("md") or "12px",
        "radius_control": rounded.get("control") or rounded.get("md") or rounded.get("sm") or "8px",
        "thai_display": thai.get("display") or ("Noto Serif Thai" if serif else "IBM Plex Sans Thai"),
        "thai_body": thai.get("body") or ("Sarabun" if serif else "IBM Plex Sans Thai"),
        "dark": luminance(bg) < 0.25,
        "display_size": px((typo.get("display-lg") or typo.get("hero-display") or {}).get("fontSize")),
    }


def estimate_axes(r: dict) -> dict:
    h, l_, s = colorsys.rgb_to_hls(*r["primary"])
    hue = h * 360
    warm = hue < 65 or hue > 330
    bg_warm = r["bg"][0] > r["bg"][2] + 0.03 and not r["dark"]
    ctrl = px(r["radius_control"])
    clamp = lambda v: max(1, min(5, round(v)))
    return {
        "warmth": clamp(3 + (1 if warm and s > 0.3 else 0) + (1 if bg_warm else 0) - (1 if 180 <= hue <= 260 else 0)
                        - (1 if r["dark"] else 0)),
        "playfulness": clamp(2 + (1 if s > 0.75 else 0) + (1 if ctrl >= 16 else 0) - (1 if r["serif"] else 0)
                             + (1 if contrast(r["accent"], r["primary"]) > 2.5 and s > 0.5 else 0)),
        "density": clamp(3 - (1 if r["display_size"] >= 64 else 0)),
        "trust": clamp(3 + (1 if 190 <= hue <= 250 and s < 0.8 else 0) - (1 if s > 0.85 and not 190 <= hue <= 250 else 0)
                       - (1 if r["dark"] and s > 0.7 else 0)),
        "expressiveness": clamp(2 + (2 if r["dark"] else 0) + (1 if r["display_size"] >= 64 else 0) + (1 if s > 0.8 else 0)),
    }


def load_style(source: str, slug: str, text: str, url: str) -> dict | None:
    fm, body = split_doc(text)
    meta = parse_yaml(fm) if fm else {}
    if not meta.get("colors"):
        return None
    r = resolve(meta)
    axes = meta.get("x-axes") if isinstance(meta.get("x-axes"), dict) else None
    tags = meta.get("x-tags") if isinstance(meta.get("x-tags"), list) else []
    return {"id": f"{source}:{slug}", "source": source, "name": str(meta.get("name") or slug),
            "description": str(meta.get("description") or "")[:240], "url": url, "tags": [str(t) for t in tags],
            "axes": {a: int(axes.get(a, 3)) for a in AXES} if axes else estimate_axes(r), "axes_estimated": not axes,
            "roles": r, "front_matter": fm, "meta": meta}


def collect(sources: list[str], refresh: bool) -> list[dict]:
    styles = []
    if "builtin" in sources:
        for p in sorted(BUILTIN.glob("*.md")):
            s = load_style("builtin", p.stem, p.read_text(encoding="utf-8"), str(p))
            if s:
                styles.append(s)
    jobs = []
    for src in ("brands", "aura"):
        if src in sources:
            repo, keep = REPOS[src]
            jobs += [(src, repo, p) for p in repo_tree(repo, refresh) if keep(p)]

    def fetch(job):
        src, repo, path = job
        text = cached_file(repo, path, refresh)
        slug = path.split("/")[-2] if src == "brands" else Path(path).stem.removesuffix("-DESIGN")
        slug = re.sub(r"[^a-z0-9.]+", "-", slug.lower()).strip("-")
        return load_style(src, slug, text, f"https://github.com/{repo}/blob/HEAD/{urllib.parse.quote(path)}") if text else None

    with ThreadPoolExecutor(max_workers=8) as pool:
        styles += [s for s in pool.map(fetch, jobs) if s]
    return styles


def find(styles: list[dict], sid: str) -> dict:
    hits = [s for s in styles if s["id"] == sid] or [s for s in styles if s["id"].split(":", 1)[1] == sid]
    if not hits:
        sys.exit(f"unknown style id {sid}; see `styles.py list`")
    return hits[0]


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

# Mood words describe almost every style, so they rank but never make a style relevant to the job.
MOOD_WORDS = {"clean", "modern", "minimal", "minimalist", "simple", "beautiful", "nice", "pretty", "warm", "cool",
              "calm", "bold", "elegant", "premium", "luxury", "friendly", "playful", "dark", "light", "soft", "cozy",
              "natural", "fresh", "professional", "trendy", "cute", "fun", "classic", "sleek", "quiet"}


def query_words(q: str | None) -> list[str]:
    """Job words from --query; commas and spaces both separate words."""
    return [w for w in re.split(r"[,\s]+", fold(q or "")) if w]


def fold(text: str) -> str:
    """Lowercase without accents, so "Café" matches "cafe"."""
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c)).lower()


def matches(s: dict, words: list[str]) -> int:
    hay = fold(" ".join([s["name"], s["description"], " ".join(s["tags"])]))
    return sum(1 for w in words if w and re.search(rf"\b{re.escape(w)}s?\b", hay))


def mode_ok(s: dict, mode: str) -> bool:
    return mode == "any" or (mode == "dark") == s["roles"]["dark"]


def line(i, s, extra="") -> str:
    r = s["roles"]
    ax = "".join(str(s["axes"][a]) for a in AXES) + ("est" if s["axes_estimated"] else "")
    fonts = f"{r['display'] or '?'} / {r['body'] or '?'}"
    return (f"{str(i) + '.' if i else '':4}{s['id']:44} {('dark' if r['dark'] else 'light'):5} {to_hex(r['primary'])} "
            f"axes {ax:8} {fonts[:34]:34} {s['name'][:40]}{extra}")


def cmd_list(a, styles):
    words = query_words(a.query)
    shown = [s for s in styles if mode_ok(s, a.mode) and (not words or matches(s, words))]
    for s in shown:
        print(line(0, s))
    print(f"{len(shown)} styles (W P D T E = warmth, playfulness, density, trust, expressiveness)")


def cmd_shortlist(a, styles):
    try:
        want = [int(x) for x in a.axes.split(",")]
        assert len(want) == 5 and all(1 <= x <= 5 for x in want)
    except (ValueError, AssertionError):
        sys.exit("--axes needs five scores 1-5: warmth,playfulness,density,trust,expressiveness")
    words = query_words(a.query)
    job = [w for w in words if w not in MOOD_WORDS]
    scored = []
    for s in styles:
        if not mode_ok(s, a.mode):
            continue
        d = math.dist(want, [s["axes"][x] for x in AXES]) + (0.5 if s["axes_estimated"] else 0)
        d -= 1.2 * min(matches(s, job), 2) + 0.3 * min(matches(s, words) - matches(s, job), 2)
        # Brand and Aura systems come from other industries: show them only when they match the job,
        # or (with no job words) when their axes are close. Built-in presets are general and always eligible.
        if s["source"] != "builtin" and (matches(s, job) == 0 if job else d > 2.0):
            continue
        scored.append((d, s))
    scored.sort(key=lambda x: x[0])
    if job and not any(matches(s, job) for _, s in scored):
        print(f"note: no style is tagged for {', '.join(job)}; ranked by axes only. "
              f"Try job nouns such as cafe, restaurant, clinic, shop, school, saas, portfolio.")
    # Variety on purpose: the user decides, so show the best fits from every source and both light and dark.
    present = {s["source"] for _, s in scored}
    share = {"builtin": 0.45, "brands": 0.35, "aura": 0.2}
    total = sum(share[x] for x in present) or 1
    quota = {x: max(1, round(a.n * share[x] / total)) for x in present}
    picked, per_source = [], {}

    def hue(rgb):
        return colorsys.rgb_to_hls(*rgb)[0] * 360

    def similar(r, p):
        dh = abs(hue(r["primary"]) - hue(p["primary"]))
        return (abs(luminance(r["bg"]) - luminance(p["bg"])) < 0.05 and min(dh, 360 - dh) < 25
                and r["serif"] == p["serif"])

    for d, s in scored:
        if len(picked) == a.n:
            break
        if per_source.get(s["source"], 0) >= quota.get(s["source"], 0):
            continue
        if any(similar(s["roles"], p["roles"]) for _, p in picked):
            continue
        picked.append((d, s))
        per_source[s["source"]] = per_source.get(s["source"], 0) + 1
    for d, s in scored:  # fill any unused quota with the next best, still avoiding near-twins
        if len(picked) == a.n:
            break
        if s not in [p for _, p in picked] and not any(similar(s["roles"], p["roles"]) for _, p in picked):
            picked.append((d, s))
    # Padding the list with poor fits hides the good ones: keep at least 5, then only options close to the best.
    picked.sort(key=lambda x: x[0])
    best = max(picked[0][0], 0) if picked else 0
    weak = [s["id"] for d, s in picked[5:] if d > best + 3.0]
    picked = picked[:5] + [(d, s) for d, s in picked[5:] if d <= best + 3.0]
    if a.mode == "any" and picked and len({s["roles"]["dark"] for _, s in picked}) == 1:
        other = next(((d, s) for d, s in scored if s["roles"]["dark"] != picked[0][1]["roles"]["dark"]), None)
        if other and other[0] <= best + 3.0:  # offer the other mode only when it still fits the job
            picked[-1] = other
    picked.sort(key=lambda x: x[0])
    for i, (d, s) in enumerate(picked, 1):
        hit = [w for w in job if matches(s, [w])]
        why = f"  fit {max(0, 10 - d):.1f}" + (f", matches {', '.join(hit)}" if hit else "")
        print(line(i, s, why))
    if weak:
        print(f"left out (poor fit for this job): {', '.join(weak)}")
    out = Path(".webcraft/preview/shortlist.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"axes": want, "query": a.query, "ids": [s["id"] for _, s in picked]}, indent=2),
                   encoding="utf-8")
    print(f"saved {out.as_posix()}; next: styles.py preview --from-shortlist")
    if job:  # whole pages for the same job are the best start for the page blueprint (page-blueprints.md)
        try:
            pages = [html.unescape(n) for n in aura_templates(a.refresh) if any(w in fold(html.unescape(n)) for w in job)]
        except Exception:  # offline: the shortlist is still valid
            pages = []
        for n in pages[:5]:
            print(f"full-page template for this job: styles.py template \"{n}\"")


CARD_CSS = """
*{box-sizing:border-box}body{margin:0;background:#e9e9e6;color:#111;font:15px/1.6 system-ui,"Noto Sans Thai",sans-serif}
header.top{padding:20px 24px}header.top h1{margin:0 0 4px;font-size:22px}header.top p{margin:0;color:#555}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:20px;padding:0 24px 40px}
.opt{border-radius:14px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.15);background:#fff}
.cap{display:flex;justify-content:space-between;gap:8px;padding:10px 14px;font:600 13px/1.4 system-ui,sans-serif;background:#fff;color:#111}
.cap a{color:#2563eb;font-weight:500}.num{font-size:18px}
.page{background:var(--bg);color:var(--fg);font-family:var(--body);padding:0 0 22px}
.nav{display:flex;align-items:center;justify-content:space-between;padding:14px 20px;border-bottom:1px solid var(--border)}
.logo{font-family:var(--display);font-weight:700;font-size:17px}.links{display:flex;gap:14px;font-size:13px;color:var(--muted)}
.hero{padding:30px 20px 18px}.eyebrow{font-family:var(--label);font-size:12px;letter-spacing:.04em;color:var(--accent);font-weight:600}
.hero h2{font-family:var(--display);font-size:30px;line-height:1.25;margin:6px 0 10px}
.hero p{color:var(--muted);margin:0 0 16px;line-height:1.75}
.btns{display:flex;gap:10px;flex-wrap:wrap}.b1,.b2{padding:11px 18px;border-radius:var(--rc);font-weight:600;font-size:14px;border:1.5px solid var(--primary)}
.b1{background:var(--primary);color:var(--onp)}.b2{background:transparent;color:var(--fg);border-color:var(--border)}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:6px 20px 0}
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--rk);padding:14px}
.card b{font-family:var(--display);display:block;margin-bottom:4px}.card span{font-size:13px;color:var(--muted)}
.badge{display:inline-block;margin-top:8px;font-size:12px;padding:2px 10px;border-radius:999px;background:var(--accent);color:var(--ona)}
.sw{display:flex;gap:6px;flex-wrap:wrap;padding:10px 14px;background:#fff;border-top:1px solid #eee;font:12px/1.3 ui-monospace,monospace;color:#333}
.sw i{display:inline-block;width:14px;height:14px;border-radius:4px;border:1px solid #0002;vertical-align:-3px;margin-right:4px}
.ok{color:#15803d}.bad{color:#b91c1c}
"""


def font_links(families: set[str]) -> str:
    out = []
    for f in sorted(x for x in families if x):
        q = urllib.parse.quote_plus(f) + ":wght@400;600;700"
        out.append(f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family={q}&display=swap">')
    return "\n".join(out)


def stack(latin: str, thai: str, serif: bool) -> str:
    fams = [f'"{x}"' for x in (latin, thai) if x]
    return ", ".join(fams + ["serif" if serif else "sans-serif"])


def cmd_preview(a, styles):
    ids = list(a.ids)
    if a.from_shortlist:
        f = Path(".webcraft/preview/shortlist.json")
        if not f.is_file():
            sys.exit("no shortlist yet: run styles.py shortlist first")
        ids += json.loads(f.read_text(encoding="utf-8"))["ids"]
    if not ids:
        sys.exit("give style ids or --from-shortlist")
    chosen = [find(styles, i) for i in ids]
    fams, cards = set(), []
    for n, s in enumerate(chosen, 1):
        r = s["roles"]
        fams |= {r["display"], r["body"], r["label"], r["thai_display"], r["thai_body"]}
        checks = [("text", r["text"], r["bg"], 4.5), ("muted", r["muted"], r["bg"], 4.5),
                  ("button", r["on_primary"], r["primary"], 4.5)]
        sw = "".join(f"<span><i style='background:{to_hex(r[k])}'></i>{k} {to_hex(r[k])}</span>"
                     for k in ("bg", "surface", "text", "primary", "accent"))
        ck = " ".join(f"<span class='{'ok' if contrast(x, y) >= need else 'bad'}'>{label} {contrast(x, y):.1f}:1</span>"
                      for label, x, y, need in checks)
        on_accent = max(((1, 1, 1), (0.07, 0.07, 0.07)), key=lambda x: contrast(x, r["accent"]))
        style = (f"--bg:{to_hex(r['bg'])};--fg:{to_hex(r['text'])};--muted:{to_hex(r['muted'])};"
                 f"--surface:{to_hex(r['surface'])};--primary:{to_hex(r['primary'])};--onp:{to_hex(r['on_primary'])};"
                 f"--accent:{to_hex(r['accent'])};--ona:{to_hex(on_accent)};--border:{to_hex(r['border'])};"
                 f"--rc:{html.escape(str(r['radius_control']))};--rk:{html.escape(str(r['radius_card']))};"
                 f"--display:{html.escape(stack(r['display'], r['thai_display'], r['serif']))};"
                 f"--body:{html.escape(stack(r['body'], r['thai_body'], False))};"
                 f"--label:{html.escape(stack(r['label'], r['thai_body'], False))}")
        src_link = s["url"] if s["url"].startswith("http") else ""
        cards.append(f"""<section class="opt"><div class="cap"><span><span class="num">#{n}</span> {html.escape(s['name'])}
 <small style="color:#666">· {s['source']} · {'dark' if r['dark'] else 'light'}</small></span>
 {f'<a href="{html.escape(src_link)}" target="_blank" rel="noopener">source</a>' if src_link else ''}</div>
<div class="page" style="{style}"><div class="nav"><span class="logo">{html.escape(a.brand)}</span>
<span class="links"><span>เมนู</span><span>เรื่องราว</span><span>ติดต่อ</span></span></div>
<div class="hero"><div class="eyebrow">{html.escape(r['display'] or 'Display')} · {html.escape(r['thai_display'])}</div>
<h2>{html.escape(a.title)}</h2><p>{html.escape(a.tagline)}</p>
<div class="btns"><span class="b1">ดูเส้นทาง</span><span class="b2">ทักไลน์</span></div></div>
<div class="cards"><div class="card"><b>เมนูแนะนำ</b><span>ข้อความตัวอย่างสั้นๆ สองบรรทัดเพื่อดูการตัดคำไทย</span>
<div class="badge">เปิดอยู่</div></div><div class="card"><b>Our story</b><span>Mixed Thai and English text 123</span></div></div></div>
<div class="sw">{sw}</div><div class="sw">{ck} · <span>{html.escape(s['id'])}</span></div></section>""")
    page = f"""<!doctype html><html lang="th"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Style options</title>{font_links(fams)}<style>{CARD_CSS}</style></head><body>
<header class="top"><h1>Style options ({len(chosen)})</h1><p>Pick by number, or mix (e.g. "colors of #3 with type of #7").
Red ratios fail WCAG AA and will be fixed when the style is adopted. Brand-only fonts (not free) show a fallback here
and get replaced by a similar free font when adopted.</p></header>
<div class="grid">{''.join(cards)}</div></body></html>"""
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    (out.parent / "preview-index.json").write_text(json.dumps({str(i): s["id"] for i, s in enumerate(chosen, 1)},
                                                              indent=2), encoding="utf-8")
    print(f"{out.as_posix()}  ({len(chosen)} options; numbers map to ids in {out.parent.as_posix()}/preview-index.json)")


def cmd_export(a, styles):
    s = find(styles, a.id)
    r = s["roles"]
    fm = s["front_matter"].rstrip()
    extra = [f'x-source: "{s["url"]}"']
    if "x-thai" not in fm:
        extra += ["x-thai:", f'  display: "{a.thai_display or r["thai_display"]}"', f'  body: "{a.thai_body or r["thai_body"]}"']
    template = (SKILL / "templates" / "DESIGN.md").read_text(encoding="utf-8")
    _, body = split_doc(template)
    body = body.replace("{{name}}", s["name"]).replace("{{source}}", s["id"])
    out = Path(a.out)
    if out.exists() and not a.force:
        sys.exit(f"{out} exists; pass --force to replace it (the old file is not kept)")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(f"---\n{fm}\n" + "\n".join(extra) + f"\n---\n{body}", encoding="utf-8")
    print(f"{out.as_posix()} written from {s['id']}; now fill Directions considered, References, Components, Decisions")


def aura_templates(refresh: bool) -> list[str]:
    repo = REPOS["aura"][0]
    names = sorted({p.split("/")[1] for p in repo_tree(repo, refresh)
                    if p.startswith("Aura_Templates/") and p.endswith("/index.html")})
    return names


def cmd_templates(a, _):
    names = aura_templates(a.refresh)
    words = query_words(a.query)
    shown = [n for n in names if not words or any(w in fold(html.unescape(n)) for w in words)]
    for n in shown[: a.limit]:
        print(html.unescape(n))
    print(f"{len(shown)} of {len(names)} full-page templates (Aura). Open one: styles.py template \"NAME\"")


def cmd_template(a, _):
    names = aura_templates(a.refresh)
    hits = [n for n in names if html.unescape(n).lower() == a.name.lower()] or \
           [n for n in names if a.name.lower() in html.unescape(n).lower()]
    if not hits:
        sys.exit(f"no template matching {a.name!r}; see styles.py templates --query WORD")
    name = hits[0]
    text = cached_file(REPOS["aura"][0], f"Aura_Templates/{name}/index.html", a.refresh)
    if not text:
        sys.exit("could not download the template")
    slug = re.sub(r"[^a-z0-9]+", "-", html.unescape(name).lower()).strip("-")[:60]
    out = Path(a.out) / slug / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"{out.as_posix()}  (open in a browser; it loads Tailwind and fonts from CDNs)")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Style library: list, shortlist, preview, export (DESIGN.md format)")
    ap.add_argument("--refresh", action="store_true", help="ignore the 7-day cache")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list")
    s.add_argument("--sources", default="builtin,brands,aura")
    s.add_argument("--query")
    s.add_argument("--mode", default="any", choices=["any", "light", "dark"])
    s = sub.add_parser("shortlist")
    s.add_argument("--axes", required=True, help="warmth,playfulness,density,trust,expressiveness (1-5 each)")
    s.add_argument("--query", help="job words (what the site is for), e.g. cafe,coffee,restaurant; "
                   "mood words like warm or modern only rank")
    s.add_argument("--n", type=int, default=9)
    s.add_argument("--mode", default="any", choices=["any", "light", "dark"])
    s.add_argument("--sources", default="builtin,brands,aura")
    s = sub.add_parser("preview")
    s.add_argument("ids", nargs="*")
    s.add_argument("--from-shortlist", action="store_true")
    s.add_argument("--brand", default="Brand")
    s.add_argument("--title", default=DEFAULT_TITLE)
    s.add_argument("--tagline", default=DEFAULT_TAGLINE)
    s.add_argument("--out", default=".webcraft/preview/styles.html")
    s.add_argument("--sources", default="builtin,brands,aura")
    s = sub.add_parser("export")
    s.add_argument("id")
    s.add_argument("--out", default=".webcraft/DESIGN.md")
    s.add_argument("--thai-display")
    s.add_argument("--thai-body")
    s.add_argument("--force", action="store_true")
    s.add_argument("--sources", default="builtin,brands,aura")
    s = sub.add_parser("templates")
    s.add_argument("--query")
    s.add_argument("--limit", type=int, default=40)
    s = sub.add_parser("template")
    s.add_argument("name")
    s.add_argument("--out", default=".webcraft/preview/templates")
    a = ap.parse_args()
    if a.cmd in ("templates", "template"):
        {"templates": cmd_templates, "template": cmd_template}[a.cmd](a, None)
        return
    sources = [x.strip() for x in getattr(a, "sources", "builtin").split(",")]
    if a.cmd == "preview" or a.cmd == "export":
        wanted = {i.split(":")[0] for i in getattr(a, "ids", []) + [getattr(a, "id", "")] if ":" in i}
        sources = [x for x in sources if not wanted or x in wanted] or sources
    styles = collect(sources, a.refresh)
    {"list": cmd_list, "shortlist": cmd_shortlist, "preview": cmd_preview, "export": cmd_export}[a.cmd](a, styles)


if __name__ == "__main__":
    main()
