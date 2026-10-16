# SvelteKit (+ Svelte)

**Docs:** `https://svelte.dev/llms.txt` lists the variants. Prefer `llms-small.txt` or single pages; the full SvelteKit file is about 650 KB. Svelte also offers an official MCP server for docs and code checks. Use it if configured.

## Look up before coding
- **Svelte major:** Svelte 5 uses runes (`$state`, `$derived`, `$effect`, `$props`) and snippets. Svelte 4 syntax (`export let`, `$:`, slots) is legacy. Match the installed major and what the file already uses.
- **Routing files:** `+page.svelte`, `+page.ts` (universal load), `+page.server.ts` (server load and form actions), `+layout.*`, `+server.ts` (endpoints).
- **Data flow:** load functions, `PageData` types, form actions with progressive enhancement (`use:enhance`).
- **Env modules:** `$env/static/private` vs `$env/static/public` (`PUBLIC_` prefix), and their dynamic variants.
- **Adapter for the deployment target:** node, vercel, static, and so on.

## Pitfalls
- Using React-only component sources. Use shadcn-svelte and Svelte libraries, or port the idea.
- Secrets in universal load (`+page.ts` runs on the client too). Use `+page.server.ts`.
- Mixing rune and legacy syntax in one component.
- Animation libraries written for React. GSAP and Motion's vanilla API work; React wrappers do not.

## Verify
- `svelte-check` (often the `check` script), `vite build`, and `vite preview`.
- Load the changed routes with JS on, and test form actions with JS disabled if they are meant to enhance progressively.
