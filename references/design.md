# Design direction

The user chooses; the agent's job is to show real, varied options and to record the choice so every agent builds the same thing. Taste-from-memory produces generic sites, so options come from a style library and from sites the user points at. Follow the steps in order. `design_lint.py` checks the result before any UI task can be closed.

If the project already has an established look and this is not a redesign: record it as DESIGN.md (export the closest style and correct the tokens to match the code, or write the front matter from the existing CSS). Mark it "Existing look: yes", then skip to step 8.

## 1. Ask for references (always)
"Do you have websites whose look you like? Paste 1–3 links, or say none." Also ask what they like about each (layout, colors, type, photos, feel).
- For each URL: `python <skill>/scripts/ref_extract.py <url>` drafts its tokens. Also take a screenshot of the site, and correct the roles by eye when the script reports low confidence.
- Famous brands are in the library too: `styles.py list --query <brand>`, for example apple, airbnb or stripe.

## 2. Score the brief (1–5 each, one-line reason)
Warmth (cool ↔ warm), Playfulness (serious ↔ playful), Density (airy ↔ dense), Trust weight (casual ↔ high-stakes), Expressiveness (quiet ↔ bold). Base each score on brief facts.

## 3. Shortlist 5–9 options
`python <skill>/scripts/styles.py shortlist --axes W,P,D,T,E --query <job words> --n 9`.
- **Job words** say what the site is for: `cafe coffee restaurant`, `clinic`, `saas`. Mood words such as warm or modern only rank.
- The library holds built-in presets, popular-brand design systems and Aura design systems (style-catalog.md).
- The script drops poor fits and prints full-page templates for the same job. Keep those for step 7.
- Add the user's reference drafts.

## 4. Preview and let the user choose
1. `python <skill>/scripts/styles.py preview --from-shortlist --brand "<name>" --title "<real headline>" --tagline "<real line>"`. This renders every option with the project's own Thai copy, plus a contrast check for each.
2. Open it in the browser and send the user the path or a screenshot.
3. The user picks a number or mixes options ("colors of #3, type of #7").
4. **If the user can't decide:**
   - open 2–3 full-page examples that fit the job: `styles.py templates --query <job>`, then `styles.py template "<name>"`;
   - or show screenshots of the reference sites;
   - ask which feels closer;
   - recommend one with a reason.
   The user still decides.

## 5. Record the choice
1. `python <skill>/scripts/styles.py export <id>` writes `.webcraft/DESIGN.md` with the chosen tokens in front matter.
2. Then fill:
   - **Directions considered:** every option shown, with its id, source URL and why it fits or doesn't, and the one chosen.
   - **References:** 2+ URLs, and at least one is a **live website** like this one (the user's reference site, or a well-known site doing the same job). Font pages, GitHub, docs, component libraries, Dribbble and example.com don't count. The benchmark pass compares against it.
   - **Icons** (icons.md) and **Motion** (motion.md).
   - **Components:** with "Searched" filled in (components.md).
   - **Decisions:** what was mixed or changed and why.
3. Fix any contrast that failed in the preview **before** building, by adjusting the token, not each component.
4. Brand fonts that aren't free get a similar free font plus a Thai pair (thai-web.md).

## 6. Component style (the user chooses)
A site can match the user's taste in colors and still feel wrong because of its buttons or cards. Some users also want one signature feature of their own.
1. `python <skill>/scripts/components.py preview --brand "<name>" --cta1 "<main action>" --cta2 "<second action>" --item "<real item>"` renders 42 variants in the chosen tokens. The groups are buttons, cards, navigation, mobile action bar, form fields, tags, image shapes and a signature element.
2. Open it and send the user the path or a screenshot. Ask them to pick one per group (for example `B2 C4 N1 M1 F1 T3 I3 S2`) and whether they want something of their own ("buttons like apple.com", "a live open-now badge").
3. Record it: `python <skill>/scripts/components.py choose B2 C4 N1 M1 I3 S2 --custom "S=<their idea>"`. This writes **Component style** in DESIGN.md with an exact spec per group.
4. Build every instance from those specs: one button style and one card style across the whole site. `design_lint.py` checks that button and image corners match the chosen variant (for example B3 means square buttons, not `rounded-full`). If the user changes their mind, record it again with `components.py choose`.

## 7. Page blueprint
Follow page-blueprints.md: start from the user's reference site, a full-page template for the same job, or a recipe. Fill **Page blueprint** in DESIGN.md ("Based on" + one row per section) and show it to the user with the brief's real or sample content in mind.

## 8. Apply tokens
Put the tokens where the stack expects them, after checking the installed major's docs (docs-map.md):
- **Tailwind 4:** `@theme` in the global CSS.
- **Tailwind 3:** `tailwind.config.*`.
- **shadcn:** CSS variables.
- **Svelte:** app.css.

Components use token classes only. A hard-coded color needs `webcraft-allow-color` and a reason.

## Guardrails (checked again in verify)
- **Contrast is checked on the rendered page**, not just between palette pairs: text over photos and gradients, badges and chips. Body text at least 4.5:1.
- **A photo under text stays recognizable:** scrim ≤ ~50% and only behind the text area. Check at 390 px.
- **One mood per page.** A dark hero on a light page needs a reason in DESIGN.md.
- **The famous-site standard** (quality-bar.md): hierarchy, space, one action color, real media, few component styles.
