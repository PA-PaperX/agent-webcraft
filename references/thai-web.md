# Thai on the web

Thai stacks vowels and tone marks above and below the baseline, has no spaces between words, and uses the Buddhist calendar in everyday dates. Generic web defaults handle all three badly.

## Language and fonts
- Set `<html lang="th">` (or `lang` on Thai sections of a bilingual page). Browsers pick fonts and line breaking by language.
- Pair every Latin typeface with a Thai one of similar structure, such as loopless sans with loopless sans or serif with serif. Good Google Fonts options include:
  - **Sans:** Noto Sans Thai, IBM Plex Sans Thai, Anuphan, Sarabun, Prompt, Kanit, Mitr, Bai Jamjuree, Chakra Petch
  - **Looped (traditional, friendly):** IBM Plex Sans Thai Looped, Sarabun, Mali
  - **Serif:** Noto Serif Thai, Trirong, Taviraj
- Load the `thai` subset as well as `latin`. In Next.js: `next/font/google` with `subsets: ['thai', 'latin']`. Use `font-display: swap`.
- Put the Thai font first in the stack for Thai pages. Otherwise Latin metrics drive line height and Thai marks get clipped.

## Spacing and line breaking
- Body line-height around 1.6–1.8. Thai stacked marks clip at the 1.2–1.4 that suits Latin text.
- Don't apply letter-spacing or tracking to Thai text. It separates vowels and tone marks from their consonants. Apply tracking only to Latin elements.
- Browsers break Thai lines with a dictionary. Avoid `word-break: break-all`, which splits inside words. For long compound words in narrow UI, insert `<wbr>` at real word boundaries.
- Prefer left alignment. Browser justification of Thai is inter-character and looks uneven.
- Don't put spaces between Thai words in copy. A space marks a phrase or sentence break.
- `text-transform: uppercase` and small caps do nothing for Thai, so a design that relies on them needs a different emphasis (weight, size or color).

## Dates, numbers, currency
- `new Intl.DateTimeFormat('th-TH', { dateStyle: 'long' })` formats Buddhist-era dates (พ.ศ.).
- Use `th-TH-u-ca-gregory` when the Gregorian year (ค.ศ.) is required.
- Currency: `new Intl.NumberFormat('th-TH', { style: 'currency', currency: 'THB' })`.
- Thai digits only on request: `th-TH-u-nu-thai`.
- Store dates in ISO/UTC; format at display time. Thailand is UTC+7 with no daylight saving.

## Content and legal
- Thai and English versions of the same text differ a lot in length, so test layouts with both.
- If the site collects personal data, plan a consent and privacy notice under Thailand's PDPA. Flag it in the brief; this is not legal advice.
