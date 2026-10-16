# Tools

The method is written in terms of capabilities. This file maps each capability to typical tools. **Last verified: 2026-10-15.** Agents and tools change. Check what actually appears in your tool list this session, use the first match that works, and fall back down the column. Never invent a command. If a tool listed here is gone, use the capability another way and note the change here with the date.

| Capability | Typical ways to do it | Fallback |
|---|---|---|
| Read and search files | the agent's file read, glob and grep tools | shell `rg` / `grep` / `find` |
| Run commands | the agent's shell or terminal tool | ask the user to run it and paste the output |
| Web search | the agent's web search tool | ask the user for links |
| Read a URL | the agent's fetch tool; `curl -sL <url>` for raw `.md` or `llms.txt` | ask the user to paste |
| Library docs | the docs ladder (docs.md); a docs MCP such as Context7 if configured | official site |
| Package facts (latest version, license, advisories) | `scripts/latest.py` (npm registry + deps.dev) | `npm view <pkg>` |
| What's installed (runtimes, Docker, databases, CLIs) and what the project uses | `scripts/env_check.py [--latest]` | `<tool> --version` one by one |
| Browser feature support | `scripts/latest.py --baseline <feature>` (web-features) | MDN or caniuse page |
| Icon search across sets | `scripts/icons.py` (Iconify API) | the icon family's website |
| Design options and preview | `scripts/styles.py list / shortlist / preview / export / templates` | describe 3 directions in chat |
| Component style options and record | `scripts/components.py preview / choose` | show variants as screenshots from reference sites |
| Tokens from a site the user likes | `scripts/ref_extract.py <url>` + a screenshot | read the site's CSS by hand |
| Design and content gate | `scripts/design_lint.py` (also run by `board.py done` for UI tasks) | manual review against verify.md |
| Browser and screenshots | built-in browser or a browser MCP (desktop apps of Claude, Codex and Antigravity have one) | `scripts/shoot.py` (Playwright via npx) |
| Framework runtime info | `next-devtools-mcp` for Next.js 16+ dev servers; Svelte's official MCP for Svelte | dev server terminal output + browser console |
| Parallel work | subagents, if the agent supports them, for independent searches or reviews | sequential work in one session |
| Asking the user | the agent's question tool (multiple choice) | a numbered list in chat |

## Per-agent notes (check in your session)
- **Claude Code:** skills from `~/.claude/skills/` or `.claude/skills/`; reads `CLAUDE.md`, which can import `@AGENTS.md`; MCP via `.mcp.json`.
- **Codex:** skills from `~/.agents/skills/` (current docs) and `~/.codex/skills/` (older installs); reads `AGENTS.md`; MCP in `~/.codex/config.toml`.
- **Antigravity:** global skills folder under `~/.gemini/`; built-in browser agent; MCP support.
- **Cursor, Gemini CLI, OpenCode and others:** use the Agent Skills format where supported, or point the agent's rules or context file at this skill's `SKILL.md`.

## Telemetry and privacy
Some MCP servers and CLIs send usage telemetry by default. `next-devtools-mcp`, for example, honors `NEXT_TELEMETRY_DISABLED=1`. Mention this to the user when adding one to a project.
