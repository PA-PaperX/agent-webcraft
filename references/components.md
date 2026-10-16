# Components

Search before writing UI by hand, but treat every found component as a draft. It gets read, restyled to DESIGN.md tokens, and vetted before it ships.

## Sourcing ladder (React projects)
1. **The project's own components.** Look in `components/`, `components/ui/` and `src/lib/`. Reuse keeps the look and the bundle consistent.
2. **shadcn/ui primitives:** `npx shadcn@latest add <name>`. Accessible building blocks (dialogs, menus, forms, tables) on Radix. This is the base layer for most other sources.
3. **21st.dev:** community sections and components (heroes, pricing, features, navbars).
   - Index: `https://21st.dev/llms.txt`.
   - With the CLI: `npx @21st-dev/cli search "<need>"`, then `21st add <user>/<slug>`.
   - Without it: `npx shadcn@latest add "https://21st.dev/r/<user>/<slug>"`.
   - Code retrieval has a free daily quota. Search is free.
4. **React Bits:** animations, text effects, backgrounds, micro-interactions.
   - `npx shadcn@latest add https://reactbits.dev/r/<Component>-<TS|JS>-<TW|CSS>`, or the same URL with `npx jsrepo@latest add`.
   - Pick the TS-TW variant for TypeScript + Tailwind projects.
5. **Magic UI** (landing-page effects): use the command on the component's docs page.
   **Aceternity UI:** `npx shadcn@latest add @aceternity/<component>`.
   **Origin UI**, now at coss.com/ui: form controls and inputs.

Svelte projects use shadcn-svelte (`npx shadcn-svelte@latest add <name>`) and Svelte-native libraries. React-only sources are references to port, not install.

## Choosing a source for a need
| Need | First try |
|---|---|
| Forms, dialogs, tables, navigation | project → shadcn → Origin UI |
| Hero, pricing, features, testimonials, footer | 21st → Magic UI / Aceternity |
| Text animation, cursor effects, backgrounds | React Bits → Magic UI |
| Charts | shadcn charts (Recharts) → project's chart lib |
| 3D or shader scenes | React Three Fiber + drei; React Bits backgrounds for lighter options |

## Vet before installing (record the result in DESIGN.md → Components)
Start with live facts for every npm dependency the component pulls in: `python <skill>/scripts/latest.py <pkg>...`. It reports license, last publish, downloads and known advisories. Icons and motion have their own guides (icons.md, motion.md).
- **Stack fit:** React major, Tailwind major (v3 classes or config break on v4 and vice versa), `motion` vs `framer-motion` import name, server or client component boundary in Next.js.
- **License:** read the source's license. React Bits' free library and paid "Pro" have different terms. When unsure, ask the user before using a component in a commercial project.
- **Accessibility:** keyboard reachable, visible focus, labels, no information carried by motion alone, honors `prefers-reduced-motion`.
- **Performance:** adds how many dependencies and KB? Does WebGL or canvas run on mobile? Effects stay off the critical path for LCP.
- **Maintenance:** last update date; open issues on the specific component, if visible.
- **Fit:** does it work with DESIGN tokens after restyling? If restyling means rewriting it, build it on shadcn instead.

## Record the search
Every row in DESIGN.md → Components has a **Searched** entry: the query and the sources tried (for example `"cafe hero" on 21st, React Bits: none fit`), or why no search was needed (`shadcn button, standard`). Search at least for hero, gallery, testimonials and footer. `design_lint.py` blocks done when a row is empty.

## After installing
Read the copied file. Replace hard-coded colors, fonts and radii with tokens. Delete unused variants and props. Make sure it renders in all three viewport sizes during verify.
