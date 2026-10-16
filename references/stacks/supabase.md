# Supabase (database, auth, storage)

**Docs:** `https://supabase.com/llms.txt` → guide pages as `.md` (auth, database, storage, functions). Load one guide at a time; `llms-full.txt` is very large.

## Look up before coding
- **Client setup for the framework:** `@supabase/ssr` for cookie-based auth in Next.js and SvelteKit. Server, browser and middleware clients differ.
- **Auth flow in use:** email/password, OTP, OAuth or magic link. Redirect URLs must match the project settings.
- **Generated types:** `supabase gen types` keeps queries typed. Regenerate after schema changes.
- **Migrations:** schema changes go through migration files (Supabase CLI), not ad-hoc dashboard edits, so every environment matches.

## Security rules (check every time)
- **Row Level Security is enabled on every table that holds user data,** with policies for each operation used. A table without RLS is readable by anyone holding the anon key.
- **The `service_role` key is server-only.** It bypasses RLS. Never import it into client code, never expose it with a public env prefix, never commit it.
- **The anon key is public by design.** Safety comes from RLS policies, not from hiding the key.
- **Storage buckets have policies too.** Public buckets serve files to anyone.
- **Personal data** triggers the PDPA notes in the brief (thai-web.md).

## Pitfalls
- Using the browser client for server-side mutations that should check auth on the server.
- Forgetting to refresh sessions in middleware when using cookie auth (check the installed `@supabase/ssr` guide).
- N+1 queries from per-row fetches. Use joins (`select('*, related(*)')`) or views.

## Verify
- Run the query paths as an anonymous user and as a signed-in user, and confirm that RLS denies what it should.
- Check the browser network tab for leaked keys or over-fetching.
