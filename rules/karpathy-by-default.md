# Karpathy guidelines by default

Apply the `karpathy-guidelines` skill to all coding work automatically. The user
does not have to type `/karpathy-guidelines`.

**Invoke `Skill(karpathy-guidelines)` before you start** whenever you are about
to write, modify, refactor, or review code. Do it before the first edit, not
after. If the same session also runs the `boss` skill, load this one too — the
guidelines govern how the work is judged, `boss` governs who does it.

**Skip it** when:

- the request is a question, an explanation, or a read-only investigation
- the change is a one-line typo or mechanical rename with no judgment involved
- the user says to skip it

The skill biases toward caution over speed; for genuinely trivial edits, use
judgment rather than ceremony.

**When delegating**, carry the substance into the brief — implementation
subagents do not inherit the skill. Every subagent brief for code work should
state: minimum code that solves the problem, touch only what the request
requires, match existing style, and a concrete verification step the agent must
run before reporting done.
