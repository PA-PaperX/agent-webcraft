# Tailwind CSS + shadcn/ui

**Docs:** Tailwind has no llms.txt (checked 2026-10-15). Use `https://tailwindcss.com/docs/<topic>`. shadcn: `https://ui.shadcn.com/llms.txt`; shadcn-svelte: `https://shadcn-svelte.com/llms.txt`.

## Check the Tailwind major first. Configuration differs completely.
| | Tailwind 3 | Tailwind 4 |
|---|---|---|
| Config | `tailwind.config.js/ts` (`theme.extend`) | CSS-first: `@import "tailwindcss";` + `@theme { --color-brand: …; }` in the global CSS |
| Build integration | PostCSS plugin `tailwindcss` | `@tailwindcss/postcss` or `@tailwindcss/vite` |
| Content scanning | `content: [...]` globs | automatic, with `@source` for extra paths |
| Custom utilities | plugins / `@layer utilities` | `@utility` |

Writing v4 syntax into a v3 project, or the reverse, silently produces no styles. `detect_stack.py` reports the major and the config style.

## shadcn/ui
- `components.json` records style, base color, aliases and the Tailwind config path. Read it before adding components.
- Components are copied into `components/ui/`. The local file is the source of truth, and it may differ from upstream.
- Theme tokens are CSS variables (`--background`, `--primary`, …). Map DESIGN.md tokens onto them rather than hard-coding colors in components.
- Add with `npx shadcn@latest add <name>`. Registries such as 21st, React Bits and Aceternity install through the same CLI (components.md).

## Pitfalls
- Arbitrary values (`text-[#123456]`, `mt-[13px]`) scattered through markup. Promote repeated values to tokens.
- Class conflicts when composing. Use the project's `cn()` helper (tailwind-merge) if it exists.
- Dark mode strategy (class vs media) must match the theme setup. Check before adding `dark:` styles.
