# Docs map

Where docs live for common web stacks. **Last verified: 2026-10-15.** URLs and paths change. If one fails, use the docs ladder in docs.md and update this file with the date.

| Package | In the installed package | Machine-readable (official) | Notes |
|---|---|---|---|
| next | `node_modules/next/dist/docs/` (16+) | `https://nextjs.org/docs/llms.txt`; pages also at `<url>.md` | `next dev` writes an AGENTS.md block pointing at the bundled docs. ≤16.1: `npx @next/codemod@latest agents-md` writes `.next-docs/` |
| react, react-dom | README, types | `https://react.dev/llms.txt` | |
| tailwindcss | README | none found (llms.txt 404) | Docs at `https://tailwindcss.com/docs/<topic>`. v3 vs v4 differ in config, so check the major first |
| shadcn (CLI + components) | `components.json` in project | `https://ui.shadcn.com/llms.txt` | Components are copied into the repo, so read the local file before its docs |
| vite | README | `https://vite.dev/llms.txt` | |
| react-router | README, types | none found (llms.txt 404) | `https://reactrouter.com` docs; v6 vs v7 APIs differ |
| svelte, @sveltejs/kit | README, types | `https://svelte.dev/llms.txt` (index) → `llms-small.txt` / `llms-medium.txt`; per package `https://svelte.dev/docs/kit/llms.txt` | The SvelteKit file is ~650 KB, so prefer llms-small or single pages |
| @supabase/* | README, types | `https://supabase.com/llms.txt` → guide pages as `.md` | `llms-full.txt` is huge, so load guides one at a time |
| motion / framer-motion | README | `https://motion.dev/llms.txt` | Package renamed from `framer-motion` to `motion`; check which one the project imports |
| gsap | README | `https://gsap.com/llms.txt` | |
| @react-three/fiber | README | `https://r3f.docs.pmnd.rs/llms.txt` | |
| zod | README, types | `https://zod.dev/llms.txt` | v3 vs v4 APIs differ |
| shadcn-svelte | `components.json` | `https://shadcn-svelte.com/llms.txt` | |

## Runtimes, backends, databases (see stack-choice.md, stacks/backend-js.md, stacks/databases.md)
All checked 2026-10-15 to return real Markdown:
- **Runtimes:** Bun `https://bun.com/llms.txt` · Deno `https://docs.deno.com/llms.txt`
- **Backends:** Elysia `https://elysiajs.com/llms.txt` · Hono `https://hono.dev/llms.txt` · Express `https://expressjs.com/llms.txt` · Fastify `https://fastify.dev/llms.txt` · NestJS `https://docs.nestjs.com/llms.txt` · Nuxt `https://nuxt.com/llms.txt`
- **ORMs:** Drizzle `https://orm.drizzle.team/llms.txt` · Prisma `https://www.prisma.io/docs/llms.txt`
- **Databases and services:** Neon `https://neon.com/llms.txt` · Turso `https://docs.turso.tech/llms.txt` · MongoDB `https://www.mongodb.com/docs/llms.txt` · Mongoose `https://mongoosejs.com/llms.txt` · Redis `https://redis.io/llms.txt` · Upstash `https://upstash.com/docs/llms.txt` · Convex `https://docs.convex.dev/llms.txt` · Firebase `https://firebase.google.com/docs/llms.txt`

Node has no llms.txt; use `https://nodejs.org/docs/latest/api/`. Astro has none found. Release lines come from `env_check.py --latest` (nodejs.org/dist/index.json).

## Icons and motion (see icons.md, motion.md)
For anything not listed, `scripts/latest.py <pkg>` probes the package homepage for an llms.txt live, and only accepts real Markdown. Several sites answer `/llms.txt` with their HTML app shell.

| Package | Machine-readable (official) | Notes |
|---|---|---|
| lucide (all framework packages) | `https://lucide.dev/llms.txt` | package names differ per framework |
| tabler, phosphor, heroicons | none found | use `scripts/icons.py search` and the sites |
| three | `https://threejs.org/llms.txt` | |
| lottie / dotlottie | `https://docs.lottiefiles.com/llms.txt` | |
| lenis | `https://lenis.darkroom.engineering/llms.txt` | |
| animejs, react-spring, rive | none found (sites return HTML) | read the docs pages |
| Any icon set | `https://api.iconify.design` (search, collections, SVG) | used by `scripts/icons.py` |
| Browser feature support | web-platform-dx/web-features (Baseline) | used by `latest.py --baseline` |

## Component sources (see components.md)
| Source | Machine-readable index |
|---|---|
| 21st.dev | `https://21st.dev/llms.txt` |
| React Bits | `https://reactbits.dev/llms.txt` |
| Magic UI | `https://magicui.design/llms.txt` |
| Aceternity UI | `https://ui.aceternity.com/llms.txt` |
| Origin UI | moved to `https://coss.com/ui` (no llms.txt found) |
