# Icons

UI icons are SVG from one icon family, never emoji. Emoji render differently on every OS, can't take design-token colors or stroke widths, and carry inconsistent meaning for screen readers. Emoji are fine inside user content, not as interface icons.

## Look up what's current, every time
Icon libraries ship new icons and majors often, and new families appear. Don't rely on a remembered list:
- `python <skill>/scripts/icons.py search "<concept>" [--prefix lucide,tabler,ph]`: searches 200+ open icon sets live (Iconify API) and shows the exact icon names.
- `python <skill>/scripts/icons.py sets --prefix lucide,tabler,ph,heroicons`: icon count, license and grid for each set.
- `python <skill>/scripts/latest.py lucide-react @phosphor-icons/react ...`: latest version, license, publish date, weekly downloads and known advisories for the framework packages.
- `detect_stack.py` reports which icon packages the project already uses. **An existing family wins** unless the redesign brief says otherwise.

## Choose a family from the design direction
The starting points below follow style-catalog.md. Confirm them with `icons.py search` for the concepts the brief needs. Coverage gaps are the usual reason to switch.

| Direction | Starting family | Why |
|---|---|---|
| Clean SaaS, Dev dark, Retail | Lucide (stroke 2 or 1.5) | neutral line style, very wide framework support |
| Dashboard dense | Lucide or Tabler | Tabler has the widest coverage of outline icons |
| Editorial, Premium calm, Portfolio | Phosphor (thin or light) | multiple weights match fine typography |
| Warm local, Playful pop | Phosphor (regular, duotone or fill) | rounded and friendly; weights for emphasis |
| Institutional trust | Material Symbols or Heroicons | familiar metaphors, conservative |
| Neo-brutalist | Phosphor bold or Tabler with thick stroke | heavy and graphic |
| Brand logos (any direction) | Simple Icons (CC0) or svgl via the 21st CLI (`21st logo <brand>`) | official marks; follow each brand's trademark rules |

## Integrate (in order of preference)
1. **The family's package for the framework,** for example `lucide-react`, `@lucide/svelte`, `@tabler/icons-react`, `@phosphor-icons/react` or `@heroicons/react`. Import icons one by one so they tree-shake. Check the package name for the stack with `latest.py`; names differ per framework.
2. **Build-time Iconify** (any set, works offline in production), for example via an unplugin or Tailwind plugin. Look up the current integration for the stack in Iconify's docs.
   Avoid runtime fetching from the public Iconify API in production. It's a network dependency and a privacy leak.
3. **A copied SVG file** for a handful of icons or custom ones: `icons.py get lucide:coffee --out src/icons/coffee.svg`.

Avoid icon fonts in new projects: they flash, are hard to make accessible, and ship every glyph.

## Rules
- **One family per product,** plus a brand-logo set if needed. Keep the same stroke width, corner style and grid (usually 24).
- **Size from a scale tied to type** (16, 20, 24). Use `currentColor` so icons follow text and token colors. Align optically with the text next to them.
- **Accessibility:** decorative icons get `aria-hidden="true"`. An icon-only button needs an accessible name (`aria-label`, or visually hidden text). Navigation icons get a text label unless the meaning is universal.
- **Thai labels** next to icons need the Thai line-height. Check the vertical centering in screenshots.
- **License:** most UI sets are MIT, ISC or Apache-2.0. Some sets require attribution (CC BY). Brand logos are trademarks. Record the family and its license in DESIGN.md.
- **Don't import a whole library** (`import * as Icons`), and don't ship an unused icon set.
