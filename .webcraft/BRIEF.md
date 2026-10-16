# Brief: Agent WebCraft

Status: **approved 2026-10-15** · Owner: project author · Last updated: 2026-10-15

## Goal
An Agent Skill that makes any coding agent markedly better at building websites. The agent:
- grounds its code in the docs for the exact versions installed in the project;
- interviews the user until the work is fully specified;
- chooses a UX/UI direction by reasoning from the brief, not from its own taste;
- coordinates with other agents through shared files in the repo.

Cost profile: heavy on the first session (scan, interview, research), light on later sessions (read state, do the task).

## Users
- Developers who use several agents on the same project, such as Claude Code, Codex, Antigravity, Cursor, Gemini CLI and OpenCode.
- First user: a Thai developer whose main stacks are Next.js 16 + React 19 + Tailwind 4 + shadcn, Vite + React, SvelteKit and Supabase.

## Decisions from the interview
| Topic | Decision |
|---|---|
| Interview style | Scan the project first, then ask in rounds of up to 4 multiple-choice questions until the checklist is complete |
| Approval | The user approves the brief before any code is written, every time |
| Where knowledge lives | Plain files in the project repo under `.webcraft/` |
| File language | English files; the agent talks to the user in the user's language |
| Other people's skills | Absorb their good ideas into ours. No runtime dependency on them; their sites and CLIs remain component sources |
| Agents supported | Any agent that reads the Agent Skills format (`SKILL.md`). Tested on Claude Code, Codex and Antigravity |
| Deep stack guidance (v1) | Next.js + React + Tailwind + shadcn; Vite + React; SvelteKit; Supabase/backend. Other stacks use the generic docs ladder |
| UI direction | Recommend 1 direction and give 2 real alternatives with reasons; the user picks |
| Team board | Included in v1: create, claim, report, check, and a read-only localhost view |
| Visual check | Use the agent's built-in browser first; fall back to a bundled Playwright script |
| Distribution | Open source on GitHub under the author's name. Written generically from the start: no personal paths and no AI attribution |

## Scope

**In v1**
1. **Discover:** scan the repo; question bank by topic; interview rounds; a brief template; the approval gate.
2. **Docs grounding:** detect the stack and its versions from the lockfile, then use the docs ladder: in-package docs → official llms.txt/markdown → docs MCP if present → official site → memory (flagged as possibly stale). Every claim cites its source.
3. **Plan:** size the work; record decisions, not code; break the plan into board tasks.
4. **Design:** score the brief on 5 axes; choose from a style catalog; emit tokens to `DESIGN.md`; recommend 1 direction plus 2 alternatives.
5. **Components:** sourcing ladder (project's own → shadcn/ui → 21st.dev → React Bits → Magic UI / Aceternity / Origin UI); checks for stack fit, license, a11y, performance and maintenance.
6. **Build:** follow project conventions; make the narrowest change; reuse before creating.
7. **Verify:** typecheck, lint, build and tests; screenshots at 3 viewport sizes that the agent actually looks at; a11y basics; runtime errors.
8. **Board:** `.webcraft/` files plus `board.py`.
9. **Thai web:** fonts, line-height, line breaking, Buddhist-era dates, `lang` attribute.
10. **Output rules:** brief, complete and direct communication (the successor to caveman).

**Not in v1:** mobile-native apps, a backend-heavy architecture guide beyond Supabase, a hosted service, Plane or GitHub Issues sync (planned later as mirrors).

## Architecture
```text
agent-webcraft/
  SKILL.md                    router: when to use / not, phases, size table, routing table
  references/
    discover.md  docs.md  docs-map.md  plan.md  design.md  style-catalog.md
    components.md  build.md  verify.md  board.md  thai-web.md  tools.md  output.md
    stacks/  nextjs.md  vite-react.md  sveltekit.md  supabase.md
  templates/  BRIEF.md  DESIGN.md  STATE.md  RULES.md  TASK.md
  scripts/    detect_stack.py  board.py  shoot.py
  evals/      scenarios.md
  README.md  LICENSE
```
Each project gets a `.webcraft/` folder (BRIEF, DESIGN, STATE, RULES, tasks/, archive/) and a short `<!-- BEGIN:webcraft -->` block in `AGENTS.md`. Every agent therefore reads STATE first, even before the skill triggers.

## Durability rules
- Method and tools are kept apart. Tool names live only in `tools.md` and `docs-map.md`, each with a "last verified" date. The agent checks a tool before using it and falls back to the capability description if it fails.
- No model names, prices or framework-version facts in the core. Anything time-sensitive is looked up and dated.
- Reasons are given instead of MUST/CRITICAL wording.
- `evals/scenarios.md` is rerun after a model or tool change.

## Token budget (targets)
| Session | Loaded |
|---|---|
| First session on a project | scan + interview + docs research + design: heavy by design |
| Later sessions | `AGENTS.md` block + STATE + one task + 1–2 references ≈ 2–4k tokens |
| `SKILL.md` | ≤ ~1.2k tokens; each reference ≤ ~800 tokens |

## Acceptance
1. All files exist; `SKILL.md` is valid for the Agent Skills format; the description is ≤ 1024 characters.
2. `detect_stack.py` reports the correct stack and versions on 3 of the author's real projects (Next, Vite, SvelteKit).
3. `board.py init/new/claim/report/check/serve` all work on a scratch repo; `check` catches an invalid board.
4. A dry run on a real project: the agent scans, asks rounds of questions, writes BRIEF.md and stops for approval.
5. The design flow produces `DESIGN.md` with 1 recommended and 2 alternative directions, with reasons.
6. Screenshots at 3 sizes are taken and inspected, through the built-in browser or Playwright.
7. The skill is linked into Claude Code, Codex and Antigravity, and a new Claude Code session lists it.
8. README and MIT LICENSE are present; no personal paths and no AI attribution.

## Risks
- **Interview fatigue:** limited to 4 questions per round with multiple choice, and questions are skipped when the repo already answers them.
- **Third-party component licenses:** checked before install and noted in DESIGN.md.
- **Agents differ in tools:** handled by `tools.md` plus capability fallbacks.
