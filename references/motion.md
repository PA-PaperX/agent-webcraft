# Motion

Motion should explain change: what appeared, where it came from, what responds to the user. Decoration that slows down a task, hides content until JS runs, or moves without the user asking costs more than it earns.

## Look up what's current, every time
Animation libraries rename, relicense and add platform features often. For example, `framer-motion` became `motion`, and GSAP is free to use under its own license, which is not MIT. Native browser features also keep reaching Baseline. Before choosing:
- `python <skill>/scripts/latest.py motion gsap lottie-react @rive-app/react-canvas ...`: latest version, **license**, publish date, downloads, advisories and llms.txt for each candidate.
- `python <skill>/scripts/latest.py --baseline view-transitions scroll-driven-animations`: whether a native feature is safe to rely on (Baseline), or needs to be progressive enhancement.
- Read the chosen library's docs for the installed version (docs-map.md). Import paths and APIs move between majors.
- `detect_stack.py` lists the motion libraries already installed. **Reuse what the project has** unless the need is clearly outside its strengths.

## Choose the lightest tool that does the job
1. **CSS transitions and keyframes, or Tailwind utilities:** hover, focus, press, enter and exit of simple elements, skeletons. No JS cost.
2. **Native platform APIs:** View Transitions for page and state changes, the Web Animations API, CSS scroll-driven animations. Check Baseline. If a feature isn't Baseline, it must degrade to no animation, not to broken layout.
3. **Framework built-ins:** Svelte transitions and `animate`, Vue `<Transition>`.
4. **Motion** (React, Vue, vanilla): component state, layout and shared-element animations, gestures, exit animations.
5. **GSAP and its plugins:** timelines, sequenced storytelling, scroll-driven scenes, text splitting. Check its license terms for the project.
6. **Designer-made assets:** Lottie or dotLottie (After Effects exports), Rive (interactive, state-machine animations). The designer's tool decides between them.
7. **Smooth-scroll libraries** (such as Lenis): only when the brief asks for that feel. Never hijack scroll speed or direction, and turn it off under reduced motion.
8. **3D and WebGL** (React Three Fiber, three.js, shaders): only for Immersive or showcase directions, with a performance budget and a static fallback.

Shortlist two candidates, compare them with `latest.py`, then record the choice and its license in DESIGN.md.

## Timing and feel (put these in DESIGN.md as motion tokens)
| Kind | Duration | Easing |
|---|---|---|
| Micro (hover, press, toggle) | 100–200 ms | ease-out |
| UI transitions (menus, dialogs, tabs) | 200–300 ms | ease-out in, ease-in out |
| Larger moves (page, hero reveal) | 300–600 ms | ease-in-out or a gentle spring |
| Direct manipulation (drag, swipe) | follows the finger | spring |

Each direction in style-catalog.md implies a motion level: none or subtle for Dashboard, Institutional and Premium; moderate for SaaS, Warm local and Retail; expressive for Playful, Brutalist, Portfolio and Immersive.

## Rules
- **Animate `transform` and `opacity`.** Animating width, height, top or left causes layout work and jank on mid-range phones.
- **`prefers-reduced-motion: reduce`:** remove non-essential motion, replace movement with an instant change or a short fade, and stop autoplay and parallax.
- **No flashing more than 3 times per second.** No motion as the only carrier of information.
- **Content is visible without JS.** Server-rendered content must not depend on an entrance animation to appear, for SEO and accessibility.
- **Next.js:** animated components are client components. Keep them at the leaves, and keep server components static.
- **One or two signature moments per page** (design.md guardrail). Everything else stays quiet.
- **Verify on a throttled mobile profile.** Watch for layout shift caused by animations in the screenshots.
