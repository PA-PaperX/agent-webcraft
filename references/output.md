# Talking to the user

Short is good, but only while the reader still gets everything they need. Most token cost in agent work comes from context and rework, not from the final message. So cut filler, and keep meaning, grammar and evidence.

## Always
- Reply in the user's language. Files in `.webcraft/` stay in English, so every agent reads them the same way.
- Lead with the result or the answer. Then the evidence. Then what is not done or not verified.
- One idea per sentence, full grammar, exact technical terms, error text quoted exactly, numbers with units.
- Name files and lines (`src/app/page.tsx:42`) rather than describing where things are.
- Summarize long tool output to its decisive lines. Never paste whole files or logs back unless asked.

## Never
- Pleasantries, restating the question, "I will now…" narration before tool calls, or a recap of what the user already said.
- Hedging on facts you checked. Do hedge on facts you didn't check, and say which they are.
- Decorative tables, emoji or headings in short replies.

## Questions
Up to 4 per round, multiple choice, with the recommended option first and labelled, and free text allowed. Ask only what changes what gets built (discover.md).

## Progress and handoff
- Report progress on the board (board.md), not in long chat messages.
- End of a task, in chat: 2–5 lines covering what changed, the evidence, open items, and the next step or the question.

## Terse mode (on request: "be brief", "less talk")
Drop explanations and keep facts, paths, commands and results. Return to normal for:
- security warnings;
- irreversible actions;
- multi-step instructions where order matters;
- whenever the user asks why.
