# Build

## Before the first edit
- Claim the task on the board.
- Read the files you will change plus one neighbor that shows the project's conventions (naming, imports, data fetching, styling).
- Check STATE → Docs notes for the APIs you will touch. If an API is not covered, ground it now (docs.md) and add a note.

## While editing
- **Narrowest change that meets acceptance.** Fix at the layer that owns the behavior. Leave unrelated code, names and formatting alone.
- **Reuse before creating:** existing components, hooks, utilities and tokens. If you have to duplicate something, extract it instead, inside the task's scope.
- **Colors, fonts, radii and spacing come from DESIGN tokens as token classes or CSS variables.** Writing `bg-[#2C1E15]` or `style={{color:'#…'}}` in a component skips the design system. `design_lint.py` counts these and blocks done when they dominate. A deliberate exception gets `webcraft-allow-color` and a reason on the same line.
- **Follow DESIGN.md exactly:** the section order and visuals in Page blueprint, and the specs in Component style (one button style and one card style for the whole site).
- **Content follows the three tiers** (content.md): real, approved sample, or designed placeholder. Never invent reviews, numbers, names or contact details, and never put placeholder text inside a button.
- **New dependencies need a reason** stated in the task log: what it replaces, its size, and its license.
- **Follow the framework's model from the docs:**
  - server and client boundaries;
  - data fetching and caching;
  - routing files;
  - env var prefixes for what is public. Server secrets never reach client code or git.
- **Every data-driven UI has its states:** loading, empty, error and success, plus long text, Thai text and small screens.
- **User-facing strings stay in one place** if the project has i18n. Don't hard-code them in components.
- **Accessible by construction:** semantic elements, labels, alt text, focusable controls and logical heading order.

## Refactors and migrations
- A refactor keeps behavior. Run the same verification before and after, and keep feature changes out of it.
- A migration (database schema, API, dependency major) needs a forward path and a rollback path. Destructive steps need separate approval from the user.

## Commits
One commit per task or per coherent step, with the task id: `T-0007 add kitchen scoop pickup`. Never commit secrets, `.env*` files with real values, or generated artifacts the project ignores.
