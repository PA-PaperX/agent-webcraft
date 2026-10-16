#!/usr/bin/env python3
"""Live facts about npm packages and web platform features, so choices rest on today's data, not memory.

Usage:
  python latest.py PKG [PKG ...] [--root PROJECT] [--json]
      Latest version (and how far the installed one is behind, if --root has node_modules), license,
      publish date, weekly downloads, known security advisories, deprecation, homepage, and an
      llms.txt docs index if the homepage has one.
  python latest.py --baseline FEATURE [FEATURE ...]
      Web platform Baseline status from web-platform-dx/web-features.
      Feature ids: https://web-platform-dx.github.io/web-features-explorer/

Sources: registry.npmjs.org, api.npmjs.org, api.deps.dev, the package homepage, raw.githubusercontent.com.
Standard library only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

UA = {"User-Agent": "agent-webcraft-latest/1"}
OSI = {"MIT", "ISC", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "MPL-2.0", "CC0-1.0", "0BSD", "Unlicense",
       "BlueOak-1.0.0", "Zlib", "Python-2.0", "CC-BY-4.0"}


def fetch(url: str, timeout: int = 15):
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.headers.get("Content-Type", ""), r.read()
    except urllib.error.HTTPError as e:
        return e.code, "", b""
    except (urllib.error.URLError, TimeoutError, OSError):
        return 0, "", b""


def fetch_json(url: str):
    status, _, body = fetch(url)
    if status != 200:
        return None
    try:
        return json.loads(body)
    except ValueError:
        return None


def ver_tuple(v: str) -> tuple:
    return tuple(int(x) for x in re.findall(r"\d+", v.split("-")[0])[:3])


def behind(installed: str, latest: str) -> str:
    a, b = ver_tuple(installed), ver_tuple(latest)
    if not a or not b or a >= b:
        return "up to date" if a == b else "ahead or prerelease"
    if a[0] < b[0]:
        return f"{b[0] - a[0]} major behind"
    if len(a) > 1 and len(b) > 1 and a[1] < b[1]:
        return f"{b[1] - a[1]} minor behind"
    return "patch behind"


def llms_txt(homepage: str | None) -> str | None:
    if not homepage or not homepage.startswith("http"):
        return None
    u = urllib.parse.urlparse(homepage)
    if u.netloc in ("github.com", "www.github.com", "npmjs.com", "www.npmjs.com"):
        return None
    candidates = [f"{u.scheme}://{u.netloc}/llms.txt"]
    path = u.path.rstrip("/")
    if path:
        candidates.append(f"{u.scheme}://{u.netloc}{path}/llms.txt")
    for c in candidates:
        status, ctype, body = fetch(c, timeout=10)
        head = body[:200].lstrip().lower()
        # Many sites answer 200 with their HTML app shell; only a markdown body counts.
        if status == 200 and "html" not in ctype and head.startswith(b"#"):
            return c
    return None


def package_facts(pkg: str, root: Path | None) -> dict:
    q = urllib.parse.quote(pkg, safe="@")
    meta = fetch_json(f"https://registry.npmjs.org/{q}/latest")
    if not meta:
        return {"package": pkg, "error": "not found on npm (check the name)"}
    version = meta.get("version", "")
    lic = meta.get("license")
    if isinstance(lic, dict):
        lic = lic.get("type")
    homepage = meta.get("homepage") or ""
    repo = meta.get("repository") or {}
    repo = repo.get("url") if isinstance(repo, dict) else repo
    facts = {"package": pkg, "latest": version, "license": lic or "none declared", "homepage": homepage,
             "repository": (repo or "").replace("git+", "").replace(".git", ""), "deprecated": meta.get("deprecated")}
    dl = fetch_json(f"https://api.npmjs.org/downloads/point/last-week/{pkg}")
    facts["weekly_downloads"] = dl.get("downloads") if dl else None
    dd = fetch_json(f"https://api.deps.dev/v3/systems/npm/packages/{urllib.parse.quote(pkg, safe='')}"
                    f"/versions/{urllib.parse.quote(version, safe='')}")
    if dd:
        facts["published"] = (dd.get("publishedAt") or "")[:10]
        facts["advisories"] = dd.get("advisoryKeys") or []
        if dd.get("licenses"):
            facts["license_spdx"] = dd["licenses"]
    if root:
        inst = root / "node_modules" / pkg / "package.json"
        if inst.is_file():
            try:
                iv = json.loads(inst.read_text(encoding="utf-8-sig")).get("version", "")
                facts["installed"] = iv
                facts["installed_status"] = behind(iv, version)
            except (OSError, ValueError):
                pass
    facts["llms_txt"] = llms_txt(homepage)
    return facts


def fmt_num(n) -> str:
    if n is None:
        return "?"
    for unit, div in (("M", 1_000_000), ("k", 1_000)):
        if n >= div:
            return f"{n / div:.1f}{unit}"
    return str(n)


def package_line(f: dict) -> str:
    if "error" in f:
        return f"{f['package']}: {f['error']}"
    spdx = f.get("license_spdx") or [f["license"]]
    lic = ", ".join(spdx)
    if not set(spdx) & OSI:
        lic = f"LICENSE {f['license']} [not a standard open-source license: read the terms]"
    parts = [f"{f['package']} {f['latest']}", lic]
    if "-" in f["latest"]:
        parts.insert(1, "PRERELEASE is tagged latest: pin the last stable version unless the user wants the prerelease")
    if f.get("published"):
        parts.append(f"published {f['published']}")
    parts.append(f"{fmt_num(f.get('weekly_downloads'))}/wk")
    if f.get("installed"):
        parts.append(f"installed {f['installed']} ({f['installed_status']})")
    if f.get("advisories"):
        parts.append(f"ADVISORIES {len(f['advisories'])}: " + ", ".join(a.get("id", "?") for a in f["advisories"][:3]))
    if f.get("deprecated"):
        parts.append(f"DEPRECATED: {str(f['deprecated'])[:80]}")
    parts.append(f"docs {f['llms_txt']}" if f.get("llms_txt") else f"home {f['homepage'] or f['repository'] or '?'}")
    return " · ".join(parts)


def baseline(feature: str) -> dict:
    url = f"https://raw.githubusercontent.com/web-platform-dx/web-features/main/features/{feature}.yml.dist"
    status, _, body = fetch(url)
    if status != 200:
        return {"feature": feature, "error": "unknown feature id; search "
                                             "https://web-platform-dx.github.io/web-features-explorer/"}
    text = body.decode("utf-8", errors="replace").split("compat_features:")[0]
    get = lambda k: (m.group(1).strip().strip('"') if (m := re.search(rf"^\s*{k}:\s*(.+)$", text, re.M)) else None)
    support = dict(re.findall(r"^\s{4}(chrome|edge|firefox|safari):\s*\"?([^\"\n]+)", text, re.M))
    return {"feature": feature, "baseline": get("baseline"), "low_date": get("baseline_low_date"),
            "high_date": get("baseline_high_date"), "support": support}


def baseline_line(b: dict) -> str:
    if "error" in b:
        return f"{b['feature']}: {b['error']}"
    sup = ", ".join(f"{k} {v}" for k, v in b["support"].items()) or "no full support data"
    if b["baseline"] == "high":
        state = f"Baseline widely available since {b['high_date']}"
    elif b["baseline"] == "low":
        state = f"Baseline newly available since {b['low_date']} (older browsers may lack it)"
    else:
        state = "NOT Baseline (limited availability): use only as progressive enhancement"
    return f"{b['feature']}: {state} · {sup}"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Live npm package facts and web platform Baseline status")
    ap.add_argument("items", nargs="+", help="npm package names, or feature ids with --baseline")
    ap.add_argument("--baseline", action="store_true", help="treat items as web-features ids")
    ap.add_argument("--root", type=Path, help="project dir, to compare with installed versions")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    with ThreadPoolExecutor(max_workers=8) as pool:
        if a.baseline:
            results = list(pool.map(baseline, a.items))
            lines = [baseline_line(r) for r in results]
        else:
            root = a.root.resolve() if a.root else None
            results = list(pool.map(lambda p: package_facts(p, root), a.items))
            lines = [package_line(r) for r in results]
    print(json.dumps(results, indent=2, ensure_ascii=False) if a.json else "\n".join(lines))
    return 1 if any("error" in r for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
