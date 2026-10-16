---
name: agent-webcraft
description: >-
  Web development method for coding agents. Interviews the user until the work is fully specified, picks
  runtime, framework and database with reasons checked against what is installed, grounds every change in
  the docs for the exact versions installed, lets the user choose a design and component style from
  previewed options (built-in presets, popular-brand design systems, Aura), sources components from
  shadcn/ui, 21st.dev and React Bits, picks SVG icons and motion libraries from live data, enforces design
  tokens, page blueprints and honest content with
  script gates, verifies with real screenshots, and lets several agents share work through .webcraft/.
  Use when building, changing, designing, animating, reviewing or debugging a website or web app (Next.js,
  React, Vite, SvelteKit, Tailwind, shadcn, Supabase and others), and whenever the repo has a .webcraft/
  folder. Not for native mobile apps, non-web scripts, or quick questions that need no project context.
---

# Agent WebCraft

Spend effort up front, then work cheaply. The first session scans, interviews, researches and designs. The results go into `.webcraft/`, so every later session, by any agent, starts from recorded facts. `<skill>` below means the folder that contains this file.

## Start of every session
1. If `.webcraft/STATE.md` exists, read it, then `RULES.md`. Open BRIEF or DESIGN only when the task touches them. If there's no `.webcraft/`, this is a first session: go to Discover.
2. Run `python <skill>/scripts/detect_stack.py`. Skip it when the lockfile fingerprint matches STATE.

## Rules checked by scripts (work that breaks them cannot be closed)
1. **Brief first.** The user approves a brief before any code, install or scaffolding, at every size. For tiny work the brief is 2–3 lines in chat.
2. **The user chooses the design** from shown options: the style (`styles.py preview`) and the component style (`components.py preview`). A page blueprint gives every section a layout and a visual. All of it is recorded in DESIGN.md.
3. **Tokens only.** Colors, type and radii come from DESIGN tokens; components contain no hard-coded colors.
4. **The user picks a mode for every missing item:** sample (photos, items), mockup (dummy values with a notice, replaced before launch), or a designed placeholder (content.md). Facts are never silently invented. Buttons keep their final labels, and the page must look finished.
5. **Verified before closing UI work:**
   - `design_lint.py` is clean;
   - screenshots at 3 widths have been looked at;
   - the critique and benchmark passes are logged with `board.py report` (verify.md).
   UI work is on the board. `design_lint.py` reports what is missing; `board.py done` runs the gate. Use `--force` only when the user says so. Before launch: `design_lint.py --release`.

## Phases (read a reference when you enter its phase)
| Phase | Purpose | Read |
|---|---|---|
| Discover | Scan, interview in rounds, brief, approval | references/discover.md, content.md |
| Stack | Runtime, framework, database, checked against the machine | references/stack-choice.md, stacks/ |
| Docs | Docs for the installed versions | references/docs.md, docs-map.md, stacks/ |
| Plan | Size, decisions, board tasks | references/plan.md |
| Design | Style and component options, previews, user's choice, page blueprint | references/design.md, page-blueprints.md, style-catalog.md, quality-bar.md, thai-web.md |
| Icons, Motion | One SVG family; lightest motion | references/icons.md, motion.md |
| Components | Find, vet, record the search | references/components.md |
| Build | Change it the project's way | references/build.md |
| Verify | Checks, screenshots, critique | references/verify.md |
| Board | Claim, report, hand off | references/board.md |

`tools.md` maps capabilities to your agent's tools; `output.md` sets how to talk.

| Size | Examples | Phases |
|---|---|---|
| Tiny | copy fix, style tweak, obvious bug | claim → build → verify → report |
| Small | one component, route, unclear bug | + plan in the task file |
| Feature | new page or flow, auth, data model | Discover for the change → plan → design → build → verify |
| Project | new site, redesign | every phase, full Discover |

## Rules for every phase
- **Version, API and price facts** come from sources opened this session or recorded in `.webcraft/`; cite the path or URL. Memory is a fallback, and you say when you use it.
- **Before adding or upgrading a library,** run `python <skill>/scripts/latest.py <pkg>...` (version, license, advisories). For browser features use `--baseline`. Reference lists are starting points; live data decides.
- **Prefer what the project already has.** Ask when an answer changes what gets built; otherwise decide and say so.
- **Stop when acceptance passes.** Extras go on the board as proposals. Keep STATE.md under ~150 lines.
