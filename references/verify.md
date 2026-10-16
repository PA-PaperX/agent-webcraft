# Verify

"It should work" is not evidence. Run checks in order from cheapest to most expensive, and report each one as pass, fail, unavailable or skipped, with the evidence. For UI work, `board.py done` runs the design gate itself and refuses while it reports errors.

## Ladder
1. **Static:** the project's own scripts, such as `typecheck`, `lint`, `check` (svelte-check) and `format:check`. Read `package.json` scripts; don't invent commands.
2. **Design gate:** `python <skill>/scripts/design_lint.py`. It checks:
   - hard-coded colors;
   - missing DESIGN records (choices, page blueprint, component style);
   - a page with no imagery, unused icon family, no container, or too many placeholder notes;
   - buttons and images that don't match the chosen Component style, and photo placeholders that ignore its placeholder spec (dark frames on a light page);
   - invented or unapproved content.

   Fix every ERROR. Each remaining warning is either fixed or listed in STATE "Known issues".
3. **Tests:** unit and integration tests that cover the change, then the full suite if it is fast.
4. **Build:** `build` for any change that touches config, routing or server code.
5. **Run it:** start the dev server (or reuse a running one) and load every changed route. Read the server output and the browser console. Use a framework MCP if present (stacks/). Fix based on the actual error text.
6. **Look at it:** screenshots at **390×844**, **768×1024** and **1440×900**, plus dark mode if supported. Open the images, then do the critique pass below.
7. **Use it:** tab through the changed UI.
   - Focus is visible and the order makes sense.
   - Controls have names.
   - Forms show errors.
   - Reduced motion is respected.
   - `lang` is set.
   - **Tap targets** are at least 44 px. In the browser console:
     `[...document.querySelectorAll('a,button,[role=button],input,select')].filter(e=>{const r=e.getBoundingClientRect();return r.width&&r.height<44}).map(e=>e.textContent.trim().slice(0,30)||e.tagName)`
     Fix anything listed, or explain it (inline text links inside paragraphs are fine).
8. **Weight:** new dependencies and their size; images sized and lazy-loaded below the fold; heavy effects don't block first paint. Run Lighthouse if available for Feature or Project work.

## Critique pass (required for UI work)
For each screenshot, write the **three weakest things**, or "none" with a reason, in the task log. Check at least:
- **Text over images:** contrast of the rendered text (not the palette pair), and whether the photo is still recognizable at 390 px.
- **Badges, chips and small text:** readable on the background they actually sit on.
- **Generic-template signs** (quality-bar.md) and repeated elements, such as the same button on every card.
- **Content:** fake, empty or placeholder content, and whether each placeholder is listed in BRIEF.
- **Thai:** clipped marks, letter-spacing or wrapping problems.

Also check the page against DESIGN.md: does every section follow the **Page blueprint**, and does every button, card and image follow the **Component style** specs?

Then do the **benchmark pass** in quality-bar.md: compare against 1–2 live reference websites from DESIGN.md and log the three biggest differences.

Log both passes on the board. `board.py done` refuses UI tasks until they are there:
```bash
python <skill>/scripts/board.py report T-0003 --agent NAME --did "critique: 390 - ...; 768 - ...; 1440 - ..."
python <skill>/scripts/board.py report T-0003 --agent NAME --did "benchmark: compared with https://... - three biggest differences ..."
```
Fix what they found, or list it in STATE "Known issues".

STATE "Known issues" can't say "none" unless the critique found nothing, and the log says so.

## Screenshot tools
- **First choice:** the agent's built-in browser or browser MCP (tools.md).
- **Fallback:** `python <skill>/scripts/shoot.py <url> --out .webcraft/shots` (Playwright via npx). The first run needs `npx playwright install chromium`, about 150 MB, so ask the user before running it.

## Before launch
`python <skill>/scripts/design_lint.py --release` fails while any mockup item, mockup notice, placeholder note, or item in "Content to be supplied" remains. Run it before any deploy the user asks for, and list what is left.

## Report and stop
- One line per check: the command or action, the result, and the decisive output line or screenshot path.
- Tick only the acceptance boxes the evidence proves.
- Log the result on the board.
- Stop when acceptance is met. Ideas beyond scope become board proposals.
