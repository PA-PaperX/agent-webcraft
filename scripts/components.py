#!/usr/bin/env python3
"""Component style: let the user pick how buttons, cards, navigation, forms, badges, images and one signature
element look, rendered in the project's own tokens, then record the picks as exact specs in DESIGN.md.

Usage:
    python components.py list
    python components.py preview [--style ID] [--brand NAME] [--cta1 TEXT] [--cta2 TEXT] [--item TEXT]
                                 [--out .webcraft/preview/components.html]
    python components.py choose B2 C4 N1 M1 F1 T3 I3 S2 [--custom "S=live queue counter"] [--design FILE]

Tokens come from .webcraft/DESIGN.md (after `styles.py export`), or from --style ID before a style is chosen.
Groups: B buttons, C cards, N navigation, M mobile action, F form fields, T tags, I images, S signature element.
The user may also describe their own variant ("buttons like apple.com"); record it with --custom GROUP=TEXT.
Standard library only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import styles as S  # noqa: E402  (shared token parsing and font helpers)

GROUPS = {"B": "Buttons", "C": "Cards", "N": "Navigation", "M": "Mobile action", "F": "Form fields",
          "T": "Tags and badges", "I": "Images", "S": "Signature element"}
REQUIRED = ("B", "C", "N", "I", "S")

# id: (name, feel, spec). Specs name token roles (primary, on-primary, surface, border, text, muted, accent,
# radius control/card/pill) so they translate to any stack.
V = {
    "B1": ("Rounded solid", "safe, familiar", "radius control; height 48; padding-x 24; fill primary, label on-primary, weight 600. Secondary: same size, 1.5px border, label text. Hover: fill 8% darker. Focus: 2px accent ring, offset 2."),
    "B2": ("Pill + arrow", "friendly, modern", "radius pill; height 48; padding-x 24; fill primary, label on-primary, weight 600; arrow-right icon 18px after the label. Hover: arrow moves 4px right (150ms). Secondary: pill with 1.5px border."),
    "B3": ("Sharp block", "confident, editorial", "radius 0-2px; height 52; padding-x 28; fill text color, label background color, weight 600. Letter-spacing only on Latin labels, never Thai. Hover: fill primary."),
    "B4": ("Soft tinted", "gentle, calm", "radius control; height 48; fill primary at 12% opacity, label primary, no border. Hover: 18%. Secondary: text-only label in text color."),
    "B5": ("Outline line", "quiet, premium", "radius control; height 48; transparent with 1.5px border in text color, label text. Hover: fill text color, label background color (200ms)."),
    "B6": ("Offset shadow", "bold, playful", "radius 0-6px; height 48; 2px border text color; hard shadow 4px 4px 0 text color; fill accent or primary. Hover: move 2px right and down, shadow 2px."),
    "B7": ("Glow gradient", "expressive, techy", "radius pill; height 48; gradient primary to accent; shadow 0 8px 24px primary at 35%. Hover: shadow grows. Use only with expressive directions; check label contrast on both ends."),
    "B8": ("Text link + underline", "light, for secondary actions", "no box; label primary weight 600 with arrow; 2px underline grows from the left on hover (200ms). Tap area still 44px tall."),
    "C1": ("Flat surface", "calm, simple", "fill surface; no border, no shadow; radius card; padding 24."),
    "C2": ("Hairline", "clean, precise", "fill background; 1px border; radius card; padding 24. Hover: border primary."),
    "C3": ("Soft shadow", "friendly, polished", "fill background; shadow 0 1px 2px + 0 8px 24px of text color at 8%; radius card (16-20px); padding 24. Hover: lift 2px."),
    "C4": ("Media top", "product and menu items", "image 4:3 on top, edge to edge inside the card; radius card on the outer box; title, one meta line, price row. The whole card is the link; no button on every card."),
    "C5": ("Image overlay", "atmospheric, visual", "image fills the card at 4:5; title and meta at the bottom over a gradient scrim (transparent to 60% black); white text; radius card."),
    "C6": ("Offset block", "bold, playful", "2px border text color; hard shadow 6px 6px 0 text color; radius 0-8px; bold title; fill background or surface."),
    "C7": ("Glass", "layered, techy", "surface at 60% opacity + backdrop blur 12px + 1px white border at 20%. Only over photos or gradients; check text contrast on the real background."),
    "N1": ("Classic bar", "clear, works everywhere", "height 64; logo left, links right, one primary button at the end; background fill, bottom border appears after scrolling."),
    "N2": ("Centered logo", "editorial, boutique", "height 72; wordmark centered, links split left and right; on mobile: wordmark left, menu button right."),
    "N3": ("Floating pill", "modern, light", "detached bar 12px from the top; radius pill; surface at 85% with backdrop blur; soft shadow; links + small primary button."),
    "N4": ("Minimal + menu", "portfolio, creative", "wordmark left, menu button right on every screen size; the menu opens a full-screen overlay with large links."),
    "M0": ("No bar", "content-led sites", "actions live in the page only."),
    "M1": ("Sticky action bar", "local business, booking", "mobile only: fixed bottom bar, two actions 50/50 with icons and labels, height 56 + safe-area padding, background fill, top border. Keep the page's last section clear of it."),
    "M2": ("Floating button", "one main action", "mobile only: round 56px primary button bottom-right with one icon; aria-label names the action."),
    "F1": ("Outlined", "clear, accessible", "height 48; 1px border; radius control; label above; focus: border primary + 2px ring at 30%."),
    "F2": ("Filled soft", "friendly", "height 48; fill surface, no border; radius control; label above; focus: 2px primary ring."),
    "F3": ("Underline", "editorial, minimal", "height 48; transparent; bottom border 1.5px; label above; focus: border primary."),
    "T1": ("Tinted pill", "soft", "radius pill; fill primary at 12%; label primary; 12-13px weight 600; padding 4px 12px."),
    "T2": ("Outline tag", "neutral, precise", "radius 4px; 1px border; label muted; 12-13px."),
    "T3": ("Status dot", "live info (open now)", "8px dot (green open, muted closed) + label in text color; no box."),
    "I1": ("Soft rounded", "friendly, safe", "radius card; one ratio per section (4:3 or 3:2); no border."),
    "I2": ("Sharp full-bleed", "editorial, cinematic", "radius 0; hero and gallery images run edge to edge."),
    "I3": ("Arch", "warm, crafted", "top corners fully rounded like an arch window (radius 999px 999px card card); ratio 3:4."),
    "I4": ("Polaroid", "playful, personal", "white frame 8px with a 28px bottom; rotate -2 to 2 degrees; small shadow; caption in the bottom strip."),
    "I5": ("Organic shape", "natural, soft", "irregular rounded mask (radius 60% 40% 55% 45% / 50% 60% 40% 50%)."),
    "S0": ("None (calm)", "quality from photos and spacing", "no special element."),
    "S1": ("Marquee strip", "lively, brand voice", "a slow horizontal strip of short phrases between two sections (loop about 40s); pauses on hover; static under reduced motion."),
    "S2": ("Hand-drawn mark", "personal, crafted", "an SVG underline or circle drawn under one key word in the hero, in accent; draw-on animation 800ms once; static under reduced motion."),
    "S3": ("Round sticker", "playful, local", "circular badge with text around the edge (for example opening days) near the hero, rotating once per 12s; static under reduced motion."),
    "S4": ("Lift on hover", "tactile, polished", "cards and buttons rise 2-4px with a growing shadow on hover (desktop pointer only)."),
    "S5": ("Paper grain", "print, craft", "subtle noise texture over the page background at 4-6% opacity; text stays on clean fills."),
    "S6": ("Soft color blobs", "dreamy, modern", "2-3 blurred shapes in primary and accent behind the hero, drifting slowly (20s); static under reduced motion."),
    "S7": ("Reveal headline", "cinematic", "the hero headline appears line by line once on load (opacity + 12px rise, 400ms, 80ms stagger); visible without JS."),
    "S8": ("Custom cursor", "creative, playful", "small dot cursor that grows over links; desktop with a fine pointer only; the normal cursor stays for text fields."),
}

# Written into every Images choice: weaker models otherwise invent dark, heavy placeholder blocks.
PHOTO_PLACEHOLDER = ("Placeholder until real or sample photos arrive: the same frame shape, ratio and corners, filled "
                     "with the surface color mixed with 12% primary (it follows the page mood: light on a light page, "
                     "never a dark block or heavy gradient), a 24-32px line icon of the subject in muted color at the "
                     "center, and a 13px muted label such as \"รูปหน้าร้าน\". No borders, dashes or grey boxes.")

ARROW = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
PIN = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></svg>'
CUP = '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M17 8h1a4 4 0 0 1 0 8h-1M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4zM6 2v2M10 2v2M14 2v2"/></svg>'
CHAT = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/></svg>'

CSS = """
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.7 var(--body)}
.top{padding:28px 24px 8px;max-width:1200px;margin:auto}.top h1{font:700 26px/1.3 var(--display);margin:0 0 6px}
.top p{margin:0;color:var(--muted)}.grp{max-width:1200px;margin:auto;padding:24px}
.grp h2{font:700 20px/1.4 var(--display);margin:0 0 12px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:16px}
.grid.wide{grid-template-columns:repeat(auto-fill,minmax(min(100%,400px),1fr))}.links,.logo,.btn{white-space:nowrap}
.tile{border:1px dashed var(--border);border-radius:12px;padding:16px;background:var(--bg);overflow:hidden}
.cap{font:600 13px/1.4 var(--label);margin-top:14px}.cap small{display:block;font-weight:400;color:var(--muted)}
.stage{min-height:120px;display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:flex-start;position:relative}
.ph{background:linear-gradient(135deg,var(--primary),var(--accent));position:relative;color:#fff;display:flex;align-items:flex-end;padding:8px 10px;font-size:12px}
.ph:after{content:"";position:absolute;inset:0;background:radial-gradient(circle at 30% 30%,#fff3,transparent 60%)}
a.x{text-decoration:none;cursor:pointer}
.btn{display:inline-flex;align-items:center;gap:8px;height:48px;padding:0 24px;font:600 15px/1 var(--body);border:0;transition:.15s}
.b1{background:var(--primary);color:var(--onp);border-radius:var(--rc)}.b1:hover{filter:brightness(.92)}
.b1s{background:transparent;color:var(--fg);border:1.5px solid var(--border);border-radius:var(--rc)}
.b2{background:var(--primary);color:var(--onp);border-radius:999px}.b2 svg{transition:transform .15s}.b2:hover svg{transform:translateX(4px)}
.b2s{background:transparent;color:var(--fg);border:1.5px solid var(--border);border-radius:999px}
.b3{background:var(--fg);color:var(--bg);border-radius:2px;height:52px;padding:0 28px}.b3:hover{background:var(--primary);color:var(--onp)}
.b4{background:color-mix(in srgb,var(--primary) 12%,transparent);color:var(--primary);border-radius:var(--rc)}
.b4:hover{background:color-mix(in srgb,var(--primary) 18%,transparent)}.b4s{background:none;color:var(--fg)}
.b5{background:transparent;color:var(--fg);border:1.5px solid var(--fg);border-radius:var(--rc);transition:.2s}.b5:hover{background:var(--fg);color:var(--bg)}
.b6{background:var(--accent);color:var(--ona);border:2px solid var(--fg);border-radius:4px;box-shadow:4px 4px 0 var(--fg)}
.b6:hover{transform:translate(2px,2px);box-shadow:2px 2px 0 var(--fg)}
.b7{background:linear-gradient(90deg,var(--primary),var(--accent));color:var(--onp);border-radius:999px;box-shadow:0 8px 24px color-mix(in srgb,var(--primary) 35%,transparent)}
.b7:hover{box-shadow:0 12px 32px color-mix(in srgb,var(--primary) 50%,transparent)}
.b8{background:none;color:var(--primary);padding:0;background-image:linear-gradient(currentColor,currentColor);background-size:0 2px;background-position:0 85%;background-repeat:no-repeat;transition:background-size .2s}
.b8:hover{background-size:100% 2px}
.card{width:100%;font-size:14px}.card b{display:block;font:700 16px/1.4 var(--display);margin-bottom:4px}.card span{color:var(--muted)}
.c1{background:var(--surface);border-radius:var(--rk);padding:20px}.c2{background:var(--bg);border:1px solid var(--border);border-radius:var(--rk);padding:20px}
.c2:hover{border-color:var(--primary)}
.c3{background:var(--bg);border-radius:18px;padding:20px;box-shadow:0 1px 2px color-mix(in srgb,var(--fg) 8%,transparent),0 8px 24px color-mix(in srgb,var(--fg) 8%,transparent);transition:.2s}
.c3:hover{transform:translateY(-2px)}
.c4{background:var(--bg);border:1px solid var(--border);border-radius:var(--rk);overflow:hidden}.c4 .ph{aspect-ratio:4/3}.c4 .in{padding:14px 16px}
.c4 .row{display:flex;justify-content:space-between;margin-top:6px;font-weight:600;color:var(--fg)}
.c5{position:relative;border-radius:var(--rk);overflow:hidden;aspect-ratio:4/5;max-height:220px}.c5 .ph{position:absolute;inset:0}
.c5 .in{position:absolute;inset:auto 0 0 0;padding:14px;color:#fff;background:linear-gradient(transparent,#0009)}.c5 .in span{color:#fffd}
.c6{background:var(--bg);border:2px solid var(--fg);border-radius:6px;padding:20px;box-shadow:6px 6px 0 var(--fg)}
.c7wrap{background:linear-gradient(135deg,var(--primary),var(--accent));padding:18px;border-radius:var(--rk);width:100%}
.c7{background:color-mix(in srgb,var(--surface) 60%,transparent);backdrop-filter:blur(12px);border:1px solid #fff3;border-radius:var(--rk);padding:18px}
.nav{width:100%;display:flex;align-items:center;justify-content:space-between;gap:10px;font-size:13px}
.logo{font:700 16px/1 var(--display)}.links{display:flex;gap:12px;color:var(--muted)}
.n1{height:56px;border-bottom:1px solid var(--border);padding:0 4px}.n1 .sm{height:36px;padding:0 14px;font-size:13px}
.n2{height:64px;border-bottom:1px solid var(--border);display:grid;grid-template-columns:1fr auto 1fr}.n2 .links:last-child{justify-content:flex-end}
.n3{height:50px;border-radius:999px;background:color-mix(in srgb,var(--surface) 85%,transparent);box-shadow:0 6px 20px #0000001f;padding:0 8px 0 18px;margin-top:8px}
.n3 .sm{height:34px;padding:0 14px;font-size:13px;border-radius:999px}
.n4{height:56px}.burger{width:40px;height:40px;border:1.5px solid var(--border);border-radius:999px;display:grid;place-items:center}
.burger i{display:block;width:16px;height:2px;background:var(--fg);box-shadow:0 5px 0 var(--fg),0 -5px 0 var(--fg)}
.phone{width:150px;height:220px;border:2px solid var(--border);border-radius:22px;position:relative;overflow:hidden;background:var(--surface)}
.phone .lines{padding:14px}.phone .lines i{display:block;height:8px;border-radius:4px;background:var(--border);margin:8px 0}
.m1{position:absolute;inset:auto 0 0 0;height:52px;display:grid;grid-template-columns:1fr 1fr;border-top:1px solid var(--border);background:var(--bg);font-size:12px;font-weight:600}
.m1 span{display:flex;align-items:center;justify-content:center;gap:6px}.m1 span:first-child{background:var(--primary);color:var(--onp)}
.m2{position:absolute;right:12px;bottom:12px;width:48px;height:48px;border-radius:999px;background:var(--primary);color:var(--onp);display:grid;place-items:center;box-shadow:0 6px 16px #0003}
.fld{width:100%;font-size:13px}.fld label{display:block;font-weight:600;margin-bottom:6px}
.fld div{height:46px;display:flex;align-items:center;padding:0 14px;color:var(--muted)}
.f1 div{border:1px solid var(--border);border-radius:var(--rc)}.f2 div{background:var(--surface);border-radius:var(--rc)}
.f3 div{border-bottom:1.5px solid var(--border);padding:0 2px}
.tag{font:600 12.5px/1 var(--body);display:inline-flex;align-items:center;gap:6px}
.t1{background:color-mix(in srgb,var(--primary) 12%,transparent);color:var(--primary);padding:6px 12px;border-radius:999px}
.t2{border:1px solid var(--border);color:var(--muted);padding:5px 10px;border-radius:4px;font-weight:500}
.t3 i{width:8px;height:8px;border-radius:50%;background:#16a34a}
.pf{width:100%;height:130px;border-radius:var(--rk);background:color-mix(in srgb,var(--surface) 88%,var(--primary));
color:var(--muted);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;font-size:13px}
.img{width:46%;height:120px}.i1{border-radius:var(--rk)}.i3{border-radius:999px 999px var(--rk) var(--rk);height:130px}
.i4{background:#fff;padding:6px 6px 22px;box-shadow:0 4px 12px #0002;transform:rotate(-2deg)}.i4 .ph{height:100%}
.i5{border-radius:60% 40% 55% 45%/50% 60% 40% 50%}
.marq{width:100%;overflow:hidden;white-space:nowrap;border-block:1px solid var(--border);padding:10px 0;font:700 18px/1.2 var(--display)}
.marq span{display:inline-block;animation:mq 18s linear infinite}@keyframes mq{to{transform:translateX(-50%)}}
.hd{font:700 26px/1.3 var(--display);position:relative;display:inline-block}.hd svg{position:absolute;left:0;bottom:-8px;width:100%;height:12px}
.hd path{stroke:var(--accent);stroke-width:4;fill:none;stroke-linecap:round;stroke-dasharray:300;stroke-dashoffset:300;animation:draw .8s .3s forwards}
@keyframes draw{to{stroke-dashoffset:0}}
.stk{width:96px;height:96px;border-radius:50%;background:var(--accent);color:var(--ona);display:grid;place-items:center;position:relative}
.stk svg{position:absolute;inset:0;animation:spin 12s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}
.lift{transition:.2s}.lift:hover{transform:translateY(-4px);box-shadow:0 14px 30px #0002}
.grain{width:100%;height:110px;border-radius:12px;background-color:var(--surface);background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120'%3E%3Cfilter id='n'%3E%3CfeTurbulence baseFrequency='.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='120' height='120' filter='url(%23n)' opacity='.12'/%3E%3C/svg%3E")}
.blobs{width:100%;height:120px;position:relative;overflow:hidden;border-radius:12px;background:var(--bg)}
.blobs i{position:absolute;width:110px;height:110px;border-radius:50%;filter:blur(28px);opacity:.55;animation:drift 10s ease-in-out infinite alternate}
.blobs i:first-child{background:var(--primary);left:10%;top:10%}.blobs i:last-child{background:var(--accent);right:10%;bottom:-10%;animation-delay:-4s}
@keyframes drift{to{transform:translate(30px,-10px) scale(1.15)}}
.rv span{display:block;font:700 22px/1.35 var(--display);opacity:0;transform:translateY(12px);animation:rv .4s forwards}
.rv span:nth-child(2){animation-delay:.12s}@keyframes rv{to{opacity:1;transform:none}}
.cur{width:100%;height:110px;border-radius:12px;background:var(--surface);cursor:none;position:relative}
.cur i{position:absolute;width:12px;height:12px;border-radius:50%;background:var(--primary);pointer-events:none;transform:translate(-50%,-50%);transition:width .15s,height .15s;left:50%;top:50%}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}.hd path{stroke-dashoffset:0}.rv span{opacity:1;transform:none}}
"""


def load_roles(style_id: str | None) -> tuple[dict, str]:
    if style_id:
        sources = ["builtin"] if style_id.startswith("builtin:") or ":" not in style_id else ["builtin", "brands", "aura"]
        s = S.find(S.collect(sources, False), style_id)
        return s["roles"], s["id"]
    f = Path(".webcraft/DESIGN.md")
    if not f.is_file():
        sys.exit("no .webcraft/DESIGN.md yet: export the chosen style first (styles.py export ID) or pass --style ID")
    fm, _ = S.split_doc(f.read_text(encoding="utf-8"))
    meta = S.parse_yaml(fm) if fm else {}
    if not meta.get("colors"):
        sys.exit("DESIGN.md has no token front matter; run styles.py export ID first")
    return S.resolve(meta), "DESIGN.md"


def demo(vid: str, a) -> str:
    e = html.escape
    c1, c2, item, brand = e(a.cta1), e(a.cta2), e(a.item), e(a.brand)
    g = vid[0]
    if g == "B":
        n = vid[1:]
        sec = {"1": f'<a class="x btn b1s">{c2}</a>', "2": f'<a class="x btn b2s">{c2}</a>',
               "4": f'<a class="x btn b4s">{c2}</a>'}.get(n, "")
        label = f"{c1} {ARROW}" if n in ("2", "8") else c1
        return f'<a class="x btn b{n}">{label}</a>{sec}'
    if g == "C":
        body = f"<b>{item}</b><span>ข้อความสั้นๆ อธิบายรายการนี้</span>"
        n = vid[1:]
        if n == "4":
            return f'<div class="card c4"><div class="ph">ภาพ</div><div class="in">{body}<div class="row"><span>ราคา</span><span>฿ —</span></div></div></div>'
        if n == "5":
            return f'<div class="card c5"><div class="ph"></div><div class="in">{body}</div></div>'
        if n == "7":
            return f'<div class="c7wrap"><div class="card c7">{body}</div></div>'
        return f'<div class="card c{n}">{body}</div>'
    if g == "N":
        links = '<span class="links"><span>เมนู</span><span>เรื่องราว</span><span>ติดต่อ</span></span>'
        n = vid[1:]
        if n == "1":
            return f'<div class="nav n1"><span class="logo">{brand}</span>{links}<a class="x btn b1 sm">{c1}</a></div>'
        if n == "2":
            return (f'<div class="nav n2"><span class="links"><span>เมนู</span><span>เรื่องราว</span></span>'
                    f'<span class="logo">{brand}</span><span class="links"><span>ติดต่อ</span></span></div>')
        if n == "3":
            return f'<div class="nav n3"><span class="logo">{brand}</span><a class="x btn b1 sm">{c1}</a></div>'
        return f'<div class="nav n4"><span class="logo">{brand}</span><span class="burger"><i></i></span></div>'
    if g == "M":
        lines = '<div class="lines"><i></i><i style="width:70%"></i><i></i><i style="width:50%"></i></div>'
        extra = {"1": f'<div class="m1"><span>{PIN} {c1}</span><span>{CHAT} {c2}</span></div>',
                 "2": f'<div class="m2">{CHAT}</div>'}.get(vid[1:], "")
        return f'<div class="phone">{lines}{extra}</div>'
    if g == "F":
        return f'<div class="fld f{vid[1:]}"><label>ชื่อของคุณ</label><div>พิมพ์ชื่อ</div></div>'
    if g == "T":
        return {"1": '<span class="tag t1">เมนูใหม่</span><span class="tag t1">แนะนำ</span>',
                "2": '<span class="tag t2">กาแฟ</span><span class="tag t2">ของหวาน</span>',
                "3": '<span class="tag t3"><i></i>เปิดอยู่ · ปิด 17:00</span>'}[vid[1:]]
    if g == "I":
        n = vid[1:]
        inner = '<div class="ph" style="height:100%">ภาพ</div>' if n == "4" else ""
        cls = "img i4" if n == "4" else f"img ph i{n}"
        return f'<div class="{cls}">{inner}</div><div class="{cls}" style="transform:rotate(2deg)">{inner}</div>' if n == "4" \
            else f'<div class="{cls}">ภาพ</div><div class="{cls}">ภาพ</div>'
    n = vid[1:]
    if n == "0":
        return '<span style="color:var(--muted)">ไม่มีลูกเล่นพิเศษ ให้ภาพและระยะห่างทำงาน</span>'
    if n == "1":
        words = " · ".join([brand, "กาแฟดริป", "ขนมโฮมเมด", "บรรยากาศสบายๆ"] * 2)
        return f'<div class="marq"><span>{words} · {words} · </span></div>'
    if n == "2":
        return ('<span class="hd">อบอุ่นเหมือน<b style="color:var(--accent)"> บ้าน</b><svg viewBox="0 0 200 12" preserveAspectRatio="none">'
                '<path d="M2 8 C 50 2, 120 12, 198 5"/></svg></span>')
    if n == "3":
        return ('<div class="stk"><svg viewBox="0 0 100 100"><defs><path id="cp" d="M50 50 m-38 0 a38 38 0 1 1 76 0 a38 38 0 1 1 -76 0"/></defs>'
                '<text font-size="11" font-weight="700" fill="currentColor"><textPath href="#cp">เปิดทุกวัน · OPEN DAILY · เปิดทุกวัน ·</textPath></text></svg>'
                '<b style="font-size:20px">★</b></div>')
    if n == "4":
        return f'<div class="card c2 lift"><b>{item}</b><span>ชี้เมาส์เพื่อดู</span></div>'
    if n == "5":
        return '<div class="grain"></div>'
    if n == "6":
        return '<div class="blobs"><i></i><i></i></div>'
    if n == "7":
        return f'<div class="rv"><span>{brand}</span><span>ข้อความเปิดตัวทีละบรรทัด</span></div>'
    return ('<div class="cur" onmousemove="var r=this.getBoundingClientRect(),d=this.firstChild;d.style.left=(event.clientX-r.left)+\'px\';'
            'd.style.top=(event.clientY-r.top)+\'px\'"><i></i></div>')


def cmd_list(_a):
    for g, name in GROUPS.items():
        print(f"{g}  {name}")
        for vid, (vname, feel, _) in V.items():
            if vid[0] == g:
                print(f"   {vid:3} {vname:22} {feel}")


def cmd_preview(a):
    r, src = load_roles(a.style)
    on_accent = max(((1, 1, 1), (0.07, 0.07, 0.07)), key=lambda x: S.contrast(x, r["accent"]))
    def css(v) -> str:  # values go inside <style>, where HTML entities are not decoded
        return re.sub(r"[<>{};]", "", str(v))
    var = (f"--bg:{S.to_hex(r['bg'])};--fg:{S.to_hex(r['text'])};--muted:{S.to_hex(r['muted'])};"
           f"--surface:{S.to_hex(r['surface'])};--primary:{S.to_hex(r['primary'])};--onp:{S.to_hex(r['on_primary'])};"
           f"--accent:{S.to_hex(r['accent'])};--ona:{S.to_hex(on_accent)};--border:{S.to_hex(r['border'])};"
           f"--rc:{css(r['radius_control'])};--rk:{css(r['radius_card'])};"
           f"--display:{css(S.stack(r['display'], r['thai_display'], r['serif']))};"
           f"--body:{css(S.stack(r['body'], r['thai_body'], False))};"
           f"--label:{css(S.stack(r['label'], r['thai_body'], False))}")
    fams = {r["display"], r["body"], r["label"], r["thai_display"], r["thai_body"]}
    groups = []
    for g, name in GROUPS.items():
        tiles = "".join(f'<div class="tile"><div class="stage">{demo(vid, a)}</div><div class="cap">{vid} · {html.escape(n)}'
                        f'<small>{html.escape(feel)}</small></div></div>'
                        for vid, (n, feel, _) in V.items() if vid[0] == g)
        if g == "I":
            tiles += (f'<div class="tile"><div class="stage"><div class="pf">{CUP}<span>รูปหน้าร้าน</span></div></div>'
                      f'<div class="cap">Placeholder frame<small>used in any image style until photos arrive</small></div></div>')
        wide = " wide" if g == "N" else ""
        groups.append(f'<section class="grp"><h2>{g} · {name}</h2><div class="grid{wide}">{tiles}</div></section>')
    page = f"""<!doctype html><html lang="th"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Component style</title>{S.font_links(fams)}<style>:root{{{var}}}{CSS}</style></head><body>
<header class="top"><h1>เลือกสไตล์คอมโพเนนต์ · Component style</h1>
<p>Tokens from {html.escape(src)}. Pick one per group, for example <b>B2 C4 N1 M1 F1 T3 I3 S2</b>. Hover to see effects.
You can also describe your own ("buttons like apple.com", "a live queue counter") and it is recorded as custom.</p></header>
{''.join(groups)}</body></html>"""
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print(f"{out.as_posix()}  ({sum(1 for _ in V)} variants in {len(GROUPS)} groups; open it and let the user choose)")


def cmd_choose(a):
    picks, rows = {}, []
    for vid in a.ids:
        vid = vid.upper()
        if vid not in V:
            sys.exit(f"unknown variant {vid}; see components.py list")
        picks[vid[0]] = vid
    custom = {}
    for c in a.custom or []:
        g, _, text = c.partition("=")
        g = g.strip().upper()[:1]
        if g not in GROUPS or not text.strip():
            sys.exit(f"--custom needs GROUP=TEXT with GROUP one of {', '.join(GROUPS)}")
        custom[g] = text.strip()
    missing = [GROUPS[g] for g in REQUIRED if g not in picks and g not in custom]
    if missing:
        sys.exit(f"choose at least one variant for: {', '.join(missing)}")
    for g, name in GROUPS.items():
        if g in picks:
            vname, _, spec = V[picks[g]]
            spec += " " + PHOTO_PLACEHOLDER if g == "I" else ""
            rows.append(f"| {name} | {picks[g]} {vname} | {spec} |")
        if g in custom:
            extra = " " + PHOTO_PLACEHOLDER if g == "I" else ""
            rows.append(f"| {name} | custom (user) | {custom[g].replace('|', '/')}{extra} |")
    block = ("## Component style\n"
             f"Chosen by the user from `.webcraft/preview/components.html` on {dt.date.today().isoformat()}. "
             "Build exactly these specs with the tokens in the front matter; one style per group across the whole site.\n\n"
             "| Group | Choice | Spec |\n|---|---|---|\n" + "\n".join(rows) + "\n\n")
    f = Path(a.design)
    if not f.is_file():
        sys.exit(f"{f} not found: export the chosen style first (styles.py export ID)")
    t = f.read_text(encoding="utf-8")
    if re.search(r"^## Component style", t, re.M):
        t = re.sub(r"^## Component style.*?(?=^## |\Z)", lambda _: block, t, flags=re.S | re.M)
    elif re.search(r"^## Components", t, re.M):
        t = re.sub(r"^## Components", lambda _: block + "## Components", t, count=1, flags=re.M)
    else:
        t = t.rstrip("\n") + "\n\n" + block
    f.write_text(t, encoding="utf-8")
    print(f"recorded {len(rows)} component choices in {f.as_posix()} (section 'Component style')")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Preview and record component style choices")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    p = sub.add_parser("preview")
    p.add_argument("--style", help="style id, when DESIGN.md is not exported yet")
    p.add_argument("--brand", default="แบรนด์ของคุณ")
    p.add_argument("--cta1", default="ดูรายละเอียด", help="main action label, e.g. ดูเส้นทาง")
    p.add_argument("--cta2", default="ติดต่อเรา", help="second action label, e.g. แอดไลน์")
    p.add_argument("--item", default="รายการแนะนำ", help="a real item name for the card samples")
    p.add_argument("--out", default=".webcraft/preview/components.html")
    c = sub.add_parser("choose")
    c.add_argument("ids", nargs="*", help="one variant per group, e.g. B2 C4 N1 M1 F1 T3 I3 S2")
    c.add_argument("--custom", action="append", help="GROUP=TEXT for the user's own variant, e.g. \"S=live queue counter\"")
    c.add_argument("--design", default=".webcraft/DESIGN.md")
    a = ap.parse_args()
    {"list": cmd_list, "preview": cmd_preview, "choose": cmd_choose}[a.cmd](a)


if __name__ == "__main__":
    main()
