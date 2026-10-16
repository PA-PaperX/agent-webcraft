#!/usr/bin/env python3
"""Screenshot a URL at standard viewport sizes with Playwright (run through npx).

Fallback for agents without a built-in browser. Usage:
    python shoot.py URL [--out DIR] [--sizes 390x844,768x1024,1440x900] [--full-page] [--dark] [--wait MS]

The first run may need the browser binary: `npx playwright install chromium` (about 150 MB download);
ask the user before running that. Prints one line per screenshot so the agent can open the images.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

PLAYWRIGHT = "playwright@1"  # pin the major so CLI flags stay stable


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Screenshots at standard viewport sizes (Playwright via npx)")
    ap.add_argument("url")
    ap.add_argument("--out", default=".webcraft/shots")
    ap.add_argument("--sizes", default="390x844,768x1024,1440x900")
    ap.add_argument("--full-page", action="store_true")
    ap.add_argument("--dark", action="store_true", help="emulate prefers-color-scheme: dark")
    ap.add_argument("--wait", type=int, default=1500, help="ms to wait after load (animations, fonts)")
    a = ap.parse_args()

    npx = shutil.which("npx")
    if not npx:
        print("npx not found: install Node.js, or use the agent's built-in browser instead", file=sys.stderr)
        return 2
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", re.sub(r"^https?://", "", a.url.lower())).strip("-")[:50] or "page"
    status = 0
    for size in a.sizes.split(","):
        w, h = size.lower().split("x")
        target = out / f"{slug}-{w}x{h}{'-dark' if a.dark else ''}.png"
        cmd = [npx, "-y", PLAYWRIGHT, "screenshot", f"--viewport-size={w},{h}", f"--wait-for-timeout={a.wait}"]
        if a.full_page:
            cmd.append("--full-page")
        if a.dark:
            cmd.append("--color-scheme=dark")
        cmd += [a.url, str(target)]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0:
            err = (r.stderr or r.stdout).strip()
            if "playwright install" in err or "Executable doesn't exist" in err:
                print("Playwright's browser is not installed. Ask the user, then run: "
                      "npx playwright install chromium", file=sys.stderr)
                return 3
            print(f"FAILED {w}x{h}: {err.splitlines()[-1] if err else 'unknown error'}", file=sys.stderr)
            status = 1
            continue
        print(target.as_posix())
    return status


if __name__ == "__main__":
    sys.exit(main())
