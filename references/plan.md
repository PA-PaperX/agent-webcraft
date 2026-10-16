# Plan

A plan records decisions so the implementer, possibly another agent with less context, does not have to make them again. It is not a draft of the code. Plans that contain the code take several times longer to write and drift from what actually gets built.

## What a plan contains
- **Files and routes** to create or change, with one line each on why.
- **Interfaces:** component props, function signatures, data shapes, API routes, DB tables and columns.
- **Choices with reasons:** library, pattern, server or client boundary, state location. One line each, citing the docs note where it applies.
- **Tests:** test names and assertions, or for UI, the states to check (loading, empty, error, long text, mobile).
- **Verify commands** and what passing looks like.
- **Review focus:** up to 5 inputs or failure modes the brief implies but no test covers yet, such as an empty cart, a slow network, a Thai name with tone marks, or an expired session. Give each one an owner task.

Include a code body only for an algorithm the interfaces do not determine.

## Size check
If the plan is longer than the brief section it implements, it is probably transcribing code. Cut it back to decisions.

## Into tasks
- One task covers one checkable outcome and fits in one working session.
- Each task has acceptance checkboxes that a reviewer can tick from evidence alone.
- Create tasks with `python <skill>/scripts/board.py new "<title>" --area <area> --accept "..." --accept "..."`.
- Order tasks so the app stays runnable after each one.
- Put cross-cutting work (design tokens, auth, data model) first.

## Approval
Small plans live in the task file and are covered by the brief approval. A Feature or Project plan is shown to the user as a short summary in their language before building starts.
