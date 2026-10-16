# Board: several agents, one source of truth

Agents differ in context size, memory and tools, and none of them remembers what another did. The board puts shared knowledge in plain files in the repo. Any agent can read and write it, git keeps the history, and a team sees it on GitHub.

## Layout (`.webcraft/`)
```text
BRIEF.md       approved scope (rarely changes)
DESIGN.md      chosen direction and tokens
RULES.md       project rules, areas, definition of done
STATE.md       ≤ ~150 lines: stack, docs notes, current focus, active tasks, last session
tasks/T-0001-<slug>.md   one file per task (front matter + brief + acceptance + log)
archive/       finished tasks and old state, which no one needs to read by default
```
`board.py init` also adds a short `<!-- BEGIN:webcraft -->` block to `AGENTS.md` (and makes `CLAUDE.md` import it). Every agent therefore reads STATE first, even when this skill has not triggered.

## Protocol
1. **Start:** read STATE and RULES, then only your task file. Don't read the archive or other tasks unless needed.
2. **Claim:** `board.py claim T-0007 --agent <name>`. One owner per task. If another agent owns a task that is in progress, ask the user before taking it over.
3. **Work:** follow the phases. Keep notes in the task file, not in chat.
4. **Report:** after each meaningful step, log what was done, where (`file:lines`), the evidence (command and result, or screenshot path), and the commit:
   `board.py report T-0007 --agent codex --did "..." --where "src/x.tsx:12-80" --evidence "pnpm test: 14 passed" --commit 3f2a1c9`
5. **Finish:** tick the acceptance boxes the evidence proves, then `board.py done T-0007 --agent <name>`. It refuses while boxes are unticked. Update STATE: current focus, plus the 3–5 lines of the last session.
6. **Hand off:** if you stop mid-task, set the status to `review` or `blocked` and log the next step precisely. The next agent continues from the log alone.

## Agent names
Use the lowercase product name: `claude`, `codex`, `antigravity`, `cursor`, `gemini`, `opencode`, or `human` for the user.

## Commands
`board.py init | new | claim | report | done | list | check | serve`. Run with `--help` for details.
- `list` prints a compact view (cheap for agents).
- `check` validates the board and exits non-zero on problems. You can run it in a pre-commit hook or CI.
- `serve` opens a read-only kanban at `http://localhost:8765` for humans.

## Keep it cheap
- STATE is a summary, not a diary.
- Move done tasks older than a week to `archive/` (`board.py check` warns).
- Log lines are one line each.
- Docs notes go in STATE, not in task logs, so they are found once and reused.
