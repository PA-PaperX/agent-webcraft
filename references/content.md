# Content: real, sample, mockup, or designed placeholder

Two failures to avoid:
- **A fake page:** invented reviews, a made-up phone number, photos of another café, presented as real. It misleads visitors, can break consumer law, and looks finished, so nobody fixes it.
- **An empty page:** every block says "waiting for the owner" and every button is disabled. It is honest but useless, and it looks broken.

**The user chooses a mode for every missing item** in Discover (discover.md) and the choice is recorded in BRIEF. Each mode has its own rules.

## 1. Real
Supplied by the user or the owner. Write facts such as the phone, LINE ID, hours and address into BRIEF (Content or Tech), so the gate can match them.

## 2. Sample (photos and items only)
Use this when the user wants the page to look finished with example photos and items.
- **Allowed:** mood and product photos (free license; never presented as the actual named place), example menu or product items with plausible prices, example copy.
- **Mark** with a small "ภาพตัวอย่าง" or "ตัวอย่าง" badge, one per section.
- **List** under BRIEF **Sample content (approved)**.
- **Not for facts.** Phone, LINE, hours, address, reviews and ratings are never samples. Use mockup or placeholder for those.

## 3. Mockup (the user's choice, for judging the design before data exists)
Some users want to see the whole site as it will look, contact block and reviews included, before the owner sends anything. That is fine as a **mockup** with these rules:
- **Values are obviously dummy and consistent.** Phone `080-000-0000`, LINE `@yourshop`, hours `00:00–00:00` or the user's guess, reviewer names like "ลูกค้าตัวอย่าง", rating text with "(ตัวอย่าง)". Never a value that could belong to a real person or shop.
- **All mockup values live in one content file,** each marked with a comment `webcraft-mockup`.
- **A visible notice:** while any mockup remains, the page shows a small fixed label "ตัวอย่างดีไซน์ · ข้อมูลยังไม่ใช่ของจริง" (Mockup), so a shared screenshot can't pass as the real site.
- **List** every item under BRIEF **Mockup content (replace before launch)**.
- **Before launch** `design_lint.py --release` fails until every mockup item is replaced and the notice is removed.

## 4. Designed placeholder
Use this when the user wants no dummy values. The placeholder keeps the **final layout and look**:
- **Photo frame:** same size, ratio and corners as the real photo. Follow the placeholder spec in DESIGN.md Component style (Images): surface mixed with 12% primary, a line icon and a short muted label. Never a dark block, heavy gradient or grey dashed box.
- **Action buttons:** keep their final label and style ("โทรหาร้าน", "ดูเส้นทาง", "แอดไลน์"). Placeholder text never goes inside a button. While the link is missing, point the button to the section that will hold it, or hide that one action. Never ship a page whose main action does nothing.
- **Facts such as hours or an address:** show the final layout with `—`, plus **one** short note per section ("ข้อมูลจริงเร็วๆ นี้"), not on every line.
- **List** every placeholder under BRIEF **Content to be supplied** and in STATE under **Known issues**.

## What `design_lint.py` checks
- **Ratings, review counts, phone numbers and LINE IDs:** pass when they're real (written in BRIEF outside the Sample and Mockup sections). They pass as a warning when BRIEF's Mockup section lists them. Otherwise they're an error.
- **Stock photos:** need BRIEF Sample content to approve photos.
- **Mockup notice:** required on the page while BRIEF lists mockup content.
- **Placeholder notes:** more than 4 visible on a page is an error.
- **`--release`:** errors on any mockup, sample or placeholder that's still listed.

## Copy
- Write specific copy from the brief: what the place or product is, for whom, where and when.
- When the owner edits content, keep Thai and English text in a single content file, with sample, mockup and placeholder items easy to find.
