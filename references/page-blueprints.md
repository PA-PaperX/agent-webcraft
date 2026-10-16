# Page blueprints

Tokens give colors and fonts; they don't give a layout. Composing a page from scratch is where generic, empty-looking sites come from. So every page starts from a **blueprint**: a proven section order with a layout and a visual for each section. Record it in DESIGN.md **Page blueprint** before building. `design_lint.py` checks that the section exists.

## Choose a starting point (in this order)
1. **The user's reference site:** follow its section order and spacing, not its text or images.
2. **A full-page Aura template for the same job.** `styles.py shortlist` prints matches. Otherwise run `styles.py templates --query <job words>` and `styles.py template "<name>"`, open the result in the browser, take a screenshot, and copy its *structure* (section order, layout, spacing, image sizes). Apply the chosen tokens and component style to it.
3. **A recipe below.**

Mix them if useful, and say what came from where in "Based on".

## Rules for every blueprint
- **Every section has a visual anchor:** a photo, an illustration, a map, an icon row, large type or a number. A section that is only a heading and one line of text is not finished.
- **Alternate layouts:** no two neighboring sections share the same layout (for example, centered text, then split, then grid).
- **Width:** one max width (about 1120–1280 px) with 20–24 px side gutters on mobile. Text columns are at most ~70 characters.
- **First screen on mobile:** shows what the place or product is, one visual, and the main action without scrolling.
- **Actions** use the final labels and design (content.md); there is one primary action per screen.

## Recipes
### Local business: café, restaurant, bakery, salon, clinic, shop, homestay
| # | Section | Layout | Visual |
|---|---|---|---|
| 1 | Header | wordmark left, 2–3 links, one action right; sticky, 56–64 px | logo or wordmark |
| 2 | Hero | full-bleed photo with a light local scrim **or** split photo/text; name, one specific line, open-now line ("เปิด 08:00–17:00 · ปิดวันพุธ"), 2 actions (directions, LINE/call) | the place itself, big |
| 3 | Signature items | 3–6 cards: photo, Thai name + English, price | product photos, same ratio |
| 4 | Atmosphere | asymmetric gallery, 3–6 photos | interior, view, people (with consent) |
| 5 | Story | split: photo + 2–3 short paragraphs | owner or making-of photo |
| 6 | Visit | hours table + map embed or static map + address + directions button | map |
| 7 | Footer | contact icons, hours repeated, small print | icon row |
| m | Mobile | sticky bottom bar with the two main actions (48 px+, safe-area padding) | icons + labels |

### Product, SaaS, app
Header with one action → hero (headline naming the outcome, product screenshot or demo) → logos of real customers only → 3 feature rows that alternate split left/right, each with a real UI shot → how it works in 3 steps → pricing (if public) → FAQ → final call to action → footer.

### Portfolio, personal, creative
Intro with name, role and one line, plus a portrait or signature work → selected work grid (large thumbnails, 2 columns) → one featured case study → about with photo → contact → footer.

### Event or campaign
Hero with date, place, one action and the key visual → what / why → schedule or agenda (timeline) → speakers or lineup (photos) → venue with map → tickets or register → FAQ → footer.

### Small online store
Header with search and cart → hero with one collection → category tiles with photos → best sellers grid → value strip (shipping, returns, payment) with icons → story → footer with policies.

### Organization, school, government, NGO
Header with clear navigation → hero with mission and the 2 most-used tasks → task tiles with icons → news or updates (cards with dates) → stats only from real sources → contact and location → footer with legal links.

### Docs, blog, content
Header with search → featured article (large image) → article list (title, date, excerpt, tag) → categories → newsletter (only if the user has one) → footer.

App screens and dashboards don't use a page blueprint. Start from shadcn blocks or a dashboard template (components.md).
