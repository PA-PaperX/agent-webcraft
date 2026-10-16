#!/usr/bin/env python3
"""Search and fetch SVG icons across 200+ open icon sets through the Iconify API (live data).

Usage:
  python icons.py search QUERY [--prefix lucide,tabler,ph] [--limit 32]
      Icon names matching a concept, grouped by set, e.g. "lucide: coffee | tabler: coffee, coffee-off".
  python icons.py sets [--prefix lucide,tabler,ph] [--query WORD] [--limit 30]
      Icon sets with icon count, license, grid height and category (largest first).
  python icons.py get PREFIX:NAME [--out FILE] [--height 24]
      The SVG of one icon (uses currentColor), printed or written to FILE.

For production, prefer the icon family's own package or a build-time Iconify integration over runtime
API calls (see references/icons.md). Standard library only.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://api.iconify.design"
UA = {"User-Agent": "agent-webcraft-icons/1"}


def get(path: str, **params) -> tuple[int, bytes]:
    qs = urllib.parse.urlencode({k: v for k, v in params.items() if v not in (None, "")})
    req = urllib.request.Request(f"{API}{path}" + (f"?{qs}" if qs else ""), headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        print(f"network error: {e}", file=sys.stderr)
        return 0, b""


def cmd_search(a) -> int:
    params = {"query": a.query, "limit": max(32, a.limit)}
    if a.prefix:
        params["prefixes" if "," in a.prefix else "prefix"] = a.prefix
    status, body = get("/search", **params)
    if status != 200:
        print(f"search failed (HTTP {status})", file=sys.stderr)
        return 1
    data = json.loads(body)
    groups: dict[str, list[str]] = {}
    for full in data.get("icons", [])[: a.limit]:
        prefix, name = full.split(":", 1)
        groups.setdefault(prefix, []).append(name)
    if not groups:
        print(f'no icons for "{a.query}"' + (f" in {a.prefix}" if a.prefix else "") +
              "; try a synonym or a broader concept")
        return 0
    for prefix, names in groups.items():
        print(f"{prefix}: {', '.join(names)}")
    print(f"({sum(map(len, groups.values()))} shown; raise --limit for more. Refer to an icon as prefix:name, "
          f"e.g. {next(iter(groups))}:{groups[next(iter(groups))][0]})")
    return 0


def cmd_sets(a) -> int:
    status, body = get("/collections", prefixes=a.prefix)
    if status != 200:
        print(f"collections failed (HTTP {status})", file=sys.stderr)
        return 1
    sets = json.loads(body)
    rows = []
    for prefix, info in sets.items():
        text = f"{prefix} {info.get('name', '')} {info.get('category', '')}".lower()
        if a.query and a.query.lower() not in text:
            continue
        lic = info.get("license") or {}
        rows.append((info.get("total", 0), prefix, info.get("name", ""), lic.get("spdx") or lic.get("title", "?"),
                     info.get("height", ""), info.get("category", "")))
    for total, prefix, name, lic, height, cat in sorted(rows, reverse=True)[: a.limit]:
        print(f"{prefix:22} {name[:30]:30} {total:>6} icons  {lic:14} grid {str(height):4} {cat}")
    if not rows:
        print("no matching sets")
    return 0


def cmd_get(a) -> int:
    if ":" not in a.icon:
        print("use PREFIX:NAME, e.g. lucide:coffee (find names with `icons.py search`)", file=sys.stderr)
        return 2
    prefix, name = a.icon.split(":", 1)
    status, body = get(f"/{urllib.parse.quote(prefix)}/{urllib.parse.quote(name)}.svg", height=a.height)
    if status != 200 or not body.lstrip().startswith(b"<svg"):
        print(f"icon {a.icon} not found (HTTP {status})", file=sys.stderr)
        return 1
    svg = body.decode("utf-8")
    if a.out:
        out = Path(a.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(svg, encoding="utf-8")
        print(out.as_posix())
    else:
        print(svg)
    return 0


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Search and fetch SVG icons across open icon sets (Iconify API)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="find icon names for a concept")
    s.add_argument("query")
    s.add_argument("--prefix", help="limit to sets, e.g. lucide or lucide,tabler,ph")
    s.add_argument("--limit", type=int, default=32)
    s = sub.add_parser("sets", help="list icon sets with count and license")
    s.add_argument("--prefix", help="comma-separated set prefixes")
    s.add_argument("--query", help="filter by name or category")
    s.add_argument("--limit", type=int, default=30)
    s = sub.add_parser("get", help="fetch one icon's SVG")
    s.add_argument("icon", help="PREFIX:NAME")
    s.add_argument("--out")
    s.add_argument("--height", default="24")
    a = ap.parse_args()
    return {"search": cmd_search, "sets": cmd_sets, "get": cmd_get}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
