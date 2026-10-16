# Stack choice: runtime, framework, database

These choices are the most expensive to change later, so they belong in Discover. Each one gets a reason the user can check. Each one is checked against what's actually installed on the machine and already in the project.

## 1. Gather facts first (no questions yet)
- `python <skill>/scripts/env_check.py [project] --latest`: what's installed on the machine (runtimes, package managers, Docker, database servers and clients, hosting CLIs), what the project already uses (lockfiles, pins, backend, data layer, compose services, env variable *names*), and today's versions of the runtimes.
- `python <skill>/scripts/latest.py <candidates>`: license, publish date, downloads and advisories for each framework, ORM or driver you might propose. Watch for a prerelease tagged `latest`.
- Read the brief's answers about users, scale, data, realtime, hosting and budget.

## 2. Rules for recommending
- **Existing project:** keep its stack unless the brief needs something it can't do. Say why you're not changing it. Switching runtime or ORM is a migration (build.md), not a preference.
- **Mixed lockfiles or package managers:** one decision, with the user.
- **Prefer what's installed** when options are otherwise close. If the best option needs an install (Docker, Bun, a CLI), say so and ask before installing.
- **Fit the job, not the hype.** For most apps the bottleneck is the database and the network, not raw framework speed. Benchmark claims from framework authors are marketing until reproduced.
- **Every recommended option comes with one line:** why this job, and the trade-off.

## 3. Ask (one round, up to 4 questions, recommended option first)
Ask only the questions the job needs. A static landing page needs no database question. State "no database, content in a data file" as the decision instead.

**Runtime and package manager**
| Option | Fits when | Trade-off |
|---|---|---|
| Node.js LTS + npm or pnpm | production default, native addons (sharp, bcrypt, canvas), most hosts | slower installs and tests than Bun |
| Bun (runtime + package manager) | greenfield services, fast dev and test loop, Elysia | not every Node API or native addon works, so test the dependency list; no LTS line |
| Node runtime + Bun as package manager and test runner | want Bun's speed without production risk | two tools to keep in mind |
| Deno | TypeScript-first, built-in tooling, secure by default | smaller framework ecosystem; npm compat is good but not total |

**App and backend framework**
| Job | First choice | Alternatives |
|---|---|---|
| Content site, landing page, blog | Next.js (static output) or Astro | SvelteKit |
| Web app with UI + API in one deployable | Next.js (route handlers, server actions) | SvelteKit, Nuxt |
| SPA talking to an existing API | Vite + React | Vite + Svelte or Vue |
| Separate API on Bun | Elysia (end-to-end types with Eden) | Hono |
| API portable across Node, Bun, Deno and edge | Hono | — |
| API with the widest middleware ecosystem | Express 5 or Fastify | — |
| Large team, modules, dependency injection | NestJS | — |

A separate backend is justified by a separate deploy or scale need, by multiple clients (web + mobile), or by long-running jobs. Otherwise the app framework's own server routes are less to run.

**Database (+ ORM)**
| Data and need | First choice | Alternatives |
|---|---|---|
| Relational data, auth, storage and realtime in one service | Supabase (Postgres) | Neon (serverless Postgres) + separate auth |
| Relational, serverless or branching dev databases | Neon | Supabase |
| Small app, edge reads, or nothing to install locally | SQLite: libSQL/Turso, or `bun:sqlite` on Bun | — |
| Documents with flexible shape | MongoDB (Atlas) | Postgres with JSONB is often enough |
| Realtime collaborative state, little backend code | Convex or Firebase | Supabase Realtime |
| Cache, rate limits, queues | Redis or Upstash Redis | — |
| ORM / query layer | Drizzle (SQL-like, light, many drivers) | Prisma (schema-first, migrations, Studio), Kysely |

Mark each option *installed / needs install / hosted*. Without Docker, a local Postgres means installing a server or using a hosted dev database. SQLite needs nothing.

**Hosting** (only if it changes the choices above): Vercel, Netlify, Cloudflare (Workers favor Hono and edge-compatible drivers), a VPS or Docker host, or Supabase/Firebase hosting.

## 4. Record
Write a **Stack decisions** table in BRIEF.md: choice, alternatives considered, reason, installed?, docs URL (from docs-map.md or `latest.py`). Later sessions read the decision instead of reopening it.
