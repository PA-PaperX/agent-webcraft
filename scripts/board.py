#!/usr/bin/env python3
"""Shared task board for several coding agents, stored as plain Markdown files in .webcraft/.

Commands (all accept --root PROJECT_DIR, default: current directory):
  init                      create .webcraft/ (never overwrites) and the AGENTS.md block
  new "Title" [--area A] [--owner X] [--accept "..."]...    create a task
  claim ID --agent NAME [--force]                             take a task (one owner per task)
  report ID --agent NAME --did "..." [--where F:L] [--evidence "..."] [--commit SHA] [--status S]
  done ID --agent NAME [--force]                              finish (all acceptance boxes ticked)
  list [--status S] [--owner X] [--all]                       compact list for agents
  check                                                       validate; exit 1 on errors
  archive [--days N]                                          move done tasks older than N days to archive/
  serve [--port 8765]                                         read-only kanban on http://127.0.0.1:PORT

Agents without this script can follow the same format by editing the files directly.
Standard library only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import shutil
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATES = SKILL_DIR / "templates"
STATUSES = ["todo", "in-progress", "review", "blocked", "done"]
KEYS = ["id", "title", "status", "owner", "area", "created", "updated"]
STATE_MAX_LINES = 150
BLOCK_BEGIN, BLOCK_END = "<!-- BEGIN:webcraft -->", "<!-- END:webcraft -->"
AGENTS_BLOCK = f"""{BLOCK_BEGIN}
## Agent WebCraft
Shared state for coding agents lives in `.webcraft/`.
- Start every session by reading `.webcraft/STATE.md`, then `.webcraft/RULES.md`.
- Code waits for an approved brief (`.webcraft/BRIEF.md`, or the task's Brief section for small work).
- Claim a task before working on it; log what you did, where (file:lines) and the evidence. Use the
  agent-webcraft skill's `scripts/board.py`, or edit the task file's front matter and Log section directly.
- Keep STATE.md short; replace its "Last session" section at the end of each session.
{BLOCK_END}"""


def today() -> str:
    return dt.date.today().isoformat()


def die(msg: str, code: int = 2):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


# ---------------------------------------------------------------------------
# Task files
# ---------------------------------------------------------------------------

class Task:
    def __init__(self, path: Path):
        self.path = path
        text = path.read_text(encoding="utf-8")
        m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.S)
        self.meta, self.body = {}, text
        if m:
            self.body = m.group(2)
            for line in m.group(1).splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    self.meta[k.strip()] = v.strip()

    def __getitem__(self, k):
        return self.meta.get(k, "")

    def section(self, name: str) -> str:
        m = re.search(rf"^## {re.escape(name)}\s*\n(.*?)(?=^## |\Z)", self.body, re.M | re.S)
        return m.group(1) if m else ""

    def acceptance(self) -> list[tuple[bool, str]]:
        return [(c.lower() == "x", t.strip())
                for c, t in re.findall(r"^\s*- \[([ xX])\]\s*(.+)$", self.section("Acceptance"), re.M)]

    def log_lines(self) -> list[str]:
        return [l[2:].strip() for l in self.section("Log").splitlines() if l.startswith("- ")]

    def add_log(self, line: str):
        entry = f"- {line}\n"
        m = re.search(r"^## Log\s*\n", self.body, re.M)
        if not m:
            self.body = self.body.rstrip("\n") + "\n\n## Log\n" + entry
            return
        nxt = re.search(r"^## ", self.body[m.end():], re.M)
        end = m.end() + nxt.start() if nxt else len(self.body)
        before = self.body[:end].rstrip("\n")
        self.body = before + "\n" + entry + ("\n" + self.body[end:] if nxt else "")

    def save(self):
        keys = KEYS + [k for k in self.meta if k not in KEYS]
        fm = "\n".join(f"{k}: {self.meta.get(k, '')}" for k in keys)
        self.path.write_text(f"---\n{fm}\n---\n{self.body}", encoding="utf-8")


def board_dir(root: Path) -> Path:
    return root / ".webcraft"


def all_tasks(root: Path, include_archive: bool = False) -> list[Task]:
    dirs = [board_dir(root) / "tasks"] + ([board_dir(root) / "archive"] if include_archive else [])
    out = []
    for d in dirs:
        if d.is_dir():
            out += [Task(p) for p in sorted(d.glob("T-*.md"))]
    return out


def find_task(root: Path, tid: str) -> Task:
    tid = tid.upper()
    if re.fullmatch(r"\d+", tid):
        tid = f"T-{int(tid):04d}"
    hits = list((board_dir(root) / "tasks").glob(f"{tid}*.md"))
    if not hits:
        die(f"task {tid} not found in .webcraft/tasks/")
    return Task(hits[0])


def next_id(root: Path) -> str:
    nums = [int(m.group(1)) for t in all_tasks(root, True) if (m := re.match(r"T-(\d+)", t["id"] or t.path.name))]
    return f"T-{(max(nums) + 1 if nums else 1):04d}"


def slugify(title: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:40].strip("-")
    return s or "task"


def render(template: str, **values) -> str:
    text = (TEMPLATES / template).read_text(encoding="utf-8")
    for k, v in values.items():
        text = text.replace("{{" + k + "}}", v)
    return text


def project_name(root: Path) -> str:
    try:
        return json.loads((root / "package.json").read_text(encoding="utf-8-sig")).get("name") or root.name
    except (OSError, ValueError):
        return root.name


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_init(a):
    root, wc = a.root, board_dir(a.root)
    for d in (wc, wc / "tasks", wc / "archive"):
        d.mkdir(parents=True, exist_ok=True)
    name = project_name(root)
    for t in ("STATE.md", "RULES.md"):
        p = wc / t
        if p.exists():
            print(f"kept     .webcraft/{t}")
        else:
            p.write_text(render(t, project=name, date=today()), encoding="utf-8")
            print(f"created  .webcraft/{t}")
    ignore = wc / ".gitignore"
    if not ignore.exists():
        # screenshots and style previews are regenerated; keep them out of git
        ignore.write_text("shots/\npreview/\n", encoding="utf-8")
        print("created  .webcraft/.gitignore (shots/, preview/)")
    agents = root / "AGENTS.md"
    text = agents.read_text(encoding="utf-8") if agents.exists() else ""
    if BLOCK_BEGIN in text and BLOCK_END in text:
        text = re.sub(re.escape(BLOCK_BEGIN) + r".*?" + re.escape(BLOCK_END), lambda _: AGENTS_BLOCK, text, flags=re.S)
        print("updated  AGENTS.md (webcraft block)")
    else:
        text = (text.rstrip("\n") + "\n\n" if text.strip() else "") + AGENTS_BLOCK + "\n"
        print(("appended " if agents.exists() else "created  ") + "AGENTS.md (webcraft block)")
    agents.write_text(text, encoding="utf-8")
    pointers = [("CLAUDE.md", True)] + ([("GEMINI.md", True)] if a.gemini_md else [])
    for fname, create in pointers:
        p = root / fname
        if p.exists():
            body = p.read_text(encoding="utf-8")
            if "@AGENTS.md" not in body:
                p.write_text(body.rstrip("\n") + "\n\n@AGENTS.md\n", encoding="utf-8")
                print(f"appended @AGENTS.md to {fname}")
            else:
                print(f"kept     {fname} (already imports AGENTS.md)")
        elif create and not a.no_claude_md:
            p.write_text("@AGENTS.md\n", encoding="utf-8")
            print(f"created  {fname} -> @AGENTS.md")


def cmd_new(a):
    wc = board_dir(a.root)
    if not wc.is_dir():
        die("no .webcraft/ here; run `board.py init` first")
    tid = next_id(a.root)
    acc = "\n".join(f"- [ ] {x}" for x in a.accept) or "- [ ] <define a checkable outcome>"
    path = wc / "tasks" / f"{tid}-{slugify(a.title)}.md"
    path.write_text(render("TASK.md", id=tid, title=a.title.replace("\n", " "), owner=a.owner or "",
                           area=a.area, date=today(), acceptance=acc), encoding="utf-8")
    print(f"{tid}  {path.relative_to(a.root).as_posix()}")


def cmd_claim(a):
    t = find_task(a.root, a.id)
    if t["status"] == "done":
        die(f"{t['id']} is done")
    owner = t["owner"]
    if owner and owner != a.agent and t["status"] in ("in-progress", "review") and not a.force:
        die(f"{t['id']} is {t['status']} and owned by {owner}; ask the user, then use --force to take it over")
    t.meta.update(owner=a.agent, status="in-progress", updated=today())
    t.add_log(f"{today()} {a.agent}: claimed" + (f" (took over from {owner})" if owner and owner != a.agent else ""))
    t.save()
    print(f"{t['id']} in-progress, owner {a.agent}")


def cmd_report(a):
    t = find_task(a.root, a.id)
    line = f"{today()} {a.agent}: {a.did}"
    if a.where:
        line += f" at {a.where}"
    if a.evidence:
        line += f"; evidence: {a.evidence}"
    if a.commit:
        line += f"; commit {a.commit}"
    t.add_log(line)
    if a.status:
        t.meta["status"] = a.status
    t.meta["updated"] = today()
    if not t["owner"]:
        t.meta["owner"] = a.agent
    t.save()
    print(f"{t['id']} logged" + (f", status {a.status}" if a.status else ""))


GATED_AREAS = {"ui", "design", "pages", "content"}


def lint_module():
    import importlib.util
    spec = importlib.util.spec_from_file_location("design_lint", Path(__file__).with_name("design_lint.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def design_gate(root: Path) -> list[str]:
    """Run design_lint for UI-facing tasks; its errors block `done`."""
    # "verify" is checked per task in cmd_done, so skip the project-wide version here
    return [f"design_lint [{k}] {m}" for k, m in lint_module().lint(root)["errors"] if k != "verify"]


def cmd_done(a):
    t = find_task(a.root, a.id)
    open_items = [txt for ok, txt in t.acceptance() if not ok]
    if not t.acceptance():
        open_items = ["(no acceptance criteria defined)"]
    real_logs = [l for l in t.log_lines() if not re.search(r": claimed", l)]
    problems = [f"unticked: {x}" for x in open_items] + ([] if real_logs else ["no work logged"])
    if t["area"] in GATED_AREAS:
        problems += design_gate(a.root)
        # verify.md: the critique and benchmark passes must be written down, not just claimed
        log = "\n".join(t.log_lines())
        if not re.search(r"\bcritique:\s*\S.{30,}", log, re.I):
            problems.append('no critique pass logged: board.py report ID --agent NAME --did "critique: 390 - ...; '
                            '768 - ...; 1440 - ..." (three weakest things per screenshot, verify.md)')
        lint = lint_module()
        bench = re.findall(r"\bbenchmark:(.*)", log, re.I)
        if not any(len(b) > 40 and any(lint.real_site(u) for u in lint.URL.findall(b)) for b in bench):
            problems.append('no benchmark pass against a real website logged: board.py report ID --agent NAME --did '
                            '"benchmark: compared with https://<live reference site> - three biggest differences" '
                            '(font pages, GitHub, docs and example.com do not count; quality-bar.md)')
    if problems and not a.force:
        die(f"{t['id']} not done:\n  " + "\n  ".join(problems))
    t.meta.update(status="done", updated=today())
    t.add_log(f"{today()} {a.agent}: done" + (" (forced)" if problems else ""))
    t.save()
    print(f"{t['id']} done")


def cmd_list(a):
    rows = [t for t in all_tasks(a.root) if (a.all or t["status"] != "done")
            and (not a.status or t["status"] == a.status) and (not a.owner or t["owner"] == a.owner)]
    if not rows:
        print("no tasks")
        return
    for t in sorted(rows, key=lambda t: (STATUSES.index(t["status"]) if t["status"] in STATUSES else 9, t["id"])):
        acc = t.acceptance()
        done = sum(ok for ok, _ in acc)
        print(f"{t['id']:7} {t['status']:11} {t['owner'] or '-':11} {t['area']:8} {done}/{len(acc)}  {t['title'][:70]}")


def run_checks(root: Path) -> tuple[list[str], list[str]]:
    errors, warns = [], []
    wc = board_dir(root)
    if not wc.is_dir():
        return ["no .webcraft/ folder (run board.py init)"], []
    state = wc / "STATE.md"
    if not state.is_file():
        errors.append("STATE.md missing")
    elif (n := len(state.read_text(encoding="utf-8").splitlines())) > STATE_MAX_LINES:
        warns.append(f"STATE.md has {n} lines (> {STATE_MAX_LINES}); move history to archive/")
    brief = wc / "BRIEF.md"
    brief_status = ""
    if brief.is_file():
        m = re.search(r"Status:\s*([^\n·]+)", brief.read_text(encoding="utf-8"))
        brief_status = (m.group(1) if m else "").strip().lower()
    seen = {}
    now = dt.date.today()
    for t in all_tasks(root):
        name = t.path.name
        missing = [k for k in KEYS if k not in t.meta]
        if missing:
            errors.append(f"{name}: missing front matter {', '.join(missing)}")
        if t["id"] and not name.upper().startswith(t["id"].upper()):
            errors.append(f"{name}: id {t['id']} does not match the file name")
        if t["id"] in seen:
            errors.append(f"{name}: duplicate id {t['id']} (also {seen[t['id']]})")
        seen[t["id"]] = name
        st = t["status"]
        if st not in STATUSES:
            errors.append(f"{name}: unknown status '{st}' (use {', '.join(STATUSES)})")
        if st in ("in-progress", "review") and not t["owner"]:
            errors.append(f"{name}: {st} without an owner")
        if st == "done":
            if any(not ok for ok, _ in t.acceptance()) or not t.acceptance():
                errors.append(f"{name}: done with unticked or missing acceptance")
            if not [l for l in t.log_lines() if ": claimed" not in l and not l.endswith(": done")]:
                errors.append(f"{name}: done without any logged work or evidence")
        try:
            age = (now - dt.date.fromisoformat(t["updated"])).days
        except ValueError:
            age = 0
            if t["updated"]:
                warns.append(f"{name}: updated '{t['updated']}' is not an ISO date")
        if st == "in-progress" and age > 3:
            warns.append(f"{name}: in-progress but untouched for {age} days")
        if st == "done" and age > 7:
            warns.append(f"{name}: done {age} days ago; run `board.py archive`")
        if st in ("in-progress", "review") and brief_status.startswith("awaiting"):
            warns.append(f"{name}: work started while BRIEF.md is still awaiting approval")
    return errors, warns


def cmd_check(a):
    errors, warns = run_checks(a.root)
    for e in errors:
        print(f"ERROR  {e}")
    for w in warns:
        print(f"warn   {w}")
    print(f"{len(errors)} error(s), {len(warns)} warning(s)")
    sys.exit(1 if errors else 0)


def cmd_archive(a):
    dest = board_dir(a.root) / "archive"
    dest.mkdir(parents=True, exist_ok=True)
    moved = 0
    for t in all_tasks(a.root):
        try:
            age = (dt.date.today() - dt.date.fromisoformat(t["updated"])).days
        except ValueError:
            continue
        if t["status"] == "done" and age >= a.days:
            shutil.move(str(t.path), str(dest / t.path.name))
            moved += 1
    print(f"archived {moved} task(s)")


# ---------------------------------------------------------------------------
# Read-only kanban
# ---------------------------------------------------------------------------

PAGE_CSS = """
:root{--bg:#f6f6f4;--card:#fff;--fg:#1d1d1b;--mut:#6b6b66;--line:#e2e2dd;--acc:#2f6fed;--ok:#1f9d55;--bad:#d64545}
@media (prefers-color-scheme:dark){:root{--bg:#141413;--card:#1f1f1d;--fg:#ececea;--mut:#a3a39d;--line:#33332f;--acc:#7aa2ff;--ok:#4cc38a;--bad:#ff7a7a}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.6 system-ui,"Noto Sans Thai","IBM Plex Sans Thai",sans-serif}
header{padding:16px 20px;border-bottom:1px solid var(--line)}h1{margin:0;font-size:20px}header p{margin:4px 0 0;color:var(--mut)}
.cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;padding:16px 20px}
.col h2{font-size:13px;text-transform:uppercase;letter-spacing:.06em;color:var(--mut);margin:0 0 8px}
.card{display:block;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 12px;margin-bottom:10px;color:inherit;text-decoration:none}
.card:hover{border-color:var(--acc)}.id{color:var(--mut);font-size:12px}.t{font-weight:600}.meta{font-size:12px;color:var(--mut)}
.bar{height:4px;background:var(--line);border-radius:2px;margin:6px 0}.bar i{display:block;height:4px;background:var(--ok);border-radius:2px}
.log{font-size:12px;color:var(--mut);margin-top:4px}.issues{padding:0 20px}.issues li{color:var(--bad)}
pre{white-space:pre-wrap;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px;margin:16px 20px}
a.back{display:inline-block;margin:16px 20px 0;color:var(--acc)}
"""


def kanban_html(root: Path) -> str:
    tasks = all_tasks(root)
    errors, warns = run_checks(root)
    focus = ""
    state = board_dir(root) / "STATE.md"
    if state.is_file():
        for m in re.finditer(r"^## Current focus\s*\n(.*?)(?=^## |\Z)", state.read_text(encoding="utf-8"), re.M | re.S):
            focus = re.sub(r"<!--.*?-->", "", m.group(1), flags=re.S).strip()
            if focus:
                break
    cols = []
    for st in STATUSES:
        cards = []
        for t in [t for t in tasks if t["status"] == st]:
            acc = t.acceptance()
            pct = int(100 * sum(ok for ok, _ in acc) / len(acc)) if acc else 0
            last = (t.log_lines() or [""])[-1]
            cards.append(f'<a class="card" href="/task/{html.escape(t["id"])}"><div class="id">{html.escape(t["id"])} · '
                         f'{html.escape(t["area"])}</div><div class="t">{html.escape(t["title"])}</div>'
                         f'<div class="meta">{html.escape(t["owner"] or "unassigned")} · {sum(ok for ok, _ in acc)}/{len(acc)}'
                         f'</div><div class="bar"><i style="width:{pct}%"></i></div>'
                         f'<div class="log">{html.escape(last[:120])}</div></a>')
        cols.append(f'<section class="col"><h2>{st} ({len(cards)})</h2>{"".join(cards)}</section>')
    issues = "".join(f"<li>{html.escape(e)}</li>" for e in errors) + "".join(
        f'<li style="color:var(--mut)">{html.escape(w)}</li>' for w in warns)
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" '
            f'content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="10">'
            f'<title>{html.escape(project_name(root))} board</title><style>{PAGE_CSS}</style></head><body>'
            f'<header><h1>{html.escape(project_name(root))}</h1><p>{html.escape(focus) or "No current focus in STATE.md"}</p>'
            f'</header>{"<ul class=issues>" + issues + "</ul>" if issues else ""}<div class="cols">{"".join(cols)}</div>'
            f'</body></html>')


def task_html(root: Path, tid: str) -> str | None:
    hits = list((board_dir(root) / "tasks").glob(f"{tid}*.md")) + list((board_dir(root) / "archive").glob(f"{tid}*.md"))
    if not hits:
        return None
    text = hits[0].read_text(encoding="utf-8")
    return (f'<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,'
            f'initial-scale=1"><title>{html.escape(tid)}</title><style>{PAGE_CSS}</style></head><body>'
            f'<a class="back" href="/">← board</a><pre>{html.escape(text)}</pre></body></html>')


def cmd_serve(a):
    root = a.root

    class Handler(BaseHTTPRequestHandler):
        def _send(self, code, body, ctype="text/html; charset=utf-8"):
            data = body.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path in ("/", "/index.html"):
                self._send(200, kanban_html(root))
            elif self.path == "/api/tasks":
                data = [{**t.meta, "acceptance": t.acceptance(), "log": t.log_lines()} for t in all_tasks(root)]
                self._send(200, json.dumps(data, ensure_ascii=False, indent=2), "application/json; charset=utf-8")
            elif self.path.startswith("/task/"):
                body = task_html(root, re.sub(r"[^A-Za-z0-9-]", "", self.path[6:]).upper())
                self._send(200, body) if body else self._send(404, "not found", "text/plain")
            else:
                self._send(404, "not found", "text/plain")

        def log_message(self, *args):
            pass

    srv = ThreadingHTTPServer(("127.0.0.1", a.port), Handler)
    print(f"board: http://127.0.0.1:{a.port}  (read-only, Ctrl+C to stop)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


# ---------------------------------------------------------------------------

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Shared task board in .webcraft/ for coding agents")
    ap.add_argument("--root", type=Path, default=Path("."), help="project directory (default: .)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("init", help="create .webcraft/ and the AGENTS.md block")
    s.add_argument("--no-claude-md", action="store_true", help="don't create CLAUDE.md if it is missing")
    s.add_argument("--gemini-md", action="store_true", help="also make GEMINI.md import AGENTS.md")
    s = sub.add_parser("new", help="create a task")
    s.add_argument("title")
    s.add_argument("--area", default="ui")
    s.add_argument("--owner", default="")
    s.add_argument("--accept", action="append", default=[], help="acceptance criterion (repeatable)")
    s = sub.add_parser("claim", help="take a task")
    s.add_argument("id")
    s.add_argument("--agent", required=True)
    s.add_argument("--force", action="store_true")
    s = sub.add_parser("report", help="log a step")
    s.add_argument("id")
    s.add_argument("--agent", required=True)
    s.add_argument("--did", required=True)
    s.add_argument("--where")
    s.add_argument("--evidence")
    s.add_argument("--commit")
    s.add_argument("--status", choices=[x for x in STATUSES if x != "done"])
    s = sub.add_parser("done", help="finish a task")
    s.add_argument("id")
    s.add_argument("--agent", required=True)
    s.add_argument("--force", action="store_true")
    s = sub.add_parser("list", help="compact task list")
    s.add_argument("--status", choices=STATUSES)
    s.add_argument("--owner")
    s.add_argument("--all", action="store_true", help="include done tasks")
    sub.add_parser("check", help="validate the board")
    s = sub.add_parser("archive", help="move old done tasks to archive/")
    s.add_argument("--days", type=int, default=7)
    s = sub.add_parser("serve", help="read-only kanban on localhost")
    s.add_argument("--port", type=int, default=8765)
    a = ap.parse_args()
    a.root = a.root.resolve()
    {"init": cmd_init, "new": cmd_new, "claim": cmd_claim, "report": cmd_report, "done": cmd_done,
     "list": cmd_list, "check": cmd_check, "archive": cmd_archive, "serve": cmd_serve}[a.cmd](a)


if __name__ == "__main__":
    main()
