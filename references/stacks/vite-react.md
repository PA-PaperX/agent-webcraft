# Vite + React (SPA)

**Docs:** `https://vite.dev/llms.txt`, `https://react.dev/llms.txt`, and the router's docs for its installed major (React Router has no llms.txt; v6 and v7 APIs differ).

## Look up before coding
- **Router setup and data APIs** for the installed router version (loaders and actions in v7 framework or data mode vs plain `<Routes>`).
- **Env vars:** only `VITE_*` reach the client, and everything that does is public.
- **Vite config:** plugin set (`@vitejs/plugin-react`, `@tailwindcss/vite` for Tailwind 4), path aliases (match `tsconfig` paths), and dev server proxy for APIs.
- **React version features in use:** Actions, `use`, form status hooks. Confirm against react.dev for the installed major.

## Pitfalls
- **SPA routing on static hosts:** deep links 404 without a fallback to `index.html`. Configure the host.
- **SEO:** a client-rendered SPA ships little HTML. If SEO matters (brief), say so early. Prerendering or a framework may fit better.
- **Data fetching in `useEffect`:** without cancellation it causes races. Prefer the router's loaders or a query library if the project has one.
- **Bundle growth:** check `vite build` output sizes after adding dependencies, and lazy-load heavy routes.

## Verify
- `tsc --noEmit` (or the project's `typecheck` script), `vite build`, and `vite preview` for a production-like check.
- Load the changed routes, including deep links and refresh.
