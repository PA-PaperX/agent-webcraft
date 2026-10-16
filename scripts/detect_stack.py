#!/usr/bin/env python3
"""Detect a web project's stack, the exact installed versions, and where version-matched docs live.

Usage:
    python detect_stack.py [PROJECT_DIR] [--json]

Read-only, standard library only. Installed versions come from node_modules (ground truth), then the
lockfile, then the package.json range (reported as a range, not a version).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

KEY_PACKAGES = [
    "next", "react", "react-dom", "vite", "@vitejs/plugin-react", "@sveltejs/kit", "svelte", "astro", "nuxt",
    "vue", "tailwindcss", "@tailwindcss/vite", "@tailwindcss/postcss", "shadcn", "typescript",
    "@supabase/supabase-js", "@supabase/ssr", "motion", "framer-motion", "gsap", "three", "@react-three/fiber",
    "react-router", "react-router-dom", "zod", "@prisma/client", "drizzle-orm", "@tanstack/react-query",
    "vitest", "jest", "@playwright/test",
]
ICON_PACKAGES = [
    "lucide-react", "@lucide/svelte", "lucide-svelte", "lucide-vue-next", "@tabler/icons-react",
    "@tabler/icons-svelte", "@tabler/icons-vue", "@phosphor-icons/react", "@phosphor-icons/vue", "phosphor-svelte",
    "@heroicons/react", "@heroicons/vue", "@radix-ui/react-icons", "react-icons", "@iconify/react", "@iconify/svelte",
    "@iconify/vue", "@iconify/tailwind4", "@iconify/tailwind", "unplugin-icons", "@mdi/js",
    "@fortawesome/react-fontawesome", "@fortawesome/fontawesome-svg-core", "simple-icons", "@hugeicons/react",
    "iconoir-react",
]
MOTION_PACKAGES = [
    "@gsap/react", "lottie-react", "lottie-web", "@lottiefiles/dotlottie-react", "@lottiefiles/dotlottie-web",
    "@rive-app/react-canvas", "@rive-app/canvas", "@react-spring/web", "@formkit/auto-animate", "animejs", "lenis",
    "@studio-freight/lenis", "tw-animate-css", "tailwindcss-animate", "@paper-design/shaders-react",
    "@react-three/drei", "svelte-motion",
]
MOTION_CORE = {"motion", "framer-motion", "gsap", "three", "@react-three/fiber"}
BACKEND_PACKAGES = ["elysia", "hono", "express", "fastify", "@nestjs/core", "koa", "@trpc/server"]
DATA_PACKAGES = ["@supabase/supabase-js", "@supabase/ssr", "drizzle-orm", "prisma", "@prisma/client", "kysely", "pg",
                 "postgres", "@neondatabase/serverless", "mysql2", "mongodb", "mongoose", "better-sqlite3",
                 "@libsql/client", "ioredis", "redis", "@upstash/redis", "firebase", "convex"]
LOCKFILES = {"pnpm-lock.yaml": "pnpm", "package-lock.json": "npm", "yarn.lock": "yarn", "bun.lock": "bun",
             "bun.lockb": "bun"}
# Keep in sync with references/docs-map.md (that file is the canonical, dated list).
DOCS_ONLINE = {
    "next": "https://nextjs.org/docs/llms.txt",
    "react": "https://react.dev/llms.txt",
    "vite": "https://vite.dev/llms.txt",
    "@sveltejs/kit": "https://svelte.dev/llms.txt",
    "svelte": "https://svelte.dev/llms.txt",
    "@supabase/supabase-js": "https://supabase.com/llms.txt",
    "motion": "https://motion.dev/llms.txt",
    "framer-motion": "https://motion.dev/llms.txt",
    "gsap": "https://gsap.com/llms.txt",
    "@react-three/fiber": "https://r3f.docs.pmnd.rs/llms.txt",
    "three": "https://threejs.org/llms.txt",
    "lucide-react": "https://lucide.dev/llms.txt",
    "@lucide/svelte": "https://lucide.dev/llms.txt",
    "lucide-svelte": "https://lucide.dev/llms.txt",
    "@lottiefiles/dotlottie-react": "https://docs.lottiefiles.com/llms.txt",
    "lenis": "https://lenis.darkroom.engineering/llms.txt",
    "elysia": "https://elysiajs.com/llms.txt",
    "hono": "https://hono.dev/llms.txt",
    "express": "https://expressjs.com/llms.txt",
    "fastify": "https://fastify.dev/llms.txt",
    "@nestjs/core": "https://docs.nestjs.com/llms.txt",
    "drizzle-orm": "https://orm.drizzle.team/llms.txt",
    "prisma": "https://www.prisma.io/docs/llms.txt",
    "@prisma/client": "https://www.prisma.io/docs/llms.txt",
    "@neondatabase/serverless": "https://neon.com/llms.txt",
    "@libsql/client": "https://docs.turso.tech/llms.txt",
    "mongoose": "https://mongoosejs.com/llms.txt",
    "mongodb": "https://www.mongodb.com/docs/llms.txt",
    "convex": "https://docs.convex.dev/llms.txt",
    "firebase": "https://firebase.google.com/docs/llms.txt",
    "@upstash/redis": "https://upstash.com/docs/llms.txt",
    "zod": "https://zod.dev/llms.txt",
    "tailwindcss": "https://tailwindcss.com/docs",
}
SCRIPT_NAMES = ("dev", "build", "start", "preview", "lint", "typecheck", "check", "test", "format")
SKIP_DIRS = {"node_modules", ".git", ".next", ".svelte-kit", "dist", "build", ".vercel", ".turbo", "out"}


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return None


def find_project(start: Path) -> Path | None:
    if (start / "package.json").is_file():
        return start
    for depth_glob in ("*/package.json", "*/*/package.json"):
        for p in sorted(start.glob(depth_glob)):
            if not SKIP_DIRS.intersection(p.parts):
                return p.parent
    return None


def lockfile(root: Path):
    for name, pm in LOCKFILES.items():
        p = root / name
        if p.is_file():
            return p, pm
    return None, None


def lock_version(lock: Path | None, pkg: str) -> str | None:
    if not lock or lock.name == "bun.lockb":
        return None
    text = lock.read_text(encoding="utf-8", errors="replace")
    esc = re.escape(pkg)
    if lock.name == "package-lock.json":
        data = load_json(lock) or {}
        entry = (data.get("packages") or {}).get(f"node_modules/{pkg}") or {}
        return entry.get("version")
    if lock.name == "pnpm-lock.yaml":
        m = re.search(rf"^\s+'?{esc}'?:\s*\n\s+specifier:.*\n\s+version:\s*'?([0-9][^\s'(]*)", text, re.M)
        if not m:
            m = re.search(rf"^\s+'?/?{esc}@([0-9][^:'(\s]*)", text, re.M)
        return m.group(1) if m else None
    if lock.name == "yarn.lock":
        m = re.search(rf'^"?{esc}@[^\n]*:\n\s+version:?\s+"?([^"\n]+)', text, re.M)
        return m.group(1) if m else None
    if lock.name == "bun.lock":
        m = re.search(rf'"{esc}":\s*\["{esc}@([^"]+)"', text)
        return m.group(1) if m else None
    return None


def resolve(root: Path, lock: Path | None, pkg: str, declared: dict) -> dict | None:
    if pkg not in declared:
        return None
    installed = load_json(root / "node_modules" / pkg / "package.json")
    if installed and installed.get("version"):
        return {"version": installed["version"], "source": "installed"}
    v = lock_version(lock, pkg)
    if v:
        return {"version": v, "source": "lockfile"}
    return {"version": declared[pkg], "source": "range (not installed)"}


def major(v: str | None) -> int | None:
    m = re.search(r"(\d+)", v or "")
    return int(m.group(1)) if m else None


def first_existing(root: Path, *rels: str) -> str | None:
    for r in rels:
        if (root / r).exists():
            return r
    return None


def tailwind_info(root: Path, ver: str | None) -> dict:
    info = {"major": major(ver)}
    cfg = next((p.name for p in root.glob("tailwind.config.*")), None)
    if cfg:
        info["config"] = cfg
    css_hits = []
    for base in ("app", "src", "styles", "."):
        d = root / base
        if not d.is_dir():
            continue
        pattern = "*.css" if base == "." else "**/*.css"
        for css in d.glob(pattern):
            if SKIP_DIRS.intersection(css.relative_to(root).parts):
                continue
            try:
                head = css.read_text(encoding="utf-8", errors="replace")[:20000]
            except OSError:
                continue
            if '@import "tailwindcss"' in head or "@import 'tailwindcss'" in head or "@theme" in head:
                css_hits.append(css.relative_to(root).as_posix())
            if len(css_hits) >= 3:
                break
    if css_hits:
        info["css_first"] = css_hits
    return info


def webcraft_info(root: Path) -> dict | None:
    wc = root / ".webcraft"
    if not wc.is_dir():
        return None
    info = {}
    brief = wc / "BRIEF.md"
    if brief.is_file():
        m = re.search(r"Status:\s*([^\n·]+)", brief.read_text(encoding="utf-8", errors="replace"))
        info["brief"] = m.group(1).strip() if m else "present"
    counts = {}
    for t in (wc / "tasks").glob("*.md") if (wc / "tasks").is_dir() else []:
        m = re.search(r"^status:\s*(\S+)", t.read_text(encoding="utf-8", errors="replace"), re.M)
        s = m.group(1) if m else "?"
        counts[s] = counts.get(s, 0) + 1
    info["tasks"] = counts
    info["state"] = (wc / "STATE.md").is_file()
    return info


def detect(start: Path) -> dict:
    root = find_project(start)
    if root is None:
        return {"error": f"no package.json found in {start} (or two levels below)"}
    pkg = load_json(root / "package.json") or {}
    declared = {**pkg.get("devDependencies", {}), **pkg.get("dependencies", {})}
    lock, pm = lockfile(root)
    versions = {p: r for p in KEY_PACKAGES if (r := resolve(root, lock, p, declared))}
    icons = {p: r for p in ICON_PACKAGES if (r := resolve(root, lock, p, declared))}
    motion = {p: r for p in MOTION_PACKAGES if (r := resolve(root, lock, p, declared))}
    motion.update({p: r for p, r in versions.items() if p in MOTION_CORE})
    backend = {p: r for p in BACKEND_PACKAGES if (r := resolve(root, lock, p, declared))}
    data = {p: r for p in DATA_PACKAGES if (r := resolve(root, lock, p, declared))}
    known = set(KEY_PACKAGES) | set(ICON_PACKAGES) | set(MOTION_PACKAGES) | set(BACKEND_PACKAGES) | set(DATA_PACKAGES)
    other = {p: r for p in pkg.get("dependencies", {}) if p not in known and (r := resolve(root, lock, p, declared))}
    v = {p: r["version"] for p, r in versions.items()}

    frameworks = []
    if "next" in v:
        routers = [n for n, rels in (("App Router", ("app", "src/app")), ("Pages Router", ("pages", "src/pages")))
                   if first_existing(root, *rels)]
        frameworks.append(f"Next.js {v['next']}" + (f" ({', '.join(routers)})" if routers else ""))
    if "@sveltejs/kit" in v:
        sv = major(v.get("svelte"))
        frameworks.append(f"SvelteKit {v['@sveltejs/kit']}" +
                          (f" · Svelte {v['svelte']} ({'runes' if sv and sv >= 5 else 'legacy syntax'})"
                           if "svelte" in v else ""))
    if "astro" in v:
        frameworks.append(f"Astro {v['astro']}")
    if "nuxt" in v:
        frameworks.append(f"Nuxt {v['nuxt']}")
    if "vite" in v and "next" not in v and "@sveltejs/kit" not in v and "astro" not in v:
        frameworks.append(f"Vite {v['vite']}" + (f" + React {v['react']} SPA" if "react" in v else ""))
    if "react" in v and "next" in v:
        frameworks.append(f"React {v['react']}")

    result = {
        "project": pkg.get("name") or root.name,
        "root": str(root),
        "package_manager": pm or "unknown (no lockfile)",
        "fingerprint": hashlib.sha1((lock or root / "package.json").read_bytes()).hexdigest()[:12],
        "frameworks": frameworks,
        "versions": versions,
        "icons": icons,
        "motion": motion,
        "backend": backend,
        "data": data,
        "other": other,
        "scripts": [s for s in SCRIPT_NAMES if s in pkg.get("scripts", {})],
    }
    if "tailwindcss" in v or "@tailwindcss/vite" in v or "@tailwindcss/postcss" in v:
        tv = v.get("tailwindcss") or v.get("@tailwindcss/vite") or v.get("@tailwindcss/postcss")
        result["tailwind"] = tailwind_info(root, tv)
    comp = load_json(root / "components.json")
    if comp:
        result["shadcn"] = {k: comp.get(k) for k in ("style", "tsx", "iconLibrary") if k in comp}
        tw = comp.get("tailwind") or {}
        result["shadcn"].update({f"tailwind.{k}": tw[k] for k in ("config", "css", "baseColor") if tw.get(k)})

    disk = []
    if (root / "node_modules/next/dist/docs").is_dir():
        disk.append("node_modules/next/dist/docs (version-matched)")
    if (root / ".next-docs").is_dir():
        disk.append(".next-docs (generated by next codemod)")
    for p in versions:
        d = root / "node_modules" / p / "docs"
        if d.is_dir() and p != "next":
            disk.append(f"node_modules/{p}/docs")
    agents = root / "AGENTS.md"
    if agents.is_file():
        text = agents.read_text(encoding="utf-8", errors="replace")
        blocks = re.findall(r"<!-- BEGIN:([\w-]+) -->", text)
        disk.append("AGENTS.md" + (f" (blocks: {', '.join(blocks)})" if blocks else ""))
    result["docs_on_disk"] = disk
    result["docs_online"] = sorted({DOCS_ONLINE[p] for p in [*versions, *icons, *motion, *backend, *data]
                                    if p in DOCS_ONLINE})
    if result.get("shadcn"):
        result["docs_online"].append("https://ui.shadcn.com/llms.txt")
    result["webcraft"] = webcraft_info(root)
    return result


def as_text(r: dict) -> str:
    if "error" in r:
        return r["error"]
    lines = [f"project: {r['project']}  ({r['package_manager']}, fingerprint {r['fingerprint']})",
             f"root: {r['root']}"]
    lines.append("framework: " + (" · ".join(r["frameworks"]) or "none detected"))
    shown = {"next", "react", "react-dom", "vite", "@sveltejs/kit", "svelte"} | MOTION_CORE | set(DATA_PACKAGES)

    def fmt(items):
        return ", ".join(f"{p} {x['version']}" + ("" if x["source"] == "installed" else f" [{x['source']}]")
                         for p, x in items)

    libs = [(p, x) for p, x in r["versions"].items() if p not in shown]
    if libs:
        lines.append("libs: " + fmt(libs))
    lines.append("icons: " + (fmt(r["icons"].items()) or "none (no SVG icon package; see references/icons.md)"))
    lines.append("motion: " + (fmt(r["motion"].items()) or "none (CSS only)"))
    lines.append("backend: " + (fmt(r["backend"].items()) or "none (framework routes only)"))
    lines.append("data: " + (fmt(r["data"].items()) or "none") + "   (machine tools: env_check.py)")
    other = list(r["other"].items())
    if other:
        lines.append("other deps: " + fmt(other[:14]) + (f" (+{len(other) - 14} more)" if len(other) > 14 else ""))
    if "tailwind" in r:
        t = r["tailwind"]
        style = []
        if t.get("css_first"):
            style.append("CSS-first in " + ", ".join(t["css_first"]))
        if t.get("config"):
            style.append("config file " + t["config"])
        lines.append(f"tailwind: v{t.get('major')}" + (f" ({'; '.join(style)})" if style else ""))
    if r.get("shadcn"):
        lines.append("shadcn: " + ", ".join(f"{k}={v}" for k, v in r["shadcn"].items()))
    lines.append("scripts: " + (", ".join(r["scripts"]) or "none"))
    lines.append("docs on disk: " + ("; ".join(r["docs_on_disk"]) or "none found"))
    lines.append("docs online: " + (", ".join(r["docs_online"]) or "see references/docs-map.md"))
    wc = r["webcraft"]
    if wc is None:
        lines.append("webcraft: none -> first session, start with Discover")
    else:
        tasks = ", ".join(f"{k}={n}" for k, n in sorted(wc["tasks"].items())) or "no tasks"
        lines.append(f"webcraft: brief {wc.get('brief', 'missing')}; {tasks}; STATE {'ok' if wc['state'] else 'missing'}")
    return "\n".join(lines)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("project", nargs="?", default=".")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    a = ap.parse_args()
    r = detect(Path(a.project).resolve())
    print(json.dumps(r, indent=2, ensure_ascii=False) if a.json else as_text(r))
    return 1 if "error" in r else 0


if __name__ == "__main__":
    sys.exit(main())
