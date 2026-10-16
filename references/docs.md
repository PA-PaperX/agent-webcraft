# Docs grounding

Frameworks ship breaking changes faster than models are retrained. Code written from memory compiles against a version that may no longer exist. So before writing code that depends on an API, convention or config format, read the docs for the version actually installed.

## 1. Know the exact version
`detect_stack.py` reports the installed version from `node_modules/<pkg>/package.json`, which is the ground truth. If `node_modules` is absent, it falls back to the lockfile and then to the `package.json` range. A range like `^16` is not a version. If only a range is known, say so and prefer docs for the newest version in that range.

## 2. Docs ladder (stop at the first rung that answers the question)
1. **In the installed package.** Shipped docs (e.g. `node_modules/next/dist/docs/`), `README.md`, `CHANGELOG.md` for breaking changes, and the `.d.ts` types, which are the actual API surface. These are free, offline and exact.
2. **Official machine-readable docs.** `llms.txt` indexes and `.md` page variants (see docs-map.md). Load the index, then only the pages you need, never a whole `llms-full.txt` unless you need nearly everything.
3. **A docs MCP server** if one is configured (e.g. Context7). Ask for the installed version explicitly.
4. **The official website**, fetched page by page.
5. **Memory.** Use it only for stable fundamentals, and label it: "from memory, not checked against vX docs".

## 3. Cite and record
- Cite what you used: `node_modules/next/dist/docs/01-app/.../caching.md` or a URL. When the project's `AGENTS.md` names a docs path (Next.js writes one), cite from that path, not from this skill's references.
- When docs contradict memory, docs win. Note deprecations you hit.
- Record reusable findings in STATE under **Docs notes**, one line each in the form `claim — source path or URL`. Example: `Tailwind 4: theme lives in CSS @theme; no tailwind.config.js (tailwindcss.com/docs/theme)`. Later sessions read the note instead of the docs. This is where Agent WebCraft saves most of its tokens.
- When the lockfile fingerprint changes, re-check the notes for the packages that moved.

## 4. Runtime truth beats both
Docs say what should happen; the running app says what does. After a change, read the dev server output and browser console (and framework MCP tools if available, see stacks/). Fix based on the actual error text.
