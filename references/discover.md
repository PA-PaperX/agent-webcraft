# Discover

Goal: a brief complete enough that nobody, human or agent, has to guess what to build. This phase is allowed to cost more than any other. Every question answered here is one that no later session has to ask again.

## 1. Scan before asking
Answer as much as you can from the repo, cheapest source first, and note each finding with its source:
1. `python <skill>/scripts/detect_stack.py`: framework, versions, package manager, scripts, docs on disk. Then run `python <skill>/scripts/env_check.py --latest` to see what this machine has installed (runtimes, Docker, databases, CLIs) and today's runtime versions.
2. `README*`, `AGENTS.md`, `CLAUDE.md`, any existing `.webcraft/` files.
3. The route/page list (e.g. `app/**/page.*`, `src/routes/**/+page.*`, `src/pages/**`).
4. Design inputs already present: `components.json`, Tailwind theme (`@theme` in CSS for v4, `tailwind.config.*` for v3), CSS variables, fonts, logo/brand assets.
5. `git log --oneline -15`, which shows what has been happening recently.

Anything the scan answers is not asked. Facts you inferred, as opposed to read, go into the brief as assumptions for the user to confirm.

## 2. Interview in rounds
- Up to 4 questions per round. Each is multiple choice, with your recommended option first and labelled, and free text always allowed. Use the agent's question tool if it has one, otherwise a numbered list.
- Order the rounds: goal and users → scope and content → look and feel → **stack** → constraints → quality bar. Within a round, ask the questions whose answers change the most.
- **The stack round** covers runtime and package manager, app or backend framework, database and ORM, and hosting. Follow stack-choice.md: every option shows a one-line reason for this job and whether it is installed, and the recommendation comes from the job plus what `env_check.py` found. Skip questions the job doesn't need, and state that decision instead.
- Ask in the user's language. Keep each option to one line, plus a short consequence where useful.
- Stop when the checklist below is complete. If the user says "enough", stop too, and record the open items as assumptions.
- **Existing project without `.webcraft/`:**
  1. Scan.
  2. Ask what the change is.
  3. Interview only about the change.
  4. Record the current design as DESIGN.md "Existing look" instead of choosing a new direction (design.md).
- **Three questions are always asked:**
  - "Do you have websites whose look you like? Anything special about their buttons, menus or details?" This drives design.md steps 1 and 6.
  - "Which real content exists: photos, logo, menu or prices, phone, LINE, map link, reviews?" Missing items become "Content to be supplied" (content.md).
  - "For each thing you don't have yet, how should it look for now?" Ask per item: photos, menu or products, phone and LINE, hours and address, reviews. Offer these modes (content.md):
    - **sample:** example photos and items, marked (rec. for photos and items);
    - **mockup:** realistic dummy values with a mockup notice, replaced before launch (rec. when the user wants to judge the full design now);
    - **placeholder:** designed frames and final button labels.
    Record the answers in BRIEF "Sample content", "Mockup content" and "Content to be supplied".

## 3. Checklist (the brief needs all of these)
- **Goal:** what this achieves and how success is measured.
- **Users:** who they are; device mix; language(s); accessibility needs.
- **Scope:** pages/flows in v1; explicit non-goals.
- **Content:**
  - where text, images and data come from, and who edits them later (hard-coded, CMS, database);
  - which real assets exist (photos, logo, menu or prices, phone, LINE, map link, review source), and which must be supplied by the owner;
  - the mode chosen for each missing item (sample, mockup or placeholder).
  Never invent facts such as reviews, phone numbers or addresses (content.md).
- **Look and feel:** brand assets; sites the user likes and dislikes, and why; tone (formal ↔ playful); any signature feature they want (a live open-now badge, a queue counter, a special button).
- **Tech:** runtime, framework, database and hosting, each with its reason (stack-choice.md); data, auth, integrations, payments.
- **Constraints:** deadline, budget, performance targets, SEO, analytics, i18n.
- **Legal:** personal data and consent (e.g. Thailand's PDPA), cookies, licensing of assets.
- **Quality bar:** browsers/devices to support, accessibility level, the definition of done.

## Question bank (adapt, don't read out)
- "Who is the main visitor?" → customers on mobile (rec.) / internal staff on desktop / both / other
- "What is the one action a visitor should take?" → buy / book / contact / sign up / read / other
- "How should it feel?" → warm & friendly / clean & professional / bold & playful / premium & calm
- "Show me 1–3 sites you like" → free text; then "what do you like about it?" → layout / colors / type / motion
- "Who updates content after launch?" → developer only (rec. for v1) / non-technical staff → needs CMS
- "Do you collect personal data?" → no / contact form only / accounts & profiles → PDPA consent + privacy page
- "Languages?" → Thai only / Thai + English (rec. if tourists) / other

## 4. Write the brief and stop
1. Fill `templates/BRIEF.md` → `.webcraft/BRIEF.md` (English). Set status to `awaiting approval`.
2. Summarize the brief in the user's language in chat, in about 10–15 lines: goal, users, scope, non-goals, look, tech, risks, assumptions.
3. Stop and ask for approval. No code, no installs, no scaffolding before the "yes".
4. After approval:
   1. Set the status to `approved <date>`.
   2. Run `board.py init` if needed.
   3. **Fill RULES.md**: the real project name, Conventions taken from the scan, and the "Do not" list.
   4. Create tasks (plan.md).
   5. Add a short "Project" section to STATE.md.
