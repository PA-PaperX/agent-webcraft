# Style library

`scripts/styles.py` reads three sources, all in the Google Stitch DESIGN.md format (tokens in YAML front matter). Each style can be listed, scored, previewed with the project's copy, and exported to `.webcraft/DESIGN.md`. Remote sources are fetched live and cached for 7 days; pass `--refresh` for the newest.

| Source | What | Notes |
|---|---|---|
| `builtin` | 16 presets in this skill's `styles/` folder | Real axis scores, Thai font pairs, icon and motion hints. All pass WCAG AA. |
| `brands` | ~80 design systems of popular sites, e.g. Apple, Airbnb, Stripe, Notion, Linear, Vercel, Spotify, Starbucks, Nike, Tesla, Uber (github.com/VoltAgent/awesome-design-md, MIT) | Community reconstructions, not official. Brand fonts are often not free, and some colors fail contrast. The preview shows both. Axis scores are estimated. |
| `aura` | 21 design systems and 107 full-page templates (github.com/PA-PaperX/Aura-Full) | Use `templates` / `template` to open whole pages when the user wants to see a complete site. Axis scores are estimated. |

## Built-in presets (W P D T E)
| id | Axes | Fits |
|---|---|---|
| clean-saas | 2 2 3 3 2 | product sites, tools |
| editorial | 3 2 2 3 3 | blogs, magazines |
| warm-local | 5 3 2 2 3 | cafés, restaurants, local shops, tourism |
| playful-pop | 4 5 2 1 5 | youth brands, events, creators |
| premium-calm | 2 1 1 4 3 | luxury, hotels, real estate |
| dev-dark | 1 2 4 3 4 | developer tools, AI products |
| dashboard-dense | 1 1 5 4 1 | admin, analytics |
| institutional-trust | 2 1 3 5 1 | government, hospitals, banks, schools |
| neo-brutalist | 2 4 2 1 5 | campaigns, indie products |
| immersive-3d | 2 3 2 2 5 | launches, showcases, games |
| creative-portfolio | 3 4 1 2 5 | designers, studios |
| retail-clear | 3 3 4 4 3 | e-commerce, booking |
| wellness-soft | 4 2 1 3 2 | spa, yoga, beauty, clinics |
| eco-organic | 4 2 2 3 2 | farms, handmade, eco brands |
| b2b-corporate | 2 1 3 4 2 | consulting, law, engineering |
| nightlife-neon | 3 5 2 1 5 | bars, music, events |

Add a preset by copying a file in `styles/` and keeping the same keys (`x-axes`, `x-thai`, `x-tags`, `x-icons`, `x-motion`).
