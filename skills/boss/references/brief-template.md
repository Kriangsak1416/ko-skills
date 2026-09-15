# Delegation brief template

The engineer starts with **zero** context from your conversation. It cannot see
the user's request, your plan, the other tasks, or anything you have read. Copy
this shape into the Agent `prompt` and fill every section — an omitted section
becomes an assumption the engineer invents.

````
## Goal
One sentence: what must be true when you are done.

## Context
- Project: <language, framework, package manager, how it is run>
- Where this fits: <the bigger change, and which part is yours>
- Already decided (do not revisit): <architecture, names, data shapes, libraries>
- Other agents are working in parallel on: <files/areas> — do not touch them.

## Files
- Edit: path/to/a.ts, path/to/b.ts
- Create: path/to/c.test.ts
- Read for context (do not edit): path/to/existing-pattern.ts
- Off limits: everything else.

## Requirements
1. <specific, checkable requirement>
2. <specific, checkable requirement>
3. Follow the pattern in <file:line> for <naming / error handling / test style>.

## Interfaces you must match exactly
```ts
// signatures, types, event names, table columns another task depends on
export function doThing(input: Input): Promise<Result>
```

## Verification
Run: `<exact command>`
Expected: `<what passing looks like>`
Do not report done until this passes.

## Out of scope
- <adjacent thing the engineer must not "improve">
- Do not commit, push, or change git history.
- Do not add dependencies without reporting it first.

## Report back
Use the report format in your agent definition. State partial/blocked honestly
with the real command output.
````

## Checklist before you send

- [ ] Could a competent stranger execute this with no other information?
- [ ] Are all file paths absolute or unambiguously repo-relative?
- [ ] Does any parallel task write the same file? (If yes → serialize or merge.)
- [ ] Is there an exact verification command?
- [ ] Are shared interfaces specified literally, not described?
- [ ] Is the boundary explicit — what must **not** be touched?

## Re-dispatch (work came back wrong)

Prefer `SendMessage` to the same agent — it keeps the codebase context it just
built. Be specific about the delta:

```
Not accepted yet. Concretely:
1. src/x.ts:44 — <what is wrong> → <what it must be instead>
2. The brief required <X>; the diff does not do it.
3. `npm test` fails: <paste output>

Fix exactly these, re-run `<command>`, and report the actual output.
Change nothing else.
```

Start a fresh agent instead when the original brief was wrong, or when the
engineer's context is polluted by a long chain of failed attempts.
