# Evaluation scenarios

Rerun these after a model change, an agent update, or an edit to the skill. Run each in a fresh session, in a throwaway copy of a real project. Record pass or fail and the date in the table at the bottom.

| # | Setup | Prompt (any language) | Expected behavior |
|---|---|---|---|
| 1 | Next.js project, no `.webcraft/` | "Build a homepage for a café in Chiang Mai" | Runs detect_stack. Scans before asking. Asks rounds of ≤4 multiple-choice questions, skipping anything the repo already answers. Writes `.webcraft/BRIEF.md` with status "awaiting approval". Summarizes in the user's language. **Writes no code.** |
| 2 | Same project, brief approved | "approved" | Creates tasks with acceptance boxes. Runs the design step: 5 axis scores, 1 recommended + 2 alternative directions that differ on ≥2 axes, with current reference URLs. Stops for the user's choice. |
| 3 | Tailwind **3** project | "Add a brand color and use it on the buttons" | Reports Tailwind v3 from detect_stack and edits `tailwind.config.*`, not `@theme`. Tiny brief approved inline. Verifies with a screenshot. |
| 4 | Next.js 16 project | "Cache this data fetch for an hour" | Reads the caching guide in `node_modules/next/dist/docs/` and cites the path. Adds a Docs note to STATE. Does not rely on memory alone. |
| 5 | Thai-language site | "The headline looks cramped" | Checks Thai line-height and letter-spacing (thai-web.md). Fixes tracking on Thai text. Screenshots at 3 sizes. |
| 6 | React + Tailwind 4 project | "Add an animated text effect to the hero" | Follows the sourcing ladder; picks a React Bits TS-TW variant or similar. Records source and license in DESIGN.md. Respects reduced motion. |
| 7 | Board with a task in progress owned by `claude` | (in Codex) "continue the menu page" | Reads STATE and the task log. Doesn't take over without asking the user. After approval, claims with `--force`, works, and reports with file:lines and evidence. |
| 8 | SvelteKit project | "Add a pricing section" | Uses Svelte 5 runes if detected. Doesn't install React-only components; uses shadcn-svelte or ports the idea. |
| 9 | Next.js + Supabase | "Show the user's orders on /account" | Checks RLS on the orders table. Keeps the service_role key server-only. Tests as anonymous and as a signed-in user. |
| 10 | Any project with `.webcraft/` | "What were we doing?" | Answers from STATE and `board.py list` in a few lines, without reading the archive or every task. |
| 11 | Project with no icon package, or with emoji used as icons | "Add icons to the menu" | Picks one SVG family from DESIGN or the direction (icons.md). Runs `icons.py search` for the concepts and `latest.py` for the package. Icon-only buttons get accessible names. No emoji. |
| 12 | React project that already has `motion` | "Make the cards animate in on scroll" | Reuses `motion` before adding GSAP. Checks `latest.py --baseline scroll-driven-animations` before using it natively. Animates transform/opacity only, respects reduced motion, and content is visible without JS. |
| 13 | Empty folder | "Build a booking site for a small clinic with an admin page" | Runs env_check before asking. The stack round offers runtime, framework and database options, each with a reason and installed/needs install (e.g. "no Docker → hosted Postgres or SQLite"). Records the Stack decisions table in BRIEF and installs nothing before approval. |
| 14 | Existing Next.js + Supabase project | "Should we move to Bun and Elysia?" | Keeps the stack unless the brief needs a change, and explains why. If moving anyway, plans it as a migration and validates dependencies on Bun first. |
| 15 | Empty folder, the user has no reference site | "Make it look modern and beautiful" | Asks for reference sites, then shortlists 8–12 styles with `styles.py shortlist` and opens the preview. **The user picks.** Exports DESIGN.md with Directions considered (all shown options + URLs), References and Thai fonts. Fixes failed contrast in tokens before building. |
| 16 | The user pastes a site they like | "I want something like this" | Runs `ref_extract.py` plus a screenshot, corrects low-confidence roles, shows it beside the shortlist, and the user chooses. |
| 17 | UI task with hard-coded colors, stock photos, invented reviews | "Done, close the task" | `board.py done` refuses. The agent fixes the tokens and lists placeholders in BRIEF "Content to be supplied" (or replaces them with real content) and logs the critique pass. It doesn't use `--force` unless the user says so. |
| 18 | Style chosen, before building | "Next step" | Runs `components.py preview` with the brief's real action labels and item. The user picks per group and may add their own idea. `components.py choose` records the specs, and the build uses one button style and one card style. |
| 19 | Café brief, owner has no photos yet, samples approved | "Build the page" | Fills Page blueprint from a recipe or the Café template. Uses marked sample photos and items. Facts (phone, hours) are designed placeholders with final button labels. The page looks finished, and the gate passes with no more than 4 placeholder notes. |
| 20 | Owner has no phone, LINE or hours yet; the user wants to see the full design | "Show it as a mockup for now" | Records the items under BRIEF "Mockup content" with obvious dummy values (080-000-0000, @yourshop) and shows the mockup notice. The lint warns, it doesn't error. `design_lint.py --release` fails until the items are real and the notice is gone. |
| 21 | The user chose B3 (sharp) buttons and I2 images; the build uses `rounded-full` buttons and the only reference is a font page | "Done?" | `design_lint.py` reports the spec mismatch and the missing real reference. The agent fixes the buttons (or asks the user and re-records the choice), adds a live reference site and benchmarks against it before `board.py done`. |

## Results
| Date | Agent / model | Passed | Notes |
|---|---|---|---|
