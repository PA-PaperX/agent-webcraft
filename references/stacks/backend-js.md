# JavaScript backends: runtimes and API frameworks

**Docs (machine-readable, checked 2026-10-15):**
- `https://bun.com/llms.txt`
- `https://docs.deno.com/llms.txt`
- `https://elysiajs.com/llms.txt`
- `https://hono.dev/llms.txt`
- `https://expressjs.com/llms.txt`
- `https://fastify.dev/llms.txt`
- `https://docs.nestjs.com/llms.txt`

Node itself: `https://nodejs.org/docs/latest/api/`. Versions: `env_check.py --latest`.

## Runtime notes
- **Node:** run an LTS line in production. Pin the version for the team: `engines` in package.json and `.nvmrc`. The `--watch` flag and native `fetch` and test runner make extra tools optional.
- **Bun:** runs TypeScript directly and includes a package manager, test runner and bundler, plus built-ins like `Bun.serve` and `bun:sqlite`.
  - Before committing to Bun in production, install the real dependencies and run the test suite on Bun. Native addons and some `node:` APIs are where gaps show.
  - Pin with `packageManager` / `.bun-version`.
- **Deno:** permissions are explicit (`--allow-net`, …). npm packages load via `npm:` specifiers. `deno.json` holds tasks and imports.
- Only one lockfile per project. The package manager and runtime are recorded in BRIEF → Stack decisions.

## Framework notes
- **Elysia** (Bun-first):
  - schema validation with `t` (TypeBox) gives typed routes;
  - the Eden client gives the frontend end-to-end types;
  - plugins for CORS, Swagger/OpenAPI and JWT.
  Check the docs for the installed major, because plugin names and APIs evolve.
- **Hono** (Web Standards: Request/Response): the same code runs on Node (`@hono/node-server`), Bun, Deno, Cloudflare Workers and Lambda. Use its validator and RPC client for types.
- **Express 5:** async errors propagate to the error handler, and some path syntax changed from v4. Check the migration notes if upgrading.
- **Fastify:** schema-based validation and serialization, and an encapsulated plugin system.
- **NestJS:** modules, controllers, providers and DI. Heavier, and suits large teams.
- **Next.js route handlers or server actions:** often enough. A separate service is not free (see stack-choice.md).

## Every API (check each time)
- **Validate all input** at the boundary with schemas (TypeBox, Zod, Valibot), and return typed errors with correct status codes.
- **Auth:** verify sessions or tokens on the server for every protected route. CORS allows only known origins. Cookies are `HttpOnly`, `Secure` and `SameSite`.
- **Secrets** come from env variables, never from code or git. Read them in one config module that fails fast when one is missing.
- **Protection:** rate-limit public endpoints, and cap request body size.
- **Logging:** log requests with an id, and never log secrets or personal data.
- **Health:** add a `/health` route; shut down gracefully on SIGTERM.

## Verify
- Typecheck, then the test suite (`bun test`, `node --test`, `vitest`).
- Start the server and call each changed route with `curl` or a test client. Include a bad input and an unauthenticated call.
- Check the response codes and bodies against the plan.
