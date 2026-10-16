# Next.js (+ React)

**Docs:** `node_modules/next/dist/docs/` for the installed version (16+), the AGENTS.md block that `next dev` maintains, `https://nextjs.org/docs/llms.txt`, and `.md` page URLs. Majors change caching, request APIs and config, so check what the installed version says before relying on memory.

## Look up before coding (topics that move between majors)
- **Router:** App Router (`app/`) or Pages Router (`pages/`). Don't mix patterns.
- **Server Components by default:** where `'use client'` is needed (state, effects, browser APIs, event handlers). Keep client components small and at the leaves.
- **Data fetching and caching:** the caching model and its config flags differ between versions. Read the installed caching guide before adding `fetch` options or route segment config.
- **Request-time APIs:** `cookies()`, `headers()`, `params` and `searchParams` (sync vs async depends on the version).
- **Mutations:** Server Actions vs Route Handlers (`app/api/**/route.ts`); revalidation after a mutation.
- **Metadata:** `metadata` or `generateMetadata`, `opengraph-image`, sitemap and robots files.
- **Assets:**
  - `next/image` sizes and remote patterns;
  - `next/font` subsets (include `thai`, see thai-web.md);
  - `next/script`.
- **Middleware or proxy file conventions and runtime:** check the installed docs for the name and location.

## Pitfalls
- Importing server-only code (DB clients, secrets) into a client component. Use `server-only` to fail loudly.
- `NEXT_PUBLIC_*` env vars are inlined into the client bundle. Never put secrets there.
- Hydration mismatches from `Date.now()`, random values, or locale formatting that differs between server and client.
- Large client components that pull a whole library. Check what `'use client'` drags in.
- Images without width and height, or without `sizes`, cause layout shift.

## Verify
- `next build` catches type, route and server/client boundary errors that dev mode tolerates.
- Run `next dev`, load each changed route, and read the terminal and browser console.
- With `next-devtools-mcp` configured (Next 16+), query runtime errors, routes and logs from the running dev server. It sends telemetry unless `NEXT_TELEMETRY_DISABLED=1`.
