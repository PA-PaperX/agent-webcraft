# Agent WebCraft

A web-development method for coding agents, packaged as an [Agent Skill](https://agentskills.io). Install it once, and any agent that reads `SKILL.md` (Claude Code, Codex, Antigravity, Cursor, Gemini CLI, OpenCode and others) builds websites the same disciplined way:

- **Interviews before building.** It scans the repo, then asks in short multiple-choice rounds until the work is fully specified, and writes a brief that you approve before any code is written.
- **Chooses the stack with reasons.** It asks about runtime (Node, Bun, Deno), framework (Next.js, Elysia, Hono and others) and database, with a reason for each option tied to the job. Each option is checked against what's already installed on the machine and used in the project.
- **Grounds code in the right docs.** It detects the exact installed versions and reads the docs that ship with them (for example `node_modules/next/dist/docs`) or the official `llms.txt`, instead of trusting training data that lags behind releases.
- **You choose the design from real options.** It asks for sites you like and extracts their tokens. Then it shortlists 8–12 styles from a library of about 110: 16 built-in presets with Thai fonts, design systems of popular sites such as Airbnb, Stripe, Notion, Linear and Spotify (VoltAgent/awesome-design-md), and Aura design systems. It renders them side by side with your own Thai copy and contrast checks. You then pick the component style: buttons, cards, menus, image shapes and one signature element, or your own idea. Every section follows a page blueprint taken from a reference site, a full-page template or a recipe for the business type. Everything is saved in the Google Stitch `DESIGN.md` format.
- **Strict where it matters, so smaller models follow too.** Script gates, not just instructions, catch hard-coded colors, missing design records, empty-looking pages and invented content. Missing content can be shown as samples, a full mockup with a visible notice, or designed placeholders, as the user chooses, and `design_lint.py --release` blocks launch until mockups are replaced. `board.py done` refuses UI work until `design_lint.py` is clean and the critique and benchmark passes are logged. A critique pass compares screenshots with the reference sites.
- **Sources components carefully.** The order is: the project's own components, then shadcn/ui, 21st.dev, React Bits, and Magic UI / Aceternity / Origin UI. Each one is checked for stack fit, license, accessibility and performance.
- **Real SVG icons and purposeful motion.** It picks one icon family to match the design and searches 200+ open icon sets live (Iconify). For motion it reaches for the lightest tool first: CSS, then native View Transitions, then Motion, GSAP, Lottie or Rive. Timing tokens and reduced-motion rules are built in.
- **Always current.** Before adding a library, it checks live facts: latest version, license, publish date, downloads and known security advisories (npm registry + deps.dev). For browser features it checks Baseline status (web-features). Lists in the skill are starting points; live data decides.
- **Verifies by looking.** Typecheck, lint, tests and build, then screenshots at 390, 768 and 1440 px that the agent actually opens and inspects.
- **Lets several agents share one project.** Everything an agent learns goes into plain files in `.webcraft/`, with a task board (`board.py`) for claiming, reporting with evidence, and a read-only kanban on localhost.

The first session on a project is deliberately thorough. Later sessions read a short `STATE.md` and one task file, so they stay cheap.

## Install

Clone into the skills folder of each agent you use, or clone once and link the others:

```bash
git clone https://github.com/<your-github-username>/agent-webcraft ~/.claude/skills/agent-webcraft   # Claude Code
git clone https://github.com/<your-github-username>/agent-webcraft ~/.agents/skills/agent-webcraft   # Codex and other Agent Skills readers
```

On Windows, link instead of cloning twice:
`mklink /J "%USERPROFILE%\.agents\skills\agent-webcraft" "%USERPROFILE%\.claude\skills\agent-webcraft"`

**Requirements:**
- Python 3.9+ (the scripts use only the standard library).
- Node.js only for the optional Playwright screenshot fallback.

## Use

Ask your agent for web work as usual, for example "build a landing page for my café" or "fix the header on mobile". The skill triggers on web tasks and on any repo with a `.webcraft/` folder.

To set up the shared board yourself:

```bash
python <skill>/scripts/board.py init      # .webcraft/ + a short block in AGENTS.md
python <skill>/scripts/board.py serve     # http://127.0.0.1:8765
```

| Script | Purpose |
|---|---|
| `scripts/detect_stack.py [dir] [--json]` | framework, exact versions, Tailwind major and config style, shadcn setup, docs on disk and online |
| `scripts/board.py init / new / claim / report / done / list / check / archive / serve` | shared task board for several agents |
| `scripts/styles.py list / shortlist / preview / export / templates` | style library: score, shortlist, preview with your copy, export to DESIGN.md, open full-page templates |
| `scripts/components.py preview / choose` | component style: 42 variants of buttons, cards, navigation, forms, tags, images and signature elements in your tokens; records the choice |
| `scripts/ref_extract.py <url>` | draft design tokens from a website you like |
| `scripts/design_lint.py [dir] [--release]` | gate: hard-coded colors, incomplete DESIGN.md, buttons or images that don't match the chosen component style, pages with too few visuals, work off the board, missing critique or a benchmark without a real website, invented content; `--release` also blocks leftover mockups and placeholders |
| `scripts/env_check.py [dir] [--latest]` | what's installed on the machine (runtimes, package managers, Docker, databases, CLIs), what the project uses, and today's runtime versions |
| `scripts/latest.py <pkg>... [--root dir]` / `--baseline <feature>` | live version, license, publish date, downloads and advisories for any npm package; Baseline status for browser features |
| `scripts/icons.py search / sets / get` | search and fetch SVG icons across 200+ open icon sets (Iconify API) |
| `scripts/shoot.py <url>` | screenshots at 3 viewport sizes via Playwright, for agents without a built-in browser |

## What gets created in your project

```text
AGENTS.md          + a short webcraft block (CLAUDE.md imports it)
.webcraft/
  BRIEF.md         approved scope
  DESIGN.md        chosen direction + tokens + component sources and licenses
  RULES.md         project rules and definition of done
  STATE.md         short current state, read first by every agent
  tasks/           one Markdown file per task: acceptance + log with evidence
  archive/         finished work
  preview/         style previews and extracted reference tokens (safe to delete)
```

All of it is plain Markdown in git, so teammates see it on GitHub too.

## Design principles

- **Method and tools are kept apart.** Tool names, docs URLs and component sources live in dated files (`references/tools.md`, `references/docs-map.md`). When something changes, one line changes.
- **No version facts in the core.** Anything that changes over time is looked up and cited.
- **Reasons instead of shouting.** Rules explain why, so capable models follow them without over-triggering.
- **Scripts enforce the rules that matter.** Weaker models skip prose, so brief approval, the design choice, tokens and honest content are checked by `design_lint.py` and the board gate.
- **Repeatable checks.** `evals/scenarios.md` lists 21 behaviors to rerun after a model or tool update.

## Deep guidance included for
Next.js + React + Tailwind + shadcn/ui · Vite + React · SvelteKit · Supabase. Other stacks use the general docs ladder.

---

## ภาษาไทย

Agent WebCraft คือ skill สำหรับ AI เขียนโค้ด ทำให้ AI ทุกตัวที่อ่าน `SKILL.md` ได้ เขียนเว็บด้วยวิธีเดียวกันอย่างมีระบบ:

- **เลือก stack อย่างมีเหตุผล:** ถามเรื่อง runtime (Node / Bun / Deno), framework (Next.js / Elysia / Hono ฯลฯ) และฐานข้อมูล พร้อมเหตุผลว่าแต่ละตัวเหมาะกับงานนี้อย่างไร และเช็กก่อนว่าเครื่องหรือโปรเจกต์มีอะไรอยู่แล้ว
- **สัมภาษณ์ก่อนลงมือ:** สแกนโปรเจกต์ก่อน แล้วถามเป็นรอบ รอบละไม่เกิน 4 ข้อแบบมีตัวเลือก จนได้ brief ที่ครบ และต้องให้คุณอนุมัติก่อนเขียนโค้ดเสมอ
- **อ้างอิงเอกสารตรงเวอร์ชัน:** อ่านเอกสารที่มากับแพ็กเกจที่ติดตั้งจริง หรือ `llms.txt` ทางการ แทนการเดาจากความรู้เก่า
- **ผู้ใช้เลือกดีไซน์เองจากตัวเลือกจริง:** ถามเว็บที่ชอบแล้วดึงสีและฟอนต์ให้ จากนั้นคัด 8–12 สไตล์จากคลังราว 110 แบบ (16 สไตล์ในตัวพร้อมฟอนต์ไทย, design system ของเว็บดังอย่าง Airbnb, Stripe, Notion, Spotify และ Aura) มาแสดงเทียบกันด้วยข้อความไทยของโปรเจกต์จริง พร้อมผลตรวจความต่างของสี แล้วให้เลือกสไตล์คอมโพเนนต์ (ปุ่ม การ์ด เมนู รูปทรงรูปภาพ และจุดเด่นเฉพาะตัว) อีกชั้น ทุกหน้าวางตามโครงหน้า (page blueprint) ที่พิสูจน์แล้วว่าใช้ได้
- **กฎเข้มที่สคริปต์บังคับได้:** AI รุ่นเล็กก็ต้องทำตาม ปิดงาน UI ไม่ได้ถ้ายังมีสี hardcode, DESIGN.md ไม่ครบ, หน้าเว็บโล่งไม่มีภาพ, placeholder เต็มหน้า, มีรีวิวที่แต่งขึ้น หรือยังไม่ได้บันทึกผล critique ส่วนข้อมูลที่ยังไม่มี ผู้ใช้เลือกได้ว่าจะใช้ตัวอย่าง, mockup ที่ดูสมจริง (มีป้ายบอก) หรือ placeholder และก่อนเปิดเว็บจริง `--release` จะไม่ยอมให้ผ่านจนกว่าจะแทนด้วยของจริง
- **เลือกคอมโพเนนต์อย่างระวัง:** เช็กความเข้ากันได้ สัญญาอนุญาต a11y และความเร็วก่อนใช้
- **ไอคอน SVG ไม่ใช่อีโมจิ:** เลือกชุดไอคอนเดียวให้เข้ากับดีไซน์ และค้นไอคอนสดจากกว่า 200 ชุด
- **Motion อย่างมีเหตุผล:** เริ่มจากเบาที่สุด (CSS → View Transitions → Motion/GSAP/Lottie/Rive) มีค่าเวลามาตรฐาน และรองรับผู้ใช้ที่ปิด motion
- **ข้อมูลล่าสุดเสมอ:** ก่อนเพิ่มไลบรารีจะเช็กเวอร์ชันล่าสุด สัญญาอนุญาต วันเผยแพร่ ยอดดาวน์โหลด และช่องโหว่ความปลอดภัยแบบสด ทุกเจ้า ทุกครั้ง
- **ตรวจงานด้วยตา:** จับภาพ 3 ขนาดจอแล้วเปิดดูจริงทุกครั้ง
- **รองรับเว็บภาษาไทย:** ฟอนต์ไทย, line-height, การตัดบรรทัด, วันที่ พ.ศ., PDPA
- **ทำงานเป็นทีมได้:** ข้อมูลทั้งหมดอยู่ใน `.webcraft/` มีกระดานงานให้ AI หลายตัวรับงานและรายงานพร้อมหลักฐาน และมีหน้าเว็บ localhost ให้คนดู

ครั้งแรกจะใช้โทเคนเยอะเพราะต้องเก็บข้อมูลให้ครบ ครั้งต่อๆ ไปอ่านแค่ STATE กับงานของตัวเอง จึงเบาและเร็ว

## License
[MIT](LICENSE)
