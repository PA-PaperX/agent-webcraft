#!/usr/bin/env python3
"""What is available for a stack decision: on this machine, and already in the project.

Usage:
    python env_check.py [PROJECT_DIR] [--latest] [--json]

Machine: JS runtimes, package managers, Python, Docker, database servers and clients, hosting CLIs, with versions.
Project: package manager and runtime pins, backend frameworks, database clients and ORMs, docker-compose services,
         and the NAMES of env variables (values are never read or printed).
--latest adds today's versions of Node (LTS and current), Bun, Deno, pnpm and Yarn, for comparison.
Standard library only.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

MACHINE_TOOLS = {
    "runtime": ["node", "bun", "deno"],
    "package manager": ["npm", "pnpm", "yarn", "bun"],
    "python": ["python", "uv"],
    "containers": ["docker", "podman"],
    "database": ["psql", "mysql", "sqlite3", "mongosh", "mongod", "redis-server", "redis-cli"],
    "hosting / platform CLI": ["git", "gh", "supabase", "vercel", "netlify", "wrangler", "railway", "flyctl", "turso"],
}
BACKEND = ["elysia", "hono", "express", "fastify", "@nestjs/core", "koa", "@trpc/server", "@hono/node-server"]
DATA = ["@supabase/supabase-js", "@supabase/ssr", "drizzle-orm", "prisma", "@prisma/client", "kysely", "pg", "postgres",
        "@neondatabase/serverless", "mysql2", "mongodb", "mongoose", "better-sqlite3", "@libsql/client", "ioredis", "redis",
        "@upstash/redis", "firebase", "firebase-admin", "convex"]
ENV_HINT = re.compile(r"(DATABASE|DB_|POSTGRES|PG|MYSQL|MONGO|REDIS|SUPABASE|NEON|TURSO|LIBSQL|FIREBASE|CONVEX|UPSTASH)",
                      re.I)
UA = {"User-Agent": "agent-webcraft-env/1"}


def tool_version(name: str) -> tuple[str, str | None]:
    path = shutil.which(name)
    if not path:
        return name, None
    try:
        r = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=15, errors="replace")
        out = (r.stdout or r.stderr).strip().splitlines()
        line = out[0] if out else "installed"
        m = re.search(r"\d+\.\d+(\.\d+)?", line)
        return name, m.group(0) if m else line[:40]
    except (OSError, subprocess.TimeoutExpired):
        return name, "installed (version unknown)"


def machine() -> dict:
    names = sorted({t for group in MACHINE_TOOLS.values() for t in group})
    with ThreadPoolExecutor(max_workers=8) as pool:
        found = dict(pool.map(tool_version, names))
    return {group: {t: found[t] for t in tools} for group, tools in MACHINE_TOOLS.items()}


def load_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return None


def project(root: Path) -> dict | None:
    pkg = load_json(root / "package.json")
    if pkg is None and not any((root / f).exists() for f in ("deno.json", "deno.jsonc")):
        return None
    pkg = pkg or {}
    deps = {**pkg.get("devDependencies", {}), **pkg.get("dependencies", {})}
    locks = [f for f in ("bun.lock", "bun.lockb", "pnpm-lock.yaml", "yarn.lock", "package-lock.json") if (root / f).exists()]
    pins = {}
    if pkg.get("packageManager"):
        pins["packageManager"] = pkg["packageManager"]
    if pkg.get("engines"):
        pins["engines"] = pkg["engines"]
    for f in (".nvmrc", ".node-version", ".bun-version", ".tool-versions"):
        if (root / f).is_file():
            pins[f] = (root / f).read_text(encoding="utf-8", errors="replace").strip().splitlines()[0][:40]
    for f in ("deno.json", "deno.jsonc", "bunfig.toml"):
        if (root / f).exists():
            pins[f] = "present"
    compose = []
    for f in ("docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"):
        p = root / f
        if p.is_file():
            images = re.findall(r"^\s*image:\s*['\"]?([\w./-]+)", p.read_text(encoding="utf-8", errors="replace"), re.M)
            compose.append(f"{f}: {', '.join(images) or 'no images'}")
    env_keys = set()
    for f in root.glob(".env*"):
        if f.is_file():
            for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
                m = re.match(r"\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=", line)
                if m and ENV_HINT.search(m.group(1)):
                    env_keys.add(f"{m.group(1)} ({f.name})")
    schema = []
    prisma = root / "prisma" / "schema.prisma"
    if prisma.is_file():
        m = re.search(r'provider\s*=\s*"(postgresql|mysql|sqlite|mongodb|sqlserver|cockroachdb)"',
                      prisma.read_text(encoding="utf-8", errors="replace"))
        schema.append(f"prisma/schema.prisma provider={m.group(1) if m else '?'}")
    for p in root.glob("drizzle.config.*"):
        m = re.search(r"dialect:\s*['\"](\w+)['\"]", p.read_text(encoding="utf-8", errors="replace"))
        schema.append(f"{p.name} dialect={m.group(1) if m else '?'}")
    if (root / "supabase" / "config.toml").is_file():
        schema.append("supabase/ (local Supabase project)")
    return {
        "lockfiles": locks,
        "pins": pins,
        "backend": {k: deps[k] for k in BACKEND if k in deps},
        "data": {k: deps[k] for k in DATA if k in deps},
        "schema": schema,
        "compose": compose,
        "env_keys": sorted(env_keys),
    }


def fetch_json(url: str):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=15) as r:
            return json.loads(r.read())
    except Exception:  # noqa: BLE001 - offline or blocked: report as unknown
        return None


def latest() -> dict:
    out = {}
    idx = fetch_json("https://nodejs.org/dist/index.json")
    if idx:
        out["node current"] = idx[0]["version"].lstrip("v")
        lts = next((x for x in idx if x.get("lts")), None)
        if lts:
            out["node LTS"] = f"{lts['version'].lstrip('v')} ({lts['lts']})"
    with ThreadPoolExecutor(max_workers=4) as pool:
        for name, meta in zip(("bun", "deno", "pnpm", "yarn"),
                              pool.map(lambda n: fetch_json(f"https://registry.npmjs.org/{n}/latest"),
                                       ("bun", "deno", "pnpm", "yarn"))):
            out[name] = meta.get("version") if meta else "unknown"
    return out


def implications(m: dict, p: dict | None) -> list[str]:
    have = {t for g in m.values() for t, v in g.items() if v}
    notes = []
    if "docker" not in have and "podman" not in have:
        notes.append("No Docker: a local Postgres/MySQL/Redis needs an installer or Docker; otherwise use SQLite "
                     "(no server) or a hosted dev database (Supabase, Neon, Turso, Upstash).")
    if "bun" in have and "node" in have:
        notes.append("Both Node and Bun are installed: Bun can be the package manager/test runner even if Node runs production.")
    elif "bun" not in have:
        notes.append("Bun is not installed: choosing Bun means installing it first (ask the user).")
    if "supabase" not in have and p and any(k.startswith("@supabase") for k in p["data"]):
        notes.append("Project uses Supabase but the Supabase CLI is missing: migrations and type generation need it.")
    if p:
        lock_pm = {"bun.lock": "bun", "bun.lockb": "bun", "pnpm-lock.yaml": "pnpm", "yarn.lock": "yarn",
                   "package-lock.json": "npm"}
        pms = sorted({lock_pm[l] for l in p["lockfiles"]})
        if len(pms) > 1:
            notes.append(f"Lockfiles from several package managers ({', '.join(p['lockfiles'])}): agree on one with "
                         "the user and delete the other lockfiles, or installs will drift.")
        for pm in pms:
            if pm not in have:
                notes.append(f"Project uses {pm} (lockfile) but {pm} is not on PATH: install it or use corepack.")
    return notes


def as_text(r: dict) -> str:
    lines = ["machine:"]
    for group, tools in r["machine"].items():
        shown = [f"{t} {v}" for t, v in tools.items() if v]
        missing = [t for t, v in tools.items() if not v]
        lines.append(f"  {group}: " + (", ".join(shown) or "none") + (f"  (missing: {', '.join(missing)})" if missing else ""))
    if r.get("latest"):
        lines.append("latest today: " + ", ".join(f"{k} {v}" for k, v in r["latest"].items()))
    p = r.get("project")
    if p is None:
        lines.append("project: no package.json here (new project, or point at the project folder)")
    else:
        lines.append("project:")
        lines.append("  lockfiles: " + (", ".join(p["lockfiles"]) or "none"))
        if p["pins"]:
            lines.append("  pins: " + ", ".join(f"{k}={v}" for k, v in p["pins"].items()))
        lines.append("  backend: " + (", ".join(f"{k} {v}" for k, v in p["backend"].items()) or "none (frontend only, "
                                                                                            "or framework routes)"))
        lines.append("  data: " + (", ".join(f"{k} {v}" for k, v in p["data"].items()) or "none"))
        for label in ("schema", "compose"):
            if p[label]:
                lines.append(f"  {label}: " + "; ".join(p[label]))
        if p["env_keys"]:
            lines.append("  env names (values not read): " + ", ".join(p["env_keys"]))
    for n in r["implications"]:
        lines.append(f"note: {n}")
    return "\n".join(lines)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Machine and project facts for stack decisions")
    ap.add_argument("project", nargs="?", default=".")
    ap.add_argument("--latest", action="store_true", help="also fetch today's runtime and package manager versions")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    root = Path(a.project).resolve()
    m = machine()
    p = project(root)
    r = {"machine": m, "project": p, "implications": implications(m, p)}
    if a.latest:
        r["latest"] = latest()
    print(json.dumps(r, indent=2, ensure_ascii=False) if a.json else as_text(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
